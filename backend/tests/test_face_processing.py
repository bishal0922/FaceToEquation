import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import numpy as np
import cv2
import os
from backend.api.main import app
from backend.api.services.face_detector import FaceDetector, FaceDetectionError
from backend.api.services.equation_generator import EquationGenerator

client = TestClient(app)

# Create test fixtures directory if it doesn't exist
TEST_FIXTURES_DIR = Path(__file__).parent / "test_fixtures"
TEST_FIXTURES_DIR.mkdir(exist_ok=True)

@pytest.fixture
def test_image():
    """Create a simple test image with a face-like pattern."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    # Draw a simple face-like pattern
    cv2.circle(img, (150, 150), 100, (255, 255, 255), -1)  # Face
    cv2.circle(img, (120, 120), 15, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (180, 120), 15, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (150, 180), (50, 20), 0, 0, 180, (0, 0, 0), -1)  # Mouth
    
    # Save test image
    test_image_path = TEST_FIXTURES_DIR / "test_face.jpg"
    cv2.imwrite(str(test_image_path), img)
    return test_image_path

@pytest.fixture
def face_detector():
    """Initialize face detector instance."""
    return FaceDetector()

@pytest.fixture
def equation_generator():
    """Initialize equation generator instance."""
    return EquationGenerator()

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/face/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_upload_invalid_file():
    """Test uploading an invalid file type."""
    files = {"file": ("test.txt", "test content", "text/plain")}
    response = client.post("/api/face/upload", files=files)
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]

def test_upload_valid_image(test_image):
    """Test uploading a valid image file."""
    with open(test_image, "rb") as f:
        files = {"file": ("test_face.jpg", f, "image/jpeg")}
        response = client.post("/api/face/upload", files=files)
        
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "landmarks" in data
    assert "equations" in data
    
    # Check landmarks structure
    landmarks = data["landmarks"]
    expected_features = [
        "jawline", "right_eyebrow", "left_eyebrow", "nose_bridge",
        "nose_tip", "right_eye", "left_eye", "outer_lips", "inner_lips"
    ]
    
    for feature in expected_features:
        assert feature in landmarks
        assert isinstance(landmarks[feature], list)
        if landmarks[feature]:  # If points were detected
            assert isinstance(landmarks[feature][0], list)
            assert len(landmarks[feature][0]) == 2  # Each point should have x, y coords

def test_analyze_endpoint(test_image):
    """Test the analyze endpoint."""
    with open(test_image, "rb") as f:
        files = {"file": ("test_face.jpg", f, "image/jpeg")}
        response = client.post("/api/face/analyze", files=files)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "landmarks" in data
    assert "image_dimensions" in data
    assert "height" in data["image_dimensions"]
    assert "width" in data["image_dimensions"]

def test_upload_different_equation_types(test_image):
    """Test generating different types of equations."""
    equation_types = ["polynomial", "trigonometric", "fourier"]
    
    for eq_type in equation_types:
        with open(test_image, "rb") as f:
            files = {"file": ("test_face.jpg", f, "image/jpeg")}
            response = client.post(
                "/api/face/upload",
                files=files,
                params={"equation_type": eq_type, "degree": 4}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check equations were generated
        assert "equations" in data
        for feature, equation in data["equations"].items():
            assert "type" in equation
            assert equation["type"] == eq_type
            assert "equation" in equation

def test_error_handling():
    """Test error handling for various scenarios."""
    # Test with empty file
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/face/upload", files=files)
    assert response.status_code in [400, 422, 500]  # One of these error codes is acceptable
    
    # Test with corrupted image data
    files = {"file": ("corrupt.jpg", b"corrupted data", "image/jpeg")}
    response = client.post("/api/face/upload", files=files)
    assert response.status_code in [400, 422, 500]

def test_cleanup():
    """Clean up test fixtures."""
    # Remove test image
    test_image_path = TEST_FIXTURES_DIR / "test_face.jpg"
    if test_image_path.exists():
        test_image_path.unlink()
    
    # Remove test fixtures directory if empty
    if TEST_FIXTURES_DIR.exists() and not any(TEST_FIXTURES_DIR.iterdir()):
        TEST_FIXTURES_DIR.rmdir()

# Run this test last to clean up
@pytest.mark.last
def test_final_cleanup():
    test_cleanup()