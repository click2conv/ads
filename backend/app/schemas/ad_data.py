from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class AdHeadlineCreate(BaseModel):
    headline_text: str = Field(..., max_length=500)
    position: Optional[int] = None


class AdHeadlineResponse(AdHeadlineCreate):
    id: int
    character_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdDescriptionCreate(BaseModel):
    description_text: str
    position: Optional[int] = None


class AdDescriptionResponse(AdDescriptionCreate):
    id: int
    character_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdExtensionCreate(BaseModel):
    extension_type: str = Field(..., max_length=100)
    extension_text: Optional[str] = None
    extension_url: Optional[str] = None
    extension_data: Optional[Dict[str, Any]] = None
    position: Optional[int] = None


class AdExtensionResponse(AdExtensionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdCaptureCreate(BaseModel):
    keyword: str = Field(..., max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field(None, max_length=50)
    advertiser_domain: Optional[str] = Field(None, max_length=500)
    advertiser_name: Optional[str] = Field(None, max_length=500)
    display_url: Optional[str] = None
    final_url: Optional[str] = None
    landing_page_url: Optional[str] = None
    ad_position: Optional[int] = None
    is_top_ad: bool = True
    source: Optional[str] = Field(None, max_length=100)
    search_id: Optional[str] = Field(None, max_length=100)
    raw_data: Optional[Dict[str, Any]] = None
    estimated_quality_score: Optional[float] = None

    headlines: List[AdHeadlineCreate] = []
    descriptions: List[AdDescriptionCreate] = []
    extensions: List[AdExtensionCreate] = []


class AdCaptureResponse(BaseModel):
    id: int
    uuid: str
    keyword: str
    location: Optional[str] = None
    device_type: Optional[str] = None
    advertiser_domain: Optional[str] = None
    advertiser_name: Optional[str] = None
    display_url: Optional[str] = None
    final_url: Optional[str] = None
    landing_page_url: Optional[str] = None
    ad_position: Optional[int] = None
    is_top_ad: bool
    captured_at: datetime
    created_at: datetime
    source: Optional[str] = None
    search_id: Optional[str] = None
    estimated_quality_score: Optional[float] = None
    is_active: bool

    headlines: List[AdHeadlineResponse] = []
    descriptions: List[AdDescriptionResponse] = []
    extensions: List[AdExtensionResponse] = []

    class Config:
        from_attributes = True


class AdSearchRequest(BaseModel):
    keyword: str = Field(..., max_length=500, description="Keyword to search for")
    location: Optional[str] = Field(None, max_length=200, description="Geographic location")
    device_type: Optional[str] = Field("desktop", description="Device type: desktop, mobile, tablet")
    max_ads: int = Field(10, ge=1, le=50, description="Maximum number of ads to capture")
    source: str = Field("manual", description="Source of the search")


class AdSearchResponse(BaseModel):
    search_id: str
    keyword: str
    location: Optional[str] = None
    device_type: Optional[str] = None
    ads_found: int
    ads_captured: List[AdCaptureResponse]
    timestamp: datetime
