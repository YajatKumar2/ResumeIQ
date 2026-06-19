# ResumeIQ Logic Notes

ResumeIQ works as a local, explainable resume-to-job matching system. The goal is not just to parse a resume, but to compare it against one target job description and return practical guidance.

## Input Flow

The user can either upload a resume file or paste resume text directly. Uploaded files can be PDF, DOCX, or TXT. The backend extracts text from the file, then sends the resume text and job description into the same analysis pipeline.

## Resume Understanding

The analyzer cleans the resume text, tokenizes it, and tries to split it into sections such as summary, skills, education, experience, projects, and certifications. It also extracts contact signals like email, phone, LinkedIn, GitHub, and location.

## Job Description Understanding

The job description is cleaned and scanned for skills, responsibilities, and important keywords. The system separates likely required skills from preferred skills using words such as required, must, need, preferred, bonus, and nice to have.

## Matching Logic

ResumeIQ uses a local skill taxonomy with aliases. For example, PostgreSQL can count toward SQL, and React.js can count toward React. It compares detected resume skills against detected job skills to produce matched skills, missing skills, and priority missing skills.

## Scoring Logic

The overall score combines five parts:

- Skills score: how many required/preferred job skills are found in the resume.
- Keyword score: overlap between meaningful resume terms and job-description terms.
- Similarity score: local cosine similarity over cleaned resume and job text.
- Experience score: checks projects/experience for job keyword overlap, action verbs, and measurable impact.
- ATS score: checks section headers, visible skills, email presence, resume length, and formatting risk.

## Suggestions

Recommendations are rule-based and explainable. If required skills are missing, ResumeIQ highlights them as priority gaps. If matched skills exist, it suggests moving them closer to the top. If bullets lack numbers, it suggests adding measurable impact. If ATS warnings exist, they are included as improvement advice.

## Evidence Layer

The system returns score reasoning, resume evidence snippets, job-description evidence snippets, and recommendation sources. This makes the output easier to trust because the user can see why the analysis was generated.

## Rewrite Suggestions

ResumeIQ generates a tailored summary, example bullet rewrites, skills to highlight, and learning focus items using local rules. These are not produced by a paid API; they are based on detected role focus, matched skills, missing required skills, and job responsibilities.

## Where A Free API Could Improve It

A free LLM/API could be added later as an optional enhancement. The local engine should still remain the core. A model could improve summary rewrites, bullet rewrites, tone, grammar, and job-specific phrasing. The safest design is to send the local analysis result to the model, not raw files alone, so the model improves wording while ResumeIQ keeps control of scoring and evidence.

## Optional LLM Boundary

The project now has an optional LLM service boundary. By default, `USE_LLM=false`, so rewrite suggestions come from local rules. If an API is added later, it should only enhance rewrite wording and should not control scoring, ATS checks, matched skills, missing skills, or evidence.

NVIDIA documents hosted NIM endpoints for prototyping and lists LLM chat-completion APIs in its API documentation: https://docs.api.nvidia.com/. ResumeIQ keeps this integration optional through `.env` settings so the app remains usable without an API key.

When enabled, the service calls an OpenAI-compatible `/chat/completions` endpoint and asks for strict JSON containing only an improved summary and bullet examples. If the key, model, network, or response format fails, ResumeIQ falls back to local rewrite suggestions.
