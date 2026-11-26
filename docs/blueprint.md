# shuhari-chatbot-v1 — Blueprint

> **Last updated:** 2026-11-26 18:40 IST

A Claude/ChatGPT-style chatbot agent built on Google ADK. It is Project 1 of the Shuhari roadmap: learn every component of a modern assistant by building it, one working end-to-end slice at a time, with tracing and evals from the first slice.

**Stack (open source):** Python 3.12 + uv · Google ADK (models via LiteLLM) · FastAPI · SQLModel + Alembic · React + TypeScript (Vite) · PostgreSQL + pgvector · mem0 · Ollama (embeddings) · Arize Phoenix (OpenTelemetry) · SearXNG · Docker · just · GitHub Actions

## Status

This blueprint is the full specification of the project: decisions, milestones, eval method, CI/CD, and every file needed to create the repo. It lives at `docs/blueprint.md`; the short day-to-day guide is [README.md](../README.md). The "Bootstrap" section at the end creates the repo, tooling, infra and CI. The agent, API, database models, frontend and eval runner are built milestone by milestone (see Milestones).

| Part | State |
| --- | --- |
| Repo layout, README, AGENTS.md, justfile, compose, Dockerfiles, CI, evals workflow | **Created.** Bootstrap steps 1–3 are done; see [tracker.md](tracker.md) |
| Backend dependencies, ruff/mypy/pytest, first tests | **Done** (bootstrap 4a) |
| Frontend dependencies, prettier, vitest, first tests | **Done** (bootstrap 4b) |
| Alembic and the first migration | Bootstrap 4c — waits on `core/config.py` |
| Backend code (agent, API, DB models, memory, eval runner) | Built in milestones 1–7 |
| Frontend app | Scaffolded with Vite in bootstrap, built from milestone 2 |

Current position and next action always live in [tracker.md](tracker.md), not here.

## One source of truth

This blueprint used to embed full copies of every file it specified — **1,002 lines of
them, about 70% of the document.** Those copies are gone. Each section now names the file,
says why it exists, and points at it.

The reason is evidence rather than taste. By 2026-11-26 the copies had drifted in at least
six known places across five pull requests: the `backend/AGENTS.md` copy had lost the
Capacity, TDD, ruff-`S` and auth-test sections, and the `frontend/AGENTS.md` copy still
said `ESLint` (changed in #7) and `App.tsx` (renamed in #11). `just docs-audit`
structurally *cannot* catch this, because a link inside a fenced block is sample text, not
a link. So every structural change had to be made in two places and remembered — which, by
this project's own rules, makes it the wrong kind of solution.

What this document still does, and the real files cannot: say **which** files exist, **why**
each exists, and how they fit together. That is the part worth keeping.

One exception: `infra/searxng/settings.yml` does not exist yet (deferred to milestone 4), so
its block is still a specification rather than a duplicate, and stays.

---

## Folder structure

```
shuhari-chatbot-v1/              ← the only git repo
├── README.md                    # Short overview: quick start, commands, daily git flow
├── AGENTS.md                    # Instructions for coding agents (repo-wide rules, commands, definition of done)
├── CLAUDE.md                    # One line: @AGENTS.md (Claude Code imports AGENTS.md)
├── justfile                     # Every dev command (run `just` to list)
├── compose.yaml                 # Postgres+pgvector, Phoenix, SearXNG, Ollama. Profile "app": + backend, frontend
├── .env.example                 # Template for .env (keys, model ids, Postgres, service URLs)
├── .env                         # Your local secrets (gitignored)
├── .gitignore
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # PR + main: backend, integration, frontend, docker; on main then publish images
│   │   └── evals.yml            # Manual + weekly: real-model evals (3 repeats) vs baseline
│   ├── rulesets/main.json       # Protection for main, applied once CI is green (`just protect-main`)
│   ├── dependabot.yml           # Monthly grouped dependency updates
│   └── pull_request_template.md
│
├── infra/
│   └── searxng/settings.yml     # SearXNG config (JSON output for the search tool)
│
├── docs/
│   ├── blueprint.md             # This file: full spec + bootstrap
│   ├── architecture.md          # How the pieces fit: agent, API, memory, DB, tracing
│   ├── roadmap.md               # Full Shuhari roadmap (Project 1 + Project 2)
│   └── decisions/               # ADRs: one short file per non-obvious choice (0001-adk-first.md ...)
│
├── localdev/                    # Gitignored. Docker volumes (localdev/data/), scratch notes, sample files
│
├── backend/                     # Python service: agents, API, memory, evals
│   ├── AGENTS.md                # Backend rules: config, DB ownership, mem0 config, evals, security
│   ├── CLAUDE.md                # @AGENTS.md
│   ├── Dockerfile               # Multi-stage uv build → slim Python image running uvicorn
│   ├── .dockerignore
│   ├── pyproject.toml           # Dependencies and tool config (ruff, mypy, pytest)
│   ├── uv.lock
│   ├── .venv/                   # Created by `uv sync` (gitignored)
│   ├── alembic.ini
│   ├── alembic/                 # Migrations for OUR tables only (env.py filters out ADK and mem0 tables)
│   ├── src/shuhari/
│   │   ├── main.py              # create_app() factory + ASGI entry point; wiring only
│   │   ├── core/                # Cross-cutting concerns
│   │   │   ├── config.py            # Settings from env: model ids, providers, keys, all DB URLs
│   │   │   ├── logging.py           # setup_logging() — JSON to stdout
│   │   │   └── exceptions.py        # AppError hierarchy + FastAPI handlers
│   │   ├── api/                 # HTTP layer
│   │   │   ├── deps.py              # Shared dependencies: DbSession, get_current_user()
│   │   │   ├── health.py            # /healthz, /readyz — unversioned, outside /api
│   │   │   └── v1/
│   │   │       ├── router.py            # Aggregator that route modules attach to
│   │   │       └── routes/              # chat (SSE), sessions, memory, feedback
│   │   ├── db/                  # Async DB access
│   │   │   ├── base.py              # SQLModel metadata — register new models here
│   │   │   └── session.py           # Async engine + get_session()
│   │   ├── models/              # SQLModel table classes, one file per concept
│   │   ├── schemas/             # Request/response models: the contract with the frontend
│   │   └── ai/                  # Everything agent-related (Google ADK)
│   │       ├── agents/
│   │       │   ├── chatbot/         # Main ADK agent: agent.py exports `root_agent`
│   │       │   └── research/        # Research orchestrator + sub-agents (milestone 6)
│   │       ├── tools/              # One file per tool, plain typed functions
│   │       ├── prompts/            # Prompt templates, one file per agent (data, not code)
│   │       ├── mcp/                # MCPToolset configs (milestone 6)
│   │       ├── memory/             # mem0 setup + ADK MemoryService wrapper (milestone 5)
│   │       ├── sessions/           # ADK DatabaseSessionService on Postgres (async driver)
│   │       ├── observability/
│   │       │   └── tracing.py          # OpenTelemetry + OpenInference export to Phoenix
│   │       └── evaluation/         # Eval scoring logic
│   │           └── graders/            # Code checks + LLM-judge rubrics
│   ├── tests/
│   │   ├── unit/                # Fast, no network/DB, mocked model; mirrors src/shuhari/ 1:1
│   │   └── integration/         # Needs Postgres; marked @pytest.mark.integration
│   └── evals/                   # Eval DATA and entry point — not importable code
│       ├── datasets/            # JSONL golden sets: chat, tools, memory, research, security
│       ├── baseline.json        # Committed baseline scores + tolerance per dataset
│       ├── run.py               # CLI: runs datasets N times, compares to baseline, logs to Phoenix
│       └── results/             # Local run outputs (gitignored)
│
└── frontend/                    # Chat UI
    ├── AGENTS.md
    ├── CLAUDE.md                # @AGENTS.md
    ├── Dockerfile               # Node build → nginx serving static files
    ├── nginx.conf               # SPA routing + /api proxy to backend (SSE/WebSocket safe)
    ├── .dockerignore
    ├── package.json
    ├── node_modules/            # Created by `npm install` (gitignored)
    └── src/
        ├── features/
        │   ├── chat/            # Message list, composer, streaming renderer, tool-call cards
        │   ├── sessions/        # Sidebar: list, rename, delete, resume conversations
        │   └── memory/          # View, edit, delete what the assistant remembers
        ├── components/ui/       # Shared presentational components
        ├── lib/
        │   ├── api.ts           # fetch + SSE client; the only place that calls the backend
        │   └── api-types.ts     # Generated by `just types` from the backend OpenAPI schema
        ├── hooks/
        └── App.tsx
```

### Backend layering

One job per layer; don't reach across them (a route goes through `api/deps.py`, not
straight into `db/`). Structure adapted from
[`bandhu-workshop/creditforge`](https://github.com/bandhu-workshop/creditforge).

- `main.py` holds no logic — it wires settings, logging, exception handlers, routers and
  the lifespan together. A factory, so tests can build their own app.
- **Code in `src/`, data outside it.** `ai/evaluation/` is importable scoring logic;
  `evals/` holds datasets, baseline and the runner CLI. Datasets under `src/` would ship
  in the wheel and the Docker image, and `.dockerignore` excludes `evals` on purpose.
- `observability/` sits under `ai/` because it handles LLM and agent spans;
  application logs are `core/logging.py`. Different concerns.
- `schemas/` is separate from `models/` so API contracts never leak DB columns.
- Versioned routes under `/api/v1`; `/healthz` and `/readyz` stay outside it so Cloud
  Run's startup probe never depends on an API version.
- No `services/` layer until milestone 3, when session list/rename/delete needs a home
  that is neither a route nor agent code.
- **Async-only, one database URL.** App code, Alembic and ADK share one
  `postgresql+asyncpg://` string; mem0 alone takes discrete connection parameters because
  it is not SQLAlchemy. `asyncpg` is the only driver we declare. See
  [ADR 0002](./decisions/0002-one-database-url.md).

---

## Architecture decisions

### One Postgres, three schema owners

| Owner | What | Schema managed by |
| --- | --- | --- |
| Our app | Tables in `models/`, registered in `db/base.py` | SQLModel + Alembic (pgvector extension enabled in the first migration) |
| ADK | Session, event and state tables | ADK. Needs `google-adk[db]` and an async driver (`asyncpg`). On ADK upgrades, use `adk migrate session` if its schema changed |
| mem0 | `mem0_memories` vector collection | mem0 |

`config.py` builds all three connection URLs from the same `POSTGRES_*` variables, and Alembic's `env.py` ignores tables it doesn't own, so autogenerate never tries to drop ADK or mem0 tables.

### Memory (mem0), configured explicitly

| Part | Choice |
| --- | --- |
| Framework | mem0 open source, in-process |
| Vector store | Postgres + pgvector (`mem0_memories`) |
| Embeddings | Ollama `nomic-embed-text`, 768 dims (local, open source) |
| Fact extraction LLM | `MEMORY_LLM_MODEL`, default `openai/gpt-6-luna` |
| History | SQLite file in `localdev/data/mem0/` |
| Retrieval | Semantic search first; reranking later |
| Isolation | Every call scoped by `user_id` |

mem0's defaults are OpenAI models and a 1536-dim vector store, so every part is set in config. Keep the embedder fixed while memory evals are built.

### Models

**Default: OpenAI's smallest, cheapest model, `openai/gpt-6-luna`, for everything** (chat agent, mem0 fact extraction, eval judge). One `OPENAI_API_KEY` runs the project. This is a learning project that may later become a personal tool, so cost stays minimal by default.

| Setting | Default | Used by |
| --- | --- | --- |
| `CHAT_MODEL` | `openai/gpt-6-luna` | ADK chat agent (`LiteLlm(model=settings.chat_model)`) |
| `MEMORY_LLM_MODEL` | `openai/gpt-6-luna` | mem0 (split into provider + model) |
| `EVAL_JUDGE_MODEL` | `openai/gpt-6-luna` | LLM-as-judge graders |

**Provision for other and frontier models.** Every model goes through LiteLLM's `provider/model` format, so switching is a `.env` change plus that provider's key; no code changes.

| Provider | Cheap | Frontier | Key |
| --- | --- | --- | --- |
| OpenAI (default) | `openai/gpt-6-luna`, `openai/gpt-6.1-terra` | `openai/gpt-6.2-sol` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-haiku-5-5` | `anthropic/claude-sonnet-5-5`, `anthropic/claude-opus-5-5` | `ANTHROPIC_API_KEY` |
| Google | `gemini/gemini-3.1-flash-lite` | `gemini/gemini-3.5-flash` | `GEMINI_API_KEY` |
| OpenAI-compatible (DeepSeek, Groq, NVIDIA ...) | any LiteLLM-supported id | | that provider's key |

Rules:
- Committed defaults (`.env.example`, CI) stay on the cheapest model. A bigger model is tried locally by changing `.env`, and kept only if `just eval` shows a clear gain worth its price.
- Compare models on the same eval datasets and baseline. Write the result as an ADR in [decisions/](decisions/) if the default ever changes.
- Set a monthly spending limit in the OpenAI dashboard.
- Model ids and prices change often; check the provider's pricing page before switching.

`config.py` is the only place that knows model ids and providers. This keeps prompts, tools and eval cases portable for Project 2 (direct Claude/OpenAI APIs).

### Security boundaries

- All local service ports bind to `127.0.0.1`.
- The agent cannot execute generated code on the host. Code execution waits for a real sandbox.
- Tool output is untrusted input. Every tool gets prompt-injection cases in `security.jsonl`.

---

## Milestones (Project 1)

Each milestone is a working vertical slice: it runs end to end, shows up in Phoenix, and has eval cases. Weeks are approximate.

| # | Milestone | Build | Learn | Done when |
| --- | --- | --- | --- | --- |
| 0 | Bootstrap (wk 1) | Repo, uv, Vite, compose, CI green, then protect main | Tooling, dependency management, CI | `just up` healthy; CI green on main; ruleset active |
| 1 | Hello agent (wk 1–2) | ADK agent on `openai/gpt-6-luna` via LiteLLM, Phoenix tracing, 10-case chat eval set | Messages, prompts, tokens, traces | **Question → answer → trace in Phoenix → eval score.** Evals run 3×; baseline saved |
| 2 | Chat app (wk 3) | FastAPI SSE endpoint + React streaming UI, Stop | HTTP streaming, cancellation, frontend state | Full streaming conversation in the browser; time-to-first-token in traces |
| 3 | Sessions (wk 4) | ADK `DatabaseSessionService` on Postgres; session list, resume; first SQLModel tables (feedback) | Context window, history, session lifecycle | Conversations survive restarts; context-carryover evals ≥ 90% |
| 4 | Tools (wk 5) | SearXNG search tool + 2 simple tools; tool-call cards in UI | Tool schemas, function calling, agent loop | Correct tool on ≥ 90% of 20 cases; injection cases for search pass 100% |
| 5 | Memory (wk 6–7) | mem0 + pgvector + Ollama embeddings; memory view/edit/delete | Embeddings, extraction, retrieval, memory lifecycle | Recall ≥ 80% on 30 planted facts; outdated, wrong and deleted memory cases pass |
| 6 | Research + MCP (wk 8–9) | Orchestrator + parallel searchers + writer; `MCPToolset` with 2–3 servers | Delegation, parallelism, tool protocols | Cited answers on 10 questions, ≥ 85% of claims supported |
| 7 | Evaluate and improve (wk 10) | Larger datasets, error analysis, prompt and retrieval iterations | Failure analysis, improvement loops | Measured gain on ≥ 2 datasets vs baseline, no regressions; write-up in [docs/](./) |

### Not yet

| Component | Add when |
| --- | --- |
| Complex agent graphs | Simple research workflows become limiting |
| Another vector database | pgvector shows a measured limitation |
| Caching layer | Measurements justify it |
| Reranking | Basic memory retrieval has been evaluated |
| Code execution | A sandbox exists (no network, limits, timeout, read-only FS) |
| Self-modifying agents | Reliable evals and rollback exist |
| Automatic prompt optimization (DSPy) | Eval datasets are stable |
| Multi-model routing | Basic cost and latency metrics work |

---

## Evaluation

### Tests vs evals

| | `backend/tests/` | `backend/evals/` |
| --- | --- | --- |
| Model calls | Mocked | Real |
| Result | Pass / fail | Mean score over 3 runs |
| Rule | Must pass 100% | No drop beyond tolerance vs `baseline.json`; security cases must pass 100% |
| Run | `just test` | `just eval` |

### Method

1. Each new capability adds unit tests **and** eval cases, including failure cases.
2. Each dataset runs 3 times; the mean is compared with `baseline.json`. A drop larger than the dataset's tolerance (default 5 percentage points) is a regression.
3. `security.jsonl` (prompt injection, unsafe tool arguments, permission boundaries) is must-pass.
4. Failing traces are opened in Phoenix, tagged by failure type, and the biggest bucket is fixed first.
5. The baseline is updated only with `just eval-baseline`, in a PR that says why.

### Metrics (added as features arrive)

Task success · tool selection accuracy · tool execution success · memory recall · context relevance · groundedness · latency (TTFT, p95) · tokens · cost per task.

---

## Getting started

### Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 22+ and npm
- Docker + Docker Compose
- [just](https://github.com/casey/just) and the GitHub CLI (`gh`)
- An OpenAI API key (Claude/Gemini keys only if you switch models)

### Order of work

| Step | What | Section |
| --- | --- | --- |
| 1 | Create repo, scaffold backend and frontend, add files, create `.env` | Bootstrap 1–3 |
| 2 | Install dependencies, set up Alembic | Bootstrap 4 |
| 3 | Start infra, pull embedding model | `just up`, `just models` |
| 4 | First commit to main, push, get CI green | Git setup below |
| 5 | Protect main | `just protect-main` |
| 6 | Milestone 1 on a branch: hello agent + Phoenix + evals | `just adk` |
| 7 | Milestone 2: full app | `just dev` |

Run modes, service URLs and the full command list are in [README.md](../README.md#quick-start).

---

## Git workflow

Solo GitHub flow: `main` is always deployable; every change goes through a short-lived branch and a PR.

### First-time setup (in this order)

1. Create the GitHub repo and push the bootstrap commit straight to `main`.
2. Fix CI until all four checks are green on `main` (add one simple test on each side).
3. Run `just protect-main`. From now on, nothing goes to `main` without a PR.

Rulesets are free on public repos; private repos need a paid GitHub plan.

### Daily flow

See [README.md](../README.md#git-flow) (`just branch` → `just draft` → `just check`/`just push` → `just ready` → `just sync`). Pull requests open as drafts with the first commit.

### main protection (`.github/rulesets/main.json`)

| Rule | Setting |
| --- | --- |
| Pull request required | Yes, 0 approvals (GitHub never lets you approve your own PR) |
| Required checks | `backend`, `integration`, `frontend`, `docker`; branch must be up to date |
| Merge method | Squash only, branch auto-deleted |
| Force push / deletion | Blocked |
| Linear history | Required |

### Pipelines

```
feature branch → PR → CI (backend, integration, frontend, docker) → squash-merge
→ CI on main → publish images to GHCR (only if all checks pass) → deploy (later)
```

| Workflow | Trigger | What it does |
| --- | --- | --- |
| CI | Every PR, push to main | See the check list below. On main only, after all pass: push `ghcr.io/<owner>/shuhari-backend` and `shuhari-frontend` (`latest` + short SHA) |
| Evals | Manual, Mondays 09:00 IST | Real-model evals, 3 repeats, vs baseline; results as artifact. Needs secret `OPENAI_API_KEY`. Optional repo variables `CHAT_MODEL`, `MEMORY_LLM_MODEL`, `EVAL_JUDGE_MODEL` override the cheap default (plus that provider's key as a secret) |

**CI checks (each must pass before a PR can merge)**

| Job | Checks |
| --- | --- |
| `backend` | ruff lint · ruff format · mypy types · pytest unit tests |
| `integration` | migrations apply on empty Postgres · `alembic check` (models and migrations in sync) · pytest integration tests |
| `frontend` | eslint · prettier format · tsc types · vitest unit tests · production build |
| `docker` | backend and frontend images build |

`just check` runs the lint, format, type and unit-test checks locally; `just check-all` runs everything above.

**No second reviewer needed.** The ruleset requires a PR and green checks, with 0 approvals, so you open, check and merge your own PRs (`just merge` merges automatically once CI is green). Dependabot PRs go through the same checks.

---

## How we work

1. Build the current milestone only, as a working vertical slice.
2. Write the eval cases for a feature first, then build it.
3. One feature or fix per branch, merged by PR.
4. Done means: `just check` passes, unit tests and eval cases are added, `just eval` shows no regression and security cases pass, new code shows up as traces in Phoenix.
5. When a convention changes, update the relevant AGENTS.md ([root](../AGENTS.md), [backend](../backend/AGENTS.md), [frontend](../frontend/AGENTS.md)) in the same commit.

---

## Bootstrap: create everything

Run these steps in order. Scaffolding comes first so the generators run in empty folders, then the files below are added on top.

### 1. Repo and folders

````bash
mkdir shuhari-chatbot-v1 && cd shuhari-chatbot-v1
git init -b main
mkdir -p docs/decisions localdev infra/searxng .github/workflows .github/rulesets
touch docs/decisions/.gitkeep
# save this blueprint as docs/blueprint.md
````

### 2. Scaffold backend and frontend

````bash
# backend: creates backend/pyproject.toml and backend/src/shuhari/__init__.py
uv init backend --package --name shuhari --python 3.12 --vcs none
mkdir -p backend/src/shuhari/{agents/chatbot,tools,sessions,db,api/routes,observability} \
         backend/tests/{unit,integration} backend/evals/{datasets,graders}
touch backend/evals/datasets/.gitkeep backend/evals/graders/.gitkeep

# frontend: Vite creates the folder itself, so it must not exist yet
npm create vite@latest frontend -- --template react-ts
(cd frontend && npm install)
````

### 3. Add the files

Create each file at its path. Take only what is inside the outer four-backtick fence (some files contain their own code blocks).

#### `README.md`

Short overview for daily use.

Source of truth: [`README.md`](../README.md). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `AGENTS.md`

Repo-wide instructions for coding agents. Start with the minimal version from the first setup and grow toward this one as milestones add real conventions.

Source of truth: [`AGENTS.md`](../AGENTS.md). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `backend/AGENTS.md`

Backend instructions: config, DB ownership, mem0, evals, security.

Source of truth: [`backend/AGENTS.md`](../backend/AGENTS.md). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `frontend/AGENTS.md`

Frontend instructions.

Source of truth: [`frontend/AGENTS.md`](../frontend/AGENTS.md). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `justfile`

All commands.

Source of truth: [`justfile`](../justfile). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `compose.yaml`

Local services (127.0.0.1 only).

Source of truth: [`compose.yaml`](../compose.yaml). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.env.example`

Environment template (copy to .env).

Source of truth: [`.env.example`](../.env.example). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.gitignore`

Source of truth: [`.gitignore`](../.gitignore). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `infra/searxng/settings.yml`

SearXNG with JSON output. Change `secret_key`.

````yaml
use_default_settings: true

server:
  secret_key: "change-me-in-localdev"   # any random string
  limiter: false

search:
  formats:
    - html
    - json   # needed for the agent's search tool
````

#### `backend/Dockerfile`

Source of truth: [`backend/Dockerfile`](../backend/Dockerfile). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `backend/.dockerignore`

Source of truth: [`backend/.dockerignore`](../backend/.dockerignore). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `frontend/Dockerfile`

Source of truth: [`frontend/Dockerfile`](../frontend/Dockerfile). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `frontend/nginx.conf`

SPA routing + /api proxy (SSE/WebSocket safe).

Source of truth: [`frontend/nginx.conf`](../frontend/nginx.conf). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `frontend/.dockerignore`

Source of truth: [`frontend/.dockerignore`](../frontend/.dockerignore). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.github/workflows/` — one workflow per failing thing

Split per area on 2026-11-26 so a red check names its own half of the repo; see
[ADR 0004 → Revision: workflow split](decisions/0004-verification-layers.md). A required
status check matches the **job** name, not the workflow name, so renaming a job
un-protects `main`.

| Workflow | Jobs | Required on `main`? |
| --- | --- | --- |
| [`backend.yml`](../.github/workflows/backend.yml) | `backend`, `integration` | `backend` yes; `integration` at C5 |
| [`frontend.yml`](../.github/workflows/frontend.yml) | `frontend` | yes |
| [`images.yml`](../.github/workflows/images.yml) | `docker`, `publish` | `docker` yes; `publish` runs on `main` only |
| [`pr.yml`](../.github/workflows/pr.yml) | `label` | no — hygiene |
| [`codeql.yml`](../.github/workflows/codeql.yml) | `analyze` (python, js-ts) | no — 1-3 min against a ~30s gating budget |

Every job writes the exact local command that reproduces a failure to the run summary.

#### `.github/workflows/evals.yml`

Evals: manual + weekly, 3 repeats vs baseline.

Source of truth: [`.github/workflows/evals.yml`](../.github/workflows/evals.yml). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.github/dependabot.yml`

Monthly grouped updates.

Source of truth: [`.github/dependabot.yml`](../.github/dependabot.yml). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.github/pull_request_template.md`

Source of truth: [`.github/pull_request_template.md`](../.github/pull_request_template.md). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

#### `.github/rulesets/main.json`

main branch protection (apply after CI is green).

Source of truth: [`.github/rulesets/main.json`](../.github/rulesets/main.json). No copy is kept here — see
[One source of truth](#one-source-of-truth) above.

Create `.env` now: config, Alembic and Compose all read it from step 4 on.

````bash
cp .env.example .env              # add OPENAI_API_KEY
````

Then point Claude Code at each AGENTS.md (one source of truth). Each `CLAUDE.md` is a single import line, which works on every OS; Claude Code's edit tools won't write through symlinks, so imports are used instead:

````bash
for d in . backend frontend; do echo "@AGENTS.md" > "$d/CLAUDE.md"; done
````

### 4. Dependencies and tooling

````bash
cd backend
uv add "google-adk[db]" litellm asyncpg sqlmodel alembic \
       fastapi "uvicorn[standard]" pydantic-settings httpx \
       mem0ai ollama arize-phoenix-otel openinference-instrumentation-google-adk
uv add --dev ruff mypy pytest pytest-asyncio
cd ..

cd frontend
npm install -D tailwindcss @tailwindcss/vite vitest prettier
cd ..
````

Then edit by hand:

| File | Change |
| --- | --- |
| `backend/pyproject.toml` | Pin `google-adk` and `mem0ai` with `~=` to the installed minor version. Add `[tool.ruff.lint]` selecting `E,F,I,UP,B,S` (`S` is flake8-bandit, which is why we install no separate `bandit`) with `S101` ignored under `tests/` and `evals/`, and `extend-exclude = ["*.md"]` so ruff does not reformat Python blocks inside docs. Add `[tool.mypy]` with `strict = true` and `ignore_missing_imports = true` — ADK, mem0 and Phoenix ship few stubs, so without it `mypy src` fails on imports alone. Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]`, `markers = ["integration: needs Postgres"]`, `asyncio_mode = "auto"` and an explicit `asyncio_default_fixture_loop_scope` |
| `frontend/package.json` | Add script `"test": "vitest"` |
| `frontend/vite.config.ts` | Add the Tailwind plugin and `server.proxy: { "/api": "http://localhost:8000" }` |

**Alembic is deliberately not part of this step.** Its `env.py` has to import
`shuhari.db.base` and `settings.database_url`, and neither exists until `core/config.py`
(milestone 1a) and `db/base.py` (milestone 1c) are written — so `alembic init` here would
produce a file that cannot be imported. Alembic is tracker step **4c**, after 1a:

````bash
cd backend
uv run alembic init -t async alembic
````

| File | Change |
| --- | --- |
| `backend/alembic/env.py` | `target_metadata` from `shuhari.db.base`, import `shuhari.models`, URL from `settings.database_url`, add the `include_object` filter from `backend/AGENTS.md` |
| `backend/alembic/script.py.mako` | Add `import sqlmodel` |

Then the first migration, which only enables pgvector:

````bash
just up
just migration "enable pgvector"
# in the generated file: op.execute("CREATE EXTENSION IF NOT EXISTS vector") in upgrade()
just db-upgrade
````

Each of 4a, 4b and 4c turns exactly one CI check green — `backend`, `frontend` and
`integration` respectively — which is what the staged required-checks rollout (C3-C5)
assumes.

### 5. Models, checks, first commit, CI, protection

````bash
just up && just models            # Postgres, Phoenix, SearXNG, Ollama + embedding model
just setup && just check-all      # must pass before the first push
git add -A && git commit -m "chore: bootstrap repo"
gh repo create shuhari-chatbot-v1 --source . --push --private   # or --public (free rulesets)
# wait for CI to be green on main, then:
just protect-main
just branch feat/hello-agent      # milestone 1 starts here
````

CI needs at least one test in each place it runs pytest/vitest, because both fail when they find no tests:

| Where | Minimal first test |
| --- | --- |
| `backend/tests/unit/` | **Done** — `test_package_structure.py` (22 cases) in bootstrap 4a. Settings tests follow in milestone 1a, against the **one** async DB URL of [ADR 0002](decisions/0002-one-database-url.md), not three |
| `backend/tests/integration/` | Connect to Postgres and confirm the `vector` extension exists — bootstrap 4c |
| `frontend/tests/unit/` | **Done** — `naming-conventions.test.ts` (4 cases) in bootstrap 4b |