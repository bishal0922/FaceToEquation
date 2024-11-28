from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from ..services import face_detector, equation_generator  # Changed this line
from ..services.face_detector import FaceDetectionError  # Changed this line
import numpy as np
import cv2
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/face", tags=["face-processing"])

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    equation_type: str = "polynomial",
    degree: int = 4
) -> Dict[str, Any]:
    """
    Process uploaded image to detect face and generate equations.
    
    Args:
        file: Uploaded image file
        equation_type: Type of equation to generate ('polynomial' or 'trigonometric')
        degree: Degree of polynomial or number of terms for trigonometric series
        
    Returns:
        Dictionary containing face outline points and generated equations
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
            
        # Process image and get face landmarks
        landmarks = await face_detector.detect_face_async(img)
        
        # Generate equations for different face parts
        equations = {}
        for part, points in landmarks.items():
            try:
                eq = equation_generator.generate(
                    points=points,
                    method=equation_type,
                    degree=degree
                )
                equations[part] = eq
            except ValueError as e:
                logger.error(f"Error generating equation for {part}: {str(e)}")
                continue
                
        return {
            "landmarks": landmarks,
            "equations": equations
        }
        
    except FaceDetectionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing image"
        )
    finally:
        await file.close()

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Analyze face without generating equations.
    Useful for previewing face detection results.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Get face landmarks only
        landmarks = await face_detector.detect_face_async(img)
        
        return {
            "landmarks": landmarks,
            "image_dimensions": {
                "height": img.shape[0],
                "width": img.shape[1]
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing image"
        )
    finally:
        await file.close()
