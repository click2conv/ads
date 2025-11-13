from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.keyword_service import KeywordService
from app.schemas.keyword import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse,
)

router = APIRouter()


@router.post("/", response_model=KeywordResponse)
async def create_keyword(
    keyword_data: KeywordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new keyword to monitor.
    """
    service = KeywordService(db)
    keyword = await service.create_keyword(keyword_data)
    return keyword


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get keyword by ID.
    """
    service = KeywordService(db)
    keyword = await service.get_keyword(keyword_id)

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    return keyword


@router.get("/", response_model=KeywordListResponse)
async def list_keywords(
    active_only: bool = Query(True),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List keywords with optional filtering.
    """
    service = KeywordService(db)
    keywords, total = await service.list_keywords(active_only, limit, offset)

    return {
        "total": total,
        "keywords": keywords
    }


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    update_data: KeywordUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update keyword settings.
    """
    service = KeywordService(db)
    keyword = await service.update_keyword(keyword_id, update_data)

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    return keyword


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete keyword (set inactive).
    """
    service = KeywordService(db)
    success = await service.delete_keyword(keyword_id)

    if not success:
        raise HTTPException(status_code=404, detail="Keyword not found")

    return {"status": "deleted", "keyword_id": keyword_id}


@router.get("/{keyword_id}/history")
async def get_monitor_history(
    keyword_id: int,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Get monitoring history for a keyword.
    """
    service = KeywordService(db)
    history = await service.get_monitor_history(keyword_id, limit)
    return history
