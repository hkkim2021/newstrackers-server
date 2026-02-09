"""Node3: Gemini 관련성 점수 매기기."""
import logging

from app.agents.state import PipelineState
from app.schemas.resume import UserProfile
from app.services.news_scorer import score_news

logger = logging.getLogger(__name__)


def scorer_node(state: PipelineState) -> dict:
    """filtered_articles → Gemini 점수 → scored_articles 반환."""
    profile = UserProfile(**state["profile"])
    filtered = state["filtered_articles"]
    min_score = state.get("min_score", 70)
    top_n = state.get("top_n", 20)

    scored = score_news(profile, filtered, min_score=min_score, top_n=top_n)

    logger.info(f"Node3: {len(scored)}건 (>= {min_score}점)")

    return {"scored_articles": scored}
