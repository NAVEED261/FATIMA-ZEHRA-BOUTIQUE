"""Chat Service Routes - AI Chat Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func

from .models import ChatMessage, ChatMessageRequest, ChatHistoryResponse, ChatMessageResponse
from .database import get_session
from .ai_client import generate_chat_response, stream_chat_response, get_system_prompt

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/messages")
async def send_message(
    message_data: ChatMessageRequest,
    session: Session = Depends(get_session)
):
    """
    Send chat message and get streaming response

    Returns: Server-Sent Events (SSE) stream
    """
    # Save user message
    user_msg = ChatMessage(
        user_id=message_data.user_id,
        session_id=message_data.session_id,
        role="user",
        content=message_data.text
    )
    session.add(user_msg)
    session.commit()

    # Get chat history
    history = session.exec(
        select(ChatMessage).where(
            ChatMessage.session_id == message_data.session_id
        ).order_by(ChatMessage.created_at)
    ).all()

    # Build messages for OpenAI
    messages = [{"role": "system", "content": get_system_prompt()}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    # Generate response
    async def response_generator():
        full_response = ""
        async for chunk in stream_chat_response(messages):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message
        assistant_msg = ChatMessage(
            user_id=message_data.user_id,
            session_id=message_data.session_id,
            role="assistant",
            content=full_response
        )
        session.add(assistant_msg)
        session.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """Get chat history for a session"""
    # Get total count
    total = session.exec(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id
        )
    ).one()

    # Get messages
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    # Reverse to get chronological order
    messages = list(reversed(messages))

    return ChatHistoryResponse(
        messages=[ChatMessageResponse.from_orm(m) for m in messages],
        total=total,
        session_id=session_id
    )


@router.delete("/history")
async def clear_chat_history(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Clear chat history for a session"""
    messages = session.exec(
        select(ChatMessage).where(
            ChatMessage.session_id == session_id
        )
    ).all()

    for msg in messages:
        session.delete(msg)

    session.commit()

    return {"message": "Chat history cleared", "session_id": session_id}
