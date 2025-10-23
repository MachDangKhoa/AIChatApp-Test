"""
chat_router.py
---------------
Handles text-only chat with Gemini (multi-turn conversation).
"""

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import ChatResponse, ChatMessage
from services.gemini_service import ask_gemini_text, ask_gemini_text_streaming
from datetime import datetime
import json

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    stream: bool = Form(False),
    history: str = Form(default="[]")
):
    """
    Handles text-based chat with Gemini, with optional streaming.

    Args:
        message (str): User's message (e.g., "bạn là ai?").
        stream (bool): Whether to stream the response.
        history (str): JSON string of previous chat messages.

    Returns:
        StreamingResponse or ChatResponse: Streams JSON chunks or returns full response.
    """
    async def stream_response():
        try:
            # Parse history safely
            try:
                history_list = json.loads(history) if history else []
            except json.JSONDecodeError:
                raise HTTPException(status_code=422, detail="Invalid JSON in history")
            
            history_messages = [ChatMessage(**msg) for msg in history_list]
            

            # Prepare messages for Gemini
            messages = [{"role": "model" if m.role == "assistant" else m.role, "content": m.content} for m in history_messages] + [
                {"role": "user", "content": message}
            ]
            response = None
            full_response = ""

            # Process text query
            if stream:
                async for chunk in ask_gemini_text_streaming(messages):
                    full_response += chunk + " "
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            else:
                response = ask_gemini_text(messages)
                yield f"data: {json.dumps({'reply': response}, ensure_ascii=False)}\n\n"

            # Update history
            current_time = datetime.now().replace(microsecond=0)
            updated_history = history_messages + [
                ChatMessage(
                    role="user",
                    content=message,
                    image_url=None,
                    file_url=None,
                    timestamp=current_time
                ),
                ChatMessage(
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
        try:
            history_list = json.loads(history) if history else []
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid JSON in history")
        history_messages = [ChatMessage(**msg) for msg in history_list]

        # Prepare messages for Gemini
        messages = [{"role": "model" if m.role == "assistant" else m.role, "content": m.content} for m in history_messages] + [
            {"role": "user", "content": message}
        ]
        response = ask_gemini_text(messages)

        # Update history
        current_time = datetime.now().replace(microsecond=0)
        updated_history = history_messages + [
            ChatMessage(
                role="user",
                content=message,
                timestamp=current_time
            ),
            ChatMessage(
                role="assistant",
                content=response,
                timestamp=current_time
            )
        ]
        # Convert datetime to ISO string for JSON serialization
        history_dict = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in updated_history
        ]
        return ChatResponse(reply=response, history=updated_history)