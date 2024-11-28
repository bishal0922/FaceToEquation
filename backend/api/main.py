from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import face_processing  # Changed this line
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FaceToEquation API",
    description="API for converting facial features to mathematical equations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(face_processing.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting FaceToEquation API")
    try:
        # Initialize any necessary services
        pass
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FaceToEquation API")
    try:
        # Cleanup any resources
        pass
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise