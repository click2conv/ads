from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Keyword(Base):
    """
    Stores keywords that users want to monitor.
    """
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)

    keyword_text = Column(String(500), nullable=False, index=True)

    # Filters
    location = Column(String(200))
    device_type = Column(String(50))  # desktop, mobile, tablet, all

    # Monitoring settings
    is_active = Column(Boolean, default=True, index=True)
    check_interval_hours = Column(Integer, default=1)  # How often to check

    # Last check info
    last_checked_at = Column(DateTime(timezone=True))
    last_check_status = Column(String(50))  # success, failed, pending

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Notes/tags
    notes = Column(Text)
    tags = Column(JSON)  # Array of tags

    # Stats
    total_checks = Column(Integer, default=0)
    total_ads_found = Column(Integer, default=0)


class KeywordMonitor(Base):
    """
    Tracks scheduled monitoring tasks for keywords.
    """
    __tablename__ = "keyword_monitors"

    id = Column(Integer, primary_key=True, index=True)

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)

    # Schedule info
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed

    # Results
    ads_found = Column(Integer, default=0)
    error_message = Column(Text)

    # Celery task ID
    task_id = Column(String(100))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
