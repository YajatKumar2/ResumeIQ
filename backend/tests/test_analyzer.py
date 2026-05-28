from backend.app.core.analyzer import analyze_resume


def test_analyzer_detects_matching_and_missing_skills():
    resume = """
    Alex Kumar
    alex@example.com

    Summary
    Data analyst with experience building Python dashboards.

    Skills
    Python, SQL, Pandas, Excel, Git

    Projects
    Built a sales analytics dashboard using Python and Pandas for 20,000 records.

    Education
    B.Tech Computer Science
    """

    job = """
    We are hiring a data analyst with Python, SQL, Tableau, machine learning, and strong
    communication skills. The candidate will analyze business data and build dashboards.
    """

    result = analyze_resume(resume, job)

    assert result.scores.overall > 40
    assert "python" in result.matched_skills
    assert "sql" in result.matched_skills
    assert "tableau" in result.missing_skills
    assert result.recommendations


def test_analyzer_reports_ats_warnings_for_sparse_resume():
    resume = "Sam Student\nBuilt websites."
    job = "Frontend developer role requiring React, JavaScript, HTML, CSS, and Git."

    result = analyze_resume(resume, job)

    assert result.scores.ats < 100
    assert result.ats.warnings
    assert "react" in result.missing_skills
