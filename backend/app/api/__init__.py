from fastapi import APIRouter
from .ads import router as ads_router
from .keywords import router as keywords_router
from .analysis import router as analysis_router
from .chat import router as chat_router

api_router = APIRouter()

api_router.include_router(ads_router, prefix="/ads", tags=["ads"])
api_router.include_router(keywords_router, prefix="/keywords", tags=["keywords"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
