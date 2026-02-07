"""
수동으로 Naver API를 호출하여 초기 뉴스 데이터를 수집하는 스크립트.

사용법:
    cd newstrackers-server
    uv run python -m scripts.seed_news
"""

import sys
import os
import logging

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    from app.core.database import Base, engine, SessionLocal
    from app.services.naver_news_collector import collect_all_keywords

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    logger.info("DB 테이블 확인/생성 완료")

    # 뉴스 수집
    db = SessionLocal()
    try:
        total = collect_all_keywords(db)
        logger.info(f"초기 뉴스 수집 완료: 총 {total}건 처리")
    except Exception as e:
        logger.error(f"수집 실패: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
