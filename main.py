import os
import uuid
from modules.spider import run_spider
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/")
def test():
    return {"message": "Hello World"}

def remove_file(path: str):
    """Cleanup task to delete the temporary file."""
    if os.path.exists(path):
        os.remove(path)

@app.post("/download")
def download(data: dict, background_tasks: BackgroundTasks):
    unique_id = uuid.uuid4().hex
    
    url = data.get("url", [])
    platform = data.get("platform", "")

    ext = data.get("file_format", "mp4")
    file_type = data.get("file_type", "video")
    
    folder = "temp/videos" if file_type == "video" else "temp/imgs"
    os.makedirs(folder, exist_ok=True)
    
    target_filename = f"{unique_id}.{ext}"
    target_path = os.path.join(folder, target_filename)

    raw_data = {
        "url": url,
        "platform": platform,
        "file_type": file_type,
        "file_format": data.get("file_format", "mp4"),
        "save_path": target_path
    }

    run_spider([raw_data])
    if not os.path.exists(target_path):
        return {"message": "Video not found"}
    
    media_type = f"video/{ext}" if file_type == "video" else f"image/{ext}"
    return FileResponse(target_path, media_type=media_type, filename=target_filename)

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
