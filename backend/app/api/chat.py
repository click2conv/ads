from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatRequest,
)

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new chat session.
    """
    service = ChatService(db)
    session = await service.create_session(
        session_name=session_data.session_name,
        context_keywords=session_data.context_keywords,
        context_date_from=session_data.context_date_from,
        context_date_to=session_data.context_date_to,
    )
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    List all chat sessions.
    """
    service = ChatService(db)
    sessions = await service.list_sessions(active_only)
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get session by ID with messages.
    """
    service = ChatService(db)
    session = await service._get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Load messages
    messages = await service.get_session_messages(session_id)
    session.messages = messages

    return session


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI and get a response.
    Creates a new session if session_id is not provided.
    """
    service = ChatService(db)

    # Create session if needed
    if not request.session_id:
        session = await service.create_session(
            context_keywords=request.context_keywords,
            context_date_from=request.context_date_from,
            context_date_to=request.context_date_to,
        )
        session_id = session.id
    else:
        session_id = request.session_id

    # Send message
    ai_message = await service.send_message(
        session_id=session_id,
        user_message=request.message,
        context_keywords=request.context_keywords,
        context_date_from=request.context_date_from,
        context_date_to=request.context_date_to,
    )

    return ai_message
