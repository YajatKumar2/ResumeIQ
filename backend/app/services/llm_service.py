from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend.app.core.schemas import JobProfile, RewriteSuggestions


DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def is_llm_enabled() -> bool:
    return os.getenv("USE_LLM", "false").lower() == "true"


def get_llm_provider_status() -> str:
    if not is_llm_enabled():
        return "local_rules"
    if not os.getenv("NVIDIA_API_KEY"):
        return "local_fallback_missing_key"
    if not os.getenv("NVIDIA_MODEL"):
        return "local_fallback_missing_model"
    return "llm_configured"


def enhance_rewrite_suggestions(
    local_suggestions: RewriteSuggestions,
    job_profile: JobProfile,
    matched_skills: list[str],
    priority_missing_skills: list[str],
) -> RewriteSuggestions:
    status = get_llm_provider_status()
    if status != "llm_configured":
        return local_suggestions.model_copy(update={"source": status})

    try:
        enhanced = request_rewrite_enhancement(
            job_profile=job_profile,
            matched_skills=matched_skills,
            priority_missing_skills=priority_missing_skills,
            local_suggestions=local_suggestions,
        )
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return local_suggestions.model_copy(update={"source": "local_fallback_api_error"})

    return enhanced


def request_rewrite_enhancement(
    job_profile: JobProfile,
    matched_skills: list[str],
    priority_missing_skills: list[str],
    local_suggestions: RewriteSuggestions,
) -> RewriteSuggestions:
    api_key = os.environ["NVIDIA_API_KEY"]
    model = os.environ["NVIDIA_MODEL"]
    base_url = os.getenv("NVIDIA_BASE_URL", DEFAULT_NVIDIA_BASE_URL).rstrip("/")
    timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))

    payload = {
        "model": model,
        "messages": build_rewrite_prompt(
            job_profile=job_profile,
            matched_skills=matched_skills,
            priority_missing_skills=priority_missing_skills,
            local_suggestions=local_suggestions,
        ),
        "temperature": 0.2,
        "max_tokens": 500,
    }
    request = Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urlopen(request, timeout=timeout) as response:
        response_payload = json.loads(response.read().decode("utf-8"))

    content = response_payload["choices"][0]["message"]["content"]
    return parse_rewrite_response(content, local_suggestions)


def build_rewrite_prompt(
    job_profile: JobProfile,
    matched_skills: list[str],
    priority_missing_skills: list[str],
    local_suggestions: RewriteSuggestions,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You improve resume wording only. Do not invent experience, scores, "
                "certifications, employers, or skills. Keep suggestions concise and truthful."
            ),
        },
        {
            "role": "user",
            "content": (
                "Improve these local ResumeIQ rewrite suggestions for the target job.\n\n"
                "Return only valid JSON with keys: tailored_summary, bullet_examples.\n"
                "bullet_examples must be an array of 2-4 strings.\n"
                "Do not include markdown fences or extra commentary.\n\n"
                f"Required skills: {', '.join(job_profile.required_skills) or 'none'}\n"
                f"Preferred skills: {', '.join(job_profile.preferred_skills) or 'none'}\n"
                f"Matched skills: {', '.join(matched_skills) or 'none'}\n"
                f"Priority gaps: {', '.join(priority_missing_skills) or 'none'}\n"
                f"Local summary: {local_suggestions.tailored_summary}\n"
                f"Local bullets: {' | '.join(local_suggestions.bullet_examples)}"
            ),
        },
    ]


def parse_rewrite_response(content: str, local_suggestions: RewriteSuggestions) -> RewriteSuggestions:
    data = json.loads(strip_json_fence(content))
    tailored_summary = data.get("tailored_summary")
    bullet_examples = data.get("bullet_examples")

    if not isinstance(tailored_summary, str) or not tailored_summary.strip():
        raise ValueError("LLM response did not include a valid tailored_summary.")
    if not isinstance(bullet_examples, list) or not all(
        isinstance(item, str) and item.strip() for item in bullet_examples
    ):
        raise ValueError("LLM response did not include valid bullet_examples.")

    return local_suggestions.model_copy(
        update={
            "source": "nvidia_llm",
            "tailored_summary": tailored_summary.strip(),
            "bullet_examples": [item.strip() for item in bullet_examples[:4]],
        }
    )


def strip_json_fence(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
