# --- 기존 news_articles 테이블 모델 (주석 처리) ---
# from pgvector.sqlalchemy import Vector
# from sqlalchemy import Column, DateTime, Integer, String, Text, func
# from sqlalchemy.dialects.postgresql import ARRAY
#
# from app.core.database import Base
#
#
# class NewsArticleModel(Base):
#     __tablename__ = "news_articles"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     title = Column(String, nullable=False)
#     description = Column(Text)
#     link = Column(String, unique=True, nullable=False)
#     pub_date = Column(DateTime(timezone=True))
#     category = Column(String)
#     keywords = Column(ARRAY(String))
#     collected_at = Column(DateTime(timezone=True), server_default=func.now())
#     embedding = Column(Vector(768), nullable=True)

# --- news_article_embeddings 테이블 모델 (AWS RDS 기존 데이터) ---
from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class NewsArticleModel(Base):
    __tablename__ = "news_article_embeddings"

    id = Column(BigInteger, primary_key=True)
    content_hash = Column(Text)
    content = Column(Text)
    embedding = Column(Vector(1536), nullable=True)
    doc_id = Column(Text)
    context_id = Column(Text)
    doc_title = Column(String)
    doc_source = Column(String)
    doc_published = Column(Integer)   # YYYYMMDD 정수형
    doc_class_code = Column(String)
    dataset_identifier = Column(Text)
    data_split = Column(Text)
    source_file = Column(Text)
    raw_meta = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
