import json
from pathlib import Path

from backend.app.core.analyzer import analyze_resume


ROOT = Path(__file__).resolve().parents[2]
SCORE_BANDS = {
    "developing": range(0, 60),
    "moderate": range(50, 80),
    "strong": range(75, 101),
}


def test_sample_evaluation_cases_land_in_expected_bands():
    cases = json.loads((ROOT / "samples" / "evaluation_cases.json").read_text(encoding="utf-8"))

    for case in cases:
        result = analyze_resume(case["resume_text"], case["job_description"])

        assert result.scores.overall in SCORE_BANDS[case["expected_band"]], case["name"]
        assert result.job_profile.required_skills, case["name"]
        assert result.recommendations, case["name"]
