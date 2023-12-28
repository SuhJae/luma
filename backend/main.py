from fastapi import FastAPI, HTTPException, status
from bson.objectid import ObjectId
import bson.errors

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from typing import Optional
from db import LumaDB
from search import ElasticsearchClient

db = LumaDB()
es = ElasticsearchClient(lumaBD=db)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

serviced_language = ["ko", "en", "ja", "zh"]


def validate_id(object_id: str) -> Optional[ObjectId]:
    try:
        ObjectId(object_id)
    except bson.errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")
    return bson.ObjectId(object_id)


def validate_language(language: str) -> None:
    if language not in serviced_language:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid language: {language}")


def validate_palace_id(palace_id: str) -> Optional[int]:
    if palace_id.isnumeric():
        palace_id = int(palace_id)
        if palace_id in range(1, 6):
            return palace_id
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid palace id")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid palace id")


@app.get("/")
def read_root():
    return FileResponse('static/index.html')


@app.get("/api/v1/media/{media_id}")
def get_media(media_id: str):
    media_id = validate_id(media_id)
    media, file_extension = db.get_file(media_id)
    if media:
        if file_extension in ["png", "jpg", "jpeg"]:
            return Response(content=media, media_type=f"image/{file_extension}")
        else:
            return Response(content=media, media_type=f"video/{file_extension}")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")


@app.get("/api/v1/photo/")
def get_photo(photo_id: str, language: str):
    validate_language(language)
    photo_id = validate_id(photo_id)
    photo = db.get_detailed_image(photo_id, language)
    if photo:
        return photo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")


@app.get("/api/v1/video/")
def get_video(video_id: str, language: str):
    validate_language(language)
    video_id = validate_id(video_id)
    video = db.get_detailed_video(video_id, language)
    if video:
        return video
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


@app.get("/api/v1/palace/")
def get_palace(palace_id: str, language: str):
    validate_language(language)
    palace_id = validate_id(palace_id)
    palace = db.get_palace(palace_id, language)
    if palace:
        return palace
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palace not found")


@app.get("/api/v1/search/")
def search(keyword: str, language: str, palace_id: str = None, cursor: int = 1):
    validate_language(language)
    # check for malicious keyword
    if keyword.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid keyword")
    if len(keyword) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search keyword too long")

    result = es.search_article(query=keyword, language=language, palace_id=palace_id, cursor=cursor)

    hits = []
    for hit in result['hits']['hits']:
        hits.append({
            "id": hit['_id'],
            "title": hit['_source']['title'],
            "text": hit['_source']['text'],
        })

    response = {
        "hits": result['hits']['total']['value'],
        "articles": hits
    }

    return response


@app.get("/api/v1/autocomplete/")
def autocomplete(keyword: str, language: str):
    validate_language(language)
    # check for malicious keyword
    if keyword.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid keyword")
    if len(keyword) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search keyword too long")

    result = es.autocomplete(query=keyword, language=language)

    suggestions = []
    for hit in result['suggest']['suggestion'][0]['options']:
        suggestions.append(hit['_source']['title'])

    response = {
        "suggestions": suggestions
    }

    return response


@app.get("/api/v1/random/")
def random_article(language: str, palace_id: str = None):
    validate_palace_id(palace_id)
    validate_language(language)
    article = db.get_palace_random(language, palace_id)
    if article:
        return article
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No article found")
