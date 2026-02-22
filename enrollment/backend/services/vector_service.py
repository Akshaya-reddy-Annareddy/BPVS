from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct
from services.encryption_service import encrypt_embedding
import uuid

client = QdrantClient(":memory:")  # local testing

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

def store_embedding(admission_id, embedding):
    init_collection()

    encrypted_embedding = encrypt_embedding(embedding)

    unique_id = str(uuid.uuid4())  # Generate valid UUID for Qdrant

    point = PointStruct(
        id=unique_id,  # FIX: use UUID instead of admission_id
        vector=embedding.tolist(),  # keep vector for similarity
        payload={
            "admission_id": admission_id,  # keep your real student ID here
            "encrypted": encrypted_embedding.decode("utf-8")
        }
    )

    client.upsert(
        collection_name="faces",
        points=[point]
    )