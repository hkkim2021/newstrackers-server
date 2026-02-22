"""Node1→2→3→4 전체 파이프라인."""
import logging
import uuid

from sqlalchemy.orm import Session

from app.agents.nodes.profile_node import profile_node as run_profile_node
from app.agents.nodes.filter_node import filter_node as run_filter_node
from app.agents.nodes.scorer_node import scorer_node as run_scorer_node
from app.agents.nodes.report_node import report_node as run_report_node
from app.agents.state import PipelineState
from app.models.resume import ResumeModel
from app.services.profile_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)


def run_full_pipeline(
    file_bytes: bytes,
    file_name: str,
    db: Session,
    days: int = 30,
    filter_limit: int = 300,
    min_score: int = 70,
    top_n: int = 20,
) -> dict:
    """PDF 업로드 → Node1→2→3→4 전체 파이프라인 실행."""

    # PDF 텍스트 추출
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise ValueError("PDF에서 텍스트를 추출할 수 없습니다.")

    # 초기 상태
    state: PipelineState = {
        "raw_text": raw_text,
        "file_name": file_name,
        "db": db,
        "days": days,
        "filter_limit": filter_limit,
        "min_score": min_score,
        "top_n": top_n,
    }

    # Node1: 프로필 분석
    logger.info("Pipeline: Node1 시작")
    state.update(run_profile_node(state))

    # DB 저장 주석 처리
    resume_id = str(uuid.uuid4())
    # resume = ResumeModel(
    #     resume_id=resume_id,
    #     file_name=file_name,
    #     raw_text=raw_text,
    #     profile=state["profile"],
    # )
    # db.add(resume)
    # db.commit()
    state["resume_id"] = resume_id

    # Node2: 1차 필터링
    logger.info("Pipeline: Node2 시작")
    state.update(run_filter_node(state))

    # Node3: 관련성 점수
    logger.info("Pipeline: Node3 시작")
    state.update(run_scorer_node(state))

    # Node4: 리포트 생성
    logger.info("Pipeline: Node4 시작")
    state.update(run_report_node(state))

    logger.info("Pipeline: 완료")

    return {
        "resume_id": resume_id,
        "file_name": file_name,
        "profile": state["profile"],
        "target_position": state["profile"].get("target_position", ""),
        "pipeline_summary": {
            "node2_filtered": len(state.get("filtered_articles", [])),
            "node3_scored": len(state.get("scored_articles", [])),
            "min_score": min_score,
        },
        "grouped_articles": state.get("grouped_articles", {}),
        "report": state.get("report", ""),
    }


def run_pipeline_by_resume_id(
    resume_id: str,
    db: Session,
    days: int = 30,
    filter_limit: int = 300,
    min_score: int = 70,
    top_n: int = 20,
) -> dict:
    """기존 resume_id로 Node2→3→4 파이프라인 실행."""
    resume = db.query(ResumeModel).filter_by(resume_id=resume_id).first()
    if not resume:
        raise ValueError(f"자소서를 찾을 수 없습니다: {resume_id}")
    if not resume.profile:
        raise ValueError(f"프로필 분석이 필요합니다: {resume_id}")

    state: PipelineState = {
        "resume_id": resume_id,
        "profile": resume.profile,
        "db": db,
        "days": days,
        "filter_limit": filter_limit,
        "min_score": min_score,
        "top_n": top_n,
    }

    # Node2→3→4
    state.update(run_filter_node(state))
    state.update(run_scorer_node(state))
    state.update(run_report_node(state))

    return {
        "resume_id": resume_id,
        "target_position": state["profile"].get("target_position", ""),
        "pipeline_summary": {
            "node2_filtered": len(state.get("filtered_articles", [])),
            "node3_scored": len(state.get("scored_articles", [])),
            "min_score": min_score,
        },
        "grouped_articles": state.get("grouped_articles", {}),
        "report": state.get("report", ""),
    }
