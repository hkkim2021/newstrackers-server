import json
import logging
from PyPDF2 import PdfReader
from io import BytesIO
from google import genai

from app.core.config import settings
from app.schemas.resume import UserProfile

logger = logging.getLogger(__name__)

PROFILE_EXTRACTION_PROMPT = """\
당신은 취업 준비생의 자기소개서를 분석하는 전문가입니다.
자기소개서를 읽고 다음 정보를 JSON으로 추출해주세요:

1. keywords: 자소서에서 핵심 역량/기술/관심사 키워드를 최대한 많이 추출 (예: ["백엔드", "프론트엔드", "Spring", "React"])
2. fields: 관련 분야 (예: ["웹 개발", "클라우드"])
3. target_position: 희망 직무 (예: "풀스택 개발자")
4. tech_stack: 구체적인 기술 스택을 카테고리별로 분류 (예: {{"backend": ["Spring Boot", "Java"], "frontend": ["React", "TypeScript"], "infra": ["AWS", "Docker"]}})
5. interested_companies: 관심 회사 (언급된 경우) (예: ["네이버", "카카오"])
6. target_industry: 목표 산업 (예: "IT/소프트웨어")
7. skills: 보유 역량 (예: ["문제해결력", "커뮤니케이션"])
8. experiences: 주요 경험 (예: ["웹 서비스 개발 프로젝트", "인턴십"])
9. interests: 관심 분야 (예: ["AI/ML", "클라우드"])

반드시 유효한 JSON만 출력하세요.

자기소개서:
{text}
"""


def extract_profile(text: str) -> UserProfile:
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    prompt = PROFILE_EXTRACTION_PROMPT.format(text=text)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    raw = response.text.strip()
    # Remove markdown code block if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"Gemini 응답 파싱 실패: {raw[:200]}")
        data = {}

    return UserProfile(**data)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)
