# shuhari-chatbot-v1

A Claude/ChatGPT-style chatbot agent built on Google ADK, as a learning project: every component of a modern assistant (agent loop, streaming, sessions, tools, memory, research, evals) is built in small end-to-end milestones, traced in Phoenix and measured with evals.

**Stack (open source):** Python 3.12 + uv · Google ADK (models via LiteLLM) · FastAPI · SQLModel + Alembic · React + TypeScript (Vite) · PostgreSQL + pgvector · mem0 · Ollama · Arize Phoenix · SearXNG · Docker · just · GitHub Actions

## Docs

| Doc | What's in it |
| --- | --- |
| [`docs/blueprint.md`](docs/blueprint.md) | The full spec: architecture decisions, milestones, eval method, CI/CD, and every file needed to bootstrap the repo |
| [`docs/architecture.md`](docs/architecture.md) | How the running system fits together (grows with each milestone) |
| [`docs/roadmap.md`](docs/roadmap.md) | The wider Shuhari roadmap (Project 1 ADK → Project 2 from scratch) |
| [`docs/decisions/`](docs/decisions/) | One short note per non-obvious choice |
| [`AGENTS.md`](AGENTS.md) | Rules for coding agents (`CLAUDE.md` links to it) |

## Layout

```
backend/     Python: ADK agents, FastAPI API, DB models, memory, tests, evals
frontend/    React + TypeScript chat UI
docs/        blueprint, architecture, roadmap, decisions
infra/       config for services run from official images
localdev/    gitignored: Docker volumes, scratch
.github/     CI, evals workflow, main protection, Dependabot
```

Full annotated tree: [`docs/blueprint.md`](docs/blueprint.md#folder-structure).

## Quick start

Prerequisites: Python 3.12 + uv, Node.js 22+, Docker, just, GitHub CLI, an OpenAI API key.

```bash
cp .env.example .env     # add OPENAI_API_KEY (models default to openai/gpt-6-luna)
just setup               # backend + frontend dependencies
just up && just models   # Postgres, Phoenix, SearXNG, Ollama + embedding model
just db-upgrade          # apply migrations
just adk                 # chat with the agent in the ADK dev UI
just dev                 # API :8000 + frontend :5173
```

Setting the repo up from nothing? Follow the Bootstrap section in [`docs/blueprint.md`](docs/blueprint.md#bootstrap-create-everything).

| Service | Dev URL | `just stack` URL |
| --- | --- | --- |
| Frontend | http://localhost:5173 | http://localhost:8080 |
| API (docs at /docs) | http://localhost:8000 | http://localhost:8000 |
| Phoenix (traces, evals) | http://localhost:6006 | http://localhost:6006 |
| SearXNG | http://localhost:8888 | http://localhost:8888 |
| Ollama | http://localhost:11434 | http://localhost:11434 |
| Postgres | localhost:5432 | localhost:5432 |

## Models

Default: **`openai/gpt-6-luna`**, OpenAI's smallest and cheapest model, for the chat agent, mem0 and the eval judge. One OpenAI key runs the whole project.

Any other model is a `.env` change (LiteLLM `provider/model` format) plus that provider's key. No code changes.

| Use | `.env` | Key |
| --- | --- | --- |
| Default, cheapest | `CHAT_MODEL=openai/gpt-6-luna` | `OPENAI_API_KEY` |
| OpenAI, mid / frontier | `openai/gpt-6.1-terra` / `openai/gpt-6.2-sol` | `OPENAI_API_KEY` |
| Claude | `anthropic/claude-haiku-5-5` / `anthropic/claude-sonnet-5-5` | `ANTHROPIC_API_KEY` |
| Gemini | `gemini/gemini-3.1-flash-lite` / `gemini/gemini-3.5-flash` | `GEMINI_API_KEY` |

Rules: keep the defaults on the cheapest model; try a bigger model only by changing `.env` locally and comparing `just eval` scores. Set a monthly spending limit in the OpenAI dashboard. Model ids and prices change; check the provider's pricing page before switching. Details: [`docs/blueprint.md`](docs/blueprint.md#models).

## Commands

| Command | What it does |
| --- | --- |
| `just` | List all commands |
| `just setup` | Install backend and frontend dependencies |
| `just up` / `just down` | Start infra / stop everything |
| `just models` | Pull the embedding model into Ollama (once) |
| `just dev` | API + frontend with hot reload (Ctrl+C stops both) |
| `just adk` | ADK dev UI for chatting with agents directly |
| `just api` / `just web` | Run only the API / only the frontend |
| `just stack` | Full stack in containers (prod-like) |
| `just logs [service]` | Follow container logs |
| `just test` / `just test-integration` | Unit tests / integration tests against Postgres |
| `just lint` / `just fmt` | Check / auto-format (ruff, mypy, eslint, prettier, tsc) |
| `just check` | Fast local check: lint + unit tests |
| `just check-all` | Everything CI runs |
| `just eval [dataset] [repeats]` | Run evals vs baseline, e.g. `just eval memory` |
| `just eval-baseline` | Save current scores as the new baseline |
| `just migration "msg"` | Generate a migration (review before applying) |
| `just db-upgrade` / `just db-downgrade` | Apply migrations / undo the last one |
| `just types` | Regenerate frontend API types from the backend |
| `just branch` / `pr` / `merge` / `sync` | Git flow helpers |
| `just protect-main` | One-time, after CI is green: protect main |

## Git flow

`main` is protected: changes land only through a PR with green CI. No second reviewer is needed (0 approvals).

```bash
just branch feat/session-store   # fresh branch from main
just check                       # before pushing
just pr                          # push + open PR
just merge                       # squash-merges when CI is green
just sync                        # back on updated main
```

Branch prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`. Commit messages: `feat: ...`, `fix: ...`. CI details: [`docs/blueprint.md`](docs/blueprint.md#pipelines).

## Definition of done

`just check` passes · unit tests and eval cases added · `just eval` shows no regression and security cases pass · new code visible as traces in Phoenix · AGENTS.md / docs updated if a convention changed.