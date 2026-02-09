"""Node4: 면접 준비 리포트 생성."""
import logging

from app.agents.state import PipelineState
from app.schemas.resume import UserProfile
from app.services.report_generator import generate_report, _group_articles

logger = logging.getLogger(__name__)


def report_node(state: PipelineState) -> dict:
    """scored_articles → 그룹핑 + Gemini 리포트 생성."""
    profile = UserProfile(**state["profile"])
    scored = state["scored_articles"]

    grouped = _group_articles(scored)
    report = generate_report(profile, scored)

    logger.info("Node4: 리포트 생성 완료")

    return {
        "grouped_articles": grouped,
        "report": report,
    }
