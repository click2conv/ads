from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create and run a new analysis.
    This will analyze ad data and generate AI-powered insights.
    """
    service = AnalysisService(db)

    analysis = await service.create_analysis(
        analysis_type=request.analysis_type,
        keywords=request.keywords,
        competitors=request.competitors,
        date_from=request.date_from,
        date_to=request.date_to,
        device_type=request.device_type,
        location=request.location,
    )

    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analysis by ID with all insights.
    """
    service = AnalysisService(db)
    analysis = await service.get_analysis(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis
