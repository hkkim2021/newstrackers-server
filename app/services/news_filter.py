import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.resume import UserProfile

logger = logging.getLogger(__name__)


def build_search_keywords(profile: UserProfile) -> list[str]:
    """프로필에서 검색용 키워드를 모두 수집한다."""
    keywords = set()

    # keywords
    keywords.update(profile.keywords)

    # tech_stack (nested dict → flatten)
    for techs in profile.tech_stack.values():
        keywords.update(techs)

    # fields, interests, interested_companies
    keywords.update(profile.fields)
    keywords.update(profile.interests)
    keywords.update(profile.interested_companies)

    # target_position (단일 문자열)
    if profile.target_position:
        keywords.add(profile.target_position)

    # 빈 문자열 제거
    keywords.discard("")

    return list(keywords)


def filter_news_by_profile(
    profile: UserProfile,
    db: Session,
    days: int = 30,
    limit: int = 300,
) -> list[dict]:
    """프로필 키워드로 뉴스를 1차 필터링한다 (Array Overlap)."""
    search_keywords = build_search_keywords(profile)

    if not search_keywords:
        logger.warning("검색 키워드가 없습니다.")
        return []

    logger.info(f"검색 키워드 {len(search_keywords)}개: {search_keywords[:10]}...")

    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = db.execute(
        text("""
            SELECT id, title, description, link, pub_date, category, keywords, collected_at
            FROM news_articles
            WHERE keywords && CAST(:keywords AS varchar[])
              AND pub_date >= :since
            ORDER BY pub_date DESC
            LIMIT :limit
        """),
        {
            "keywords": search_keywords,
            "since": since,
            "limit": limit,
        },
    )

    articles = []
    for row in result.mappings():
        articles.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "link": row["link"],
            "pub_date": row["pub_date"].isoformat() if row["pub_date"] else None,
            "category": row["category"],
            "keywords": row["keywords"],
            "collected_at": row["collected_at"].isoformat() if row["collected_at"] else None,
        })

    logger.info(f"1차 필터링 결과: {len(articles)}건")
    return articles


