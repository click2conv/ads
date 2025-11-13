from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatSession(Base):
    """
    Stores chat conversation sessions.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Session info
    session_name = Column(String(500))

    # Context
    context_keywords = Column(JSON)  # Keywords in context
    context_date_from = Column(DateTime(timezone=True))
    context_date_to = Column(DateTime(timezone=True))

    # Metadata
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True))

    # Stats
    total_messages = Column(Integer, default=0)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    Individual messages in a chat session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    # Message details
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)

    # Context at time of message
    context_data = Column(JSON)  # Relevant data that was referenced

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    session = relationship("ChatSession", back_populates="messages")
