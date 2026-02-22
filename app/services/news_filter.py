import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.resume import UserProfile
from app.services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)


def build_search_keywords(profile: UserProfile) -> list[str]:
    """프로필에서 검색용 키워드를 모두 수집한다."""
    keywords = set()

    keywords.update(profile.keywords)

    for techs in profile.tech_stack.values():
        keywords.update(techs)

    keywords.update(profile.fields)
    keywords.update(profile.interests)
    keywords.update(profile.interested_companies)

    if profile.target_position:
        keywords.add(profile.target_position)

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


# --- 키워드 검색 주석 처리 ---
# def _keyword_search(db, search_keywords, limit):
#     patterns = [f"%{kw}%" for kw in search_keywords if kw]
#     result = db.execute(
#         text("""
#             SELECT id, doc_title, content, doc_id, doc_published, doc_class_code, created_at
#             FROM news_article_embeddings
#             WHERE doc_title ILIKE ANY(CAST(:patterns AS text[]))
#                OR content  ILIKE ANY(CAST(:patterns AS text[]))
#             ORDER BY doc_published DESC
#             LIMIT :limit
#         """),
#         {"patterns": patterns, "limit": limit},
#     )
#     articles = []
#     for row in result.mappings():
#         articles.append(_row_to_dict(row))
#     return articles


def _vector_search(
    db: Session,
    query_embedding: list[float],
    limit: int,
) -> list[dict]:
    """pgvector cosine similarity 검색 (1536차원, OpenAI 임베딩)."""
    result = db.execute(
        text("""
            SELECT id, doc_title, content, doc_id, doc_published, doc_class_code, created_at,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM news_article_embeddings
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """),
        {"embedding": str(query_embedding), "limit": limit},
    )

    articles = []
    for row in result.mappings():
        article = _row_to_dict(row)
        article["similarity"] = float(row["similarity"])
        articles.append(article)
    return articles


def _row_to_dict(row) -> dict:
    """DB row를 pipeline 표준 dict로 변환한다."""
    doc_published = row["doc_published"]
    if doc_published:
        try:
            pub_date = datetime.strptime(str(doc_published), "%Y%m%d").isoformat()
        except ValueError:
            pub_date = None
    else:
        pub_date = None

    return {
        "id": row["id"],
        "title": row["doc_title"] or "",
        "description": (row["content"] or "")[:300],
        "link": row["doc_id"] or "",
        "pub_date": pub_date,
        "category": row["doc_class_code"],
        "keywords": [],   # 기존 테이블에 keywords 컬럼 없음
        "collected_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


# --- RRF 병합 주석 처리 ---
# def _reciprocal_rank_fusion(keyword_results, vector_results, k=60):
#     scores = {}
#     article_map = {}
#     for rank, article in enumerate(keyword_results):
#         aid = article["id"]
#         scores[aid] = scores.get(aid, 0) + 1.0 / (k + rank + 1)
#         article_map[aid] = article
#     for rank, article in enumerate(vector_results):
#         aid = article["id"]
#         scores[aid] = scores.get(aid, 0) + 1.0 / (k + rank + 1)
#         if aid not in article_map:
#             article_map[aid] = article
#     sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
#     merged = []
#     for aid in sorted_ids:
#         article = article_map[aid]
#         article["rrf_score"] = scores[aid]
#         merged.append(article)
#     return merged


def filter_news_by_profile(
    profile: UserProfile,
    db: Session,
    days: int = 30,
    limit: int = 300,
) -> list[dict]:
    """프로필 기반 벡터 검색만 사용 (날짜 필터 없음 — 기존 2021년 데이터)."""
    query_text = _build_profile_query_text(profile)

    if not query_text:
        logger.warning("프로필 쿼리 텍스트가 비어있습니다.")
        return []

    query_embedding = generate_embedding(query_text)
    if not query_embedding:
        logger.error("프로필 임베딩 생성 실패")
        return []

    articles = _vector_search(db, query_embedding, limit)
    logger.info(f"벡터 검색 결과: {len(articles)}건")

    return articles
