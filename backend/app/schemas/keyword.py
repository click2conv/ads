from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class KeywordCreate(BaseModel):
    keyword_text: str = Field(..., max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field("desktop", max_length=50)
    check_interval_hours: int = Field(1, ge=1, le=168)  # 1 hour to 1 week
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class KeywordUpdate(BaseModel):
    keyword_text: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    check_interval_hours: Optional[int] = Field(None, ge=1, le=168)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class KeywordResponse(BaseModel):
    id: int
    keyword_text: str
    location: Optional[str] = None
    device_type: Optional[str] = None
    is_active: bool
    check_interval_hours: int
    last_checked_at: Optional[datetime] = None
    last_check_status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    total_checks: int
    total_ads_found: int

    class Config:
        from_attributes = True


class KeywordListResponse(BaseModel):
    total: int
    keywords: List[KeywordResponse]
