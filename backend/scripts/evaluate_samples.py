import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.core.analyzer import analyze_resume  # noqa: E402


def main() -> None:
    cases = json.loads((ROOT / "samples" / "evaluation_cases.json").read_text(encoding="utf-8"))

    print("case,expected,overall,skills,keywords,experience,ats,priority_gaps")
    for case in cases:
        result = analyze_resume(case["resume_text"], case["job_description"])
        priority_gaps = "; ".join(result.priority_missing_skills) or "none"
        print(
            ",".join(
                [
                    case["name"],
                    case["expected_band"],
                    str(result.scores.overall),
                    str(result.scores.skills),
                    str(result.scores.keywords),
                    str(result.scores.experience),
                    str(result.scores.ats),
                    priority_gaps,
                ]
            )
        )


if __name__ == "__main__":
    main()
