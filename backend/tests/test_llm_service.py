from backend.app.core.schemas import JobProfile, RewriteSuggestions
from backend.app.services.llm_service import (
    build_rewrite_prompt,
    enhance_rewrite_suggestions,
    get_llm_provider_status,
    parse_rewrite_response,
)


class FakeResponse:
    def __init__(self, payload: str):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload.encode("utf-8")


def test_llm_status_defaults_to_local_rules(monkeypatch):
    monkeypatch.delenv("USE_LLM", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)

    assert get_llm_provider_status() == "local_rules"


def test_llm_enabled_without_key_falls_back(monkeypatch):
    monkeypatch.setenv("USE_LLM", "true")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.setenv("NVIDIA_MODEL", "nvidia/example-model")

    local = RewriteSuggestions(
        tailored_summary="Local summary",
        bullet_examples=["Local bullet"],
        skills_to_highlight=["python"],
        learning_focus=["sql"],
    )

    enhanced = enhance_rewrite_suggestions(
        local_suggestions=local,
        job_profile=JobProfile(required_skills=["python"], preferred_skills=[], responsibilities=[]),
        matched_skills=["python"],
        priority_missing_skills=["sql"],
    )

    assert enhanced.source == "local_fallback_missing_key"
    assert enhanced.tailored_summary == "Local summary"


def test_rewrite_prompt_keeps_truthfulness_guardrails():
    local = RewriteSuggestions(
        tailored_summary="Local summary",
        bullet_examples=["Local bullet"],
        skills_to_highlight=["python"],
        learning_focus=[],
    )

    messages = build_rewrite_prompt(
        job_profile=JobProfile(
            required_skills=["python"],
            preferred_skills=["communication"],
            responsibilities=["Analyze reports"],
        ),
        matched_skills=["python"],
        priority_missing_skills=[],
        local_suggestions=local,
    )

    assert "Do not invent" in messages[0]["content"]
    assert "Return only valid JSON" in messages[1]["content"]
    assert "python" in messages[1]["content"]


def test_parse_rewrite_response_accepts_plain_json():
    local = RewriteSuggestions(
        tailored_summary="Local summary",
        bullet_examples=["Local bullet"],
        skills_to_highlight=["python"],
        learning_focus=[],
    )

    enhanced = parse_rewrite_response(
        '{"tailored_summary":"Better summary","bullet_examples":["Better bullet"]}',
        local,
    )

    assert enhanced.source == "nvidia_llm"
    assert enhanced.tailored_summary == "Better summary"
    assert enhanced.bullet_examples == ["Better bullet"]
    assert enhanced.skills_to_highlight == ["python"]


def test_parse_rewrite_response_accepts_fenced_json():
    local = RewriteSuggestions(
        tailored_summary="Local summary",
        bullet_examples=["Local bullet"],
        skills_to_highlight=[],
        learning_focus=[],
    )

    enhanced = parse_rewrite_response(
        '```json\n{"tailored_summary":"Better summary","bullet_examples":["Better bullet"]}\n```',
        local,
    )

    assert enhanced.source == "nvidia_llm"
    assert enhanced.tailored_summary == "Better summary"


def test_llm_configured_uses_mocked_api(monkeypatch):
    monkeypatch.setenv("USE_LLM", "true")
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    monkeypatch.setenv("NVIDIA_MODEL", "nvidia/test-model")

    response_payload = (
        '{"choices":[{"message":{"content":"'
        '{\\"tailored_summary\\":\\"API summary\\",'
        '\\"bullet_examples\\":[\\"API bullet\\"]}'
        '"}}]}'
    )

    def fake_urlopen(request, timeout):
        assert request.full_url.endswith("/chat/completions")
        assert timeout == 20
        return FakeResponse(response_payload)

    monkeypatch.setattr("backend.app.services.llm_service.urlopen", fake_urlopen)

    local = RewriteSuggestions(
        tailored_summary="Local summary",
        bullet_examples=["Local bullet"],
        skills_to_highlight=["python"],
        learning_focus=[],
    )

    enhanced = enhance_rewrite_suggestions(
        local_suggestions=local,
        job_profile=JobProfile(required_skills=["python"], preferred_skills=[], responsibilities=[]),
        matched_skills=["python"],
        priority_missing_skills=[],
    )

    assert enhanced.source == "nvidia_llm"
    assert enhanced.tailored_summary == "API summary"
    assert enhanced.bullet_examples == ["API bullet"]
