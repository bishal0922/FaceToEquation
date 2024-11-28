import os
import cv2
import dlib
import numpy as np
from typing import Dict, List, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class FaceDetectionError(Exception):
    """Custom exception for face detection errors."""
    pass

class FaceDetector:
    def __init__(self):
        """Initialize face detector with required models."""
        try:
            # Load face detection models
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Get the absolute path to the project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
            # Construct path to the model file
            model_path = os.path.join(
                project_root,
                "backend",
                "api",
                "models",
                "shape_predictor_68_face_landmarks.dat"
            )
            
            logger.info(f"Loading face predictor model from: {model_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model file not found at {model_path}. Please ensure the file exists in the correct location."
                )
            
            # Initialize dlib's face detector and shape predictor
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(model_path)
            
            # Thread pool for async operations
            self.thread_pool = ThreadPoolExecutor(max_workers=3)
            logger.info("FaceDetector initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing FaceDetector: {str(e)}")
            raise

    def _process_landmarks(self, shape) -> Dict[str, List[Tuple[float, float]]]:
        """
        Process dlib face landmarks into meaningful facial features.
        
        Args:
            shape: dlib full_object_detection object
            
        Returns:
            Dictionary containing points for different facial features
        """
        # Convert landmarks to numpy array
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        
        # Define facial feature ranges
        JAWLINE = list(range(0, 17))
        RIGHT_EYEBROW = list(range(17, 22))
        LEFT_EYEBROW = list(range(22, 27))
        NOSE_BRIDGE = list(range(27, 31))
        NOSE_TIP = list(range(31, 36))
        RIGHT_EYE = list(range(36, 42))
        LEFT_EYE = list(range(42, 48))
        OUTER_LIPS = list(range(48, 60))
        INNER_LIPS = list(range(60, 68))
        
        # Create normalized points for each feature
        features = {
            "jawline": landmarks[JAWLINE].tolist(),
            "right_eyebrow": landmarks[RIGHT_EYEBROW].tolist(),
            "left_eyebrow": landmarks[LEFT_EYEBROW].tolist(),
            "nose_bridge": landmarks[NOSE_BRIDGE].tolist(),
            "nose_tip": landmarks[NOSE_TIP].tolist(),
            "right_eye": landmarks[RIGHT_EYE].tolist(),
            "left_eye": landmarks[LEFT_EYE].tolist(),
            "outer_lips": landmarks[OUTER_LIPS].tolist(),
            "inner_lips": landmarks[INNER_LIPS].tolist()
        }
        
        # Normalize coordinates to [0, 1] range
        for feature in features:
            points = np.array(features[feature])
            if len(points) > 0:
                x_min, y_min = points.min(axis=0)
                x_max, y_max = points.max(axis=0)
                
                # Avoid division by zero
                x_range = x_max - x_min or 1
                y_range = y_max - y_min or 1
                
                normalized = [
                    [(x - x_min) / x_range, (y - y_min) / y_range]
                    for x, y in points
                ]
                features[feature] = normalized
        
        return features

    def detect_face(self, image: np.ndarray) -> Dict[str, List[Tuple[float, float]]]:
        """
        Detect face landmarks in an image.
        
        Args:
            image: numpy array of the image in BGR format
            
        Returns:
            Dictionary containing normalized coordinates for facial features
            
        Raises:
            FaceDetectionError: If no face is detected or processing fails
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using dlib
            faces = self.detector(gray)
            
            if len(faces) == 0:
                raise FaceDetectionError("No face detected in the image")
            
            if len(faces) > 1:
                logger.warning("Multiple faces detected, using the first one")
            
            # Get facial landmarks
            shape = self.predictor(gray, faces[0])
            
            # Process and return normalized landmarks
            return self._process_landmarks(shape)
            
        except FaceDetectionError:
            raise
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            raise FaceDetectionError(f"Error processing image: {str(e)}")

    async def detect_face_async(self, image: np.ndarray) -> Dict[str, List[Tuple[float, float]]]:
        """
        Asynchronous version of face detection.
        
        Args:
            image: numpy array of the image in BGR format
            
        Returns:
            Dictionary containing normalized coordinates for facial features
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, self.detect_face, image)

face_detector = FaceDetector()
