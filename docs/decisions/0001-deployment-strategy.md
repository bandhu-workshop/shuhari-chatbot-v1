# 0001 — Deployment strategy: local-first, GCP later

> **Last updated:** 2026-11-26 12:44 IST

- **Status:** Accepted
- **Date:** 2026-11-26
- **Supersedes:** nothing

## Context

The target production environment is Google Cloud Run plus GCP managed infrastructure.
Development happens locally on a laptop, with `compose.yaml` providing Postgres+pgvector,
Phoenix, SearXNG and Ollama.

The question was whether to provision GCP early and develop against it, or build locally
through all milestones and port afterwards.

Two facts shaped the answer:

1. **The blueprint is already ~80% portable.** `backend/AGENTS.md` already requires every
   service address to come from an env var, and ADK's `DatabaseSessionService` is
   Postgres-backed rather than in-process. Those two decisions are most of what Cloud Run needs.
2. **The difficulty is concentrated in the self-hosted services, not the app.** Ollama,
   SearXNG, Phoenix and mem0's SQLite history are all long-lived and stateful, which is
   the opposite of what a scale-to-zero platform is for. The FastAPI backend itself is easy.

## Decision

Work in phases, split by **cost asymmetry** rather than by timeline:

| Phase | When | What | Effort |
| --- | --- | --- | --- |
| **0** | Milestones 1–3 | Adopt the portability rules (see `backend/AGENTS.md` → Portability, `frontend/AGENTS.md` → Portability) | ~1 day, spread out |
| **1 — spike** | Right after milestone 1 works locally | Deploy *only* the hello-agent to Cloud Run + Cloud SQL by hand with `gcloud`. Then delete every resource | A weekend, a few dollars |
| **2** | Milestones 2–7 | Pure local development. Do not touch GCP | — |
| **3** | After milestone 7 | Terraform + Workload Identity Federation + real deploy + observability + cloud evals | 2–3 weeks of evenings |

Two rules follow from this:

- **Do now what is cheap now and expensive to retrofit** — the Phase 0 list. Structured
  logging and the auth seam are the two that genuinely hurt if deferred, because they touch
  every module and every route respectively.
- **Defer anything whose cost is the same whenever you do it** — buying GCP resources.
  Provisioning infrastructure for an app whose shape is not yet known, and paying for it
  while learning, is a recurring tax with no offsetting benefit.

### Why the Phase 1 spike, given Phase 2 is "don't touch GCP"

Deploying a hello-world teaches roughly 30% of Cloud Run. The rest — migrations, connection
limits, cold starts, secrets, streaming timeouts, cost — only appears under a real workload.
Discovering all of it at milestone 7 means some of it becomes a refactor instead of a config
change. The spike surfaces those problems while the app is ~200 lines, then gets torn down so
nothing is paid for during Phase 2.

## What local can and cannot replicate

There is no Cloud Run emulator worth using. Fidelity is uneven, and it is worth knowing where:

| GCP piece | Local equivalent | Fidelity |
| --- | --- | --- |
| Cloud SQL + pgvector | the pgvector container in `compose.yaml` | ~100% — it is just Postgres |
| Secret Manager | `.env` | 100% — the code reads env vars either way |
| Cloud Logging | stdout | 100% *if* logs are JSON |
| Cloud Trace | Phoenix via OTEL | ~90% — same instrumentation, different exporter |
| Cloud Run runtime | `just stack` | ~70% — no scale-to-zero, no cold starts, no 10s SIGTERM, no `$PORT` enforcement |
| IAM / service accounts | nothing | 0% |
| Load balancer / TLS / domain | nothing | 0% |

The data layer is essentially perfectly replicable; IAM and networking are not replicable at
all. The unreplicable parts are exactly the parts worth learning, which is the argument for
Phase 1.

**The discipline that closes most of the runtime gap costs nothing: `just stack` must pass
before any deploy.** It catches the `$PORT`, nginx-proxy and env-var classes of bug, and
`just check-all` already builds the images.

## Known hard parts, deferred to Phase 3

- **Ollama embeddings.** An L4 GPU on Cloud Run is roughly $0.67/hr while running; CPU-only
  works for a 137M-param embedding model but is slower. Either way the model must be baked
  into the image or volume-mounted, or every cold start re-downloads it.
- **SearXNG will work *worse* in GCP than on a laptop.** It is a scraper, and upstream engines
  block datacenter IP ranges far more aggressively than residential ones.
- **Phoenix** needs persistent storage and is a development/eval tool rather than a production
  monitoring system. `tracing.py` is already a no-op when `PHOENIX_COLLECTOR_ENDPOINT` is
  unset, so production can simply omit it.
- **mem0's `history_db_path`** is SQLite on local disk. Cloud Run's filesystem is per-instance
  and ephemeral, so two instances means two divergent histories. Decide at milestone 5;
  Postgres is the likely answer.
- **`nginx.conf` proxies to `http://backend:8000`**, a compose-network name. On Cloud Run the
  options are an nginx sidecar using `127.0.0.1` (containers in one instance share localhost),
  or dropping nginx entirely and serving the static build from Firebase Hosting / GCS with CORS.
- **Cloud SQL's default connection path is a unix socket** (`/cloudsql/<name>`), not host:port.
  This is why each DB URL must be individually overridable rather than only composed from
  `POSTGRES_*`.
- **Evals make real model calls**, so running them in cloud CI costs real money.

## The rule we expect to break, deliberately

`backend/AGENTS.md` says: don't use vendor-hosted memory, search or tracing services.

**That is a learning rule, not a production commandment.** Self-hosting mem0, SearXNG and
Phoenix locally is how the mechanics get learned. In GCP the same rule becomes a cost-and-ops
rule and may simply be wrong. A legitimate end state is Cloud Trace instead of Phoenix, a
hosted embeddings API instead of Ollama, and a search API instead of SearXNG — precisely
because by then we understand what is being replaced.

守破離: learn the form, then break it where it stops serving.

## Consequences

- Milestones 1–3 carry a small, explicit tax (the Phase 0 rules) in exchange for Phase 3 being
  a provisioning exercise rather than a refactor.
- GCP costs nothing until the Phase 1 spike, and nothing again until Phase 3.
- `just stack` becomes a gate, not an occasional sanity check.
- The Phase 1 spike is throwaway by design. Its artifacts are notes and deleted resources,
  not committed Terraform.

## Revisit when

- Milestone 7 completes (Phase 3 begins in earnest), or
- the Phase 1 spike surfaces something that invalidates the phasing, or
- a requirement appears for multi-user access from outside the LAN before milestone 7.
