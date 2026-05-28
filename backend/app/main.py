from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.analyzer import analyze_resume
from backend.app.core.parser import MAX_UPLOAD_SIZE_BYTES, SUPPORTED_EXTENSIONS, extract_text_from_file
from backend.app.core.schemas import AnalysisResult, TextAnalysisRequest


app = FastAPI(
    title="ResumeIQ API",
    description="Local resume-to-job matching and ATS analysis API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze-text", response_model=AnalysisResult)
def analyze_text(payload: TextAnalysisRequest) -> AnalysisResult:
    if not payload.resume_text.strip() or not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Resume text and job description are required.")

    return analyze_resume(payload.resume_text, payload.job_description)


@app.post("/analyze-upload", response_model=AnalysisResult)
async def analyze_upload(
    resume: UploadFile = File(...),
    job_description: str = Form(""),
) -> AnalysisResult:
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    extension = Path(resume.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Use: {allowed}.")

    contents = await resume.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded resume file is empty.")
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Resume file is too large. Maximum size is 5 MB.")

    with NamedTemporaryFile(delete=True, suffix=extension) as temp_file:
        temp_file.write(contents)
        temp_file.flush()
        try:
            resume_text = extract_text_from_file(Path(temp_file.name))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from resume.")

    return analyze_resume(resume_text, job_description)
