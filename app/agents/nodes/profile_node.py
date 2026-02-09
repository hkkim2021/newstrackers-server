"""Node1: 자소서 프로필 분석."""
import logging

from app.agents.state import PipelineState
from app.services.profile_extractor import extract_profile

logger = logging.getLogger(__name__)


def profile_node(state: PipelineState) -> dict:
    """raw_text → Gemini 프로필 추출 → profile dict 반환."""
    raw_text = state["raw_text"]

    profile = extract_profile(raw_text)
    profile_dict = profile.model_dump()

    logger.info(f"Node1: 프로필 추출 완료 - {profile.target_position}")

    return {"profile": profile_dict}
