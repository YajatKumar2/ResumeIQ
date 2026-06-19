# Privacy And Limits

ResumeIQ is designed as a local-first portfolio MVP. It processes resume text for analysis and does not intentionally store uploaded resumes or analysis results.

## Current Privacy Behavior

- Uploaded files are written to a temporary file only while parsing.
- The backend returns analysis results directly to the frontend.
- The project does not include accounts, database storage, or resume history.
- `.env` is ignored by Git and should contain private API keys only on the local machine.

## Optional API Use

If `USE_LLM=true`, only rewrite-suggestion context is sent to the configured OpenAI-compatible API. ResumeIQ keeps scoring, skill matching, ATS checks, and evidence local.

Do not enable API enhancement for sensitive resumes unless the user understands that some resume/job context may be sent to the external provider.

## Current Limits

- Scanned image-only PDFs may not extract meaningful text.
- The ATS score is a local heuristic, not an official ATS guarantee.
- Skill extraction depends on the current local skill taxonomy.
- Rewrite suggestions are guidance, not automatically verified career advice.
- This is not yet a production SaaS system with authentication, encryption-at-rest, audit logs, or user data controls.
