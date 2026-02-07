import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import ResumeModel
from app.schemas.resume import ResumeAnalysisResponse, ResumeUploadResponse
from app.services.profile_extractor import extract_profile, extract_text_from_pdf
from app.services.report_generator import generate_report_by_resume_id

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출할 수 없습니다.")

    resume_id = str(uuid.uuid4())
    resume = ResumeModel(
        resume_id=resume_id,
        file_name=file.filename,
        raw_text=raw_text,
    )
    db.add(resume)
    db.commit()

    return ResumeUploadResponse(
        resume_id=resume_id,
        file_name=file.filename,
        message="자소서 업로드 완료",
    )


@router.post("/analyze/{resume_id}", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str,
    db: Session = Depends(get_db),
):
    resume = db.query(ResumeModel).filter_by(resume_id=resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="자소서를 찾을 수 없습니다.")

    if not resume.raw_text:
        raise HTTPException(status_code=400, detail="자소서 텍스트가 비어있습니다.")

    profile = extract_profile(resume.raw_text)
    resume.profile = profile.model_dump()
    db.commit()

    return ResumeAnalysisResponse(
        resume_id=resume_id,
        profile=profile,
    )


@router.post("/full-analysis")
async def full_analysis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Node1→2→3→4 전체 파이프라인: PDF 업로드 → 프로필 추출 → 뉴스 필터링 → 리포트 생성"""
    # Node1-1: PDF 텍스트 추출
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출할 수 없습니다.")

    # Node1-2: DB 저장 + Gemini 프로필 분석
    resume_id = str(uuid.uuid4())
    profile = extract_profile(raw_text)

    resume = ResumeModel(
        resume_id=resume_id,
        file_name=file.filename,
        raw_text=raw_text,
        profile=profile.model_dump(),
    )
    db.add(resume)
    db.commit()

    # Node2→3→4: 뉴스 필터링 → 점수 → 리포트
    result = generate_report_by_resume_id(resume_id, db)

    return {
        "resume_id": resume_id,
        "file_name": file.filename,
        "profile": profile.model_dump(),
        **result,
    }
