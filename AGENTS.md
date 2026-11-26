# shuhari-chatbot-v1

> **Last updated:** 2026-11-26 17:48 IST

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
  updated on every edit. `just docs-audit` enforces this mechanically: it fails when a
  doc's content changed without its stamp line changing in the same change. Bumping the
  stamp is part of editing a doc, not a step to remember afterwards.
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
| What talks to what? What state is it in? | [`docs/architecture.md`](docs/architecture.md) |
| How big must this scale? | [`docs/decisions/0003-capacity-target.md`](docs/decisions/0003-capacity-target.md) — 50 concurrent users |
| How do we check our own work? Why isn't tool X here? | [`docs/decisions/0004-verification-layers.md`](docs/decisions/0004-verification-layers.md) |
| What do the labels mean? | [`docs/github-workflow/repo-branch-protection.md`](docs/github-workflow/repo-branch-protection.md#labels) |
| How do I open a pull request? | [Pull requests](#pull-requests) below |
| How do I verify a feature in a browser? | [Browser verification](#browser-verification-playwright-mcp) below |
| What style do I write code in? | [Coding style](#coding-style) below |
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

`just docs-audit` (part of `just check`) checks four things mechanically: every tracked
Markdown doc carries a `Last updated` stamp, no stamp is in the future, every relative link
resolves, and **a doc whose content changed had its stamp changed in the same change**.

That last check is what makes the stamps mean anything — a stamp that is merely *present*
says nothing. Comparing a stamp's time against the commit's time does not work, because the
stamp is written minutes before the commit and every doc then looks stale. The exact
question is whether the same change touched both, which has no tolerance to tune.

Links inside fenced code blocks are ignored, because a link in a fence is sample text
rather than a link.

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

## Coding style

Applies to every change in this repo.

- **Don't over-engineer.** Simple, readable and reliable beats clever. No abstraction
  before the second real use.
- **Never assume.** When something is genuinely ambiguous, ask — but only what is
  necessary, and batch the questions into one round rather than a drip. Where an
  assumption is unavoidable, **state it explicitly** in the PR description and in a
  comment next to the code that depends on it.
- **TDD for deterministic code.** The failing test comes first, then the implementation.
  Cover the happy path, the edge cases and the genuinely hard cases — then stop. No test
  explosion: a test that cannot fail for a real reason is maintenance without signal.
- **Follow the patterns already here.** Read the surrounding code before adding to it.
  Consistency with this codebase outranks personal preference, and outranks what is
  idiomatic somewhere else.
- **Keep the diff minimal.** Prefer the smallest change that does the job. Not a rule to
  follow off a cliff — when the right fix is bigger, make it and say why.
- **AI code is evaluated, not unit-tested.** Prompts, instructions and agent behaviour are
  non-deterministic; they are measured by `evals/`, which is its own job. Never write
  assertions against model output. **But the deterministic parts of AI code — tools,
  parsers, scoring functions, retry and fallback logic — do get unit tests.** That is what
  makes the system reliable.
- **Prefer a well-known library to writing it yourself**, when one genuinely solves the
  problem. Vet it first: open source, not paid, actively maintained, no known
  vulnerabilities, and no more surface area than we need. A new dependency needs a reason
  in the commit message.

## How we work

Development goes through the **superpowers skills**, not ad hoc. For anything new — a
feature, a refactor, infrastructure, even a plan with no code in it — the order is:

| Stage | Skill |
| --- | --- |
| Before any design work | `superpowers:brainstorming` |
| Turning the brief into steps | `superpowers:writing-plans` |
| Implementing | `superpowers:test-driven-development`, then `executing-plans` or `subagent-driven-development` |
| Something broke | `superpowers:systematic-debugging` — before proposing a fix |
| Before claiming done | `superpowers:verification-before-completion` |
| Before merging | `superpowers:requesting-code-review`, then `receiving-code-review` |
| Finishing the branch | `superpowers:finishing-a-development-branch` |

The output of `brainstorming` and `writing-plans` is saved into the feature folder under
`localdev/features/` — that is what those folders are for. Don't leave it in the chat.

Why this is a rule and not a preference: these skills carry exactly the steps that get
skipped under momentum — writing the test first, verifying before claiming success, and
not grading your own work.

## Pull requests

**Draft first, always.** The pull request is opened with the *first* commit, not when the
work is finished.

| Step | Command |
| --- | --- |
| Branch from fresh `main` | `just branch feat/x` |
| First commit, then open the draft | `just draft` |
| Keep committing, watching CI each push | `just push` |
| Green and finished: ready + auto-merge | `just ready` |
| Back to `main` afterwards | `just sync` |

Why draft-first rather than opening when done:

- **CI runs on every push**, so a failure appears in the commit that caused it, instead of
  surfacing ten commits later with nothing to bisect.
- **A draft pull request cannot be merged** — not by hand, not by auto-merge. The draft
  state is a safety interlock, not a label.
- `backend`, `docker` and `frontend` are required checks under the **strict** policy, so a
  branch that falls behind `main` has to be updated before it merges. Pushing early
  surfaces that immediately rather than at merge time.

Rules that still apply:

- One logical change per pull request, and `backend/` or `frontend/` but not both — see
  [Working preferences](#working-preferences).
- The title becomes the squash commit message on `main`. Write it as one.
- The description says what changed, why, and **how it was verified**. Add `Closes #n`
  when an issue exists.
- Never mark a pull request ready with a red required check. Fix it, or state in the
  description why it is expected to fail.
- **Label every pull request.** `area:*` labels are applied automatically from the changed
  paths, so in practice this means the three manual ones when they apply: `run:e2e`,
  `needs:decision`, `blocked`. Scheme and reasoning:
  [`docs/github-workflow/repo-branch-protection.md`](docs/github-workflow/repo-branch-protection.md#labels).
- When a feature is finished and its tests pass, verify it in a browser before marking
  ready — see [Browser verification](#browser-verification-playwright-mcp).

Deliberately not used here: reviewers and CODEOWNERS, required approvals (0 is correct for
a solo repo), labels and milestones, stacked pull requests. Review ceremony with no second
reviewer is cost without benefit.

## Capacity target

**50 concurrent users.** Build for that and no further; see
[`docs/decisions/0003-capacity-target.md`](docs/decisions/0003-capacity-target.md), which
is mostly a list of things we are deciding *not* to build.

## Verification

How we check our own work — static checks, tests, fuzzing, load — and, just as
importantly, the tools we deliberately skip:
[`docs/decisions/0004-verification-layers.md`](docs/decisions/0004-verification-layers.md).

## Browser verification (Playwright MCP)

`.mcp.json` commits a project-scope `playwright` MCP server. It drives a real browser —
navigate, click, fill, screenshot, read console and network logs — so a feature can be
checked *running*, not merely read.

**When to use it:** when a feature is complete and its tests pass, verify it end to end
through the UI before marking the pull request ready. Also any time something needs to be
*observed* running — "the stream renders blank", "the session does not resume". Mid-feature
is fine where it helps. What it is not for is routine code changes: if nothing needs
watching in a browser, do not open one.

**How to use it:** start the app, navigate to the relevant URL, walk the path a user walks,
then cross-reference what you saw against the matching log or trace and the code that owns
that layer — so the fix lands in the right place (UI vs API vs agent vs DB).

| Resource | Where |
| --- | --- |
| Frontend code | `frontend/src/` |
| Frontend dev URL | `http://localhost:5173` — `just web`, or `just dev` for both halves |
| Backend code | `backend/src/shuhari/` |
| Backend URL | `http://localhost:8000` — `/healthz`, `/readyz`, `/api/v1/...` |
| Prod-like stack | `http://localhost:8080` — `just stack`; nginx serves the built frontend and proxies `/api`. **Verify here before claiming a feature works**, because `just dev` hides the proxy and `$PORT` classes of bug |
| Logs | JSON on stdout: `just logs backend`. Never a log file — see Portability in [`backend/AGENTS.md`](backend/AGENTS.md) |
| Traces | Phoenix, `http://localhost:6006` |
| Agent dev UI | `just adk` |
| Postgres / SearXNG / Ollama | `localhost:5432` / `:8888` / `:11434` |

Keep this table current as each piece becomes real; a stale resource table is worse than
none.

This is the one place an MCP server is **preferred** over the CLI (see [Rules](#rules)):
there is no shell equivalent for driving a browser.

**Scripted Playwright tests are a separate thing, arriving at milestone 2** with the first
real UI, in `frontend/tests/e2e/`, triggered on demand by the `run:e2e` label and never on
every pull request. The MCP server answers *"does this work?"*; a scripted suite answers
*"did this stop working?"* — tracker row F8.

## Rules
- Keep code simple and readable. No extra layers or new frameworks.
- Stack is fixed: Python 3.12 + uv, Google ADK, FastAPI, SQLModel + Alembic, Postgres + pgvector, mem0, Phoenix, React + Vite. Ask before adding anything else.
- Model: `openai/gpt-6-luna` from `.env`. Never hardcode a model or switch to a costlier one.
- Secrets only in `.env`; never commit it.
- Work on a branch; never commit to `main` once it's protected.
- Always use the `git`/`gh` CLI. Branch names: `feat/`, `fix/`, `refactor/`, `docs/`, `chore/`.
  Squash-merge only; the PR title becomes the commit message on `main`, so write it as one.
  Open the pull request as a **draft** with the first commit — see [Pull requests](#pull-requests).
- **With squash merges, a commit trailer belongs on one commit, not every commit.** Squash
  concatenates all the commit bodies, so a trailer repeated on four commits appears four
  times on `main`. Put it on the final commit, or in the pull request body.
- **Prefer the CLI over MCP servers.** `git` and `gh` for anything version-control or
  GitHub, ordinary shell tools for everything else — they are scriptable, inspectable, and
  already what the `justfile` uses. **This is a preference, not a prohibition:** when an MCP
  server is genuinely the better or the only tool for a job, use it and mention it in one
  line. What to avoid is routing routine git, GitHub or file work through one merely because
  it happens to be connected.
- Small steps: show the plan for anything touching more than 3 files.
- Edit `AGENTS.md`, never `CLAUDE.md` (it only contains `@AGENTS.md`).

## Done means
Code runs, `just check` passes (once it exists), and every new feature has a test.