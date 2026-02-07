from pydantic import BaseModel


class UserProfile(BaseModel):
    target_position: str = ""
    target_industry: str = ""
    keywords: list[str] = []
    fields: list[str] = []
    tech_stack: list[str] = []
    interested_companies: list[str] = []
    skills: list[str] = []
    experiences: list[str] = []
    interests: list[str] = []


class ResumeUploadResponse(BaseModel):
    resume_id: str
    file_name: str
    message: str


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    profile: UserProfile
