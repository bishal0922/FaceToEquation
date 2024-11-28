from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import face_processing

app = FastAPI()

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