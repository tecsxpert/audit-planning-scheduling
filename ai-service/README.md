# AI Service

This Flask service provides the AI features for Tool-21 Audit Planning and Scheduling.

## Prerequisites

- Python 3.11+
- A virtual environment
- Optional: `GROQ_API_KEY` for live Groq responses

## Setup

```powershell
cd ai-service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment variables

- `GROQ_API_KEY`: optional live model API key
- `GROQ_MODEL`: optional model name override
- `CHROMA_PATH`: optional local ChromaDB storage path
- `RAG_COLLECTION_NAME`: optional ChromaDB collection name

## Run

```powershell
cd ai-service
& "..\.venv\Scripts\python.exe" app.py
```

The service runs on `http://127.0.0.1:5000`.

## API reference

### `GET /health`

Returns service health, rate-limit configuration, and RAG readiness metadata.

### `POST /describe`

Input:

```json
{"text":"Plan a high-risk audit with multiple dependencies."}
```

Returns a professional description, context sources, and generation metadata.

### `POST /recommend`

Input:

```json
{"text":"An audit is delayed because evidence is incomplete."}
```

Returns exactly three structured recommendations.

### `POST /generate-report`

Input:

```json
{"text":"Create an audit planning report for an overdue engagement."}
```

Returns structured report JSON.

### `POST /generate-report?stream=true`

Returns Server-Sent Events for incremental frontend rendering.

### `POST /analyse-document`

Input:

```json
{"text":"Audit kickoff delayed. Dependency on finance approval remains open."}
```

Returns summary plus a structured findings array.

### `POST /batch-process`

Input:

```json
{"items":["Item one","Item two"]}
```

Processes up to 20 items with a 100 ms per-item delay and returns a results array.

### `POST /query`

Input:

```json
{"question":"What should be checked first in audit planning?"}
```

Returns an answer plus the source files used from the local knowledge base.

## Tests

```powershell
cd ai-service
& "..\.venv\Scripts\python.exe" -m pytest tests -q
```

## Demo preparation assets

- [demo_script.md](./demo_script.md)
- [demo_day_checklist.md](./demo_day_checklist.md)
- [delivery_notes.md](./delivery_notes.md)
- [final_ai_qa.md](./final_ai_qa.md)

## Dry run and readiness scripts

```powershell
cd ai-service
& "..\.venv\Scripts\python.exe" scripts\run_dry_demo.py
& "..\.venv\Scripts\python.exe" scripts\groq_readiness_check.py
```
