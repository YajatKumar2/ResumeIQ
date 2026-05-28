from __future__ import annotations

import math
import re
from collections import Counter

from backend.app.core.schemas import AnalysisResult, AtsCheck, JobProfile, ScoreBreakdown
from backend.app.data.skills import ACTION_VERBS, SECTION_HEADERS, SKILL_ALIASES, STOPWORDS


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]*")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
REQUIRED_MARKERS = {
    "required",
    "requirement",
    "requirements",
    "must",
    "need",
    "needs",
    "should have",
    "responsibilities include",
}
PREFERRED_MARKERS = {
    "preferred",
    "nice to have",
    "plus",
    "bonus",
    "good to have",
    "advantage",
}
RESPONSIBILITY_MARKERS = {
    "responsibilities",
    "responsible",
    "will",
    "build",
    "develop",
    "analyze",
    "prepare",
    "create",
    "maintain",
    "support",
    "collaborate",
}


def analyze_resume(resume_text: str, job_description: str) -> AnalysisResult:
    cleaned_resume = clean_text(resume_text)
    cleaned_job = clean_text(job_description)

    resume_sections = split_resume_sections(resume_text)
    resume_skills = extract_skills(cleaned_resume)
    job_profile = extract_job_profile(job_description)
    job_skills = set(job_profile.required_skills) | set(job_profile.preferred_skills)
    resume_keywords = extract_keywords(cleaned_resume)
    job_keywords = extract_keywords(cleaned_job)

    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    priority_missing_skills = sorted(set(job_profile.required_skills) - resume_skills)

    skills_score = score_skill_match(
        resume_skills=resume_skills,
        required_skills=set(job_profile.required_skills),
        preferred_skills=set(job_profile.preferred_skills),
    )
    keyword_score = score_keyword_alignment(cleaned_resume, cleaned_job)
    semantic_score = round(cosine_similarity(cleaned_resume, cleaned_job) * 100)
    experience_score = score_experience_alignment(resume_sections, cleaned_job)
    ats_check = evaluate_ats_readiness(resume_text, resume_sections, resume_skills)

    overall = round(
        skills_score * 0.35
        + keyword_score * 0.20
        + semantic_score * 0.15
        + experience_score * 0.15
        + ats_check.score * 0.15
    )

    section_analysis = analyze_sections(resume_sections, job_skills, missing_skills)
    recommendations = build_recommendations(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        priority_missing_skills=priority_missing_skills,
        job_keywords=job_keywords,
        resume_sections=resume_sections,
        ats_warnings=ats_check.warnings,
    )

    return AnalysisResult(
        summary=build_summary(overall, matched_skills, missing_skills),
        scores=ScoreBreakdown(
            overall=overall,
            skills=skills_score,
            keywords=keyword_score,
            semantic_similarity=semantic_score,
            experience=experience_score,
            ats=ats_check.score,
        ),
        job_profile=job_profile,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        priority_missing_skills=priority_missing_skills,
        resume_keywords=resume_keywords,
        job_keywords=job_keywords,
        section_analysis=section_analysis,
        ats=ats_check,
        recommendations=recommendations,
    )


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    text = EMAIL_PATTERN.sub(" ", text)
    text = URL_PATTERN.sub(" ", text)
    tokens = [token.lower().strip(".-") for token in TOKEN_PATTERN.findall(text)]
    return [
        token
        for token in tokens
        if len(token) > 2
        and token not in STOPWORDS
        and "@" not in token
        and not token.endswith(".com")
    ]


def extract_skills(text: str) -> set[str]:
    padded = f" {text.lower()} "
    found = set()

    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = r"(?<![a-z0-9+#])" + re.escape(alias.lower().strip()) + r"(?![a-z0-9+#])"
            if re.search(pattern, padded):
                found.add(canonical)
                break

    return found


def extract_job_profile(job_description: str) -> JobProfile:
    cleaned_job = clean_text(job_description)
    all_skills = extract_skills(cleaned_job)
    required_skills = set()
    preferred_skills = set()

    for sentence in split_sentences(job_description):
        cleaned_sentence = clean_text(sentence)
        sentence_skills = extract_skills(cleaned_sentence)
        if not sentence_skills:
            continue

        if contains_marker(cleaned_sentence, PREFERRED_MARKERS):
            preferred_skills.update(sentence_skills)
        elif contains_marker(cleaned_sentence, REQUIRED_MARKERS):
            required_skills.update(sentence_skills)

    uncategorized = all_skills - required_skills - preferred_skills
    if required_skills:
        preferred_skills.update(uncategorized)
    else:
        required_skills.update(uncategorized)

    preferred_skills -= required_skills

    return JobProfile(
        required_skills=sorted(required_skills),
        preferred_skills=sorted(preferred_skills),
        responsibilities=extract_responsibilities(job_description),
    )


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+|\n+", text) if sentence.strip()]


def contains_marker(text: str, markers: set[str]) -> bool:
    return any(marker in text for marker in markers)


def extract_responsibilities(job_description: str, limit: int = 5) -> list[str]:
    responsibilities = []
    for sentence in split_sentences(job_description):
        cleaned_sentence = clean_text(sentence)
        if contains_marker(cleaned_sentence, RESPONSIBILITY_MARKERS):
            responsibilities.append(sentence.strip(" -•"))

    if responsibilities:
        return responsibilities[:limit]

    return split_sentences(job_description)[: min(limit, 3)]


def extract_keywords(text: str, limit: int = 20) -> list[str]:
    words = tokenize(text)
    section_words = {
        header_word
        for aliases in SECTION_HEADERS.values()
        for alias in aliases
        for header_word in alias.split()
    }
    words = [word for word in words if word not in section_words]
    single_counts = Counter(words)
    phrase_counts = Counter(
        " ".join(pair)
        for pair in zip(words, words[1:])
        if pair[0] != pair[1] and pair[0] not in STOPWORDS and pair[1] not in STOPWORDS
    )
    ranked_phrases = [phrase for phrase, count in phrase_counts.most_common(8) if count > 1]
    ranked_words = [word for word, _ in single_counts.most_common(limit)]
    return (ranked_phrases + ranked_words)[:limit]


def score_skill_match(
    resume_skills: set[str], required_skills: set[str], preferred_skills: set[str]
) -> int:
    required_score = percent(len(resume_skills & required_skills), max(len(required_skills), 1))
    if not preferred_skills:
        return required_score

    preferred_score = percent(len(resume_skills & preferred_skills), len(preferred_skills))
    return round(required_score * 0.75 + preferred_score * 0.25)


def score_keyword_alignment(resume_text: str, job_text: str) -> int:
    resume_tokens = set(tokenize(resume_text))
    job_tokens = set(tokenize(job_text))
    if not job_tokens:
        return 0

    return percent(len(resume_tokens & job_tokens), len(job_tokens))


def split_resume_sections(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections: dict[str, list[str]] = {"other": []}
    current = "other"

    header_lookup = {
        alias: canonical for canonical, aliases in SECTION_HEADERS.items() for alias in aliases
    }

    for line in lines:
        normalized = re.sub(r"[^a-zA-Z ]", "", line).lower().strip()
        header = detect_section_header(normalized, header_lookup)
        if header:
            current = header
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {name: "\n".join(content).strip() for name, content in sections.items() if content}


def detect_section_header(normalized_line: str, header_lookup: dict[str, str]) -> str | None:
    if normalized_line in header_lookup:
        return header_lookup[normalized_line]

    if len(normalized_line.split()) <= 4:
        for alias, canonical in header_lookup.items():
            if normalized_line.startswith(alias + " ") or normalized_line.endswith(" " + alias):
                return canonical

    return None


def cosine_similarity(first: str, second: str) -> float:
    first_counts = Counter(tokenize(first))
    second_counts = Counter(tokenize(second))
    vocabulary = set(first_counts) | set(second_counts)

    if not vocabulary:
        return 0.0

    dot_product = sum(first_counts[word] * second_counts[word] for word in vocabulary)
    first_norm = math.sqrt(sum(value * value for value in first_counts.values()))
    second_norm = math.sqrt(sum(value * value for value in second_counts.values()))

    if first_norm == 0 or second_norm == 0:
        return 0.0

    return dot_product / (first_norm * second_norm)


def score_experience_alignment(resume_sections: dict[str, str], job_text: str) -> int:
    experience_text = " ".join(
        resume_sections.get(section, "") for section in ("experience", "projects", "summary")
    ).lower()
    if not experience_text:
        return 20

    job_tokens = set(tokenize(job_text))
    experience_tokens = set(tokenize(experience_text))
    overlap_score = percent(len(job_tokens & experience_tokens), max(len(job_tokens), 1))

    action_count = sum(1 for verb in ACTION_VERBS if verb in experience_text)
    action_score = min(action_count * 12, 40)

    metric_score = 20 if re.search(r"\b\d+%|\b\d+\+|\b\d{2,}\b", experience_text) else 0
    project_bonus = 12 if resume_sections.get("projects") and overlap_score >= 20 else 0
    return min(round(overlap_score * 0.8 + action_score + metric_score + project_bonus), 100)


def evaluate_ats_readiness(
    resume_text: str, resume_sections: dict[str, str], resume_skills: set[str]
) -> AtsCheck:
    strengths = []
    warnings = []
    score = 100

    expected_sections = {"skills", "education", "experience"}
    missing_sections = sorted(expected_sections - set(resume_sections))

    if missing_sections:
        score -= len(missing_sections) * 12
        warnings.append(f"Missing clear section headers: {', '.join(missing_sections)}.")
    else:
        strengths.append("Uses clear core section headers.")

    if len(resume_skills) >= 5:
        strengths.append("Includes a visible technical skills set.")
    else:
        score -= 12
        warnings.append("Skills are limited or not easy for an ATS parser to detect.")

    if re.search(r"[\w.-]+@[\w.-]+\.\w+", resume_text):
        strengths.append("Email contact information appears machine-readable.")
    else:
        score -= 8
        warnings.append("Email contact information was not detected.")

    word_count = len(tokenize(resume_text))
    if word_count < 180:
        score -= 12
        warnings.append("Resume text looks short; add stronger bullets and project detail.")
    elif word_count > 1000:
        score -= 8
        warnings.append("Resume may be too long; keep the most role-relevant content.")
    else:
        strengths.append("Resume length looks reasonable for automated screening.")

    if "\t" in resume_text or resume_text.count("|") > 8:
        score -= 8
        warnings.append("Heavy tables or columns may reduce parser reliability.")

    return AtsCheck(score=max(score, 0), strengths=strengths, warnings=warnings)


def analyze_sections(
    resume_sections: dict[str, str], job_skills: set[str], missing_skills: list[str]
) -> dict[str, str]:
    result = {}

    for section in ("summary", "skills", "experience", "projects", "education"):
        content = resume_sections.get(section, "")
        if not content:
            result[section] = "Not detected clearly. Add this section if it is relevant to the role."
            continue

        section_skills = extract_skills(clean_text(content))
        overlap = sorted(section_skills & job_skills)
        if overlap:
            result[section] = f"Relevant signals found: {', '.join(overlap)}."
        else:
            result[section] = "Detected, but it could use more role-specific language."

    if missing_skills:
        result["skill_gap"] = f"Priority gaps to address: {', '.join(missing_skills[:8])}."
    else:
        result["skill_gap"] = "No major required skill gaps detected from the job description."

    return result


def build_recommendations(
    matched_skills: list[str],
    missing_skills: list[str],
    priority_missing_skills: list[str],
    job_keywords: list[str],
    resume_sections: dict[str, str],
    ats_warnings: list[str],
) -> list[str]:
    recommendations = []

    if priority_missing_skills:
        recommendations.append(
            "Prioritize required skill gaps first: "
            + ", ".join(priority_missing_skills[:5])
            + ". Add them only where you can honestly show coursework, projects, internships, or practice."
        )

    if missing_skills:
        recommendations.append(
            "Add evidence for these job-relevant skills if you have experience with them: "
            + ", ".join(missing_skills[:6])
            + "."
        )

    if matched_skills:
        recommendations.append(
            "Move the strongest matched skills closer to the top of the resume: "
            + ", ".join(matched_skills[:6])
            + "."
        )

    top_keywords = [keyword for keyword in job_keywords[:8] if keyword not in matched_skills]
    if top_keywords:
        recommendations.append(
            "Use more job-specific wording around: " + ", ".join(top_keywords[:6]) + "."
        )

    if "summary" not in resume_sections:
        recommendations.append(
            "Add a 2-3 line summary tailored to this role, mentioning your target role, core skills, and strongest project or experience."
        )

    experience_text = resume_sections.get("experience", "") + "\n" + resume_sections.get("projects", "")
    if not re.search(r"\b\d+%|\b\d+\+|\b\d{2,}\b", experience_text):
        recommendations.append(
            "Quantify impact in bullets where possible, such as accuracy, users, records processed, time saved, or performance improvement."
        )

    for warning in ats_warnings[:2]:
        recommendations.append(f"ATS improvement: {warning}")

    if not recommendations:
        recommendations.append(
            "The resume is well aligned. Focus on tightening bullet wording and keeping the most relevant achievements near the top."
        )

    return recommendations


def build_summary(overall: int, matched_skills: list[str], missing_skills: list[str]) -> str:
    if overall >= 75:
        fit = "strong"
    elif overall >= 50:
        fit = "moderate"
    else:
        fit = "developing"

    matched = ", ".join(matched_skills[:4]) if matched_skills else "few direct skill matches"
    missing = ", ".join(missing_skills[:4]) if missing_skills else "no major detected skill gaps"

    return (
        f"This resume shows a {fit} fit for the target role. "
        f"Key matches include {matched}. Main gaps: {missing}."
    )


def percent(part: int, total: int) -> int:
    if total <= 0:
        return 0
    return min(round((part / total) * 100), 100)
