# AI Developer 1 Delivery Notes

## Scope completed

- Days 1-7 AI service implementation
- Days 8-15 testing, streaming, docs, optimisation, and seeded knowledge base
- Days 16-20 demo-prep assets, dry-run tooling, and readiness checks

## Final owned artifacts

- AI endpoint routes
- Prompt templates
- Groq fallback client
- Chroma-backed local RAG service
- 10 seeded domain knowledge documents
- Pytest coverage for the main endpoints
- Demo script and demo-day checklist
- Dry-run benchmark and readiness scripts

## Known environment dependency

Live Groq responses require:

- `GROQ_API_KEY`

Without that key, the app returns valid fallback payloads so the UI and contract can still be demonstrated.
