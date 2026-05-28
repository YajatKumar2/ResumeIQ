import {
  AlertCircle,
  ArrowRight,
  BadgeCheck,
  BriefcaseBusiness,
  ClipboardCheck,
  FileText,
  Gauge,
  Loader2,
  Upload,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { analyzeUpload } from "./api";
import type { AnalysisResult } from "./types";

const scoreItems = [
  ["skills", "Skills"],
  ["keywords", "Keywords"],
  ["semantic_similarity", "Similarity"],
  ["experience", "Experience"],
  ["ats", "ATS"],
] as const;

export function App() {
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const canAnalyze = Boolean(resume && jobDescription.trim() && !isLoading);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resume) {
      setError("Upload a resume file before analyzing.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await analyzeUpload(resume, jobDescription);
      setAnalysis(result);
    } catch (caughtError) {
      setAnalysis(null);
      setError(caughtError instanceof Error ? caughtError.message : "Resume analysis failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const fileLabel = useMemo(() => {
    if (!resume) return "PDF, DOCX, or TXT up to 5 MB";
    return `${resume.name} • ${(resume.size / 1024).toFixed(1)} KB`;
  }, [resume]);

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
          <label className="upload-zone">
            <input
              accept=".pdf,.docx,.txt"
              type="file"
              onChange={(event) => setResume(event.target.files?.[0] ?? null)}
            />
            <Upload size={24} />
            <span>Upload Resume</span>
            <small>{fileLabel}</small>
          </label>

          <label className="job-input">
            <span>Job Description</span>
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
        {analysis ? <Results analysis={analysis} /> : <EmptyState />}
      </section>
    </main>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <ClipboardCheck size={40} />
      <h2>Analysis results will appear here</h2>
      <p>Upload a resume and paste a job description to generate the first match report.</p>
    </div>
  );
}

function Results({ analysis }: { analysis: AnalysisResult }) {
  return (
    <div className="results-grid">
      <section className="score-panel">
        <div>
          <p className="eyebrow">Overall Match</p>
          <strong>{analysis.scores.overall}</strong>
        </div>
        <p>{analysis.summary}</p>
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

      <Panel icon={<BriefcaseBusiness size={20} />} title="Job Profile">
        <div className="stacked-list">
          <ListBlock title="Required" items={analysis.job_profile.required_skills} />
          <ListBlock title="Preferred" items={analysis.job_profile.preferred_skills} />
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
  tone: "good" | "warning";
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

function formatLabel(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
