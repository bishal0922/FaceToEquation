from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from ..services.face_detector import face_detector, FaceDetectionError
from ..services.equation_generator import get_generator
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

equation_generator = get_generator()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    logger.info("health check")
    return {"status": "healthy"}

@router.post("/upload")
async def upload_image( file: UploadFile = File(...), equation_type: str = "polynomial", degree: int = 4) -> Dict[str, Any]:
    """
    Process uploaded image to detect face and generate equations.
    """
    logger.info(f"=== Starting upload_image endpoint ===")
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
    logger.info(f"Parameters - equation_type: {equation_type}, degree: {degree}")

    # Validate file type
    if not file.content_type.startswith('image/'):
        logger.error(f"Invalid content type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Read image file
        logger.info("Reading file contents...")
        contents = await file.read()
        logger.info(f"File contents read successfully. Size: {len(contents)} bytes")

        logger.info("Converting file to numpy array...")
        nparr = np.frombuffer(contents, np.uint8)
        logger.info(f"Numpy array shape: {nparr.shape}")

        logger.info("Decoding image with OpenCV...")
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("OpenCV failed to decode the image")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        logger.info(f"Image decoded successfully. Shape: {img.shape}")
            
        # Process image and get face landmarks
        logger.info("Starting face detection...")
        landmarks = await face_detector.detect_face_async(img)
        logger.info(f"Face detection completed. Found features: {list(landmarks.keys())}")
        
        # Generate equations for different face parts
        logger.info("Starting equation generation...")
        equations = {}
        for part, points in landmarks.items():
            try:
                logger.info(f"Generating equation for {part} with {len(points)} points")
                eq = equation_generator.generate(
                    points=points,
                    method=equation_type,
                    degree=degree
                )
                equations[part] = eq
                logger.info(f"Successfully generated equation for {part}")
            except ValueError as e:
                logger.error(f"Error generating equation for {part}: {str(e)}")
                continue
        
        logger.info(f"Completed equations for {len(equations)} facial features")
        logger.info("=== Completed upload_image endpoint successfully ===")
                
        return {
            "landmarks": landmarks,
            "equations": equations
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
        logger.info("Closing file upload")
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
