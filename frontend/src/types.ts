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

export type AnalysisResult = {
  summary: string;
  scores: ScoreBreakdown;
  job_profile: JobProfile;
  matched_skills: string[];
  missing_skills: string[];
  priority_missing_skills: string[];
  resume_keywords: string[];
  job_keywords: string[];
  section_analysis: Record<string, string>;
  ats: AtsCheck;
  recommendations: string[];
};
