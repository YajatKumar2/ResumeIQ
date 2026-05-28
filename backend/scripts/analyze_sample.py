from pathlib import Path
import sys



ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.core.analyzer import analyze_resume  # noqa: E402


def main() -> None:
    resume_text = (ROOT / "samples" / "sample_resume.txt").read_text(encoding="utf-8")
    job_description = (ROOT / "samples" / "sample_job_description.txt").read_text(encoding="utf-8")
    analysis = analyze_resume(resume_text, job_description)
    print(analysis.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
