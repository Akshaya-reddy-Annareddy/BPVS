from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks
import shutil
import os
import cv2
from services.video_service import process_video
from services.vector_service import init_collection
import uuid

app = FastAPI(root_path="")
job_status = {}

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

def process_video_background(video_path, student_id, job_id):
    try:
        print("Processing started...")
        success = process_video(video_path, student_id)

        if success:
            print("Processing completed successfully")
            job_status[job_id] = "completed"
        else:
            print("Processing failed")
            job_status[job_id] = "failed"

    except Exception as e:
        print("Processing error:", e)
        job_status[job_id] = "failed"

    if os.path.exists(video_path):
        os.remove(video_path)


# Serve enrollment page
@app.get("/")
def serve_index():
    return FileResponse("../frontend/index.html")

@app.get("/attendance")
def serve_attendance():
    return FileResponse("../frontend/attendance.html")

@app.on_event("startup")
def startup_event():
    init_collection()
    
# Upload endpoint
@app.post("/upload-video/")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):

    video_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job_id = str(uuid.uuid4())
    job_status[job_id] = "processing"

    background_tasks.add_task(process_video_background, video_path, 1, job_id)

    return {"job_id": job_id, "message": "Upload successful. Processing started."}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    status = job_status.get(job_id, "not_found")
    return {"status": status}


