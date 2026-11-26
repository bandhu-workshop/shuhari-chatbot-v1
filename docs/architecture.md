# Architecture

> **Last updated:** 2026-11-26 13:44 IST

How the running system fits together. Grows with each milestone. **State is marked
honestly** — most of this is designed but not yet built.

For *where we are*, see [tracker.md](./tracker.md). For *why* a choice was made, see
[decisions/](./decisions/). This file answers *what talks to what*.

---

## The shape

```
browser ──HTTP/SSE──▶ FastAPI (/api/v1) ──▶ ADK agent ──LiteLLM──▶ model provider
                          │                     │
                          │                     ├──▶ tools (SearXNG, ...)
                          │                     └──▶ mem0 (memory)
                          ▼
                      Postgres + pgvector
                          ▲
                          └── ADK sessions · our tables · mem0 vectors
                                  (three schema owners, one database)

                      OpenTelemetry ──▶ Phoenix (traces, evals)
```

| Piece | Where | State |
| --- | --- | --- |
| React UI | `frontend/src/` | scaffold only |
| HTTP API | `backend/src/shuhari/api/` | skeleton |
| Agent | `backend/src/shuhari/ai/agents/chatbot/` | skeleton |
| Memory | `backend/src/shuhari/ai/memory/` | skeleton — milestone 5 |
| Tracing | `backend/src/shuhari/ai/observability/` | skeleton — milestone 1 |
| Postgres + pgvector, Phoenix, SearXNG, Ollama | `compose.yaml` | defined, not yet started |

---

## Backend layering

One job per layer; **don't reach across them**. A route gets its session from
`api/deps.py`, never by building an engine. Full tree and rules:
[../backend/AGENTS.md](../backend/AGENTS.md) → Layout.

| Layer | Job |
| --- | --- |
| `main.py` | `create_app()` factory. Wiring only — no logic |
| `core/` | config, logging, exceptions. Knows nothing about agents or routes |
| `api/` | HTTP. `deps.py` is the only door to the DB and to identity |
| `db/` | async engine and session; `base.py` holds the metadata Alembic reads |
| `models/` | SQLModel tables |
| `schemas/` | request/response contracts — what the frontend sees |
| `ai/` | everything agent-related: agents, tools, prompts, memory, sessions, tracing, eval scoring |

`schemas/` is kept apart from `models/` so API contracts never leak DB columns. The
frontend's `api-types.ts` is generated from `schemas/` via `just types`, which turns a
contract mismatch into a build error.

---

## One database, three schema owners

Each owner manages its own tables and **never** another's.

| Owner | Tables | Managed by |
| --- | --- | --- |
| Our app | whatever is registered in `db/base.py`, defined in `models/` | SQLModel + Alembic |
| ADK | session / event / state tables | ADK itself (`adk migrate session` on upgrades) |
| mem0 | the `mem0_memories` vector collection | mem0 itself |

Alembic's `env.py` carries an `include_object` filter so autogenerate never proposes
dropping ADK's or mem0's tables. Alembic is also the only place extensions are enabled —
the first migration runs `CREATE EXTENSION IF NOT EXISTS vector`.

**Connections:** one URL, async-only. `core/config.py` derives
`postgresql+asyncpg://…` from `POSTGRES_*` and that single string serves our app code,
Alembic and ADK. mem0 alone takes discrete `host`/`port`/`user`/`password`/`dbname`
parameters, because it does not use SQLAlchemy. Reasoning and rejected alternatives:
[decisions/0002-one-database-url.md](./decisions/0002-one-database-url.md).

---

## Identity

One `get_current_user()` dependency in `api/deps.py` is the only source of `user_id`.
Locally it returns a hardcoded dev user; in production it will verify a real token behind
the same signature. Every route and every memory call takes `user_id` from it — never from
a literal or a query parameter, because memory records are scoped by user and retrofitting
identity would touch every route and every test.

---

## Observability, split in two

| Concern | Where | Goes to |
| --- | --- | --- |
| Application logs | `core/logging.py` | JSON on stdout (Cloud Logging parses it in production) |
| LLM and agent spans | `ai/observability/tracing.py` | OpenTelemetry + OpenInference → Phoenix |

Deliberately separate: they have different shapes and different consumers. `tracing.py` is
a no-op when `PHOENIX_COLLECTOR_ENDPOINT` is unset, so production can simply omit Phoenix.

---

## Tests and evals are different things

| | What | Must |
| --- | --- | --- |
| `backend/tests/` | deterministic, mocked model, no network | pass 100% |
| `backend/evals/` | real model calls, scored, 3 runs per dataset | not regress past tolerance vs `baseline.json` |

Eval **code** lives in `ai/evaluation/` (importable, typed, unit-tested). Eval **data**
lives in `backend/evals/` (datasets, baseline, runner CLI), outside `src/` so it is never
packaged into the wheel or the Docker image.

---

## Deployment

Local-first by decision, GCP in phases:
[decisions/0001-deployment-strategy.md](./decisions/0001-deployment-strategy.md). The
portability rules that keep Cloud Run cheap to reach are in
[../backend/AGENTS.md](../backend/AGENTS.md) → Portability.
