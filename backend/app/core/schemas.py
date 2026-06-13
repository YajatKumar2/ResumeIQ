from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    overall: int = Field(ge=0, le=100)
    skills: int = Field(ge=0, le=100)
    keywords: int = Field(ge=0, le=100)
    semantic_similarity: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    ats: int = Field(ge=0, le=100)


class AtsCheck(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: list[str]
    warnings: list[str]


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    location: str | None = None


class JobProfile(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]


class AnalysisEvidence(BaseModel):
    score_factors: list[str]
    resume_evidence: list[str]
    job_evidence: list[str]
    recommendation_sources: list[str]


class RewriteSuggestions(BaseModel):
    tailored_summary: str
    bullet_examples: list[str]
    skills_to_highlight: list[str]
    learning_focus: list[str]


class AnalysisResult(BaseModel):
    summary: str
    scores: ScoreBreakdown
    contact_info: ContactInfo
    job_profile: JobProfile
    evidence: AnalysisEvidence
    rewrite_suggestions: RewriteSuggestions
    matched_skills: list[str]
    missing_skills: list[str]
    priority_missing_skills: list[str]
    resume_keywords: list[str]
    job_keywords: list[str]
    section_analysis: dict[str, str]
    ats: AtsCheck
    recommendations: list[str]


class TextAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
