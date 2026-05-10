# AI Developer 1 Demo Script

Date prepared: 2026-05-10

## 8-minute demo section owned by AI Developer 1

### 1. Describe endpoint

Input:

```json
{"text":"Schedule a high-risk audit with multiple dependencies and a tight deadline."}
```

Expected output highlights:

- Professional audit-planning description
- Context sources from the knowledge base
- Response metadata showing model/fallback details

What to say:

`This endpoint turns a short audit planning prompt into a professional description and enriches it with relevant audit knowledge context.`

### 2. Recommend endpoint

Input:

```json
{"text":"There is a delayed audit with missing evidence and conflicting owners."}
```

Expected output highlights:

- Exactly 3 recommendations
- Each recommendation has `action_type`, `description`, and `priority`

What to say:

`This endpoint gives structured next-step recommendations so the team can act instead of manually drafting follow-up actions.`

### 3. Generate Report endpoint

Input:

```json
{"text":"Prepare a status report for an audit programme with dependency risk."}
```

Expected output highlights:

- `title`
- `executive_summary`
- `overview`
- `top_items`
- `recommendations`

What to say:

`This endpoint produces a report-ready summary that can be displayed immediately in the UI or used in a workflow downstream.`

### 4. Streaming report demo

Endpoint:

`POST /generate-report?stream=true`

Expected output highlights:

- SSE events streamed section by section
- Frontend can show the report incrementally

What to say:

`We also support streaming so the user does not wait for the full report before seeing useful output.`

### 5. Analyse document endpoint

Input:

```json
{"text":"Kickoff delayed. Dependency on finance approval remains open. Evidence not ready."}
```

Expected output highlights:

- Summary
- Structured findings array
- Risk levels for the extracted issues

What to say:

`This endpoint identifies risks and planning signals from raw audit-related text and returns structured findings instead of free-form text only.`

### 6. Query endpoint

Input:

```json
{"question":"What should be checked first in audit planning?"}
```

Expected output highlights:

- Knowledge-grounded answer
- Source file list from the local RAG knowledge base

What to say:

`This is the RAG capability. It answers using our seeded domain knowledge and shows which sources supported the answer.`

## Demo close

What to say:

`My contribution covered the AI service endpoints, prompt structure, retrieval pipeline, report streaming, endpoint testing, demo QA, and the documentation needed to run and review the service.`
