from fastapi import APIRouter

from app.api.v1.endpoints import news, resume

api_router = APIRouter()

api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
