from keras_facenet import FaceNet
import cv2
import numpy as np

embedder = FaceNet()

def get_embedding(face):
    if face is None:
        return None

    try:
        face = cv2.resize(face, (160,160))
    except:
        return None

    face = np.expand_dims(face, axis=0)
    embedding = embedder.embeddings(face)

    if embedding is None or len(embedding) == 0:
        return None

    return embedding[0]


def average_embeddings(embeddings):
    return np.mean(embeddings, axis=0)