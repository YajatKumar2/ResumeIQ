import type { AnalysisResult } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function analyzeUpload(
  resume: File,
  jobDescription: string,
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("resume", resume);
  formData.append("job_description", jobDescription);

  const response = await fetch(`${API_BASE_URL}/analyze-upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Resume analysis failed.");
  }

  return response.json();
}
