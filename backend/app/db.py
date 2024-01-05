from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from kheritageapi.models import PalaceDetail, PalaceImageItem, PalaceVideoItem
from bson.objectid import ObjectId
from pymongo import MongoClient
from typing import Optional
import requests
import gridfs
import time
import os


class LumaDB:
    def __init__(self, mongo_client_param: MongoClient = None) -> None:
        if mongo_client_param is None:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            self.mongo_client = MongoClient(mongo_uri)
        else:
            self.mongo_client = mongo_client_param
        self.db = self.mongo_client.luma

        self.palace_db = self.db.palaces
        self.media_meta_db = self.db.media_meta
        self.media_db = gridfs.GridFS(self.db, collection="images")
        self.thumbnail = gridfs.GridFS(self.db, collection="thumbnails")

    @staticmethod
    def download_file(url: str, max_retries: int = 3, retry_delay: int = 5) -> Optional[bytes]:
        server_error_strikes = 0
        for attempt in range(max_retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.content
            except HTTPError as e:
                if 400 <= e.response.status_code < 600:
                    server_error_strikes += 1
                if server_error_strikes >= 3:
                    return None
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except (ConnectionError, Timeout, RequestException) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise e

        raise Exception(f"Failed to download {url}")

    def save_file(self, url: str, overwrite: bool = False) -> Optional[ObjectId]:
        if not overwrite:
            existing = self.media_meta_db.find_one({"url": url})
            if existing:
                return existing["_id"]
        file_content = self.download_file(url)
        if file_content:
            return self.media_db.put(file_content, url=url)
        else:
            return None

    def get_file(self, image_id: ObjectId):
        # check if image_id is valid
        if not self.media_db.exists(image_id):
            return None
        response = self.media_db.get(image_id)
        file = response.read()
        file_extension = response.url.split(".")[-1]

        return file, file_extension

    def save_thumbnail(self, image: bytes, entry_id: ObjectId) -> None:
        self.thumbnail.put(image, _id=entry_id)

    def get_thumbnail(self, entry_id: ObjectId) -> Optional[bytes]:
        if not self.thumbnail.exists(entry_id):
            return None
        response = self.thumbnail.get(entry_id)
        return response.read()

    def save_detailed_image(self, image: PalaceImageItem) -> ObjectId:
        saved_image = self.save_file(image.url)
        document = {
            "media": saved_image,
            "name": {
                "ko": image.name_ko,
                "en": image.name_en,
                "ja": image.name_ja,
                "zh": image.name_zh,
            },
            "explanation": {
                "ko": image.explanation_ko,
                "en": image.explanation_en,
                "ja": image.explanation_ja,
                "zh": image.explanation_zh,
            },
        }
        return self.media_meta_db.insert_one(document).inserted_id

    def get_detailed_image(self, image_id: ObjectId, language: str) -> Optional[dict]:
        result = self.media_meta_db.find_one({"_id": image_id})
        if "media" in result:
            return {
                "name": result["name"][language],
                "explanation": result["explanation"][language],
                "media": str(result["media"]),
            }
        else:
            return None

    def save_detailed_video(self, video: PalaceVideoItem) -> ObjectId:
        document = {
            "name": {
                "ko": video.name_ko,
                "en": video.name_en,
                "ja": video.name_ja,
                "zh": video.name_zh,
            },
            "video": {
                "ko": self.save_file(video.url_ko),
                "en": self.save_file(video.url_en),
                "ja": self.save_file(video.url_ja),
                "zh": self.save_file(video.url_zh),
            },
        }
        return self.media_meta_db.insert_one(document).inserted_id

    def get_detailed_video(self, video_id: ObjectId, language: str) -> Optional[dict]:
        result = self.media_meta_db.find_one({"_id": video_id})
        if "video" in result:
            video = str(result["video"][language])
            # if video is not found, try other languages
            if video == "None":
                for lang in ["ko", "en", "ja", "zh"]:
                    video = str(result["video"][lang])
                    if video != "None":
                        break
            return {
                "name": result["name"][language],
                "video": video,
            }
        else:
            return None

    def save_palace(self, palace: PalaceDetail, overwrite: bool = False) -> ObjectId:
        if not overwrite:
            existing = self.palace_db.find_one({"serial_number": palace.serial_number})
            if existing:
                return existing["_id"]

        with self.mongo_client.start_session() as session:
            try:
                session.start_transaction()

                saved_thumbnail = self.save_file(palace.thubnail)
                saved_main_image = [self.save_file(image) for image in palace.main_image if image]
                saved_detail_image = [self.save_detailed_image(image) for image in palace.detail_image_list]
                saved_main_video = [self.save_file(video) for video in palace.main_video if video]
                saved_detail_video = [self.save_detailed_video(video) for video in palace.detail_video_list]

                document = {
                    "serial_number": palace.serial_number,
                    "palace_code": palace.palace_code,
                    "detail_code": palace.detail_code,
                    "thumbnail": saved_thumbnail,
                    "name": {
                        "ko": palace.name_ko,
                        "en": palace.name_en,
                        "ja": palace.name_ja,
                        "zh": palace.name_zh,
                    },
                    "explanation": {
                        "ko": palace.explanation_ko,
                        "en": palace.explanation_en,
                        "ja": palace.explanation_ja,
                        "zh": palace.explanation_zh,
                    },
                    "main_image": saved_main_image,
                    "main_video": saved_main_video,
                    "detail_image": saved_detail_image,
                    "detail_video": saved_detail_video,
                }

                result = self.palace_db.insert_one(document).inserted_id
                session.commit_transaction()
                return result
            except Exception as e:
                session.abort_transaction()
                raise e

    @staticmethod
    def building_mongo_to_dict(result: dict, language: str) -> dict:
        return {
            "name": result["name"][language],
            "url": result["url_slug"],
            "explanation": result["explanation"][language],
            "palace_code": result["palace_code"],
            "thumbnail": str(result["thumbnail"]),
            "main_image": [str(image) for image in result["main_image"]],
            "main_video": [str(video) for video in result["main_video"]],
            "detail_image": [str(image) for image in result["detail_image"]],
            "detail_video": [str(video) for video in result["detail_video"]],
        }

    @staticmethod
    def building_mongo_to_preview(result: dict, language: str) -> dict:
        return {
            "name": result["name"][language],
            "url": result["url_slug"],
            "palace_code": result["palace_code"],
            "explanation": result["explanation"][language],
            "thumbnail": str(result["thumbnail"]),
        }

    def get_building(self, palace_id: ObjectId, language: str) -> Optional[dict]:
        result = self.palace_db.find_one({"_id": palace_id})

        if result:
            return self.building_mongo_to_dict(result, language)
        else:
            return None

    def get_building_from_slug(self, slug: str, language: str) -> Optional[dict]:
        result = self.palace_db.find_one({"url_slug": slug})

        if result:
            return self.building_mongo_to_dict(result, language)
        else:
            return None

    def get_palace_elements(self, palace_id: int, language: str) -> Optional[list]:
        # find all with the same palace_code in the dict of object id and name in the language
        result = self.palace_db.find({"palace_code": palace_id})

        return_arr = []
        for palace in result:
            return_arr.append({
                "name": palace["name"][language],
                "id": str(palace["_id"]),
                "url": palace["url_slug"]
            })
            # sort by alphabetically
        return_arr.sort(key=lambda x: x["name"])
        return return_arr

    def get_building_random(self, language: str, palace_id: str = None, count: int = 20) -> list[dict]:
        if palace_id:
            # get all buildings with the same palace_code and sort by detail_code
            result = self.palace_db.find({"palace_code": int(palace_id)}).sort("detail_code", 1)
            return [self.building_mongo_to_preview(palace, language) for palace in result]
        else:
            result = self.palace_db.aggregate(
                [
                    {"$sample": {"size": count}},
                ]
            )

        return [self.building_mongo_to_preview(palace, language) for palace in result]
