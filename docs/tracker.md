# Project tracker — big picture

> **Last updated:** 2026-11-26 12:44 IST

The single place that answers "where are we and what's next". Update it whenever a
step, milestone or track row changes state — in the same PR that caused the change.

Feature-level working notes live in `localdev/features/` (untracked); see
[localdev/features/README.md](../localdev/features/README.md).

Status legend: `done` · `in progress` · `next` · `blocked` · `todo` · `n/a yet`

---

## Where we are right now

**Bootstrap, step 4.** The repo exists on GitHub, `main` is protected, and the
scaffolding is committed. Nothing runs yet: there is no `uv.lock`, no source beyond
the uv stub, and no tests, so all four CI checks fail.

**Immediate next action:** bootstrap step 4 — install dependencies and set up Alembic.

---

## Bootstrap (blueprint "Bootstrap")

| Step | What | Status | Notes |
| --- | --- | --- | --- |
| 1 | Repo and folders | **done** | 2026-11-26 |
| 2 | Scaffold backend (uv) and frontend (Vite react-ts) | **done** | 2026-11-26. Vite 9 shipped oxlint, not ESLint — unresolved, see Open questions |
| 3 | Add the specified files, create `.env` | **done** | 2026-11-26. Root `README.md`/`AGENTS.md` kept; `infra/searxng/settings.yml` deferred to milestone 4 |
| 3b | GitHub remote, merge settings, protect `main` | **done** | 2026-11-26. Ruleset active without CI checks; see CI/CD track |
| 4 | Dependencies + Alembic init | **next** | Creates `uv.lock`; installs prettier + vitest. Unblocks 3 of 4 CI checks |
| 5 | Models, `just check-all` green, first CI green | todo | Needs one test in each place CI runs pytest/vitest |

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

## Cross-cutting tracks

These cut across milestones. Each row is a step, in order.

### Authentication (identity: *who is this*)

| Step | What | When | Status |
| --- | --- | --- | --- |
| A1 | One `get_current_user()` FastAPI dependency returning a hardcoded dev user | Milestone 1 | **next** |
| A2 | Every route and mem0 call takes `user_id` from A1, never a literal or query param | Milestone 1+ | todo |
| A3 | Real identity provider (Firebase Auth or IAP) behind the same dependency | Deployment phase 3 | todo |
| A4 | Token verification + session cookie handling in `lib/api.ts` | Deployment phase 3 | todo |

Why A1 first: retrofitting identity touches every route, every test and every memory
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
| — | `alembic init` + `env.py` filter, `script.py.mako` imports sqlmodel | Bootstrap 4 | **next** |
| 0001 | `CREATE EXTENSION IF NOT EXISTS vector` | Bootstrap 4 | todo |
| 0002 | `feedback` table (first SQLModel table) | Milestone 3 | todo |
| — | ADK session/event/state tables | Milestone 3 | todo — created by ADK, not Alembic |
| — | `mem0_memories` vector collection | Milestone 5 | todo — created by mem0, not Alembic |

Flow: edit `db/models.py` → `just migration "msg"` → **read the generated file** →
`just db-upgrade` → commit both. CI runs `alembic check`.

### Observability

| Step | What | When | Status |
| --- | --- | --- | --- |
| O1 | `tracing.py`: OTEL + OpenInference → Phoenix, no-op when endpoint unset | Milestone 1 | todo |
| O2 | Structured JSON logs to stdout, with `session_id` / `user_id` in context | Milestone 1 | todo |
| O3 | Time-to-first-token visible in traces | Milestone 2 | todo |
| O4 | Swap the OTEL exporter to Cloud Trace in production | Deployment phase 3 | todo |

### Evaluation

| Step | What | When | Status |
| --- | --- | --- | --- |
| E1 | `evals/run.py` + 10-case chat dataset + `baseline.json` | Milestone 1 | todo |
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

### CI/CD

| Step | What | When | Status |
| --- | --- | --- | --- |
| C1 | `ci.yml` with backend / integration / frontend / docker + publish | Bootstrap 3 | **done** |
| C2 | Ruleset on `main` — PR required, squash only, linear, no force-push | Bootstrap 3b | **done** |
| C3 | Add `backend` + `docker` to required checks | Bootstrap 4 | todo |
| C4 | Add `frontend` to required checks | Bootstrap 5 | todo |
| C5 | Add `integration` to required checks | Bootstrap 5 | todo |
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

### Frontend

| Step | What | When | Status |
| --- | --- | --- | --- |
| F1 | Tailwind + vite proxy + `test` script | Bootstrap 4 | **next** |
| F2 | `lib/api.ts` as the only caller of the backend; `VITE_API_BASE_URL` | Milestone 2 | todo |
| F3 | Streaming renderer, Stop button, SSE reconnect | Milestone 2 | todo |
| F4 | Sessions sidebar | Milestone 3 | todo |
| F5 | Tool-call cards | Milestone 4 | todo |
| F6 | Memory view/edit/delete | Milestone 5 | todo |
| F7 | `just types` generating `api-types.ts` from OpenAPI | Milestone 2 | todo |

---

## Open questions

| # | Question | Raised | Blocking |
| --- | --- | --- | --- |
| Q1 | oxlint (what Vite 9 scaffolded) or ESLint (what `frontend/AGENTS.md` says)? | 2026-11-26 | Bootstrap 4 — pick before adding frontend deps |
| Q2 | mem0 `history_db_path`: keep SQLite or move to Postgres? | 2026-11-26 | Milestone 5 |
| Q3 | Should `localdev/features/` be tracked in git instead of ignored? | 2026-11-26 | No — reversible with `git mv` |

---

## Decisions log

| Date | Decision | Where |
| --- | --- | --- |
| 2026-11-26 | Local-first development; GCP in phases; portability rules now | [decisions/0001-deployment-strategy.md](decisions/0001-deployment-strategy.md) |
| 2026-11-26 | Public repo under `bandhu-workshop`, MIT, no AI authorship in commits | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
| 2026-11-26 | Ruleset (not classic protection); required CI checks added incrementally | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
| 2026-11-26 | Squash-only merges, not rebase — every commit on `main` is a CI-verified state | [github-workflow/repo-branch-protection.md](github-workflow/repo-branch-protection.md) |
