# shuhari-chatbot-v1

Learning project: a Claude/ChatGPT-style chatbot built with Google ADK, one small working milestone at a time.

## Read first
- `README.md`: overview, commands, git flow
- `docs/blueprint.md`: the plan (stack, milestones, bootstrap steps, file contents)
- `docs/decisions/`: ADRs. `0001-deployment-strategy.md` sets the local-first/GCP-later phasing and the portability rules that milestones 1-3 must follow
- `docs/github-workflow/repo-branch-protection.md`: branch protection, merge rules, commit conventions

## Current stage
Bootstrap (blueprint "Bootstrap" section). Only build what the current step or milestone needs.

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