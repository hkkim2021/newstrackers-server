from typing import Any

from typing_extensions import TypedDict


class PipelineState(TypedDict, total=False):
    """Node1→2→3→4 파이프라인 상태."""
    # Input
    resume_id: str
    file_name: str
    raw_text: str

    # Node1: 프로필 분석
    profile: dict

    # Node2: 1차 필터링
    search_keywords: list[str]
    filtered_articles: list[dict]

    # Node3: 관련성 점수
    scored_articles: list[dict]

    # Node4: 리포트
    grouped_articles: dict
    report: str

    # Config
    days: int
    min_score: int
    top_n: int
    filter_limit: int

    # DB session
    db: Any
