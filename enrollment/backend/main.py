from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks
import shutil
import os
import cv2
from services.video_service import process_video
from services.vector_service import init_collection, search_embedding
from services.embedding_service import get_embedding
import uuid
import requests
from services.liveness_service import PassiveLivenessDetector
import numpy as np
from datetime import datetime
import pytz
import time

DJANGO_API = "https://fictional-space-adventure-975www67xxr427vv5-8000.app.github.dev/"

def send_attendance_to_django(admission_id):
    try:
        response = requests.post(
            f"{DJANGO_API}/attendance/mark/",
            json={
                "admission_id": admission_id,
                "subject_name": "AI",      # temporary (later dynamic)
                "lecturer_id": "L001"     # temporary
            },
            timeout=3 #reduce timeout for speed
        )
        print("Attendance API Response:", response.text)
    except Exception as e:
        print("Attendance API Error:", e)

liveness_detector = PassiveLivenessDetector()
app = FastAPI(root_path="")
job_status = {}

# Prevent duplicate API calls (per session)
attendance_cache = {}  # key: (admission_id, subject, date)

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

def process_video_background(video_path, admission_id, job_id):
    try:
        print(f"Processing started for student: {admission_id}")
        success = process_video(video_path, admission_id)

        if success:
            print("Processing completed successfully")

            # NEW: Notify Django that face is enrolled
            try:
                requests.post(
                    "http://127.0.0.1:8000/accounts/mark-face-enrolled/",
                    json={"admission_id": admission_id},
                    timeout=5
                )
                print("Django face_enrolled updated")
            except Exception as e:
                print("Failed to update Django face status:", e)

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

@app.on_event("startup")
def startup_event():
    init_collection()
    
# Upload endpoint
@app.post("/upload-video/")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    admission_id: str = Form(...)
):
    print("DEBUG: file received =", file.filename)
    print("DEBUG: admission_id received =", admission_id)

    # STEP 1: Check enrollment status from Django
    try:
        user_check = requests.get(
            f"http://127.0.0.1:8000/accounts/check-enrollment/{admission_id}/",
            timeout=5
        )
        user_data = user_check.json()
    except Exception as e:
        return {"status": "error", "message": "Django server not reachable"}

    if user_data.get("blocked"):
        return {
            "status": "blocked",
            "message": "Enrollment blocked. Contact Admin."
        }

    overwrite = user_data.get("allow_overwrite", False)

    # STEP 2: Save video
    video_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job_id = str(uuid.uuid4())
    job_status[job_id] = "processing"

    # PASS overwrite flag to video processor
    background_tasks.add_task(
        process_video_background,
        video_path,
        admission_id,
        job_id,
        overwrite  # NEW PARAM
    )

    return {
        "job_id": job_id,
        "message": "Upload successful. Processing started."
    }

@app.get("/status/{job_id}")
def get_status(job_id: str):
    status = job_status.get(job_id, "not_found")
    return {"status": status}

@app.post("/verify-face/")
async def verify_face(files: list[UploadFile] = File(...)):
    try:
        frames = []
        best_frame = None
        best_sharpness = 0

        # Decode all frames first (FAST)
        for file in files:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                frames.append(frame)

        if len(frames) < 3:
            return {
                "status": "error",
                "message": "Not enough frames captured"
            }

        # RUN LIVENESS ONLY ONCE (OPTIMIZED)
        print("1.Frames received = ", len(frames))

        start_time = time.time()
        is_live, msg = liveness_detector.detect_liveness(frames)
        print("Liveness Time:", time.time() - start_time)
        print("2.Liveness Result:", msg)

        if not is_live:
            return {
                "status": "spoof_detected",
                "message": "Liveness failed"
            }

        # Select sharpest frame (BEST QUALITY)
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

            if sharpness > best_sharpness:
                best_sharpness = sharpness
                best_frame = frame

        if best_frame is None:
            return {
                "status": "error",
                "message": "No valid frame"
            }

        # Generate embedding (Face Recognition)
        print("3.Starting embedding...")
        embedding = get_embedding(best_frame)
        print("4.Embedding completed")

        if embedding is None:
            return {
                "status": "no_face",
                "message": "Face not detected"
            }

        # Search in vector DB
        print("5.Searching vector DB..")
        match = search_embedding(embedding)
        print("6.Search completed")

        if match is None:
            return {
                "status": "unknown",
                "message": "Face not recognized"
            }

        admission_id = match["admission_id"]

        # REAL COLLEGE LOGIC (One per subject per day)
        ist = pytz.timezone("Asia/Kolkata")
        today = datetime.now(ist).date()
        subject = "AI"

        cache_key = f"{admission_id}_{subject}_{today}"

        if cache_key not in attendance_cache:
            send_attendance_to_django(admission_id)
            attendance_cache[cache_key] = True
        else:
            return {
                "status": "duplicate",
                "message": "Attendance already marked today for this subject"
            }

        return {
            "status": "recognized",
            "admission_id": admission_id,
            "confidence": float(match["score"]),
            "message": "Attendance marked successfully"
        }

    except Exception as e:
        print("Verification error:", e)
        return {"status": "error", "message": str(e)}