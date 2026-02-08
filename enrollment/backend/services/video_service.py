import cv2
from services.frame_service import extract_frames
from services.face_service import get_face
from services.embedding_service import get_embedding, average_embeddings
from services.vector_service import store_embedding
from utils.cleanup import delete_file

def process_video(video_path, student_id):

    frame_paths = extract_frames(video_path)
    accepted = 0
    embeddings = []

    for path in frame_paths:
        frame = cv2.imread(path)

        #Skip bad frames
        if frame is None:
            continue

        h, w = frame.shape[:2]

        #Reject tiny frames
        if h<100 or w<100:
            continue

        face = get_face(frame)

        if face is None:
            continue

        emb = get_embedding(face)
        if emb is None:
            continue
        
        if emb is not None:
            embeddings.append(emb)
            accepted += 1

        print("Accepted frames:", accepted)

        delete_file(path)

    if len(embeddings) == 0:
        return False

    avg_embedding = average_embeddings(embeddings)
    store_embedding(student_id, avg_embedding)

    delete_file(video_path)

    return True
