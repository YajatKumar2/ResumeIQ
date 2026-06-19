# Optional API Enhancement

ResumeIQ works without any paid or external API. The optional NVIDIA/OpenAI-compatible API integration only improves rewrite wording.

## Setup

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Fill in:

```text
USE_LLM=true
NVIDIA_API_KEY=your_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/llama-3.1-nemotron-nano-8b-v1
LLM_TIMEOUT_SECONDS=20
```

Check configuration:

```bash
make llm-status
```

Expected configured output:

```text
enabled: True
status: llm_configured
has_api_key: True
```

## What The API Does

The API receives local rewrite context and returns:

- improved tailored summary
- improved bullet examples

The API does not control:

- match score
- ATS score
- skill matching
- missing skills
- evidence
- contact extraction

If the API key, model, network, timeout, or response format fails, ResumeIQ automatically falls back to local rewrite suggestions.
