import logging
from datetime import datetime

import httpx
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.keywords import NEWS_KEYWORDS
from app.models.news import NewsArticleModel
from sqlalchemy import func

logger = logging.getLogger(__name__)

NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"


def search_news(keyword: str, display: int = 100, sort: str = "date") -> list[dict]:
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }
    params = {
        "query": keyword,
        "display": display,
        "sort": sort,
    }
    with httpx.Client(timeout=30) as client:
        response = client.get(NAVER_NEWS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    return data.get("items", [])


def _clean_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text).replace("&quot;", '"').replace("&amp;", "&")


def _parse_pub_date(date_str: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except (ValueError, TypeError):
        return None


def save_to_db(articles: list[dict], keyword: str, category: str, db: Session):
    for item in articles:
        link = item.get("originallink") or item.get("link", "")
        if not link:
            continue

        existing = db.query(NewsArticleModel).filter_by(link=link).first()
        if existing:
            if keyword not in (existing.keywords or []):
                db.execute(
                    update(NewsArticleModel)
                    .where(NewsArticleModel.link == link)
                    .values(keywords=func.array_append(NewsArticleModel.keywords, keyword))
                )
        else:
            article = NewsArticleModel(
                title=_clean_html(item.get("title", "")),
                description=_clean_html(item.get("description", "")),
                link=link,
                pub_date=_parse_pub_date(item.get("pubDate")),
                category=category,
                keywords=[keyword],
            )
            db.add(article)

    db.commit()


def collect_all_keywords(db: Session):
    total = 0
    for category, keywords in NEWS_KEYWORDS.items():
        for keyword in keywords:
            try:
                articles = search_news(keyword)
                save_to_db(articles, keyword, category, db)
                total += len(articles)
                logger.info(f"[{category}] '{keyword}': {len(articles)}건 수집")
            except Exception as e:
                logger.error(f"[{category}] '{keyword}' 수집 실패: {e}")
    return total


def run_batch():
    logger.info("뉴스 배치 수집 시작")
    db = SessionLocal()
    try:
        total = collect_all_keywords(db)
        logger.info(f"뉴스 배치 수집 완료: 총 {total}건 처리")
    except Exception as e:
        logger.error(f"뉴스 배치 수집 실패: {e}")
        db.rollback()
    finally:
        db.close()
