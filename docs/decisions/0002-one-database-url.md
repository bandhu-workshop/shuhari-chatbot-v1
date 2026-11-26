# 0002 — One database URL, async-only

> **Last updated:** 2026-11-26 13:31 IST

- **Status:** Accepted
- **Date:** 2026-11-26
- **Amends:** `docs/blueprint.md` (which specified three DB URLs and a sync Alembic path)

## Context

One Postgres instance, three consumers, each with its own idea of how to connect:

| Consumer | Needs | Negotiable? |
| --- | --- | --- |
| ADK `DatabaseSessionService` | `postgresql+asyncpg://` | **No.** ADK 2.x requires an async driver |
| mem0 pgvector | libpq connection: either `connection_string` **or** discrete `host`/`port`/`user`/`password`/`dbname` | Yes |
| Our tables (SQLModel + Alembic) | sync psycopg **or** async asyncpg | Yes |

The blueprint resolved this with three URLs built from `POSTGRES_*`: `app_db_url`
(`+psycopg`, sync), `adk_db_url` (`+asyncpg`), `mem0_db_url` (plain). That means two
drivers in `pyproject.toml`, three env overrides for production, and a standing
question of "which URL does this library want".

Two findings changed the picture:

1. **mem0's pgvector takes discrete connection parameters**, and that form is the
   better-documented one. `connection_string` support is version-dependent — an
   upstream issue shows config validation rejecting fields and listing the allowed
   set as `dbname, host, collection_name, user, password, embedding_model_dims, port`,
   with no `connection_string` at all. So the third URL was both redundant *and* the
   less reliable way to configure mem0.
2. **asyncpg is mandatory anyway** because of ADK. psycopg is the optional extra, not
   the other way round. Someone upgrading ADK to 2.0 hit exactly the failure the
   three-URL design invites: sync SQLAlchemy code sharing the ADK URL broke, and they
   had to strip `+asyncpg` off the string for sync consumers.

## Decision

**One SQLAlchemy URL, one driver, and mem0 gets components.**

- `core/config.py` keeps its `POSTGRES_*` fields as the single source and derives
  exactly one URL: `database_url` → `postgresql+asyncpg://…`, used by our app code,
  **Alembic**, and ADK. One string, three consumers.
- mem0 receives `postgres_host`, `postgres_port`, `postgres_user`, `postgres_password`
  and `postgres_db` as discrete parameters. No URL, and no string parsing anywhere.
- `asyncpg` is the only Postgres driver we declare. `psycopg[binary]` is dropped.
  (mem0 pulls whatever libpq binding it needs transitively — that is mem0's
  dependency, not one we declare or upgrade.)
- Alembic uses the async template: `alembic init -t async`.

## Consequences

- `pyproject.toml` loses a dependency; `core/config.py` exposes one URL instead of three.
- Production override surface is a single `DATABASE_URL`.
- **Cloud SQL still works.** libpq treats a `host` beginning with `/` as a Unix socket
  directory, so mem0's `host` becomes `/cloudsql/<instance>` unchanged, and one
  `DATABASE_URL` covers everything else. The portability rule in `backend/AGENTS.md`
  shrinks from "every DB URL is individually overridable" to one variable.
- `alembic/env.py` carries ~15 lines of `asyncio.run` + `connection.run_sync`
  boilerplate, which `alembic init -t async` **generates**. Alembic gains no speed from
  being async — it is a CLI run once per deploy. This is purely the price of one driver.
- The sync Alembic path is the more common one online, so fewer tutorials will match
  ours. Accepted: the async template is official and documented.

## Why this is the low-maintenance option, not just the small one

The cost is fifteen generated lines in a file opened once and never reopened. The saving
is one fewer dependency to upgrade, one URL instead of three to keep consistent, no
string manipulation that can break on a library upgrade, and avoidance of a
version-dependent mem0 parameter. Ongoing obligations, not setup cost.

## Revisit when

- ADK stops requiring an async driver (then sync-everything becomes an option), or
- mem0 drops discrete connection parameters in favour of `connection_string` only, or
- we need a sync SQLAlchemy path for something real (a batch job, a data export).

## Open risk, unrelated to this decision but adjacent

Two upstream ADK issues affect asyncpg + Postgres and should be checked before
milestone 3: [#4366](https://github.com/google/adk-python/issues/4366) (tz-aware
datetimes into `TIMESTAMP WITHOUT TIME ZONE`) and
[#7276](https://github.com/google/adk-python/issues/7276) (false `StaleSessionError`
when two events share a timestamp). Tracked in `docs/tracker.md`.
