"""Node2: 키워드 기반 뉴스 1차 필터링."""
import logging

from app.agents.state import PipelineState
from app.schemas.resume import UserProfile
from app.services.news_filter import build_search_keywords, filter_news_by_profile

logger = logging.getLogger(__name__)


def filter_node(state: PipelineState) -> dict:
    """profile → DB Array Overlap 검색 → filtered_articles 반환."""
    profile = UserProfile(**state["profile"])
    db = state["db"]
    days = state.get("days", 30)
    filter_limit = state.get("filter_limit", 300)

    search_keywords = build_search_keywords(profile)
    filtered = filter_news_by_profile(profile, db, days=days, limit=filter_limit)

    logger.info(f"Node2: {len(filtered)}건 필터링 (키워드 {len(search_keywords)}개)")

    return {
        "search_keywords": search_keywords,
        "filtered_articles": filtered,
    }
