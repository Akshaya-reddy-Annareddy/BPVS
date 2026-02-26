import cv2
import numpy as np
from services.embedding_service import get_embedding
from services.vector_service import client, COLLECTION_NAME

SIMILARITY_THRESHOLD = 0.6

# Add Haar face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def recognize_face(frame):
    try:
        # Detect face first
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None, "No face detected"

        # Take largest face (important for webcam)
        (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]

        face_crop = frame[y:y+h, x:x+w]

        # Convert to RGB AFTER crop
        face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

        # Now generate embedding from FACE ONLY
        embedding = get_embedding(face_rgb)

        if embedding is None:
            return None, "Embedding failed"

        # Search in Qdrant
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding.tolist(),
            limit=1
        )

        if not search_result:
            return None, "No match found"

        best_match = search_result[0]
        score = best_match.score
        print("Best match score:", score)

        if score < SIMILARITY_THRESHOLD:
            return None, "Low confidence match"

        admission_id = best_match.payload["admission_id"]
        return {
            "admission_id": admission_id,
            "score": score
        }, "Match successful"

    except Exception as e:
        print("Recognition Error:", e)
        return None, "Recognition failed"