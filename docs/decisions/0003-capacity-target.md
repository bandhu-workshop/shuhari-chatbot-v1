# 0003 — Capacity target: 50 concurrent users

> **Last updated:** 2026-11-26 14:52 IST

**Status:** accepted · **Date:** 2026-11-26

## Context

"Build it so it scales" is not a requirement, it is an invitation to build everything. A
number is a requirement. Without one, every design discussion drifts toward Redis, caches,
queues and worker pools that this project will never need, and each of those is a
permanent maintenance obligation rather than a one-time cost.

## Decision

**The target is 50 concurrent users.** Design for that, verify against it, and treat
anything beyond it as a future project's problem.

A concurrent user here means one person with a chat session open, sending a turn every
~30 seconds, where a turn takes 2–10 seconds of model time.

## What 50 concurrent users actually costs

| Component | Load at 50 users | Consequence for the design |
| --- | --- | --- |
| FastAPI + SSE | 50 long-lived open streams | One async uvicorn worker handles this without noticing. **No gunicorn, no worker count to tune** — Cloud Run scales by instance, not by process, and running 4 workers locally would hide that while quadrupling the DB pool |
| Identity check | tens of microseconds per request | Never the bottleneck. **Don't cache it**, don't put it in Redis |
| Our DB queries | a few per turn, mostly session reads | A pool of 10–20 per instance is ample |
| **LLM provider** | ~5–25 requests/sec of multi-second calls | **The real ceiling.** It is a rate limit and a token budget, not our code |
| **Ollama embeddings** | one local instance, one call per memory operation | **The local bottleneck, from milestone 5 onward.** The first place to actually measure |

The conclusion that matters: at this size the bottleneck is never our Python. It is the
model provider, and locally it is Ollama. Optimising FastAPI would be optimising the wrong
thing.

## Consequences

Things we therefore **do**:

- **DB pool size from an env var, with a small default.** Each instance holds its own pool,
  and Cloud SQL's `max_connections` scales with instance memory — a small tier sits around
  25 *total* connections, and each idle connection costs ~2–3 MB of shared memory. So
  `pool_size × instance_count` is the number that matters, never `pool_size` alone. Verify
  the live value with `SHOW max_connections;` before deployment phase 3.
- **Keep one async worker per container.** Cloud Run's default is 80 concurrent requests
  per instance (configurable up to 1,000), so all 50 users can legitimately land on a
  single instance. That is fine, and it is another reason the pool default matters more
  than the instance count.
- **Load-test with one Locust scenario at 50 users** (tracker row V5), recording p95 and
  p99 rather than the mean.

Things we therefore **don't build**:

| Not building | Because |
| --- | --- |
| Redis | Nothing at 50 users needs it. Rate limiting, if it ever arrives, goes in Postgres or at the edge |
| A caching layer | The expensive call is the LLM's, and caching model output is an eval problem, not a performance one |
| A task queue | No background work exists yet. SSE is the streaming mechanism |
| Horizontal-scaling design, sharding, read replicas | One Postgres, one Cloud Run service |
| Tuned worker/thread pools | See above: one async worker |

If any of these later turns out to be needed, the Locust scenario will show it. **Measure
first.** A number from a measurement reopens this ADR; an intuition does not.

## Notes

Load-test numbers produced on a laptop are **relative, not absolute** — the load generator
and the server compete for the same CPU. They are for comparing before and after a change,
not for predicting production capacity.

Cloud SQL and Cloud Run specifics here were checked on 2026-11-26 and belong to deployment
phase 3 ([ADR 0001](0001-deployment-strategy.md)); re-verify them then rather than trusting
this file.
