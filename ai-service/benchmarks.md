# Day 12 Benchmarks

## Methodology
- 50 requests per endpoint
- 5 concurrent workers
- Target latency: < 1500ms for p95

## Baseline Results (Before optimization)

| Endpoint | P50 (ms) | P95 (ms) | P99 (ms) |
|----------|---------|---------|---------|
| `/categorise` | 850 | 1200 | 1450 |
| `/describe` | 920 | 1350 | 1600 |
| `/recommend` | 1100 | 1650 | 1900 |
| `/query` | 1400 | 2100 | 2400 |
| `/generate-report` | (Async - 202 accepted in 45ms) |

## Optimizations applied
1. Enabled Redis caching for identical prompts.
2. Tuned Groq `max_tokens` limits appropriately per endpoint to reduce output generation time.
3. Preloaded the `SentenceTransformer` RAG model at startup rather than on first query to eliminate cold-start spikes.

## Post-Optimization Results

| Endpoint | P50 (ms) | P95 (ms) | P99 (ms) |
|----------|---------|---------|---------|
| `/categorise` | 420 | 750 | 950 |
| `/describe` | 450 | 800 | 1020 |
| `/recommend` | 480 | 950 | 1200 |
| `/query` | 850 | 1300 | 1450 |
| `/generate-report` | (Async - 202 accepted in 25ms) |

All endpoints now successfully pass the < 1500ms P95 target constraint.
