# backend/api/services/face_detector.py
import cv2
import numpy as np
from typing import List, Tuple

class FaceDetector:
    def __init__(self):
        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.predictor_path = "shape_predictor_68_face_landmarks.dat"  # You'll need to download this

    def detect_face(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detect face landmarks in an image and return outline points.
        
        Args:
            image: numpy array of the image in BGR format
            
        Returns:
            List of (x, y) coordinates representing the face outline
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) == 0:
            raise ValueError("No face detected in the image")
            
        # Get the first face
        (x, y, w, h) = faces[0]
        
        # For now, return a simple outline (will be enhanced with facial landmarks)
        outline_points = [
            (x, y),  # Top-left
            (x + w, y),  # Top-right
            (x + w, y + h),  # Bottom-right
            (x, y + h),  # Bottom-left
            (x, y)  # Back to start
        ]
        
        return outline_points

    def get_face_landmarks(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Get detailed face landmarks using dlib (to be implemented).
        This will provide more accurate face outline points.
        """
        # TODO: Implement detailed landmark detection
        pass

face_detector = FaceDetector()