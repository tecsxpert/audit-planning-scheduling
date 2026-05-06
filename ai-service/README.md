# AI Service - Tool-21 Audit Planning and Scheduling

This Flask service provides the AI features for Audit Planning and Scheduling, leveraging Groq LLMs and ChromaDB RAG.

## Features
- **RAG-Powered Queries**: Answer audit questions using local domain knowledge.
- **Asynchronous Reporting**: Handle long-running report generation without blocking.
- **Security First**: PII scanning, prompt injection detection, and rate limiting integrated.
- **Resilience**: Circuit breaker pattern and exponential backoff for external API calls.
- **Caching**: Redis integration for high-performance response retrieval.

## Setup

```powershell
cd ai-service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables
- `GROQ_API_KEY`: API key for Groq Cloud.
- `GROQ_MODEL`: Defaults to `llama-3.3-70b-versatile`.
- `REDIS_URL`: URL for Redis cache (e.g., `redis://localhost:6379`).
- `CHROMA_PATH`: Path for local ChromaDB storage.

## API Reference

### `GET /health`
Returns service status, uptime, and cache metrics.

### `POST /describe`
Generates a professional description of an audit item.
Input: `{"text": "..."}`

### `POST /recommend`
Provides exactly three actionable recommendations.
Input: `{"text": "..."}`

### `POST /query`
Answers questions based on the RAG knowledge base.
Input: `{"question": "..."}`

### `POST /generate-report`
Asynchronously generates a boardroom-ready report. Returns a `job_id`.
Input: `{"text": "..."}`

### `GET /jobs/<job_id>`
Poll for the status of an asynchronous report generation task.

### `POST /analyse-document`
Performs deep analysis and findings extraction from text.

### `POST /batch-process`
Efficiently processes multiple items (up to 20) with automated pacing.

## Security and Compliance
- **PII Scanning**: Rejects requests containing Emails, Phone Numbers, or Credit Cards.
- **Injection Protection**: Detects and blocks "jailbreak" or prompt-override attempts.
- **Circuit Breaker**: Automatically trips if Groq API fails consecutively, preventing cascading failures.
