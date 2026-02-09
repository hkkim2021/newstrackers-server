"""기존 기사 중 embedding이 NULL인 것을 배치로 임베딩 생성하는 스크립트.

사용법:
    uv run python -m scripts.backfill_embeddings
    uv run python -m scripts.backfill_embeddings --batch-size 50 --limit 1000
"""

import argparse
import logging
import time

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.embedding_service import (
    _build_embedding_text,
    generate_embeddings_batch,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def backfill(batch_size: int = 50, limit: int | None = None):
    db = SessionLocal()
    total_updated = 0

    try:
        # 총 대상 수 확인
        count_result = db.execute(
            text("SELECT COUNT(*) FROM news_articles WHERE embedding IS NULL")
        )
        total_null = count_result.scalar()
        target = min(total_null, limit) if limit else total_null
        logger.info(f"임베딩 없는 기사: {total_null}건, 처리 대상: {target}건")

        while True:
            if limit and total_updated >= limit:
                break

            current_limit = min(batch_size, (limit - total_updated) if limit else batch_size)

            rows = db.execute(
                text("""
                    SELECT id, title, description
                    FROM news_articles
                    WHERE embedding IS NULL
                    ORDER BY id
                    LIMIT :limit
                """),
                {"limit": current_limit},
            ).mappings().all()

            if not rows:
                break

            texts = [
                _build_embedding_text(row["title"], row["description"])
                for row in rows
            ]

            embeddings = generate_embeddings_batch(texts, batch_size=current_limit)

            updated_in_batch = 0
            for row, embedding in zip(rows, embeddings):
                if embedding is not None:
                    db.execute(
                        text("""
                            UPDATE news_articles
                            SET embedding = CAST(:embedding AS vector)
                            WHERE id = :id
                        """),
                        {"embedding": str(embedding), "id": row["id"]},
                    )
                    updated_in_batch += 1

            db.commit()
            total_updated += updated_in_batch
            logger.info(
                f"배치 완료: {updated_in_batch}건 업데이트 "
                f"(누적 {total_updated}/{target})"
            )

            # API rate limit 배려
            time.sleep(1)

    except Exception as e:
        logger.error(f"백필 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    logger.info(f"백필 완료: 총 {total_updated}건 임베딩 생성")
    return total_updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="기존 기사 임베딩 백필")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    backfill(batch_size=args.batch_size, limit=args.limit)
