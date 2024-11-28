from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from ..services.face_detector import face_detector, FaceDetectionError
from ..services.equation_generator import get_generator
from ..services.advanced_equation_generator import AdvancedEquationGenerator
import numpy as np
import cv2
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/face", tags=["face-processing"])

# equation_generator = get_generator()
# Initialize the advanced equation generator
equation_generator = AdvancedEquationGenerator()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    logger.info("health check")
    return {"status": "healthy"}

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Process uploaded image to detect face and generate advanced equations.
    """
    logger.info("=== Starting upload_image endpoint ===")
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

    # Validate file type
    if not file.content_type.startswith('image/'):
        logger.error(f"Invalid content type: {file.content_type}")
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
            logger.error("OpenCV failed to decode the image")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
            
        # Process image and get face landmarks
        logger.info("Starting face detection...")
        landmarks = await face_detector.detect_face_async(img)
        logger.info(f"Face detection completed. Found features: {list(landmarks.keys())}")
        
        # Generate equations using advanced generator
        logger.info("Starting advanced equation generation...")
        equations = {}
        for feature, points in landmarks.items():
            try:
                logger.info(f"Generating advanced equation for {feature}")
                equations[feature] = equation_generator.generate(feature, points)
                logger.info(f"Successfully generated equation for {feature}")
            except Exception as e:
                logger.error(f"Error generating equation for {feature}: {str(e)}")
                continue
        
        return {
            "landmarks": landmarks,
            "equations": equations,
            "image_dimensions": {
                "height": img.shape[0],
                "width": img.shape[1]
            }
        }

    except FaceDetectionError as e:
        logger.error(f"Face detection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in upload_image: {str(e)}", exc_info=True)
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
