from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_text_endpoint_returns_structured_result():
    response = client.post(
        "/analyze-text",
        json={
            "resume_text": """
            Priya Sharma
            priya@example.com

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
    assert "react" in body["matched_skills"]
    assert "typescript" in body["missing_skills"]
    assert "typescript" not in body["priority_missing_skills"]
    assert body["job_profile"]["required_skills"]
    assert body["job_profile"]["preferred_skills"]


def test_analyze_text_endpoint_rejects_empty_input():
    response = client.post(
        "/analyze-text",
        json={"resume_text": "", "job_description": "Python developer role."},
    )

    assert response.status_code == 400
