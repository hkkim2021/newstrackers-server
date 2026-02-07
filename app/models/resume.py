from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, func

from app.core.database import Base


class ResumeModel(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, unique=True, nullable=False)
    file_name = Column(String)
    raw_text = Column(Text)
    profile = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
