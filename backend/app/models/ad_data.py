from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class AdCapture(Base):
    """
    Main table for storing captured ad data.
    NEVER delete records - all historical data is preserved.
    """
    __tablename__ = "ad_captures"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))

    # Search context
    keyword = Column(String(500), index=True, nullable=False)
    location = Column(String(200), index=True)  # Geographic location
    device_type = Column(String(50), index=True)  # desktop, mobile, tablet

    # Ad identification
    advertiser_domain = Column(String(500), index=True)
    advertiser_name = Column(String(500), index=True)

    # URLs
    display_url = Column(Text)
    final_url = Column(Text)
    landing_page_url = Column(Text)

    # Ad position
    ad_position = Column(Integer)  # 1, 2, 3, etc.
    is_top_ad = Column(Boolean, default=True)

    # Timestamps
    captured_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Metadata
    source = Column(String(100))  # manual, api, scheduled
    search_id = Column(String(100), index=True)  # Group related captures
    raw_data = Column(JSON)  # Store any additional data

    # Quality score estimate (if available)
    estimated_quality_score = Column(Float)

    # Active status (for soft deletes if needed, but we preserve data)
    is_active = Column(Boolean, default=True)

    # Relationships
    headlines = relationship("AdHeadline", back_populates="ad_capture", cascade="all, delete-orphan")
    descriptions = relationship("AdDescription", back_populates="ad_capture", cascade="all, delete-orphan")
    extensions = relationship("AdExtension", back_populates="ad_capture", cascade="all, delete-orphan")


class AdHeadline(Base):
    """
    Stores individual headlines for an ad.
    Ads can have multiple headlines (typically 3-15).
    """
    __tablename__ = "ad_headlines"

    id = Column(Integer, primary_key=True, index=True)
    ad_capture_id = Column(Integer, ForeignKey("ad_captures.id"), nullable=False)

    headline_text = Column(String(500), nullable=False)
    position = Column(Integer)  # Order in which headline appears
    character_count = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    ad_capture = relationship("AdCapture", back_populates="headlines")


class AdDescription(Base):
    """
    Stores individual descriptions for an ad.
    Ads typically have 2-4 descriptions.
    """
    __tablename__ = "ad_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    ad_capture_id = Column(Integer, ForeignKey("ad_captures.id"), nullable=False)

    description_text = Column(Text, nullable=False)
    position = Column(Integer)  # Order in which description appears
    character_count = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    ad_capture = relationship("AdCapture", back_populates="descriptions")


class AdExtension(Base):
    """
    Stores ad extensions (sitelinks, callouts, structured snippets, etc.)
    """
    __tablename__ = "ad_extensions"

    id = Column(Integer, primary_key=True, index=True)
    ad_capture_id = Column(Integer, ForeignKey("ad_captures.id"), nullable=False)

    extension_type = Column(String(100), index=True)  # sitelink, callout, structured_snippet, call, location, price
    extension_text = Column(Text)
    extension_url = Column(Text)

    # For structured data
    extension_data = Column(JSON)

    position = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    ad_capture = relationship("AdCapture", back_populates="extensions")
