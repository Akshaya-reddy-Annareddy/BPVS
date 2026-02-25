import cv2
import numpy as np


class PassiveLivenessDetector:
    def __init__(self):
        # Haar face detector (lightweight & stable)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def detect_liveness(self, frames):
        """
        frames: list of cv2 images
        Returns: (bool, message)
        """

        if len(frames) < 5:
            return False, "Not enough frames for liveness"

        movement_detected = False
        face_detected_count = 0

        prev_gray = None

        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5
            )

            if len(faces) > 0:
                face_detected_count += 1

            # Motion detection
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                non_zero_count = np.count_nonzero(diff)

                if non_zero_count > 5000:  # movement threshold
                    movement_detected = True

            prev_gray = gray

        if face_detected_count < len(frames) // 2:
            return False, "Face not consistently detected"

        if not movement_detected:
            return False, "No movement detected (possible spoof)"

        return True, "Live face detected"