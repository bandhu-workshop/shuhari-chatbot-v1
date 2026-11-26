# shuhari-chatbot-v1

> **Last updated:** 2026-11-26 13:44 IST

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
- File and folder naming: see [Naming](#naming) below.
- ADRs in `docs/decisions/NNNN-slug.md`, numbered in decision order.
- `docs/` is tracked and reviewed. `localdev/` is gitignored scratch space.

## Documentation map

Which document answers which question. **Check here before writing a new doc** — almost
always the answer belongs in one of these, not in a new file.

| Question | Document |
| --- | --- |
| Where are we? What's next? | [`docs/tracker.md`](docs/tracker.md) |
| What talks to what? | [`docs/architecture.md`](docs/architecture.md) |
| Why was this decided? | [`docs/decisions/NNNN-*.md`](docs/decisions/) — **ADRs override the blueprint** |
| What was originally specified? | [`docs/blueprint.md`](docs/blueprint.md) |
| How do branches, PRs and protection work? | [`docs/github-workflow/repo-branch-protection.md`](docs/github-workflow/repo-branch-protection.md) |
| Where is Project 2 going? | [`docs/roadmap.md`](docs/roadmap.md) |
| How do I run it? What commands exist? | [`README.md`](README.md), `just --list` |
| Backend rules: layers, DB ownership, portability | [`backend/AGENTS.md`](backend/AGENTS.md) |
| Frontend rules: naming, conventions | [`frontend/AGENTS.md`](frontend/AGENTS.md) |
| Working notes on a feature in progress | `localdev/features/{backend,frontend,mix}/` (untracked) |

**Where a new fact goes:**

- a decision with alternatives considered → an ADR, numbered next
- a rule an agent must follow → the nearest `AGENTS.md`
- a change in status → `docs/tracker.md`, in the same PR as the change
- thinking in progress → the feature folder in `localdev/features/`
- how two pieces connect → `docs/architecture.md`

## Documentation audit

`just docs-audit` (part of `just check`) checks mechanically that every tracked Markdown
doc carries a `Last updated` stamp, that no stamp is in the future, and that every
relative link resolves. Links inside fenced code blocks are ignored, because
`docs/blueprint.md` embeds whole copies of other files.

It cannot check meaning. Those stay human:

- does any doc contradict an ADR? ADRs win — fix the doc.
- does the tracker match reality?
- are the `Last updated` stamps actually current, or just present?

## Naming

Lowercase everywhere. The date prefix applies to **dated working documents** only —
things that are a snapshot of one moment. It deliberately does not apply to code, to
tool-fixed filenames, or to living documents.

| Kind | Convention | Example |
| --- | --- | --- |
| Dated working documents — feature notes, debug notes, planning docs | `YYYY-MM-DD_name-in-kebab-case` | `2026-11-26_hello-agent/`, `2026-11-26_sse-reconnect.md` |
| Living documents — revised continuously, never a snapshot | `kebab-case.md`, **no date** | `blueprint.md`, `tracker.md`, `repo-branch-protection.md` |
| ADRs | `NNNN-kebab-case.md`, numbered by decision order | `0002-one-database-url.md` |
| Python modules and packages | `snake_case`, ruff/PEP 8 | `core/config.py`, `ai/observability/tracing.py` |
| Frontend files | `kebab-case.tsx` / `.ts` | `message-list.tsx`, `use-chat.ts` |
| Tool-fixed names | exactly what the tool requires | `pyproject.toml`, `Dockerfile`, `justfile`, `__init__.py`, `AGENTS.md` |

Why the date prefix is scoped this way:

- A date prefix on a living document claims it is a snapshot of that day, and is wrong by
  the next edit. Sequence for those comes from the `Last updated` stamp and git history.
- Python cannot import a module whose name starts with a digit or contains a hyphen, so
  `2026-11-26-config.py` is unusable.
- ADRs are ordered by *decision*, not by calendar. `0001` before `0002` is the point.
- The underscore after the date marks where the date ends, so the boundary stays visible.
  Matches the global convention in `~/.claude/CLAUDE.md`.

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