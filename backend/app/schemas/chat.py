from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSessionCreate(BaseModel):
    session_name: Optional[str] = Field(None, max_length=500)
    context_keywords: Optional[List[str]] = None
    context_date_from: Optional[datetime] = None
    context_date_to: Optional[datetime] = None


class ChatMessageCreate(BaseModel):
    role: str = Field(..., max_length=50)
    content: str


class ChatMessageResponse(ChatMessageCreate):
    id: int
    session_id: int
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    context_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    session_name: Optional[str] = None
    context_keywords: Optional[List[str]] = None
    context_date_from: Optional[datetime] = None
    context_date_to: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    total_messages: int
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: Optional[int] = Field(None, description="Existing session ID or None for new")
    message: str = Field(..., description="User message")
    context_keywords: Optional[List[str]] = Field(None, description="Keywords for context")
    context_date_from: Optional[datetime] = Field(None, description="Start date for context")
    context_date_to: Optional[datetime] = Field(None, description="End date for context")
