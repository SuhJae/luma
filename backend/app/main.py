from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi import FastAPI, Request, HTTPException, status
from bson.objectid import ObjectId
import bson.errors
from typing import Optional
import json

from app.db import LumaDB
from app.search import ElasticsearchClient

db = LumaDB()
es = ElasticsearchClient(lumaBD=db)
app = FastAPI()
app.mount("/assets", StaticFiles(directory="app/static/assets"), name="assets")

serviced_language = ["ko", "en", "ja", "zh"]
ui_language = {}
for lang in serviced_language:
    with open(f"app/assets/lang/{lang}.json", "r", encoding="utf-8") as f:
        ui_language[lang] = json.load(f)


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


@app.get("/api/v1/media/{media_id}")
async def get_media(request: Request, media_id: str):
    media_id = validate_id(media_id)
    try:
        media, file_extension = db.get_file(media_id)
    except TypeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    if file_extension in ["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "ico"]:
        return Response(content=media, media_type=f"image/{file_extension}")
    elif file_extension in ["mp4", "webm", "ogg"]:
        range_header = request.headers.get('Range')
        if range_header:
            return await partial_file_response(media, range_header, f"video/{file_extension}")
        else:
            return Response(content=media, media_type=f"video/{file_extension}")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media format not supported")


async def partial_file_response(data: bytes, range_header: str, media_type: str):
    start, end = 0, None
    file_size = len(data)

    if "=" in range_header:
        _, range_header = range_header.split("=")
        start, end = range_header.split("-")
        start = int(start)
        end = int(end) if end else None

    if end:
        file_content = data[start:end + 1]
    else:
        file_content = data[start:]

    headers = {
        'Content-Range': f'bytes {start}-{start + len(file_content) - 1}/{file_size}',
        'Accept-Ranges': 'bytes',
    }

    return Response(content=file_content, status_code=status.HTTP_206_PARTIAL_CONTENT, media_type=media_type,
                    headers=headers)


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


@app.get("/api/v1/building/")
def get_palace(building_id: str, language: str):
    validate_language(language)
    building_id = validate_id(building_id)
    building = db.get_building(building_id, language)
    if building:
        return building
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Palace not found")


@app.get("/api/v1/buildingurl/")
def get_palace_url(building_name: str, language: str):
    validate_language(language)
    if len(building_name) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL too long")
    building = db.get_building_from_slug(building_name, language)
    if building:
        return building
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
    if palace_id == "0":
        palace_id = None
    if palace_id:
        validate_palace_id(palace_id)
    validate_language(language)
    article = db.get_building_random(language, palace_id)
    if article:
        return article
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No article found")


@app.get("/api/v1/languages/")
async def get_languages(language: str):
    validate_language(language)
    return JSONResponse(content=ui_language[language], status_code=status.HTTP_200_OK)


@app.get("/api/v1/buildings/")
async def get_palace_elements(palace_id: str, language: str):
    validate_language(language)
    palace_id = validate_palace_id(palace_id)
    palace_elements = db.get_palace_elements(palace_id, language)
    if palace_elements:
        return palace_elements
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No palace elements found")


# SPA catch-all endpoint
@app.get("/{catchall:path}")
async def spa_route(catchall: str):
    # Ignore API paths
    if catchall.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    # provide logo.png and sw.js
    elif catchall == "logo.png":
        return FileResponse('app/static/logo.png')
    elif catchall == "sw.js":
        return FileResponse('app/static/sw.js')
    elif catchall == "robots.txt":
        return FileResponse('app/static/robots.txt')
    elif catchall == "font.css":
        return FileResponse('app/static/font.css')

    # Serve SPA for non-API requests
    return FileResponse('app/static/index.html')
