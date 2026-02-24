import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import math

mp_face_mesh = mp.solutions.face_mesh

# Eye landmark indices (MediaPipe)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


class PassiveLivenessDetector:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

        self.ear_history = deque(maxlen=20)
        self.blink_count = 0
        self.prev_ear = None

    def calculate_ear(self, landmarks, eye_indices):
        points = [landmarks[i] for i in eye_indices]

        # Vertical distances
        v1 = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
        v2 = np.linalg.norm(np.array(points[2]) - np.array(points[4]))

        # Horizontal distance
        h = np.linalg.norm(np.array(points[0]) - np.array(points[3]))

        ear = (v1 + v2) / (2.0 * h)
        return ear

    def detect_liveness(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return False, "No face detected"

        face_landmarks = results.multi_face_landmarks[0]
        h, w, _ = frame.shape

        landmarks = []
        for lm in face_landmarks.landmark:
            landmarks.append((int(lm.x * w), int(lm.y * h)))

        # Calculate EAR
        left_ear = self.calculate_ear(landmarks, LEFT_EYE)
        right_ear = self.calculate_ear(landmarks, RIGHT_EYE)

        ear = (left_ear + right_ear) / 2.0
        self.ear_history.append(ear)

        # Blink detection
        EAR_THRESHOLD = 0.21

        if self.prev_ear is not None:
            if self.prev_ear > EAR_THRESHOLD and ear < EAR_THRESHOLD:
                self.blink_count += 1

        self.prev_ear = ear

        # Require at least 1 blink
        if self.blink_count >= 1:
            return True, "Live face detected"

        return False, "Blink not detected yet"