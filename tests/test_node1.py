"""
Node 1 테스트: 뉴스 수집 + 자소서 분석

사용법:
    cd newstrackers-server
    uv run pytest tests/test_node1.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- Naver News Collector 테스트 ---


class TestNaverNewsCollector:
    def test_search_news_returns_items(self):
        """Naver News API 호출이 결과를 반환하는지 확인"""
        from app.services.naver_news_collector import search_news

        articles = search_news("AI", display=5)
        assert isinstance(articles, list)
        assert len(articles) > 0
        assert "title" in articles[0]
        assert "link" in articles[0]

    def test_clean_html(self):
        """HTML 태그 제거 확인"""
        from app.services.naver_news_collector import _clean_html

        result = _clean_html("<b>테스트</b> &amp; &quot;뉴스&quot;")
        assert result == '테스트 & "뉴스"'

    def test_parse_pub_date(self):
        """날짜 파싱 확인"""
        from app.services.naver_news_collector import _parse_pub_date

        result = _parse_pub_date("Mon, 01 Jan 2024 00:00:00 +0900")
        assert result is not None
        assert result.year == 2024

        result_none = _parse_pub_date("invalid date")
        assert result_none is None

    def test_save_and_dedup(self):
        """DB 저장 및 중복 키워드 병합 확인"""
        from app.core.database import Base, engine, SessionLocal
        from app.models.news import NewsArticleModel
        from app.services.naver_news_collector import save_to_db

        # 테스트용 테이블 생성
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

        try:
            # 테스트 데이터
            test_articles = [
                {
                    "title": "테스트 뉴스",
                    "description": "테스트 설명",
                    "originallink": "https://test.example.com/unique-test-article-12345",
                    "link": "https://test.example.com/unique-test-article-12345",
                    "pubDate": "Mon, 01 Jan 2024 00:00:00 +0900",
                }
            ]

            # 첫 번째 저장
            save_to_db(test_articles, "AI", "IT", db)
            article = db.query(NewsArticleModel).filter_by(
                link="https://test.example.com/unique-test-article-12345"
            ).first()
            assert article is not None
            assert "AI" in article.keywords

            # 동일 link로 다른 키워드 저장 → array_append 확인
            save_to_db(test_articles, "인공지능", "IT", db)
            db.refresh(article)
            assert "AI" in article.keywords
            assert "인공지능" in article.keywords

        finally:
            # 테스트 데이터 정리
            db.query(NewsArticleModel).filter_by(
                link="https://test.example.com/unique-test-article-12345"
            ).delete()
            db.commit()
            db.close()


# --- Profile Extractor 테스트 ---


class TestProfileExtractor:
    def test_extract_text_from_pdf(self):
        """PDF 텍스트 추출 함수 존재 확인"""
        from app.services.profile_extractor import extract_text_from_pdf

        assert callable(extract_text_from_pdf)

    def test_extract_profile(self):
        """Gemini를 사용한 프로필 추출 확인"""
        from app.services.profile_extractor import extract_profile
        from app.schemas.resume import UserProfile

        sample_text = """
        저는 컴퓨터공학을 전공하고 백엔드 개발자를 희망합니다.
        Spring Boot와 React를 활용한 웹 서비스 개발 프로젝트 경험이 있으며,
        AWS 클라우드 환경에서의 배포 경험도 있습니다.
        네이버와 카카오에서 인턴십을 수행하며 실무 역량을 키웠습니다.
        AI/ML 분야에도 관심이 있어 TensorFlow를 활용한 개인 프로젝트를 진행했습니다.
        """

        profile = extract_profile(sample_text)
        assert isinstance(profile, UserProfile)
        assert profile.target_position != ""
        assert len(profile.keywords) > 0
        assert len(profile.tech_stack) > 0

    def test_user_profile_schema(self):
        """UserProfile 스키마 새 필드 확인"""
        from app.schemas.resume import UserProfile

        profile = UserProfile(
            target_position="백엔드 개발자",
            target_industry="IT",
            keywords=["백엔드", "Spring"],
            fields=["웹 개발"],
            tech_stack=["Spring Boot", "React"],
            interested_companies=["네이버"],
            skills=["문제해결력"],
            experiences=["인턴십"],
            interests=["AI/ML"],
        )
        assert profile.target_position == "백엔드 개발자"
        assert "Spring Boot" in profile.tech_stack
        assert "네이버" in profile.interested_companies
        assert "웹 개발" in profile.fields


# --- DB 연동 테스트 ---


class TestDatabase:
    def test_db_connection(self):
        """DB 연결 확인"""
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            result = db.execute(
                __import__("sqlalchemy").text("SELECT 1")
            ).scalar()
            assert result == 1
        finally:
            db.close()

    def test_resume_model_crud(self):
        """Resume 모델 CRUD 확인"""
        from app.core.database import Base, engine, SessionLocal
        from app.models.resume import ResumeModel

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

        try:
            resume = ResumeModel(
                resume_id="test-uuid-12345",
                file_name="test.pdf",
                raw_text="테스트 자기소개서 내용",
            )
            db.add(resume)
            db.commit()

            fetched = db.query(ResumeModel).filter_by(resume_id="test-uuid-12345").first()
            assert fetched is not None
            assert fetched.file_name == "test.pdf"

        finally:
            db.query(ResumeModel).filter_by(resume_id="test-uuid-12345").delete()
            db.commit()
            db.close()
