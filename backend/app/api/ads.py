from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.services.ad_service import AdService
from app.schemas.ad_data import (
    AdCaptureCreate,
    AdCaptureResponse,
    AdSearchRequest,
    AdSearchResponse,
)

router = APIRouter()


@router.post("/capture", response_model=AdCaptureResponse)
async def capture_ad(
    ad_data: AdCaptureCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Capture a single ad.
    """
    service = AdService(db)
    ad = await service.capture_ad(ad_data)
    return ad


@router.post("/capture/batch", response_model=List[AdCaptureResponse])
async def capture_multiple_ads(
    ads_data: List[AdCaptureCreate],
    search_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Capture multiple ads from a single search.
    """
    service = AdService(db)
    ads = await service.capture_multiple_ads(ads_data, search_id)
    return ads


@router.get("/{ad_id}", response_model=AdCaptureResponse)
async def get_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single ad by ID.
    """
    service = AdService(db)
    ad = await service.get_ad(ad_id)

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    return ad


@router.get("/", response_model=dict)
async def search_ads(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    advertiser: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Search ads with various filters.
    """
    service = AdService(db)
    ads, total = await service.search_ads(
        keyword=keyword,
        location=location,
        device_type=device_type,
        advertiser=advertiser,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "ads": ads
    }


@router.get("/advertisers/list", response_model=List[str])
async def get_advertisers(
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of unique advertisers.
    """
    service = AdService(db)
    advertisers = await service.get_advertisers(limit)
    return advertisers


@router.get("/keywords/list", response_model=List[str])
async def get_keywords(
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of unique keywords.
    """
    service = AdService(db)
    keywords = await service.get_keywords(limit)
    return keywords


@router.get("/history/{advertiser}", response_model=List[AdCaptureResponse])
async def get_ad_history(
    advertiser: str,
    keyword: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical ads for a specific advertiser.
    """
    service = AdService(db)
    ads = await service.get_ad_history(advertiser, keyword, limit)
    return ads


@router.get("/stats/overview")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get overall statistics about captured ads.
    """
    service = AdService(db)
    stats = await service.get_stats()
    return stats
