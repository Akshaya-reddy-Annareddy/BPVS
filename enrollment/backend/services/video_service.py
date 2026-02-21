import cv2
from services.frame_service import extract_frames
from services.face_service import get_face
from services.embedding_service import get_embedding, average_embeddings
from services.vector_service import store_embedding
from utils.cleanup import delete_file
import shutil
import os

def cleanup_files(video_path, frames_folder="frames"):
    # delete video
    if os.path.exists(video_path):
        os.remove(video_path)

    # delete frames folder
    if os.path.exists(frames_folder):
        shutil.rmtree(frames_folder)

def process_video(video_path, student_id):

    print("Step 1: Starting video processing")

    frame_paths = extract_frames(video_path)
    print(f"Step 2: Frames extracted: {len(frame_paths)}")
    accepted = 0
    rejected = 0
    embeddings = []

    for path in frame_paths:
        frame = cv2.imread(path)

        #Skip bad frames
        if frame is None:
            rejected += 1
            continue

        h, w = frame.shape[:2]

        #Reject tiny frames
        if h<100 or w<100:
            continue

        face = get_face(frame)

        if face is None:
            rejected += 1
            continue
        
        print("Step 4: Generating embeddings...")

        emb = get_embedding(face)
        if emb is None:
            rejected += 1
            continue
        
        if emb is not None:
            print(f"Step 5: Embeddings generated: {len(emb)}")
            embeddings.append(emb)
            accepted += 1

        print(f"Accepted frames: {accepted}, Rejected: {rejected}")

        delete_file(path)

    if len(embeddings) == 0:
        return False

    print("Step 6: Averaging embeddings...")
    avg_embedding = average_embeddings(embeddings)

    print("Step 7: Storing embedding...")
    store_embedding(student_id, avg_embedding)

    print("Step 8: Done storing")
    cleanup_files(video_path)

    return True
