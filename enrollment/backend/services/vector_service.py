from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct

client = QdrantClient(":memory:")  # local testing

COLLECTION_NAME = "students"

def init_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE),
    )

def store_embedding(student_id, embedding):
    points = [
        PointStruct(
            id=student_id,
            vector=embedding,
            payload={"student_id": student_id}
        )
    ]

    client.upsert(
        collection_name="faces",
        points=points
    )

