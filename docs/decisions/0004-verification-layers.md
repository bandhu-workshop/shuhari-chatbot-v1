# 0004 — How we verify: the layers we use, and the ones we skip

> **Last updated:** 2026-11-26 14:52 IST

**Status:** accepted · **Date:** 2026-11-26 · **Revised:** 2026-11-26 (see Revision below)

## Context

There is a well-known stack for verifying an authenticated Python API: `bandit`, `semgrep`,
`pip-audit`, `gitleaks`, `pytest`, `mitmproxy`, `jwt_tool`, Schemathesis, OWASP ZAP,
Locust, `k6`, `py-spy`. All of it is free and all of it is defensible.

Applied in full to this project it would be roughly ten new tools for a single-user
learning app with a [50-concurrent-user target](0003-capacity-target.md) and no deployment.
Each one is a recurring obligation: a config file, a CI job, a version to bump, and output
to triage. The question is not "is this tool good" but "does it find a bug we would
otherwise ship".

## Decision

Adopt four layers, with a strong bias toward tools we already have or that GitHub runs for
free. **The skipped column is the operative half of this ADR** — it exists so the list
doesn't quietly grow back.

### Layer 1 — static, on every commit

| Use | Instead of | Why |
| --- | --- | --- |
| **ruff's `S` rules** | `bandit` | Ruff *is* flake8-bandit under the `S` prefix — hardcoded secrets, weak hashing, `eval`, insecure random. Already a dependency, already in `just lint`. One tool, not two |
| **GitHub Dependabot** | `pip-audit` | Already configured in `.github/dependabot.yml` for `uv`, `npm`, `github-actions` and `docker`. Free, monthly, grouped, and nothing to remember |
| **GitHub secret scanning + push protection** | `gitleaks` | Free on public repositories, and push protection **rejects the push** rather than failing CI once the secret is already in remote history. Enabled 2026-11-26 — see Revision |
| **GitHub Dependency Review** | part of what `pip-audit` would do | A pull-request gate that refuses a dependency change carrying a known high-severity advisory. Dependabot alerts tell you *after* the merge; this refuses the merge. Runs in seconds and needs nothing installed |
| **CodeQL** | `semgrep` | Taint tracking and dataflow analysis, which ruff genuinely cannot do. Free on public repositories. **Not a required check** — see Speed below |
| — | `semgrep` | **Skipped.** Its value here is its JWT and OWASP rulesets, and we issue no tokens (see below). Revisit only if that changes |

Dependabot's `uv` ecosystem has a known rough edge: it does not honour
`versioning-strategy` and can rewrite lower bounds in `pyproject.toml` to versions that
leave `uv.lock` inconsistent. CI must therefore assert lock consistency explicitly —
`uv sync --frozen` uses the lockfile as-is and will *not* catch this, so the `backend` job
runs `uv lock --check`.

### Layer 2 — tests (the layer that actually finds auth bugs)

Scanners cannot find authorization bugs, because user A reading user B's data is a
perfectly well-formed request. Three test shapes carry nearly all the value:

1. **Every route has an identity dependency.** One test walks `app.routes` and fails on any
   route absent from an explicit public allow-list. This catches the route someone forgets,
   mechanically, forever.
2. **Cross-user isolation (IDOR/BOLA).** User A asks for user B's session or memory and gets
   404 or 403. Written as a role × route × expected-status matrix, so adding a case is one line.
3. **No mass assignment.** A write endpoint ignores fields the caller must not set.

These are tracker rows **Z1** and **Z4**. Coverage is measured with `pytest-cov` on the
auth module only (target 95%), not repo-wide — a repo-wide coverage number is theatre, and
with the package still mostly empty `__init__.py` files it would read near 100% and mean
nothing. `[tool.coverage.report]` therefore sets no `fail_under`.

### Layer 3 — dynamic, when there is something to point at

| Tool | When | Why it earns its place |
| --- | --- | --- |
| **Schemathesis** | milestone 2 | Reads the OpenAPI schema we already generate for `just types` and throws generated input at it. Finds 500s and schema violations for almost no setup cost |
| **mitmproxy** | once, when cookies first ship | A single manual session to confirm `HttpOnly`, `Secure`, `SameSite`, and that no token leaks into a URL or a log. Learn-once; nothing committed |
| **`/security-review`** | on every auth diff | Built into Claude Code. Zero setup |
| OWASP ZAP | **deferred to deployment phase 3** | A DAST scanner is meaningless until something is publicly reachable |
| Burp Suite, `jwt_tool` | **skipped** | Both target our own token issuance, which does not exist |

### Layer 4 — load

| Use | Instead of | Why |
| --- | --- | --- |
| **Locust**, one scenario, **50 users** | `k6` | Python, so it reuses our models and our `.env`. One tool doing the job plainly |
| **`py-spy`** as a diagnostic | a profiling habit | Reach for it when a load test is slow, never on a schedule |

## Explicitly not adopted

- **`gunicorn -w 4` locally.** Cloud Run runs one container and scales by instance. Four
  local workers hide that and quadruple the DB pool. See [ADR 0003](0003-capacity-target.md).
- **Redis** for rate limiting, token denylists or sessions. A fifth container for a problem
  50 users do not have.
- **Login rate limiting, refresh-token rotation, token-family revocation, `alg: none` and
  issuer/audience tests.** All correct, all conditional on us issuing our own tokens. We
  decided not to: `get_current_user()` returns a hardcoded dev user until there is a real
  deployment (tracker rows A1–A4). Writing these tests now would mean writing the token
  service to test, which is the actual cost.

## Consequences

Total new weight: **two dev dependencies** (`schemathesis`, `locust`), both arriving later
than milestone 1; **one ruff config block**; **two GitHub settings to confirm**; **one CI
line**. Everything else is a tool we already run.

Tracker rows **V1–V6** carry the sequencing. If a skipped tool is ever added, it is added
here first, with the bug it would have caught.

## Speed

A verification layer that slows the feedback loop gets worked around, so the gating
pipeline has a budget: **it finishes in about 35 seconds** and adding to it requires a
reason.

| | Wall clock |
| --- | --- |
| `ci.yml` gating jobs, in parallel | ~35s |
| `dependency-review` | ~10s, parallel — no effect on wall clock |
| coverage | +~1s |
| **CodeQL** | **1-3 min, in its own workflow, not a required check** |

CodeQL is decoupled on purpose: gating a 35-second pipeline on a 3-minute scan defeats the
point of the fast pipeline. Its findings go to the Security tab, and it also runs weekly so
that an advisory published after a merge is still caught.

One workflow with parallel jobs beats several workflows. Each extra workflow repeats
checkout, toolchain setup and dependency install (~8-10s), while jobs *inside* one workflow
already run in parallel — so splitting by topic costs overhead and buys nothing. A separate
workflow is justified only when the **trigger** differs, which is why CodeQL is separate.

## Revision — 2026-11-26

Reconsidered against a standard Python CI checklist (ruff, mypy, pytest, pytest-cov,
pip-audit, pip-licenses, gitleaks, bandit, Dependabot, CodeQL, Dependency Review).

**Added:** CodeQL, Dependency Review, `pytest-cov`. None had been considered in the first
draft, and each does something nothing else here does.

**Still skipped,** for the reasons already given: `bandit` (ruff's `S` *is* flake8-bandit —
running both runs identical rules twice), `gitleaks` (GitHub secret scanning with push
protection is strictly better), `pip-audit` (a third reader of the same OSV/PyPI advisory
data that Dependabot alerts and Dependency Review already consume).

**Deferred:** `pip-licenses` — worth a monthly scheduled job if this is ever redistributed,
but not a pull-request gate, and it needs translating for `uv`. Also Trivy, Grype, Syft,
OSV-Scanner and Semgrep; Trivy on our own images is the first of those worth revisiting.

**A correction this revision forced.** The original version of this ADR justified skipping
`gitleaks` on the grounds that GitHub secret scanning replaced it — but secret scanning was
never actually switched on. Tracker row V2 ("confirm it is on") sat at `todo` for several
pull requests, so during that window there was no secret scanning of any kind. The ADR
described an intended configuration as though it were the live one.

Now enabled and verified on 2026-11-26: `secret_scanning`,
`secret_scanning_push_protection`, and Dependabot **security updates** (separate from the
version updates in `dependabot.yml`, and also previously off). Two further toggles,
`secret_scanning_non_provider_patterns` and `secret_scanning_validity_checks`, are accepted
by the API but stay `disabled` — they appear to need the web UI or are unavailable on a free
public repository. Not pursued.

**The lesson, worth more than the fix:** an ADR that swaps a tool for a platform feature has
to verify the feature is enabled, in the same change. Otherwise the ADR reads as coverage
while the gap is wide open.
