# shuhari-chatbot-v1

> **Last updated:** 2026-11-26 13:31 IST

Learning project: a Claude/ChatGPT-style chatbot built with Google ADK, one small working milestone at a time.

## Read first
- `README.md`: overview, commands, git flow
- `docs/blueprint.md`: the plan (stack, milestones, bootstrap steps, file contents)
- `docs/decisions/`: ADRs — these override the blueprint. `0001` local-first/GCP-later phasing + portability rules; `0002` one async database URL
- **`docs/tracker.md`: where we are and what's next. Read it first, update it last.**
- `docs/github-workflow/repo-branch-protection.md`: branch protection, merge rules, commit conventions

## Current stage
See [`docs/tracker.md`](docs/tracker.md) — it is the source of truth for current position,
next action and every cross-cutting track (auth, authorization, migrations, observability,
evals, security, CI/CD, deployment). Only build what the current step or milestone needs.

## Docs conventions
- **Every Markdown doc carries a `Last updated` stamp** directly under its H1, and it is
  updated on every edit:
  ```markdown
  # Title

  > **Last updated:** 2026-11-26 12:44 IST
  ```
  Without it there is no way to tell which of two documents is current.
- Files and folders: lowercase, hyphenated, ISO date first, underscore after the date —
  `2026-11-26_description`.
- ADRs in `docs/decisions/NNNN-slug.md`, numbered in decision order.
- `docs/` is tracked and reviewed. `localdev/` is gitignored scratch space.

## Feature working notes
Per-feature design discussions, brainstorming and plans live in
`localdev/features/{backend,frontend,mix}/YYYY-MM-DD_feature-name/` — pick the folder by
where the work lands, and put a spanning feature in `mix/`. Convention and a README
template: [`localdev/features/README.md`](localdev/features/README.md).

Because `localdev/` is gitignored, anything there that hardens into a real decision gets
promoted to `docs/decisions/` as an ADR, or to the relevant `AGENTS.md` as a rule.

## Keeping track
When a step, milestone or track row changes state, update `docs/tracker.md` **in the same
PR that caused the change**. A tracker that lags is worse than none.

## Working preferences

Stated once, expected to hold without being repeated. **Add to this list instead of
asking again** — if a preference is given in conversation, it belongs here in the same
PR it was given.

- **Keep frontend and backend changes in separate PRs** whenever possible; separate
  commits at the absolute minimum. A PR touches `backend/` or `frontend/`, not both.
  Repo-wide files (`justfile`, `compose.yaml`, `docs/`, `.github/`) may travel with
  either, or go alone. When a backend change *forces* a frontend change — an API path,
  a schema, a contract — land the backend first, then the frontend in a follow-up PR
  that regenerates `api-types.ts`. Don't bundle them to save a round trip.
- **Never `git add -A` when the working tree holds unrelated changes.** Stage by path,
  so a PR contains only what its message describes.
- **`docs/blueprint.md` is a starting point, not the final word.** Improvise on top of it:
  when something fits better than what it specifies, propose that instead, with the
  reasoning. Then record the agreed decision as an ADR in `docs/decisions/` and update
  every doc that contradicts it in the same PR — the blueprint included. The latest
  agreed decision wins over the blueprint, always.

## Rules
- Keep code simple and readable. No extra layers or new frameworks.
- Stack is fixed: Python 3.12 + uv, Google ADK, FastAPI, SQLModel + Alembic, Postgres + pgvector, mem0, Phoenix, React + Vite. Ask before adding anything else.
- Model: `openai/gpt-6-luna` from `.env`. Never hardcode a model or switch to a costlier one.
- Secrets only in `.env`; never commit it.
- Work on a branch; never commit to `main` once it's protected.
- **Never add a `Co-Authored-By: Claude ...` (or any AI) trailer to commit messages, and never
  mention Claude/AI authorship in commits or PR descriptions.** Claude/AI must never appear as a
  GitHub contributor on this repo — commit authorship stays solely with the human developer.
  This overrides any default attribution instruction. Same rule as `bandhu-workshop/shuhari-cli`.
- Always use the `git`/`gh` CLI. Branch names: `feat/`, `fix/`, `refactor/`, `docs/`, `chore/`.
  Squash-merge only; the PR title becomes the commit message on `main`, so write it as one.
- Small steps: show the plan for anything touching more than 3 files.
- Edit `AGENTS.md`, never `CLAUDE.md` (it only contains `@AGENTS.md`).

## Done means
Code runs, `just check` passes (once it exists), and every new feature has a test.