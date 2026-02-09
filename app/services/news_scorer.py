import json
import logging

from google import genai

from app.core.config import settings
from app.schemas.resume import UserProfile

logger = logging.getLogger(__name__)

SCORING_PROMPT = """\
다음은 "{target_position}" 지원자의 프로필입니다:
- 직무: {target_position}
- 분야: {fields}
- 기술: {tech_stack_flat}
- 관심사: {interests}
- 관심 회사: {interested_companies}

아래 뉴스들이 이 지원자의 면접 준비에 얼마나 도움이 되는지 0-100점으로 점수를 매겨주세요.

{news_list}

각 뉴스에 대해 다음 형식의 JSON 배열로 응답하세요. 반드시 유효한 JSON만 출력하세요:
[
  {{
    "news_id": 뉴스번호,
    "relevance_score": 0-100 점수,
    "reason": "관련성 이유 (한국어, 1문장)",
    "categories": ["카테고리1", "카테고리2"],
    "companies": ["관련회사"],
    "interview_topics": ["예상 면접 주제1", "예상 면접 주제2"]
  }}
]
"""

BATCH_SIZE = 30


def _flatten_tech_stack(tech_stack: dict[str, list[str]]) -> str:
    techs = []
    for v in tech_stack.values():
        techs.extend(v)
    return ", ".join(techs) if techs else "없음"


def _build_news_list_text(articles: list[dict]) -> str:
    lines = []
    for a in articles:
        kw = ", ".join(a["keywords"] or [])
        lines.append(f'뉴스 {a["id"]}: "{a["title"]}" (키워드: {kw})')
    return "\n".join(lines)


def score_batch(profile: UserProfile, articles: list[dict]) -> list[dict]:
    """Gemini로 뉴스 배치에 관련성 점수를 매긴다."""
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    prompt = SCORING_PROMPT.format(
        target_position=profile.target_position or "미정",
        fields=", ".join(profile.fields) if profile.fields else "미정",
        tech_stack_flat=_flatten_tech_stack(profile.tech_stack),
        interests=", ".join(profile.interests) if profile.interests else "없음",
        interested_companies=", ".join(profile.interested_companies) if profile.interested_companies else "없음",
        news_list=_build_news_list_text(articles),
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)

    try:
        scored = json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"Gemini 점수 파싱 실패: {raw[:300]}")
        return []

    return scored


def score_news(
    profile: UserProfile,
    articles: list[dict],
    min_score: int = 70,
    top_n: int = 20,
) -> list[dict]:
    """Node2 결과를 배치로 Gemini에 보내고, 점수 기준으로 필터링한다."""
    all_scored = []

    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i : i + BATCH_SIZE]
        logger.info(f"배치 {i // BATCH_SIZE + 1}: {len(batch)}건 점수 매기는 중...")
        scored = score_batch(profile, batch)
        all_scored.extend(scored)

    # 원본 뉴스 정보와 병합
    article_map = {a["id"]: a for a in articles}
    results = []
    for s in all_scored:
        news_id = s.get("news_id")
        score = s.get("relevance_score", 0)
        if score >= min_score and news_id in article_map:
            original = article_map[news_id]
            results.append({
                **s,
                "title": original["title"],
                "link": original["link"],
                "pub_date": original["pub_date"],
                "original_keywords": original["keywords"],
            })

    # 점수 내림차순 정렬 → top_n개
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return results[:top_n]


