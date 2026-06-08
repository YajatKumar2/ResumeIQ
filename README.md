# ResumeIQ

ResumeIQ is a web-based AI resume analysis platform that compares a resume against a target job description and gives a structured, practical fit analysis.

The first version focuses on the core intelligence layer:

- Extract resume text from PDF, DOCX, or TXT files.
- Accept resume uploads up to 5 MB.
- Parse resume sections such as summary, skills, education, experience, and projects.
- Extract role-specific skills and keywords from a job description.
- Separate likely required skills from preferred/nice-to-have skills.
- Score resume-to-job alignment using local NLP-style methods.
- Generate targeted suggestions without paid APIs.
- Provide ATS-readiness checks for machine readability and recruiter clarity.

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
    main.py            # FastAPI app
  tests/
    test_analyzer.py
frontend/
  src/
    App.tsx          # Upload flow and analysis dashboard
    api.ts           # Backend API client
samples/
  sample_resume.txt
  sample_job_description.txt
requirements.txt
```

## Quick Start

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest
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

Run the calibration examples:

```bash
python backend/scripts/evaluate_samples.py
```

Start the backend:

```bash
uvicorn backend.app.main:app --reload
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

Open the app at:

```text
http://127.0.0.1:5173
```
