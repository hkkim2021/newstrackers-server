import json
import logging
from collections import defaultdict

from google import genai

from app.core.config import settings
from app.schemas.resume import UserProfile

logger = logging.getLogger(__name__)

REPORT_PROMPT = """\
당신은 취업 준비생을 위한 면접 준비 리포트를 작성하는 전문 컨설턴트입니다.

## 지원자 프로필
- 희망 직무: {target_position}
- 분야: {fields}
- 기술 스택: {tech_stack_flat}
- 관심사: {interests}
- 관심 회사: {interested_companies}

## 직무별 그룹핑된 뉴스 데이터
{grouped_data}

위 데이터를 기반으로 아래 형식의 면접 준비 리포트를 마크다운으로 작성해주세요.
반드시 아래 구조를 따르고, 실제 뉴스 데이터를 근거로 작성하세요.

---

# 면접 준비 리포트 - {{직무명}}

## 요약
- 분석 기간: 최근 1개월
- 총 분석 뉴스: {{N}}개
- 주요 관심 기업: {{기업명(뉴스수)}} 나열
- 핵심 키워드: {{키워드}} 나열

## 1. 직무별 산업 동향

(각 카테고리별로)
### 1-N. {{카테고리명}} ({{뉴스수}}개 뉴스)

**주요 트렌드:**
- 트렌드 요약 (뉴스 근거)

**회사별 동향:**
- **{{회사명}}**: 동향 요약
  - 예상 질문: "관련 면접 질문"

## 2. SWOT 분석

### Strengths (강점)
- 지원자 프로필 기반 강점

### Weaknesses (약점)
- 보완이 필요한 부분
- **보완 방법:** 구체적 제안

### Opportunities (기회)
- 시장/채용 트렌드 기반 기회

### Threats (위협)
- 리스크 요인

## 3. 예상 면접 질문 (우선순위별)

### High Priority (거의 확실히 나올 질문)

#### 기술 경험
1. **"질문"**
   - 근거: 관련 뉴스
   - 답변 팁: 구체적 조언

#### 성능/트렌드
(추가 질문들)

### Company-Specific Questions

#### {{회사명}} 지원 시
- "회사 특화 질문"

---
"""


def _flatten_tech_stack(tech_stack: dict[str, list[str]]) -> str:
    techs = []
    for category, items in tech_stack.items():
        if items:
            techs.append(f"{category}: {', '.join(items)}")
    return " | ".join(techs) if techs else "없음"


def _group_articles(scored_articles: list[dict]) -> dict:
    """scored articles를 카테고리별 → 회사별로 그룹핑한다."""
    by_category = defaultdict(list)

    for a in scored_articles:
        categories = a.get("categories", ["기타"])
        for cat in categories:
            by_category[cat].append(a)

    grouped = {}
    for cat, articles in by_category.items():
        # 회사별 서브그룹
        by_company = defaultdict(list)
        for a in articles:
            companies = a.get("companies", ["기타"])
            for comp in companies:
                by_company[comp].append({
                    "title": a.get("title", ""),
                    "score": a.get("relevance_score", 0),
                    "reason": a.get("reason", ""),
                    "interview_topics": a.get("interview_topics", []),
                })

        grouped[cat] = {
            "count": len(articles),
            "companies": dict(by_company),
        }

    return grouped


def generate_report(
    profile: UserProfile,
    scored_articles: list[dict],
) -> str:
    """Gemini로 면접 준비 리포트를 생성한다."""
    grouped = _group_articles(scored_articles)

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    prompt = REPORT_PROMPT.format(
        target_position=profile.target_position or "미정",
        fields=", ".join(profile.fields) if profile.fields else "미정",
        tech_stack_flat=_flatten_tech_stack(profile.tech_stack),
        interests=", ".join(profile.interests) if profile.interests else "없음",
        interested_companies=", ".join(profile.interested_companies) if profile.interested_companies else "없음",
        grouped_data=json.dumps(grouped, ensure_ascii=False, indent=2),
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    return response.text.strip()


