from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_llm_status_does_not_expose_api_key(monkeypatch):
    monkeypatch.setenv("USE_LLM", "true")
    monkeypatch.setenv("NVIDIA_API_KEY", "secret-key")
    monkeypatch.setenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-nano-8b-v1")

    response = client.get("/llm-status")
    body = response.json()

    assert response.status_code == 200
    assert body["enabled"] is True
    assert body["status"] == "llm_configured"
    assert body["has_api_key"] is True
    assert "secret-key" not in str(body)


def test_analyze_text_endpoint_returns_structured_result():
    response = client.post(
        "/analyze-text",
        json={
            "resume_text": """
            Priya Sharma
            priya@example.com
            Bengaluru, India
            https://github.com/priyasharma

            Summary
            Frontend developer with React and JavaScript project experience.

            Skills
            React, JavaScript, HTML, CSS, Git

            Projects
            Built a responsive dashboard using React for 500 users.

            Education
            B.Tech Computer Science
            """,
            "job_description": """
            We need a frontend developer with React, JavaScript, HTML, CSS, and Git.
            Preferred skills include TypeScript and REST API integration.
            Responsibilities include building responsive user interfaces.
            """,
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["scores"]["overall"] > 50
    assert body["contact_info"]["email"] == "priya@example.com"
    assert body["contact_info"]["github"] == "https://github.com/priyasharma"
    assert "react" in body["matched_skills"]
    assert "typescript" in body["missing_skills"]
    assert "typescript" not in body["priority_missing_skills"]
    assert body["job_profile"]["required_skills"]
    assert body["job_profile"]["preferred_skills"]
    assert body["evidence"]["score_factors"]
    assert body["rewrite_suggestions"]["tailored_summary"]


def test_analyze_text_endpoint_rejects_empty_input():
    response = client.post(
        "/analyze-text",
        json={"resume_text": "", "job_description": "Python developer role."},
    )

    assert response.status_code == 400


def test_analyze_upload_accepts_txt_resume():
    response = client.post(
        "/analyze-upload",
        data={
            "job_description": "Python developer role requiring Python, SQL, Git, and REST API skills."
        },
        files={
            "resume": (
                "resume.txt",
                b"Alex\nalex@example.com\nSkills\nPython, SQL, Git\nProjects\nBuilt a REST API.",
                "text/plain",
            )
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert "python" in body["matched_skills"]


def test_analyze_upload_rejects_empty_job_description():
    response = client.post(
        "/analyze-upload",
        data={"job_description": ""},
        files={"resume": ("resume.txt", b"Python resume", "text/plain")},
    )

    assert response.status_code == 400


def test_analyze_upload_rejects_large_file():
    response = client.post(
        "/analyze-upload",
        data={"job_description": "Python developer role."},
        files={"resume": ("resume.txt", b"x" * (5 * 1024 * 1024 + 1), "text/plain")},
    )

    assert response.status_code == 413
