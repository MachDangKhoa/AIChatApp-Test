"""
image_router.py
----------------
Routes for image upload and visual question answering.
"""

import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.image_service import save_uploaded_image, ask_gemini_with_image, ask_gemini_with_image_streaming
from models.schemas import ImageChatRequest, ImageChatResponse, ImageChatMessage
from datetime import datetime
from fastapi.responses import StreamingResponse
import json

router = APIRouter()


@router.post("/", response_model=ImageChatResponse)
async def chat_with_image(
    question: str = Form(...),
    file: UploadFile = File(...),
    stream: bool = Form(False),
    history: str = Form(default="[]")
):
    """
    Handles image-based queries with Gemini, with optional streaming.

    Args:
        question (str): User's question about the image.
        file (UploadFile): Uploaded image file.
        stream (bool): Whether to stream the response.
        history (str): JSON string of previous chat messages.

    Returns:
        StreamingResponse or dict: Streams JSON chunks or returns full response.
    """
    async def stream_response():
        try:
            # Parse history
            history_list = json.loads(history) if history else []
            history_messages = [ImageChatMessage(**msg) for msg in history_list]
            image_path = save_uploaded_image(file)
            filename = os.path.basename(image_path)
            image_url = f"http://127.0.0.1:8000/temp_uploads/{filename}"

            response = None
            full_response = ""  # To collect chunks for history

            # Process image query
            if stream:
                async for chunk in ask_gemini_with_image_streaming(question, image_path):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            else:
                response = ask_gemini_with_image(question, image_path)
                yield f"data: {json.dumps({'reply': response}, ensure_ascii=False)}\n\n"

            # Update history
            current_time = datetime.now().replace(microsecond=0)
            updated_history = history_messages + [
                ImageChatMessage(
                    role="user",
                    content=question,
                    image_url=image_url,
                    file_url=None,
                    timestamp=current_time
                ),
                ImageChatMessage(
                    role="assistant",
                    content=response if response else full_response.strip(),
                    image_url=None,
                    file_url=None,
                    timestamp=current_time
                )
            ]

            # Convert datetime to ISO string for JSON serialization
            history_dict = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "image_url": msg.image_url,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in updated_history
            ]

            yield f"data: {json.dumps({'history': history_dict, 'status': 'complete'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    if stream:
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    else:
        # Non-streaming response
        history_list = json.loads(history) if history else []
        history_messages = history_list
        image_path = save_uploaded_image(file)
        filename = os.path.basename(image_path)
        image_url = f"http://127.0.0.1:8000/temp_uploads/{filename}"
        response = ask_gemini_with_image(question, image_path)
        current_time = datetime.now().replace(microsecond=0)
        updated_history = history_messages + [
            {
                "role": "user",
                "content": question,
                "image_url": image_url,
                "timestamp": current_time.isoformat()
            },
            {
                "role": "assistant",
                "content": response,
                "image_url": None,
                "timestamp": current_time.isoformat()
            }
        ]
        return {"reply": response, "history": updated_history}