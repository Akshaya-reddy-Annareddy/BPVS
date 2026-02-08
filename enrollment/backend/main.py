from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
import cv2
from services.video_service import process_video
from services.vector_service import init_collection

app = FastAPI(root_path="")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use * temporarily for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_frames(video_path, output_folder="frames"):
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_path = f"{output_folder}/frame_{frame_count}.jpg"
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    cap.release()

# Serve enrollment page
@app.get("/")
def serve_index():
    return FileResponse("../frontend/index.html")

@app.on_event("startup")
def startup_event():
    init_collection()
    
# Upload endpoint
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"uploads/{file.filename}"

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    success = process_video(video_path, student_id=1)

    if success:
        return {"message": "Enrollment successful"}
    else:
        return {"message": "No valid face detected"}