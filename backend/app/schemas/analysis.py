from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="Type: keyword, competitor, timerange, overall")
    keywords: Optional[List[str]] = Field(None, description="Keywords to analyze")
    competitors: Optional[List[str]] = Field(None, description="Competitor domains")
    date_from: Optional[datetime] = Field(None, description="Start date")
    date_to: Optional[datetime] = Field(None, description="End date")
    device_type: Optional[str] = Field(None, description="Device type filter")
    location: Optional[str] = Field(None, description="Location filter")


class AnalysisInsightResponse(BaseModel):
    id: int
    insight_type: str
    category: str
    title: str
    description: str
    examples: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    priority: str
    confidence_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: int
    analysis_type: str
    keywords: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    total_ads_analyzed: Optional[int] = None
    total_headlines_analyzed: Optional[int] = None
    total_descriptions_analyzed: Optional[int] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    insights: List[AnalysisInsightResponse] = []

    class Config:
        from_attributes = True
