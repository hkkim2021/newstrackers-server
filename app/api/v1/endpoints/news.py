from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.news import NewsArticleModel
from app.services.naver_news_collector import collect_all_keywords
from app.agents.graphs.pipeline import run_pipeline_by_resume_id

router = APIRouter()


@router.post("/collect")
def trigger_news_collection(db: Session = Depends(get_db)):
    total = collect_all_keywords(db)
    return {"message": f"뉴스 수집 완료: {total}건 처리"}


@router.get("/")
def list_news(
    category: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(NewsArticleModel)
    if category:
        query = query.filter(NewsArticleModel.category == category)
    if keyword:
        query = query.filter(NewsArticleModel.keywords.any(keyword))
    articles = query.order_by(NewsArticleModel.pub_date.desc()).offset(offset).limit(limit).all()

    return {
        "count": len(articles),
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "link": a.link,
                "pub_date": a.pub_date.isoformat() if a.pub_date else None,
                "category": a.category,
                "keywords": a.keywords,
                "collected_at": a.collected_at.isoformat() if a.collected_at else None,
            }
            for a in articles
        ],
    }


@router.get("/report/{resume_id}")
def generate_report(
    resume_id: str,
    days: int = 30,
    min_score: int = 70,
    top_n: int = 20,
    db: Session = Depends(get_db),
):
    """Node2→3→4 파이프라인: 뉴스 필터링 → 점수 → 리포트 생성"""
    try:
        return run_pipeline_by_resume_id(
            resume_id, db, days=days, min_score=min_score, top_n=top_n,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
