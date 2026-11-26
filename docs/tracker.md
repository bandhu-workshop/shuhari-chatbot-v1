# Project tracker — big picture

> **Last updated:** 2026-11-26 16:02 IST

The single place that answers "where are we and what's next". Update it whenever a
step, milestone or track row changes state — in the same PR that caused the change.

Feature-level working notes live in `localdev/features/` (untracked); see
[localdev/features/README.md](../localdev/features/README.md).

Status legend: `done` · `in progress` · `next` · `blocked` · `todo` · `n/a yet`

---

## Where we are right now

**Bootstrap, step 4.** The repo is on GitHub, `main` is protected, the layered package
skeleton is in place and all 19 layer packages import. Step 4a has landed: 142 packages
resolved with no conflicts, ruff/mypy/pytest configured, and 22 unit tests passing.

CI: `backend`, `docker` and `frontend` green. `integration` red (no Alembic yet — step
4c, which has to wait for `core/config.py`).

`backend`, `docker` and `frontend` are now **required** checks on `main`, strict policy.
`integration` is not, because it cannot pass until 4c.

**Immediate next action:** milestone 1a — `core/config.py`. It unblocks 4c (Alembic), which
turns `integration` green and completes the required-checks rollout at C5.

---

## Bootstrap (blueprint "Bootstrap")

| Step | What | Status | Notes |
| --- | --- | --- | --- |
| 1 | Repo and folders | **done** | 2026-11-26 |
| 2 | Scaffold backend (uv) and frontend (Vite react-ts) | **done** | 2026-11-26. Vite 9 shipped oxlint; kept, see decisions log |
| 3 | Add the specified files, create `.env` | **done** | 2026-11-26. Root `README.md`/`AGENTS.md` kept; `infra/searxng/settings.yml` deferred to milestone 4 |
| 3b | GitHub remote, merge settings, protect `main` | **done** | 2026-11-26. Ruleset active without CI checks; see CI/CD track |
| 3c | Backend layered structure refactor | **done** | 2026-11-26. Adapted from creditforge; see backend/AGENTS.md → Layout |
| 4a | Backend dependencies, ruff/mypy/pytest config, first test | **done** | 2026-11-26. Turned `backend` green. No resolver conflicts. Alembic deliberately deferred to 4c — see below |
| 4b | Frontend dev deps (tailwind, vitest, prettier), format the scaffold, `.prettierignore`, first vitest test | **done** | 2026-11-26. Turned `frontend` green. Also fixed a vacuous type check (`tsc --noEmit` checks nothing with project references), the stale `Lint (eslint)` label, and aligned CI Node to 26 to match the Docker image |
| 4c | `db/base.py`, `alembic init -t async`, `env.py` wiring, migration 0001 (`CREATE EXTENSION vector`), first integration test | todo | **Blocked on 1a.** `env.py` imports `shuhari.db.base` and `settings.database_url`, so it cannot be written before `core/config.py` exists. Turns `integration` green |
| 5 | `just check-all` green, then tighten the ruleset (C3–C5) | todo | Each of 4a/4b/4c turns exactly one check green |

---

## Milestones (Project 1)

| # | Milestone | Status | Done when |
| --- | --- | --- | --- |
| 0 | Bootstrap | **in progress** | `just up` healthy; CI green on main; ruleset active |
| 1 | Hello agent | todo | Question → answer → trace in Phoenix → eval score; evals run 3×, baseline saved |
| 2 | Chat app (SSE + React) | todo | Full streaming conversation in the browser; time-to-first-token in traces |
| 3 | Sessions | todo | Conversations survive restarts; context-carryover evals ≥ 90% |
| 4 | Tools (SearXNG + 2) | todo | Correct tool on ≥ 90% of 20 cases; injection cases pass 100% |
| 5 | Memory (mem0 + pgvector) | todo | Recall ≥ 80% on 30 planted facts; outdated/wrong/deleted cases pass |
| 6 | Research + MCP | todo | Cited answers on 10 questions, ≥ 85% of claims supported |
| 7 | Evaluate and improve | todo | Measured gain on ≥ 2 datasets vs baseline, no regressions |

---

## Milestone 1 — "Hello agent", broken into features

One PR per row, in this order. All backend; no frontend work in milestone 1 at all.
Each gets a folder under `localdev/features/backend/YYYY-MM-DD_<name>/`.

| # | Feature | What lands | Tracker rows | Depends on |
| --- | --- | --- | --- | --- |
| 1a | **config** | `core/config.py`: `POSTGRES_*` → one `database_url`, model ids, service URLs, `DATABASE_URL` override, `.env` optional. Unit tests. | B2, deployment P0 | step 4a |
| 1b | **logging** | `core/logging.py`: JSON to stdout, `session_id`/`user_id` in context. Unit tests. | B2, O2 | 1a |
| 1c | **app skeleton** | `main.py` `create_app()`, `core/exceptions.py`, `api/health.py` (`/healthz`, `/readyz`), `api/deps.py` (`DbSession` + `get_current_user()`), `db/base.py`, `db/session.py`, SIGTERM lifespan. Unit tests. | B3, B4, A1, A2 | 1a, 1b |
| 1d | **the agent** | `ai/agents/chatbot/agent.py` exporting `root_agent` via `LiteLlm(settings.chat_model)`, `ai/prompts/chatbot.md`. Runnable with `just adk`. | milestone 1 core | 1a |
| 1e | **tracing** | `ai/observability/tracing.py`: OTEL + OpenInference → Phoenix, no-op when `PHOENIX_COLLECTOR_ENDPOINT` unset. | O1 | 1d |
| 1f | **evals** | `ai/evaluation/` scoring + graders, `evals/datasets/chat.jsonl` (10 cases), `evals/run.py`, `baseline.json`. Runs 3×. | E1 | 1d, 1e |

Milestone 1 is done when a question produces an answer, a trace appears in Phoenix, and
`just eval chat` scores it against a saved baseline.

Note `db/` lands in 1c only because `/readyz` checks the database. No tables exist until
milestone 3 — the first migration (`CREATE EXTENSION vector`) comes in step 4a.

---

## Cross-cutting tracks

These cut across milestones. Each row is a step, in order.

### Authentication (identity: *who is this*)

| Step | What | When | Status |
| --- | --- | --- | --- |
| A1 | `get_current_user()` in `api/deps.py`, returning a hardcoded dev user | Milestone 1 | **next** |
| A2 | Every route and mem0 call takes `user_id` from A1, never a literal or query param | Milestone 1+ | todo |
| A3 | Real identity provider (Firebase Auth or IAP) behind the same dependency | Deployment phase 3 | todo |
| A4 | Token verification + session cookie handling in `lib/api.ts` | Deployment phase 3 | todo |

**Scope decided 2026-11-26: the seam only.** A1 and A2 land in milestone 1c; A3 and A4
stay at deployment phase 3. Until there is a deployment there is no second user and no
attacker, so building real identity now would mean building a token service in order to
have something to test. The token-level checks that go with it — `alg: none`, refresh
rotation, token-family revocation, issuer/audience, login rate limiting — are therefore
explicitly out of scope; see [decisions/0004-verification-layers.md](decisions/0004-verification-layers.md).

Why A1 first anyway: retrofitting identity touches every route, every test and every memory
record. See `backend/AGENTS.md` → Portability.

### Authorization (permissions: *what may they do*)

| Step | What | When | Status |
| --- | --- | --- | --- |
| Z1 | All session and memory queries filtered by `user_id` | Milestone 3 / 5 | todo |
| Z2 | Tools that change state get an explicit allow-list | Milestone 4 | todo |
| Z3 | User approval step for state-changing tools | After milestone 4 | todo |
| Z4 | Verify cross-user isolation with a test that tries to read another user's data | Milestone 5 | todo |

### Database and migrations (step-wise)

One Postgres, three schema owners — ours (Alembic), ADK's (itself), mem0's (itself).
Never manage another owner's tables.

| Rev | What it does | Milestone | Status |
| --- | --- | --- | --- |
| — | `alembic init -t async` + `env.py` filter, `script.py.mako` imports sqlmodel | Bootstrap 4 | **next** |
| 0001 | `CREATE EXTENSION IF NOT EXISTS vector` | Bootstrap 4 | todo |
| 0002 | `feedback` table (first SQLModel table in `models/`, registered in `db/base.py`) | Milestone 3 | todo |
| — | ADK session/event/state tables | Milestone 3 | todo — created by ADK, not Alembic |
| — | `mem0_memories` vector collection | Milestone 5 | todo — created by mem0, not Alembic |

Flow: edit a table in `models/` (register it in `db/base.py`) → `just migration "msg"` → **read the generated file** →
`just db-upgrade` → commit both. CI runs `alembic check`.

### Observability

| Step | What | When | Status |
| --- | --- | --- | --- |
| O1 | `ai/observability/tracing.py`: OTEL + OpenInference → Phoenix, no-op when endpoint unset | Milestone 1 | todo |
| O2 | `core/logging.py`: JSON logs to stdout, with `session_id` / `user_id` in context | Milestone 1 | todo |
| O3 | Time-to-first-token visible in traces | Milestone 2 | todo |
| O4 | Swap the OTEL exporter to Cloud Trace in production | Deployment phase 3 | todo |

### Evaluation

| Step | What | When | Status |
| --- | --- | --- | --- |
| E1 | `evals/run.py` + `ai/evaluation/` scoring + 10-case chat dataset + `baseline.json` | Milestone 1 | todo |
| E2 | Tool-selection + injection datasets | Milestone 4 | todo |
| E3 | Memory datasets (recall, outdated, wrong, deleted) | Milestone 5 | todo |
| E4 | Citation-support dataset | Milestone 6 | todo |
| E5 | Error analysis and a measured improvement vs baseline | Milestone 7 | todo |

### Security

| Step | What | When | Status |
| --- | --- | --- | --- |
| S1 | No code execution on the host; no `UnsafeLocalCodeExecutor` | always | **done** (rule) |
| S2 | Tool output treated as untrusted; injection case per new tool | Milestone 4+ | todo |
| S3 | `security.jsonl` must-pass at 100% | Milestone 4 | todo |
| S4 | Secrets from Secret Manager, not `.env` | Deployment phase 3 | todo |

### Verification

Which tools we use to check our own work, and in what order. The *skipped* tools and the
reasoning live in [decisions/0004-verification-layers.md](decisions/0004-verification-layers.md)
— read it before adding anything to this list.

| Step | What | When | Status |
| --- | --- | --- | --- |
| V1 | Ruff `S` rules (flake8-bandit) enabled in `pyproject.toml` — replaces `bandit` | Bootstrap 4a | **done** | 
| V2 | Confirm GitHub secret scanning + push protection are on (free, public repo) — replaces `gitleaks`. Dependabot already configured | Bootstrap 4a | todo |
| V3 | The three auth tests: route-has-identity-dependency, cross-user isolation, no mass assignment | Milestone 1c, extended at 3 and 5 | todo — rows Z1, Z4 |
| V4 | Schemathesis against our own `openapi.json` | Milestone 2 | todo |
| V5 | Locust: one scenario, 50 users, p95/p99 recorded | After milestone 2 | todo — target per [ADR 0003](decisions/0003-capacity-target.md) |
| V6 | One mitmproxy session to verify cookie flags and that no token leaks into a URL or log | When cookies first ship (phase 3) | todo |
| V7 | OWASP ZAP API scan | Deployment phase 3 | todo — meaningless until publicly reachable |

`just check` already runs the mechanical half (docs audit, lint, unit tests). `/security-review`
runs on every auth diff at no setup cost.

### CI/CD

| Step | What | When | Status |
| --- | --- | --- | --- |
| C1 | `ci.yml` with backend / integration / frontend / docker + publish | Bootstrap 3 | **done** |
| C2 | Ruleset on `main` — PR required, squash only, linear, no force-push | Bootstrap 3b | **done** |
| C3 | Add `backend` + `docker` to required checks | Bootstrap 4a | **done** | 
| C8 | `uv lock --check` in the `backend` job — `--frozen` alone misses a drifted `pyproject.toml` | Bootstrap 4 | **done** |
| C4 | Add `frontend` to required checks | Bootstrap 4b | **done** — strict policy on, so branches must be up to date | 
| C5 | Add `integration` to required checks | After 4c | todo — the last one; then all four are required and strict |
| C6 | Images published to GHCR on main | Bootstrap 5 | todo — job exists, gated on the four checks |
| C7 | Deploy job | Deployment phase 3 | todo — placeholder comment in `ci.yml` |

Each check is added to `.github/rulesets/main.json` in the PR that makes it pass, then
`just protect-main` re-applied. See
[github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md).

### Deployment (GCP / Cloud Run)

Governed by [decisions/0001-deployment-strategy.md](decisions/0001-deployment-strategy.md).

| Phase | What | Status |
| --- | --- | --- |
| 0 | Portability rules adopted while building milestones 1–3 | **in progress** |
| 1 | Throwaway spike: hello-agent → Cloud Run + Cloud SQL, then delete | todo — after milestone 1 |
| 2 | Pure local development, milestones 2–7 | todo |
| 3 | Terraform + Workload Identity Federation + real deploy + cloud observability | todo — after milestone 7 |

### Backend structure

| Step | What | When | Status |
| --- | --- | --- | --- |
| B1 | Layered skeleton: `core`/`api`/`db`/`models`/`schemas`/`ai` | Bootstrap 3c | **done** |
| B2 | `core/config.py`, `core/logging.py`, `core/exceptions.py` | Milestone 1 | todo |
| B3 | `main.py` factory + `api/health.py` + `api/deps.py` | Milestone 1 | todo |
| B4 | `db/base.py` + `db/session.py` | Milestone 1 | todo |
| B5 | `tests/unit/test_package_structure.py` enforcing the layout | Bootstrap 4a | **done** | 
| B6 | `services/` layer added when session CRUD needs a home | Milestone 3 | todo |
| B7 | Check ADK issues [#4366](https://github.com/google/adk-python/issues/4366) and [#7276](https://github.com/google/adk-python/issues/7276) (asyncpg + Postgres bugs) before wiring sessions | Milestone 3 | todo |

### Frontend

| Step | What | When | Status |
| --- | --- | --- | --- |
| F1 | Tailwind + vite proxy + `test` script | Bootstrap 4b | **done** | 
| F2 | `lib/api.ts` as the only caller of the backend; `VITE_API_BASE_URL` (`/api/v1`). Also add `@import "tailwindcss";` to `src/index.css` — deliberately omitted in 4b because Tailwind's preflight restyles the page, which belongs with the first real UI, not with a toolchain PR | Milestone 2 | todo |
| F3 | Streaming renderer, Stop button, SSE reconnect | Milestone 2 | todo |
| F4 | Sessions sidebar | Milestone 3 | todo |
| F5 | Tool-call cards | Milestone 4 | todo |
| F6 | Memory view/edit/delete | Milestone 5 | todo |
| F7 | `just types` generating `api-types.ts` from OpenAPI | Milestone 2 | todo |

---

## Open questions

| # | Question | Raised | Blocking |
| --- | --- | --- | --- |
| ~~Q1~~ | ~~oxlint or ESLint?~~ **Resolved: oxlint.** Already scaffolded and wired to `npm run lint`; no rule yet needs ESLint's ecosystem | 2026-11-26 | closed |
| Q2 | mem0 `history_db_path`: keep SQLite or move to Postgres? | 2026-11-26 | Milestone 5 |
| Q3 | Should `localdev/features/` be tracked in git instead of ignored? | 2026-11-26 | No — reversible with `git mv` |
| Q4 | Add SPDX headers + `CITATION.cff` like creditforge and shuhari-cli? | 2026-11-26 | No |
| Q5 | `docs/blueprint.md` embeds full copies of files that now exist for real (`backend/AGENTS.md` at lines 553-735, `frontend/AGENTS.md` from 736, PR template, justfile, compose.yaml...). Replace those sections with pointers so there is one source of truth? | 2026-11-26 | **Recommend yes — the copies are already unreliable.** Audited 2026-11-26: the backend copy is missing PR #13's Capacity, TDD, ruff-`S` and auth-test sections; the frontend copy still says `ESLint` (changed in PR #7) and `App.tsx` (renamed in PR #11). Six known divergences across five PRs. Syncing a line at a time is theatre while the rest rots; the audit cannot catch it because a fenced copy is sample text, not a link |

---

## Decisions log

| Date | Decision | Where |
| --- | --- | --- |
| 2026-11-26 | Local-first development; GCP in phases; portability rules now | [decisions/0001-deployment-strategy.md](decisions/0001-deployment-strategy.md) |
| 2026-11-26 | Public repo under `bandhu-workshop`, MIT, no AI authorship in commits | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
| 2026-11-26 | Ruleset (not classic protection); required CI checks added incrementally | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
| 2026-11-26 | Squash-only merges, not rebase — every commit on `main` is a CI-verified state | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
| 2026-11-26 | One async database URL; mem0 gets discrete params; `psycopg` dropped | [decisions/0002-one-database-url.md](decisions/0002-one-database-url.md) |
| 2026-11-26 | oxlint, not ESLint, for frontend linting | [../frontend/AGENTS.md](../frontend/AGENTS.md) |
| 2026-11-26 | Backend layered as `core`/`api`/`db`/`models`/`schemas`/`ai`, adapted from creditforge; evals split code-vs-data; routes versioned `/api/v1` | [../backend/AGENTS.md](../backend/AGENTS.md) → Layout |
| 2026-11-26 | Coding style: no over-engineering, never assume, TDD for deterministic code, evals for AI code, prefer a vetted well-known library, minimal diffs | [../AGENTS.md](../AGENTS.md#coding-style) |
| 2026-11-26 | Development goes through the superpowers skills — brainstorm, plan, TDD, verify, review — with output saved to the feature folder | [../AGENTS.md](../AGENTS.md#how-we-work) |
| 2026-11-26 | Capacity target 50 concurrent users; no Redis, cache, queue or worker tuning | [decisions/0003-capacity-target.md](decisions/0003-capacity-target.md) |
| 2026-11-26 | Verification: ruff `S` + Dependabot + secret scanning + three auth tests + Schemathesis + Locust. Skipped: bandit, semgrep, pip-audit, gitleaks, k6, ZAP, Burp, jwt_tool, Redis | [decisions/0004-verification-layers.md](decisions/0004-verification-layers.md) |
| 2026-11-26 | AuthN scope: the seam only (A1/A2) now; real identity (A3/A4) stays at deployment phase 3 | [decisions/0004-verification-layers.md](decisions/0004-verification-layers.md) |
