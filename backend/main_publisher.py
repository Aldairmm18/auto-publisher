from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
import sys

app = FastAPI(title="Auto Publisher API (Standalone)", version="1.0")

class PublishRequest(BaseModel):
    text: str
    image_path: str = "test_image.jpg"
    video_path: str = "test_video.mp4"
    platforms: list[str] = ["facebook", "instagram", "youtube", "tiktok"]

def launch_publishers_process(req: PublishRequest):
    script_path = os.path.join(os.path.dirname(__file__), "publisher_worker.py")
    platforms_str = ",".join(req.platforms)
    
    # sys.executable obliga a usar el Python del entorno virtual (.venv)
    cmd = [
        sys.executable,  
        script_path,
        "--text", req.text,
        "--image", req.image_path,
        "--video", req.video_path,
        "--platforms", platforms_str
    ]
    print(f"[API] Lanzando worker con CMD...")
    subprocess.Popen(cmd)

@app.post("/api/publish")
async def publish_content(req: PublishRequest, background_tasks: BackgroundTasks):
    """
    Recibe la solicitud y lanza un proceso separado para publicar.
    """
    # Pasamos req como parametro a la funcion del background task
    background_tasks.add_task(launch_publishers_process, req)
    return {
        "status": "success", 
        "message": "Publicación iniciada en un proceso independiente", 
        "platforms": req.platforms
    }
