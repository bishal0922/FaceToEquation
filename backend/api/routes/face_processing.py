from fastapi import APIRouter, UploadFile, File
from api.services import face_detector, equation_generator
import numpy as np
import cv2

router = APIRouter()

@router.get("/")
async def hello():
    return {"message": "Hello World"}

@router.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process image and generate outline
    face_outline = face_detector.detect_face(img)
    
    # Generate equations
    equations = equation_generator.generate(face_outline)
    
    return {"outline": face_outline, "equations": equations}