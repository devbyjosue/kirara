import os
import json
import uuid
from datetime import datetime, timezone
from modules.spider import run_spider
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from modules.database import init_database, list_downloads, normalize_platform, record_download
from utils.identify_domain import identify_domain


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

origins = [
    "http://localhost",
    "http://localhost:4321",
    "http://127.0.0.1:4321",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.on_event("startup")
def on_startup():
    init_database()


@app.get("/")
def test():
    return {"message": "Hello World"}


def _extract_scraped_title(results_path: str = "results.json") -> str | None:
    if not os.path.exists(results_path):
        return None

    try:
        with open(results_path, "r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    if isinstance(payload, list) and payload:
        first_item = payload[0]
    elif isinstance(payload, dict):
        first_item = payload
    else:
        return None

    title = first_item.get("title") if isinstance(first_item, dict) else None
    if not isinstance(title, str):
        return None
    cleaned_title = title.strip()
    return cleaned_title or None


def _resolve_platform(url: str) -> str:
    detected_platform = identify_domain(url)
    return normalize_platform(detected_platform)

def remove_file(path: str):
    """Cleanup task to delete the temporary file."""
    if os.path.exists(path):
        os.remove(path)

@app.post("/download")
def download(data: dict, background_tasks: BackgroundTasks):
    unique_id = uuid.uuid4().hex

    url = (data.get("url", "") or "").strip()
    if not url:
        return {"message": "URL is required"}

    platform = _resolve_platform(url)

    file_type = (data.get("file_type", "video") or "video").strip().lower()
    if file_type not in {"video", "image"}:
        file_type = "video"

    default_ext = "mp4" if file_type == "video" else "jpg"
    ext = (data.get("file_format", default_ext) or default_ext).strip().lower()
    
    folder = "temp/videos" if file_type == "video" else "temp/imgs"
    os.makedirs(folder, exist_ok=True)
    
    target_filename = f"{unique_id}.{ext}"
    target_path = os.path.join(folder, target_filename)

    raw_data = {
        "url": url,
        "platform": platform,
        "file_type": file_type,
        "file_format": ext,
        "save_path": target_path
    }

    run_spider([raw_data])
    if not os.path.exists(target_path):
        return {"message": "Video not found"}

    downloaded_at = datetime.now(timezone.utc).isoformat()
    title = _extract_scraped_title()
    record_download(
        name=target_filename,
        title=title,
        url=url,
        file_format=ext,
        file_type=file_type,
        platform=platform,
        downloaded_at=downloaded_at,
    )

    background_tasks.add_task(remove_file, target_path)
    
    media_type = f"video/{ext}" if file_type == "video" else f"image/{ext}"
    return FileResponse(target_path, media_type=media_type, filename=target_filename)


@app.get("/downloads")
def get_downloads(
    platform: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
):
    selected_platform = normalize_platform(platform) if platform else None
    downloads = list_downloads(platform=selected_platform, limit=limit)
    return {
        "platform": selected_platform,
        "limit": limit,
        "downloads": downloads,
    }

sample = [
    # {
    #     'url': 'https://twitter.com/AlertaMundoNews/status/2034032012953002006',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # },
    # {
    #     'url': 'https://twitter.com/GeddyJaibo/status/2034337288633606515',
    #     'file_type': 'image',
    #     'file_format': 'jpg'
    # },
    # {
    #     'url': 'https://www.instagram.com/reels/DQaYJ16DPna/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # },
    # {
    #     'url':'https://www.instagram.com/shitposthero/p/DWMP3dWDk13/',
    #     'file_type': 'image',
    #     'file_format': 'jpg'
    # }
    # {
    #     'url': 'https://www.facebook.com/100064441644698/videos/pcb.10159944371444699/10159944371389699/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # }
    {
        'url': 'https://youtube.com/shorts/FRI_283DKjQ?si=hSaQN_gjglG5JErz',
        'file_type': 'video',
        'file_format': 'mp4'
    }
    # {
    #     'url': 'https://www.facebook.com/facebook/videos/671204259264003/',
    #     'file_type': 'video',
    #     'file_format': 'mp4'
    # }
]
def main():
    run_spider(sample)



if __name__ == "__main__":
    # main()
    pass
