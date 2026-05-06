# Day 14: Prompt QA against Demo Data

## Process
- **Data Source**: 30 seeded mock records spanning `Financial`, `IT`, `Compliance`, and `Operational` audits.
- **Goal**: Validate that all endpoints (`/categorise`, `/describe`, `/recommend`, `/query`, `/generate-report`) return professional, demo-ready output without hallucinations or formatting breaks.

## Results Summary

| Endpoint | Demo Readiness | Key Observations |
|----------|----------------|------------------|
| `/categorise` | PASS | Successfully categorized 30/30 records correctly. Handled vague descriptions by defaulting to "Uncategorised" safely. |
| `/describe` | PASS | Descriptions are punchy and highly professional. Tone constraints applied strictly. |
| `/recommend` | PASS | Consistently generated 3 actionable recommendations per record. Priorities (High/Medium/Low) align with severity. |
| `/query` | PASS | RAG system correctly cites dummy documents. Fallback triggered correctly for out-of-domain questions. |
| `/generate-report`| PASS | Generated structured JSON reports perfectly. No Markdown leakages into JSON values. |

## Adjustments Made
No prompt changes were strictly necessary as Day 6 and Day 10 tune-ups proved sufficient for the seeded demo data. The system is extremely stable.
