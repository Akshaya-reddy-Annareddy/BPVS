import cv2
import numpy as np
import dlib
from scipy.spatial import distance as dist

class PassiveLivenessDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # For blink detection
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        return (A + B) / (2.0 * C)

    def detect_liveness(self, frames):

        if len(frames) < 8:
            return False, "Not enough frames"

        face_detected_count = 0
        movement_detected = False
        blink_detected = False
        texture_variation = []
        reflection_score = 0

        prev_gray = None
        prev_landmarks = None

        for frame in frames:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                face_detected_count += 1

            # Motion Detection 
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                if np.count_nonzero(diff) > 8000:
                    movement_detected = True
            prev_gray = gray

            # Texture Analysis (print detection) 
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            texture_variation.append(laplacian_var)

            # Screen reflection detection 
            bright_pixels = np.sum(gray > 240)
            if bright_pixels > 5000:
                reflection_score += 1

            # Blink detection 
            dlib_faces = self.detector(gray)

            for face in dlib_faces:
                shape = self.predictor(gray, face)
                coords = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])

                leftEye = coords[42:48]
                rightEye = coords[36:42]

                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)

                ear = (leftEAR + rightEAR) / 2.0

                if ear < 0.20:
                    blink_detected = True

        # Decision Rules 

        if face_detected_count < len(frames) // 2:
            return False, "Face not consistent"

        if not movement_detected:
            return False, "No real movement"

        if not blink_detected:
            return False, "No eye blink detected"

        if np.std(texture_variation) < 5:
            return False, "Low texture variation (Printed photo suspected)"

        if reflection_score > 4:
            return False, "Screen reflection detected"

        return True, "Live human confirmed"