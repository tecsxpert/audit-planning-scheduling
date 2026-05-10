# AI Developer 1 Demo Day Checklist

## Before demo

- Confirm Flask AI service starts successfully on port `5000`
- Confirm `/health` returns `200`
- Confirm `rag_document_count` is `10`
- Confirm `embedding_model_preloaded` is `true`
- Confirm `/describe`, `/recommend`, `/generate-report`, `/analyse-document`, and `/query` return `200`
- Confirm `/generate-report?stream=true` streams SSE events
- Confirm `.env` contains `GROQ_API_KEY` if live Groq output is required

## Demo inputs to keep ready

- Describe input
- Recommend input
- Generate report input
- Analyse document input
- Query input

## If Groq is unavailable

- Explain that the service supports a fallback response path
- Continue demoing endpoint structure and JSON shape
- Show seeded RAG sources and endpoint stability
