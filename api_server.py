import os
import shutil
import tempfile
from typing import Optional

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fh_core import FaceHuntCore

app = FastAPI(
    title="FaceHunt API",
    description="API to find people in videos using a reference image.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

core = FaceHuntCore()

def save_temp_file(file: UploadFile) -> str:
    """Saves an uploaded file to a secure temporary location and returns the path."""
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            return temp_file.name
    finally:
        file.file.close()

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Validates the reference image in real-time."""
    temp_path = None
    try:
        temp_path = save_temp_file(file)
        success, embedding, message = core.validate_image_file(temp_path)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"message": message}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/validate-video")
async def validate_video(
    source: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Validates the video source (URL or file) in real-time."""
    if not (source or file) or (source and file):
        raise HTTPException(status_code=400, detail="You must provide either a URL or a file, but not both.")

    video_source_to_validate = ""
    temp_path = None
    try:
        if file:
            temp_path = save_temp_file(file)
            video_source_to_validate = temp_path
        else:
            video_source_to_validate = source

        success, source_type, message = core.validate_video_source(video_source_to_validate)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"message": message, "source_type": source_type}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/recognize")
async def recognize_faces(
    reference_image: UploadFile = File(...),
    mode: str = Form(...),
    video_file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None)
):
    """Main endpoint to run the entire recognition process."""
    if not (video_file or video_url) or (video_file and video_url):
        raise HTTPException(status_code=400, detail="You must provide either video_file or video_url.")

    image_temp_path = None
    video_temp_path = None
    try:
        image_temp_path = save_temp_file(reference_image)
        video_source = video_url if video_url else save_temp_file(video_file)
        if video_file:
             video_temp_path = video_source

        result = core.execute_workflow(
            image_path=image_temp_path,
            mode=mode,
            video_source=video_source
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if image_temp_path and os.path.exists(image_temp_path):
            os.remove(image_temp_path)
        if video_temp_path and os.path.exists(video_temp_path):
            os.remove(video_temp_path)

if __name__ == "__main__":
    print("Starting FaceHunt API Server...")
    print("Access the documentation at: http://127.0.0.1:8000/docs")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)