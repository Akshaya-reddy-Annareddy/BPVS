from mtcnn import MTCNN
import cv2

detector = MTCNN()

def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

def get_face(frame):
    try:
        results = detector.detect_faces(frame)
    except Exception:
        return None
    
    if len(results) == 0:
        return None

    x, y, w, h = results[0]['box']

    # Fix negative coordinates
    x = max(0, x)
    y = max(0, y)

    face = frame[y:y+h, x:x+w]

    # Reject invalid faces
    if face is None or face.size == 0:
        return None

    # Reject very small faces
    if face.shape[0] < 80 or face.shape[1] < 80:
        return None

    # Reject blurry faces
    if is_blurry(face):
        return None

    return face