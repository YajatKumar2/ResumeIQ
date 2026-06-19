export type ScoreBreakdown = {
  overall: number;
  skills: number;
  keywords: number;
  semantic_similarity: number;
  experience: number;
  ats: number;
};

export type JobProfile = {
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
};

export type AtsCheck = {
  score: number;
  strengths: string[];
  warnings: string[];
};

export type ContactInfo = {
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  location: string | null;
};

export type AnalysisEvidence = {
  score_factors: string[];
  resume_evidence: string[];
  job_evidence: string[];
  recommendation_sources: string[];
};

export type RewriteSuggestions = {
  source: string;
  tailored_summary: string;
  bullet_examples: string[];
  skills_to_highlight: string[];
  learning_focus: string[];
};

export type AnalysisResult = {
  summary: string;
  scores: ScoreBreakdown;
  contact_info: ContactInfo;
  job_profile: JobProfile;
  evidence: AnalysisEvidence;
  rewrite_suggestions: RewriteSuggestions;
  matched_skills: string[];
  missing_skills: string[];
  priority_missing_skills: string[];
  resume_keywords: string[];
  job_keywords: string[];
  section_analysis: Record<string, string>;
  ats: AtsCheck;
  recommendations: string[];
};
