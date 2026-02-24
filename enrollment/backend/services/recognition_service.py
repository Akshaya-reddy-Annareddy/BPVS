import cv2
import numpy as np
from services.embedding_service import get_embedding
from services.vector_service import client, COLLECTION_NAME

SIMILARITY_THRESHOLD = 0.6  # or 0.7 for strict college system

def recognize_face(frame):
    """
    Takes a frame, detects face, generates embedding,
    and searches in Qdrant for matching student.
    """

    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Generate embedding (reuse your existing model)
        embedding = get_embedding(rgb_frame)

        if embedding is None:
            return None, "No face detected"

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

        # Check similarity threshold
        if score < SIMILARITY_THRESHOLD:
            return None, "Low confidence match"

        admission_id = best_match.payload["admission_id"]
        return {
            "admission_id":admission_id,
            "score":score
        }, "Match successful"

    except Exception as e:
        print("Recognition Error:", e)
        return None, "Recognition failed"