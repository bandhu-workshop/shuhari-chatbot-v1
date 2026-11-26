set dotenv-load

# list commands
default:
    @just --list

# --- setup & infra ---

# install backend and frontend dependencies
setup:
    cd backend && uv sync
    cd frontend && npm install

# start Postgres+pgvector, Phoenix, SearXNG, Ollama
up:
    docker compose up -d

# stop everything (infra and app containers)
down:
    docker compose --profile app down

# pull the embedding model into Ollama (once, after `just up`)
models:
    docker compose exec ollama ollama pull {{env("EMBED_MODEL", "nomic-embed-text")}}

# full stack in containers (prod-like): frontend :8080, API :8000
stack:
    docker compose --profile app up -d --build

# follow logs, e.g. `just logs backend`
logs service="":
    docker compose --profile app logs -f {{service}}

# --- run ---

# API (:8000) + frontend (:5173); Ctrl+C stops both.
# `kill 0` is deliberate: it stops the whole group, including uvicorn's reloader and vite's child processes.
dev: up
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    (cd backend && uv run uvicorn shuhari.main:app --reload --port 8000) &
    (cd frontend && npm run dev) &
    wait

# ADK dev UI to chat with agents directly
adk:
    cd backend && uv run adk web src/shuhari/agents

api:
    cd backend && uv run uvicorn shuhari.main:app --reload --port 8000

web:
    cd frontend && npm run dev

# --- quality ---

# fast tests: backend unit + frontend
test:
    cd backend && uv run pytest -m "not integration"
    cd frontend && npm run test -- --run

# integration tests (needs `just up` and migrations applied)
test-integration: up db-upgrade
    cd backend && uv run pytest -m integration

lint:
    cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy src
    cd frontend && npm run lint && npx prettier --check . && npx tsc --noEmit

fmt:
    cd backend && uv run ruff format . && uv run ruff check --fix .
    cd frontend && npx prettier --write .

# mechanical documentation checks: stamps present, links resolve
docs-audit:
    python3 scripts/docs_audit.py

# fast local check before every commit: docs + lint + unit tests
check: docs-audit lint test

# everything CI runs: lint, unit, migrations check, integration, frontend build, docker builds
check-all: check test-integration
    cd backend && uv run alembic check
    cd frontend && npm run build
    docker compose --profile app build

# --- evals ---

# run evals (3 repeats, compared to baseline), e.g. `just eval memory`
eval dataset="all" repeats="3": up
    cd backend && uv run python -m evals.run --dataset {{dataset}} --repeats {{repeats}}

# save current scores as the new baseline (commit it in a PR that says why)
eval-baseline dataset="all": up
    cd backend && uv run python -m evals.run --dataset {{dataset}} --repeats 3 --update-baseline

# --- database (Alembic) ---

# create a migration from model changes; review the file before applying
migration msg:
    cd backend && uv run alembic revision --autogenerate -m "{{msg}}"

db-upgrade:
    cd backend && uv run alembic upgrade head

# undo the last migration
db-downgrade:
    cd backend && uv run alembic downgrade -1

# --- contract ---

# regenerate frontend API types from the running backend's OpenAPI schema
types:
    cd frontend && npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/api-types.ts

# --- git flow (needs gh CLI) ---

# start a feature branch from fresh main, e.g. `just branch feat/session-store`
branch name:
    git switch main && git pull --ff-only && git switch -c {{name}}

# push the branch and open a PR filled from commit messages
pr:
    git push -u origin HEAD
    gh pr create --fill

# squash-merge automatically once CI is green, delete the branch
merge:
    gh pr merge --squash --delete-branch --auto

# back to main after a merge
sync:
    git switch main && git pull --ff-only && git fetch --prune

# apply merge settings + .github/rulesets/main.json; safe to re-run after editing the ruleset
protect-main:
    #!/usr/bin/env bash
    set -euo pipefail
    gh repo edit --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false --delete-branch-on-merge --enable-auto-merge
    id=$(gh api repos/{owner}/{repo}/rulesets --jq '.[] | select(.name=="protect-main") | .id' | head -1)
    if [ -n "$id" ]; then
      gh api repos/{owner}/{repo}/rulesets/"$id" --method PUT --input .github/rulesets/main.json >/dev/null
      echo "updated ruleset $id"
    else
      gh api repos/{owner}/{repo}/rulesets --method POST --input .github/rulesets/main.json >/dev/null
      echo "created ruleset"
    fi
