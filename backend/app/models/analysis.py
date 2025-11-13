from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Analysis(Base):
    """
    Stores AI-generated analysis results.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    # Analysis scope
    analysis_type = Column(String(100), index=True)  # keyword, competitor, timerange, overall

    # Filters used
    keywords = Column(JSON)  # Array of keywords analyzed
    competitors = Column(JSON)  # Array of competitor domains
    date_from = Column(DateTime(timezone=True))
    date_to = Column(DateTime(timezone=True))
    device_type = Column(String(50))
    location = Column(String(200))

    # Results
    summary = Column(Text)  # Overall summary
    total_ads_analyzed = Column(Integer)
    total_headlines_analyzed = Column(Integer)
    total_descriptions_analyzed = Column(Integer)

    # AI metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True))

    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed

    # Relationships
    insights = relationship("AnalysisInsight", back_populates="analysis", cascade="all, delete-orphan")


class AnalysisInsight(Base):
    """
    Individual insights from an analysis.
    """
    __tablename__ = "analysis_insights"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    # Insight details
    insight_type = Column(String(100), index=True)  # pattern, recommendation, trend, gap, winner
    category = Column(String(100))  # headline, description, extension, overall

    title = Column(String(500))
    description = Column(Text)

    # Supporting data
    examples = Column(JSON)  # Array of examples
    metrics = Column(JSON)  # Relevant metrics

    # Priority/confidence
    priority = Column(String(50))  # high, medium, low
    confidence_score = Column(Float)  # 0.0 to 1.0

    # Actionable items
    recommendations = Column(JSON)  # Array of actionable recommendations

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    analysis = relationship("Analysis", back_populates="insights")
