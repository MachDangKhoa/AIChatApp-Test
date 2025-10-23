"""
schemas.py
-----------
Defines Pydantic models for request and response validation.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChatMessage(BaseModel):
    """Represents a single chat message (user or assistant)."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    image_url: Optional[str] = None
    file_url: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v else None
        }


class ChatRequest(BaseModel):
    """Request model for multi-turn chat."""
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Response model containing assistant reply."""
    reply: str
    history: List[ChatMessage]

class ImageChatMessage(BaseModel):
    """Represents a single message in image-based chat."""
    role: str  # "user" or "assistant"
    content: str
    image_url: Optional[str] = None
    file_url: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v else None
        }

class ImageChatRequest(BaseModel):
    """Request model for image Q&A."""
    question: str
    history: Optional[List[ImageChatMessage]] = []

class ImageChatResponse(BaseModel):
    """Response model for image-based chat."""
    reply: str
    history: List[ImageChatMessage]


class CSVChatMessage(BaseModel):
    """Represents a single message in CSV-based chat."""
    role: str
    content: str
    image_url: Optional[str] = None
    file_url: Optional[str] = None  
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v else None
        }

class CSVChatRequest(BaseModel):
    """Request model for CSV data chat."""
    question: str
    history: Optional[List[CSVChatMessage]] = []

class CSVChatResponse(BaseModel):
    """Response model for CSV-based chat."""
    reply: str
    history: List[CSVChatMessage]
