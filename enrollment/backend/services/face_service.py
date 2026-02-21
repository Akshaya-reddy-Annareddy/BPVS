from mtcnn import MTCNN
import cv2

detector = MTCNN()

def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

def get_face(frame):
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.detect_faces(frame)
    except Exception:
        print("MTCNN error:")
        return None
    
    if len(results) == 0:
        return None

    x, y, w, h = results[0]['box']

    # Fix negative coordinates
    x = max(0, x)
    y = max(0, y)

    face = frame[y:y+h, x:x+w]

    # Reject invalid faces only
    if face is None or face.size == 0:
        return None

    # Allow smaller faces (webcam friendly)
    if face.shape[0] < 40 or face.shape[1] < 40:
        return None

    # Make blur check less strict
    if is_blurry(face, threshold=30):  
        return None


    return face