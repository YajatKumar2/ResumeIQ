import {
  AlertCircle,
  ArrowRight,
  BadgeCheck,
  BriefcaseBusiness,
  ClipboardCheck,
  Download,
  FileText,
  Gauge,
  Loader2,
  RefreshCcw,
  Upload,
} from "lucide-react";
import { ChangeEvent, FormEvent, useMemo, useRef, useState } from "react";
import { analyzeText, analyzeUpload } from "./api";
import type { AnalysisResult } from "./types";

const scoreItems = [
  ["skills", "Skills"],
  ["keywords", "Keywords"],
  ["semantic_similarity", "Similarity"],
  ["experience", "Experience"],
  ["ats", "ATS"],
] as const;

const maxFileSizeBytes = 5 * 1024 * 1024;
const supportedExtensions = [".pdf", ".docx", ".txt"];
type ResumeInputMode = "paste" | "upload";

const sampleResumeText = `Priya Sharma
priya.sharma@example.com
Bengaluru, India

Summary
Computer science student with hands-on experience building web applications and data-driven dashboards using Python, SQL, JavaScript, and React.

Skills
Python, SQL, JavaScript, React, HTML, CSS, Git, Excel, Data Analysis

Projects
Student Performance Dashboard
Built a dashboard using Python, SQL, and Excel to analyze academic performance data for 5,000 student records. Created charts to identify attendance and score trends.

Portfolio Web App
Developed a responsive personal portfolio using React, JavaScript, HTML, and CSS. Added project cards, contact form, and mobile-friendly layout.

Education
B.Tech in Computer Science`;

const sampleJobDescription = `We are hiring a Junior Data Analyst to support business reporting and data-driven decision-making. The ideal candidate should have strong skills in Python, SQL, Excel, and Pandas, with experience cleaning datasets, analyzing trends, and preparing reports or dashboards.

Responsibilities include collecting and cleaning data, writing SQL queries, building dashboards, identifying business insights, and explaining findings to non-technical stakeholders.

Required skills:
Python, SQL, Excel, Pandas, data analysis, data visualization, problem solving

Preferred skills:
Tableau, Power BI, machine learning, statistics, communication, Git`;

export function App() {
  const [resumeInputMode, setResumeInputMode] = useState<ResumeInputMode>("upload");
  const [resume, setResume] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const hasResumeInput = resumeInputMode === "upload" ? Boolean(resume) : Boolean(resumeText.trim());
  const canAnalyze = Boolean(hasResumeInput && jobDescription.trim() && !isLoading);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (resumeInputMode === "upload" && !resume) {
      setError("Upload a resume file before analyzing.");
      return;
    }
    if (resumeInputMode === "paste" && !resumeText.trim()) {
      setError("Paste resume text before analyzing.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Paste a target job description before analyzing.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result =
        resumeInputMode === "upload"
          ? await analyzeUpload(resume as File, jobDescription)
          : await analyzeText(resumeText, jobDescription);
      setAnalysis(result);
    } catch (caughtError) {
      setAnalysis(null);
      setError(caughtError instanceof Error ? caughtError.message : "Resume analysis failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setError("");

    if (!file) {
      setResume(null);
      return;
    }

    const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!supportedExtensions.includes(extension)) {
      setResume(null);
      event.target.value = "";
      setError("Use a PDF, DOCX, or TXT resume file.");
      return;
    }

    if (file.size > maxFileSizeBytes) {
      setResume(null);
      event.target.value = "";
      setError("Resume file is too large. Maximum size is 5 MB.");
      return;
    }

    setResume(file);
  }

  function handleReset() {
    setResume(null);
    setResumeText("");
    setJobDescription("");
    setAnalysis(null);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  const fileLabel = useMemo(() => {
    if (!resume) return "PDF, DOCX, or TXT up to 5 MB";
    return `${resume.name} • ${(resume.size / 1024).toFixed(1)} KB`;
  }, [resume]);

  function handleModeChange(mode: ResumeInputMode) {
    setResumeInputMode(mode);
    setError("");
    setAnalysis(null);
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <div className="brand-mark">
            <FileText size={28} />
          </div>
          <div>
            <p className="eyebrow">ResumeIQ</p>
            <h1>Resume-to-job fit analysis</h1>
          </div>
        </div>

        <form className="analysis-form" onSubmit={handleSubmit}>
          <div className="form-header">
            <span>Input</span>
            <button className="ghost-button" onClick={handleReset} type="button">
              <RefreshCcw size={16} />
              Reset
            </button>
          </div>

          <div className="segmented-control" aria-label="Resume input mode">
            <button
              className={resumeInputMode === "upload" ? "active" : ""}
              onClick={() => handleModeChange("upload")}
              type="button"
            >
              <Upload size={16} />
              Upload
            </button>
            <button
              className={resumeInputMode === "paste" ? "active" : ""}
              onClick={() => handleModeChange("paste")}
              type="button"
            >
              <FileText size={16} />
              Paste Text
            </button>
          </div>

          {resumeInputMode === "upload" ? (
            <label className="upload-zone">
              <input
                accept=".pdf,.docx,.txt"
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
              />
              <Upload size={24} />
              <span>Upload Resume</span>
              <small>{fileLabel}</small>
            </label>
          ) : (
            <label className="resume-text-input">
              <span>
                Resume Text
                <button
                  className="text-button"
                  onClick={() => setResumeText(sampleResumeText)}
                  type="button"
                >
                  Use sample
                </button>
              </span>
              <textarea
                value={resumeText}
                onChange={(event) => setResumeText(event.target.value)}
                placeholder="Paste extracted resume text here..."
              />
            </label>
          )}

          <label className="job-input">
            <span>
              Job Description
              <button
                className="text-button"
                onClick={() => setJobDescription(sampleJobDescription)}
                type="button"
              >
                Use sample
              </button>
            </span>
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the target job description here..."
            />
          </label>

          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <button className="primary-button" disabled={!canAnalyze} type="submit">
            {isLoading ? <Loader2 className="spin" size={18} /> : <Gauge size={18} />}
            Analyze Resume
          </button>
        </form>
      </section>

      <section className="results-area">
        {analysis ? (
          <Results analysis={analysis} />
        ) : (
          <EmptyState hasInput={Boolean(resume || resumeText || jobDescription)} />
        )}
      </section>
    </main>
  );
}

function EmptyState({ hasInput }: { hasInput: boolean }) {
  return (
    <div className="empty-state">
      <ClipboardCheck size={40} />
      <h2>{hasInput ? "Ready when your inputs are complete" : "Analysis results will appear here"}</h2>
      <p>
        {hasInput
          ? "Upload a supported resume and add a job description, then run the analysis."
          : "Upload a resume and paste a job description to generate the first match report."}
      </p>
    </div>
  );
}

function Results({ analysis }: { analysis: AnalysisResult }) {
  function handleDownloadReport() {
    const report = buildMarkdownReport(analysis);
    const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `resumeiq-analysis-${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="results-grid">
      <section className="score-panel">
        <div>
          <p className="eyebrow">Overall Match</p>
          <strong>{analysis.scores.overall}</strong>
        </div>
        <div className="score-copy">
          <p>{analysis.summary}</p>
          <button className="download-button" onClick={handleDownloadReport} type="button">
            <Download size={17} />
            Download Report
          </button>
        </div>
      </section>

      <section className="breakdown-panel">
        {scoreItems.map(([key, label]) => (
          <div className="score-row" key={key}>
            <span>{label}</span>
            <div className="meter">
              <div style={{ width: `${analysis.scores[key]}%` }} />
            </div>
            <strong>{analysis.scores[key]}</strong>
          </div>
        ))}
      </section>

      <Panel icon={<FileText size={20} />} title="Contact Info">
        <div className="contact-grid">
          <ContactItem label="Email" value={analysis.contact_info.email} />
          <ContactItem label="Phone" value={analysis.contact_info.phone} />
          <ContactItem label="LinkedIn" value={analysis.contact_info.linkedin} />
          <ContactItem label="GitHub" value={analysis.contact_info.github} />
          <ContactItem label="Location" value={analysis.contact_info.location} />
        </div>
      </Panel>

      <Panel icon={<BadgeCheck size={20} />} title="Matched Skills">
        <TagList items={analysis.matched_skills} emptyText="No direct matches detected yet." tone="good" />
      </Panel>

      <Panel icon={<AlertCircle size={20} />} title="Missing Skills">
        <TagList
          items={analysis.missing_skills}
          emptyText="No major missing skills detected."
          tone="warning"
        />
      </Panel>

      <Panel icon={<Gauge size={20} />} title="Priority Gaps">
        <TagList
          items={analysis.priority_missing_skills}
          emptyText="No required-skill gaps detected."
          tone="critical"
        />
      </Panel>

      <Panel icon={<BriefcaseBusiness size={20} />} title="Job Profile">
        <div className="stacked-list">
          <ListBlock title="Required" items={analysis.job_profile.required_skills} />
          <ListBlock title="Preferred" items={analysis.job_profile.preferred_skills} />
          <ListBlock title="Responsibilities" items={analysis.job_profile.responsibilities} />
        </div>
      </Panel>

      <Panel icon={<ClipboardCheck size={20} />} title="Recommendations">
        <ul className="recommendations">
          {analysis.recommendations.map((item) => (
            <li key={item}>
              <ArrowRight size={16} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel icon={<ArrowRight size={20} />} title="Rewrite Suggestions">
        <div className="source-pill">{formatSource(analysis.rewrite_suggestions.source)}</div>
        <div className="rewrite-block">
          <strong>Tailored summary</strong>
          <p>{analysis.rewrite_suggestions.tailored_summary}</p>
        </div>
        <div className="stacked-list">
          <ListBlock title="Bullet examples" items={analysis.rewrite_suggestions.bullet_examples} />
          <ListBlock title="Skills to highlight" items={analysis.rewrite_suggestions.skills_to_highlight} />
          <ListBlock title="Learning focus" items={analysis.rewrite_suggestions.learning_focus} />
        </div>
      </Panel>

      <Panel icon={<FileText size={20} />} title="Analysis Evidence">
        <div className="stacked-list">
          <ListBlock title="Score reasoning" items={analysis.evidence.score_factors} />
          <ListBlock title="Resume signals" items={analysis.evidence.resume_evidence} />
          <ListBlock title="Job description signals" items={analysis.evidence.job_evidence} />
          <ListBlock title="Suggestion sources" items={analysis.evidence.recommendation_sources} />
        </div>
      </Panel>

      <Panel icon={<Gauge size={20} />} title="ATS Readiness">
        <div className="ats-summary">
          <strong>{analysis.ats.score}</strong>
          <span>ATS score</span>
        </div>
        <ListBlock title="Strengths" items={analysis.ats.strengths} />
        <ListBlock title="Warnings" items={analysis.ats.warnings} />
      </Panel>

      <Panel icon={<FileText size={20} />} title="Section Analysis">
        <div className="section-list">
          {Object.entries(analysis.section_analysis).map(([section, text]) => (
            <div key={section}>
              <strong>{formatLabel(section)}</strong>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function Panel({
  children,
  icon,
  title,
}: {
  children: React.ReactNode;
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        {icon}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function TagList({
  emptyText,
  items,
  tone,
}: {
  emptyText: string;
  items: string[];
  tone: "critical" | "good" | "warning";
}) {
  if (!items.length) return <p className="muted">{emptyText}</p>;

  return (
    <div className="tag-list">
      {items.map((item) => (
        <span className={`tag ${tone}`} key={item}>
          {item}
        </span>
      ))}
    </div>
  );
}

function ListBlock({ items, title }: { items: string[]; title: string }) {
  return (
    <div className="list-block">
      <strong>{title}</strong>
      {items.length ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">None detected.</p>
      )}
    </div>
  );
}

function ContactItem({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="contact-item">
      <span>{label}</span>
      <strong>{value ?? "Not detected"}</strong>
    </div>
  );
}

function formatLabel(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatSource(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function buildMarkdownReport(analysis: AnalysisResult) {
  const lines = [
    "# ResumeIQ Analysis Report",
    "",
    `Generated: ${new Date().toLocaleString()}`,
    "",
    "## Overall Fit",
    "",
    `Score: ${analysis.scores.overall}/100`,
    "",
    analysis.summary,
    "",
    "## Score Breakdown",
    "",
    `- Skills: ${analysis.scores.skills}/100`,
    `- Keywords: ${analysis.scores.keywords}/100`,
    `- Similarity: ${analysis.scores.semantic_similarity}/100`,
    `- Experience: ${analysis.scores.experience}/100`,
    `- ATS: ${analysis.scores.ats}/100`,
    "",
    "## Matched Skills",
    "",
    listForReport(analysis.matched_skills),
    "",
    "## Missing Skills",
    "",
    listForReport(analysis.missing_skills),
    "",
    "## Priority Gaps",
    "",
    listForReport(analysis.priority_missing_skills),
    "",
    "## Contact Info",
    "",
    `- Email: ${analysis.contact_info.email ?? "Not detected"}`,
    `- Phone: ${analysis.contact_info.phone ?? "Not detected"}`,
    `- LinkedIn: ${analysis.contact_info.linkedin ?? "Not detected"}`,
    `- GitHub: ${analysis.contact_info.github ?? "Not detected"}`,
    `- Location: ${analysis.contact_info.location ?? "Not detected"}`,
    "",
    "## Recommendations",
    "",
    listForReport(analysis.recommendations),
    "",
    "## Rewrite Suggestions",
    "",
    `Source: ${formatSource(analysis.rewrite_suggestions.source)}`,
    "",
    "### Tailored Summary",
    "",
    analysis.rewrite_suggestions.tailored_summary,
    "",
    "### Bullet Examples",
    "",
    listForReport(analysis.rewrite_suggestions.bullet_examples),
    "",
    "## ATS Readiness",
    "",
    `ATS Score: ${analysis.ats.score}/100`,
    "",
    "### Strengths",
    "",
    listForReport(analysis.ats.strengths),
    "",
    "### Warnings",
    "",
    listForReport(analysis.ats.warnings),
    "",
    "## Analysis Evidence",
    "",
    "### Score Reasoning",
    "",
    listForReport(analysis.evidence.score_factors),
    "",
    "### Resume Signals",
    "",
    listForReport(analysis.evidence.resume_evidence),
    "",
    "### Job Description Signals",
    "",
    listForReport(analysis.evidence.job_evidence),
  ];

  return `${lines.join("\n")}\n`;
}

function listForReport(items: string[]) {
  if (!items.length) return "- None detected.";
  return items.map((item) => `- ${item}`).join("\n");
}
