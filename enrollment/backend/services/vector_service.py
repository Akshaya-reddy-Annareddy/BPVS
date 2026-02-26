from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct
from services.encryption_service import encrypt_embedding
import uuid

client = QdrantClient(host="localhost", port=6333)  # local testing

COLLECTION_NAME = "faces"

def init_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if "faces" not in names:
        client.create_collection(
            collection_name="faces",
            vectors_config=VectorParams(
                size=512,   # FaceNet embedding size
                distance=Distance.COSINE
            ),
        )

def search_embedding(query_embedding, threshold=0.6):
    init_collection()
    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding.tolist(),  
            limit=1
        )

        if not results.points:
            print("No points found in Qdrant")
            return None

        best_match = results.points[0]
        print("Best match score:", best_match.score)

        if best_match.score < threshold:
            print("Match below threshold")
            return None

        return {
            "admission_id": best_match.payload["admission_id"],
            "score": best_match.score
        }

    except Exception as e:
        print("Qdrant search error:", e)
        return None
    
def delete_embedding_by_admission(admission_id):
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "admission_id",
                            "match": {"value": admission_id}
                        }
                    ]
                }
            }
        )
        print(f"Old embedding deleted for {admission_id}")
    except Exception as e:
        print("Delete error:", e)


def store_embedding(admission_id, embedding, overwrite=False):
    init_collection()

    # Only delete if overwrite is allowed
    if overwrite:
        delete_embedding_by_admission(admission_id)

    encrypted_embedding = encrypt_embedding(embedding)

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding.tolist(),
        payload={
            "admission_id": admission_id,
            "encrypted": encrypted_embedding.decode("utf-8")
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )

    print("Embedding stored successfully for:", admission_id)