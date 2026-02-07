import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router
from app.services.naver_news_collector import run_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and start scheduler
    Base.metadata.create_all(bind=engine)
    logger.info("DB 테이블 생성 완료")

    scheduler.add_job(run_batch, "cron", hour=2, minute=0, id="news_batch")
    scheduler.start()
    logger.info("뉴스 배치 스케줄러 시작 (매일 02:00)")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("스케줄러 종료")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
