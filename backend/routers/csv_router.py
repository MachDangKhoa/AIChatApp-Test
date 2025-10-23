"""
csv_router.py
--------------
FastAPI routes for handling CSV-based chat interactions WITH STREAMING SUPPORT.
STRUCTURE SIMILAR TO chat_router.py
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import CSVChatResponse, CSVChatMessage
from services.csv_service import (
    summarize_csv, 
    save_uploaded_csv, 
    ask_gemini_about_data, 
    ask_gemini_about_data_streaming,
    download_csv_from_url, 
    generate_histogram_data
)
from datetime import datetime
import json
import re

router = APIRouter()

@router.post("/", response_model=CSVChatResponse)
async def chat_with_csv(
    question: str = Form(...),
    file: UploadFile = File(None),
    url: str = Form(None),
    stream: bool = Form(False),
    history: str = Form(default="[]")
):
    """
    Handles CSV-based chat with Gemini, with optional streaming.
    STRUCTURE IDENTICAL TO chat_router.py

    Args:
        question (str): User's analytical question about the CSV.
        file (UploadFile, optional): CSV file uploaded by the user.
        url (str, optional): Direct URL pointing to a raw CSV file.
        stream (bool): Whether to stream the response.
        history (str): JSON string of previous chat messages.

    Returns:
        StreamingResponse or CSVChatResponse: Streams JSON chunks or returns full response.
    """
    async def stream_response():
        try:
            # Parse history safely
            try:
                history_list = json.loads(history) if history else []
            except json.JSONDecodeError:
                raise HTTPException(status_code=422, detail="Invalid JSON in history")
            history_messages = [CSVChatMessage(**msg) for msg in history_list]

            file_url = None
            content_text = None
            response = None
            file_name = None
            full_response = ""

            # Load CSV content from uploaded file or URL
            if file:
                content_bytes = await file.read()
                content_text = content_bytes.decode("utf-8-sig")
                file_name = file.filename or "uploaded_file.csv"
                if not content_text.strip():
                    yield f"data: {json.dumps({'error': 'The CSV file is empty or contains no data.'}, ensure_ascii=False)}\n\n"
                    return
                file_url = save_uploaded_csv(file, content_bytes)
            elif url:
                content_text = download_csv_from_url(url)
                file_name = url.split('/')[-1] or "remote_file.csv"
                file_url = url
            else:
                yield f"data: {json.dumps({'error': 'Must provide either file or URL.'}, ensure_ascii=False)}\n\n"
                return

            # Detect histogram requests
            histogram_match = re.search(
                r"(?:histogram|vẽ biểu đồ|biểu đồ phân phối|phân phối|vẽ histogram|plot|chart|graph)\s*(?:cột |cho |của |về |for |of |)\s*(?:cột |column |)\s*['\"]?([\w\s]+?)['\"]?(\s*(?:dùm tôi|nha|please|\s*$|\b))",
                question.lower()
            )

            if histogram_match:
                # Handle histogram (non-streaming, instant response)
                column = histogram_match.group(1).strip()
                hist_data = generate_histogram_data(content_text, column)
                if "error" in hist_data:
                    response = hist_data["error"]
                else:
                    response = f"📊 Histogram data for '{column}':\n{json.dumps(hist_data, indent=2)}"
                yield f"data: {json.dumps({'reply': response}, ensure_ascii=False)}\n\n"
                full_response = response
            else:
                # Handle AI analysis
                summary = summarize_csv(content_text)
                if summary.startswith("❌"):
                    yield f"data: {json.dumps({'error': summary}, ensure_ascii=False)}\n\n"
                    return

                # Process with streaming or non-streaming
                if stream:
                    async for chunk in ask_gemini_about_data_streaming(question, summary, file_name):
                        full_response += chunk
                        yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                else:
                    response = ask_gemini_about_data(question, summary, file_name)
                    yield f"data: {json.dumps({'reply': response}, ensure_ascii=False)}\n\n"
                    full_response = response

            # Update history
            current_time = datetime.now().replace(microsecond=0)
            updated_history = history_messages + [
                CSVChatMessage(
                    role="user",
                    content=question,
                    image_url=None,
                    file_url=file_url,
                    timestamp=current_time
                ),
                CSVChatMessage(
                    role="assistant",
                    content=full_response if not response else response,
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
                    "file_url": msg.file_url,
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
        # Non-streaming response (identical to chat_router structure)
        try:
            history_list = json.loads(history) if history else []
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="Invalid JSON in history")
        history_messages = [CSVChatMessage(**msg) for msg in history_list]

        file_url = None
        content_text = None
        file_name = None

        # Load CSV content
        if file:
            content_bytes = await file.read()
            content_text = content_bytes.decode("utf-8-sig")
            file_name = file.filename or "uploaded_file.csv"
            if not content_text.strip():
                raise HTTPException(status_code=400, detail="The CSV file is empty or contains no data.")
            file_url = save_uploaded_csv(file, content_bytes)
        elif url:
            content_text = download_csv_from_url(url)
            file_name = url.split('/')[-1] or "remote_file.csv"
            file_url = url
        else:
            raise HTTPException(status_code=400, detail="Must provide either file or URL.")

        # Detect histogram
        histogram_match = re.search(
            r"(?:histogram|vẽ biểu đồ|biểu đồ phân phối|phân phối|vẽ histogram|plot|chart|graph)\s*(?:cột |cho |của |về |for |of |)\s*(?:cột |column |)\s*['\"]?([\w\s]+?)['\"]?(\s*(?:dùm tôi|nha|please|\s*$|\b))",
            question.lower()
        )

        if histogram_match:
            column = histogram_match.group(1).strip()
            hist_data = generate_histogram_data(content_text, column)
            if "error" in hist_data:
                response = hist_data["error"]
            else:
                response = f"📊 Histogram data for '{column}':\n{json.dumps(hist_data, indent=2)}"
        else:
            summary = summarize_csv(content_text)
            if summary.startswith("❌"):
                raise HTTPException(status_code=400, detail=summary)
            response = ask_gemini_about_data(question, summary, file_name)

        # Update history
        current_time = datetime.now().replace(microsecond=0)
        updated_history = history_messages + [
            CSVChatMessage(
                role="user",
                content=question,
                file_url=file_url,
                file_name=file_name,
                timestamp=current_time
            ),
            CSVChatMessage(
                role="assistant",
                content=response,
                file_url=None,
                file_name=file_name,
                timestamp=current_time
            )
        ]

        return CSVChatResponse(reply=response, history=updated_history)