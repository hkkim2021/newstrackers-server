from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.database import Base


class NewsArticleModel(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    link = Column(String, unique=True, nullable=False)
    pub_date = Column(DateTime(timezone=True))
    category = Column(String)
    keywords = Column(ARRAY(String))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding = Column(Vector(768), nullable=True)
