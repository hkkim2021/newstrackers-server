import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.resume import UserProfile
from app.services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)


def build_search_keywords(profile: UserProfile) -> list[str]:
    """프로필에서 검색용 키워드를 모두 수집한다."""
    keywords = set()

    # keywords
    keywords.update(profile.keywords)

    # tech_stack (nested dict → flatten)
    for techs in profile.tech_stack.values():
        keywords.update(techs)

    # fields, interests, interested_companies
    keywords.update(profile.fields)
    keywords.update(profile.interests)
    keywords.update(profile.interested_companies)

    # target_position (단일 문자열)
    if profile.target_position:
        keywords.add(profile.target_position)

    # 빈 문자열 제거
    keywords.discard("")

    return list(keywords)


def _build_profile_query_text(profile: UserProfile) -> str:
    """프로필 정보를 자연어 쿼리 텍스트로 변환한다."""
    parts = []

    if profile.target_position:
        parts.append(profile.target_position)

    if profile.target_industry:
        parts.append(profile.target_industry)

    if profile.fields:
        parts.append(" ".join(profile.fields))

    if profile.interests:
        parts.append(" ".join(profile.interests))

    if profile.keywords:
        parts.append(" ".join(profile.keywords))

    for techs in profile.tech_stack.values():
        parts.append(" ".join(techs))

    if profile.interested_companies:
        parts.append(" ".join(profile.interested_companies))

    return " ".join(parts).strip()


def _keyword_search(
    db: Session,
    search_keywords: list[str],
    since: datetime,
    limit: int,
) -> list[dict]:
    """기존 Array Overlap 키워드 검색."""
    result = db.execute(
        text("""
            SELECT id, title, description, link, pub_date, category, keywords, collected_at
            FROM news_articles
            WHERE keywords && CAST(:keywords AS varchar[])
              AND pub_date >= :since
            ORDER BY pub_date DESC
            LIMIT :limit
        """),
        {
            "keywords": search_keywords,
            "since": since,
            "limit": limit,
        },
    )

    articles = []
    for row in result.mappings():
        articles.append(_row_to_dict(row))
    return articles


def _vector_search(
    db: Session,
    query_embedding: list[float],
    since: datetime,
    limit: int,
) -> list[dict]:
    """pgvector cosine similarity 검색."""
    result = db.execute(
        text("""
            SELECT id, title, description, link, pub_date, category, keywords, collected_at,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM news_articles
            WHERE embedding IS NOT NULL
              AND pub_date >= :since
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """),
        {
            "embedding": str(query_embedding),
            "since": since,
            "limit": limit,
        },
    )

    articles = []
    for row in result.mappings():
        article = _row_to_dict(row)
        article["similarity"] = float(row["similarity"])
        articles.append(article)
    return articles


def _row_to_dict(row) -> dict:
    """DB row를 dict로 변환한다."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "link": row["link"],
        "pub_date": row["pub_date"].isoformat() if row["pub_date"] else None,
        "category": row["category"],
        "keywords": row["keywords"],
        "collected_at": row["collected_at"].isoformat() if row["collected_at"] else None,
    }


def _reciprocal_rank_fusion(
    keyword_results: list[dict],
    vector_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """RRF 알고리즘으로 두 검색 결과를 병합한다."""
    scores: dict[int, float] = {}
    article_map: dict[int, dict] = {}

    # 키워드 검색 결과 순위 점수
    for rank, article in enumerate(keyword_results):
        aid = article["id"]
        scores[aid] = scores.get(aid, 0) + 1.0 / (k + rank + 1)
        article_map[aid] = article

    # 벡터 검색 결과 순위 점수
    for rank, article in enumerate(vector_results):
        aid = article["id"]
        scores[aid] = scores.get(aid, 0) + 1.0 / (k + rank + 1)
        if aid not in article_map:
            article_map[aid] = article

    # RRF 점수 내림차순 정렬
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    merged = []
    for aid in sorted_ids:
        article = article_map[aid]
        article["rrf_score"] = scores[aid]
        merged.append(article)

    return merged


def filter_news_by_profile(
    profile: UserProfile,
    db: Session,
    days: int = 30,
    limit: int = 300,
) -> list[dict]:
    """프로필 기반 하이브리드 검색: 키워드 + 벡터 + RRF 병합."""
    search_keywords = build_search_keywords(profile)

    if not search_keywords:
        logger.warning("검색 키워드가 없습니다.")
        return []

    logger.info(f"검색 키워드 {len(search_keywords)}개: {search_keywords[:10]}...")

    since = datetime.now(timezone.utc) - timedelta(days=days)

    # 1) 키워드 검색
    keyword_results = _keyword_search(db, search_keywords, since, limit)
    logger.info(f"키워드 검색 결과: {len(keyword_results)}건")

    # 2) 벡터 검색
    vector_results = []
    try:
        query_text = _build_profile_query_text(profile)
        if query_text:
            query_embedding = generate_embedding(query_text)
            if query_embedding:
                vector_results = _vector_search(db, query_embedding, since, limit)
                logger.info(f"벡터 검색 결과: {len(vector_results)}건")
            else:
                logger.warning("프로필 임베딩 생성 실패, 키워드 결과만 사용")
        else:
            logger.warning("프로필 쿼리 텍스트가 비어있음, 키워드 결과만 사용")
    except Exception as e:
        logger.error(f"벡터 검색 실패, 키워드 결과만 사용: {e}")

    # 3) RRF 병합 또는 키워드 결과만 반환
    if vector_results:
        merged = _reciprocal_rank_fusion(keyword_results, vector_results)
        articles = merged[:limit]
        logger.info(
            f"Hybrid RRF merge: 키워드 {len(keyword_results)}건 + "
            f"벡터 {len(vector_results)}건 → 병합 {len(articles)}건"
        )
    else:
        articles = keyword_results
        logger.info(f"1차 필터링 결과 (키워드만): {len(articles)}건")

    return articles
