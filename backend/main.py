"""
main.py
--------
Entry point for the FastAPI backend application.

Includes routers for:
- Text-based multi-turn chat
- Image-based Q&A
- CSV data analysis chat

Author: Dang Khoa
Created: Oct 2025
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chat_router, image_router, csv_router

# Initialize FastAPI application
app = FastAPI(title="AI Chat Backend", version="1.0.0")

app.mount("/temp_uploads", StaticFiles(directory="data/temp_uploads"), name="temp_uploads")

# Allow CORS for local development (frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For test/demo, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])
app.include_router(image_router.router, prefix="/api/image", tags=["Image"])
app.include_router(csv_router.router, prefix="/api/csv", tags=["CSV"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "✅ AI Chat Backend is running successfully!"}
