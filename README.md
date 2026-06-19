# ResumeIQ

ResumeIQ is a web-based AI resume analysis platform that compares a resume against a target job description and gives a structured, practical fit analysis.

It is built as a local-first, explainable portfolio MVP: the core scoring and analysis work without paid APIs, while optional NVIDIA/OpenAI-compatible rewrite enhancement can improve wording when configured.

## Features

- Extract resume text from PDF, DOCX, or TXT files.
- Analyze either uploaded resumes or directly pasted resume text.
- Accept resume uploads up to 5 MB.
- Parse resume sections such as summary, skills, education, experience, and projects.
- Extract role-specific skills and keywords from a job description.
- Separate likely required skills from preferred/nice-to-have skills.
- Score resume-to-job alignment using local NLP-style methods.
- Generate targeted suggestions without paid APIs.
- Optionally enhance rewrite suggestions with an NVIDIA/OpenAI-compatible API.
- Provide ATS-readiness checks for machine readability and recruiter clarity.
- Extract contact signals such as email, phone, LinkedIn, GitHub, and location.
- Export a Markdown analysis report.

## Tech Stack

- Backend: FastAPI, Python
- Frontend: React, Vite, TypeScript
- Parsing: pypdf, python-docx
- Analysis: local keyword extraction, skill taxonomy, cosine similarity, rule-based ATS checks
- Optional enhancement: NVIDIA/OpenAI-compatible chat-completions endpoint

## Project Structure

```text
backend/
  app/
    core/
      analyzer.py      # Local resume/job matching engine
      parser.py        # PDF, DOCX, and TXT text extraction
      schemas.py       # Shared data models
    data/
      skills.py        # Skill taxonomy and aliases
    services/
      llm_service.py   # Optional rewrite enhancement boundary
    main.py            # FastAPI app
  tests/
    test_analyzer.py
docs/
  resumeiq_logic.md
  privacy_and_limits.md
  api_enhancement.md
frontend/
  src/
    App.tsx          # Upload flow and analysis dashboard
    api.ts           # Backend API client
samples/
  sample_resume.txt
  sample_job_description.txt
requirements.txt
```

## How It Works

ResumeIQ extracts resume text, splits it into sections, extracts contact details and skills, then compares the resume against the target job description. The job description is parsed for likely required skills, preferred skills, responsibilities, and keywords.

The final score combines skills, keywords, local similarity, experience/project alignment, and ATS-readiness checks. Recommendations are generated from explainable local rules. Optional API enhancement only improves rewrite wording; it does not control scoring or evidence.

## Quick Start

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create optional local environment settings when needed:

```bash
cp .env.example .env
```

By default, `USE_LLM=false`, so ResumeIQ works fully without any API key.

Optional NVIDIA/OpenAI-compatible rewrite enhancement:

```bash
USE_LLM=true
NVIDIA_API_KEY=your_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/llama-3.1-nemotron-nano-8b-v1
LLM_TIMEOUT_SECONDS=20
```

Only rewrite suggestions are API-enhanced. Scoring, ATS checks, skill matching, and evidence remain local.

Check API configuration:

```bash
make llm-status
```

Or, after starting the backend:

```text
http://127.0.0.1:8000/llm-status
```

The API key is never returned by the status endpoint.

More details:

- [Logic notes](docs/resumeiq_logic.md)
- [API enhancement notes](docs/api_enhancement.md)
- [Privacy and limits](docs/privacy_and_limits.md)
- [Project status](docs/project_status.md)

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

You can also use the project shortcuts:

```bash
make setup
make test
make backend
make frontend
make llm-status
```

Run tests:

```bash
python -m pytest
```

Or:

```bash
make test
```

If `pytest` uses Anaconda instead of the project virtual environment, run:

```bash
conda deactivate
source .venv/bin/activate
which python
python -m pytest
```

`which python` should point to:

```text
/Users/yajatchowdary/Documents/ResumeIQ/.venv/bin/python
```

Run a sample analysis:

```bash
python backend/scripts/analyze_sample.py
```

Or:

```bash
make sample
```

Run the calibration examples:

```bash
python backend/scripts/evaluate_samples.py
```

Or:

```bash
make calibrate
```

Start the backend:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Or:

```bash
make backend
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Or:

```bash
make frontend
```

Run the full local verification:

```bash
make verify
```

Open the app at:

```text
http://127.0.0.1:5173
```
