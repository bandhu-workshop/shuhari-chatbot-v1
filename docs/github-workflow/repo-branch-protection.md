# GitHub workflow and branch protection

> **Last updated:** 2026-11-26 17:15 IST

Solo-developer workflow for this repository. The repo lives at
`bandhu-workshop/shuhari-chatbot-v1` (public). Same conventions as
[`bandhu-workshop/shuhari-cli`](https://github.com/bandhu-workshop/shuhari-cli),
with the differences noted at the bottom.

- All changes land on `main` via pull request — no direct pushes.
- 0 approvals required (solo maintainer); CI (`.github/workflows/ci.yml`) is the
  actual merge gate.
- Squash-merge only; merge commits and rebase merges are disabled so `main` keeps
  a linear history. For a squash merge the PR title becomes the commit message on
  `main` — write it as a proper commit message (e.g. `feat: add session store`).
- Branch names: `feat/…`, `fix/…`, `refactor/…`, `docs/…`, `chore/…`.
- Open the pull request as a **draft** with the first commit — see
  [Daily flow](#daily-flow--draft-first).
- Use the `git`/`gh` CLI for all GitHub operations, in preference to an MCP server.
- Commit attribution follows the tooling default. The earlier rule forbidding a
  `Co-Authored-By: Claude …` trailer was withdrawn on 2026-11-26.

## Daily flow — draft first

```bash
just branch feat/session-store   # fresh main, new branch
# ... first commit ...
just draft                       # push + open a DRAFT pr, assigned to you
# ... keep committing ...
just push                        # push + watch this branch's CI
just ready                       # mark ready, then squash-merge once CI is green
just sync                        # back to main
```

**The pull request opens with the first commit, not when the work is finished.** Three
reasons, in order of how much they matter:

1. **CI runs on every push.** A failure appears in the commit that caused it, rather than
   surfacing ten commits later with nothing to bisect. This is the whole point.
2. **A draft cannot be merged.** Not by hand, not by auto-merge. The draft state is a
   safety interlock, not a label — which is what makes it safe to open early.
3. **Required checks are `strict`,** so a branch that falls behind `main` must be updated
   before it merges. Pushing early surfaces that immediately instead of at merge time.

`just draft` assigns the pull request to you (`--assignee @me`) so it appears in your own
list, and fills the body from the commit messages. `just merge` remains for a pull request
that is already out of draft.

Never mark a pull request ready while a required check is red. Fix it, or say in the
description why it is expected to fail.

## Scope of a pull request

One concern per PR. Specifically:

- **Frontend and backend changes stay in separate PRs** whenever possible. A PR touches
  `backend/` or `frontend/`, not both. Repo-wide files (`justfile`, `compose.yaml`,
  `docs/`, `.github/`) may travel with either, or alone.
- When a backend change **forces** a frontend change — an API path, a schema, a response
  shape — land the backend PR first, then a follow-up frontend PR that regenerates
  `src/lib/api-types.ts` via `just types`. `main` is briefly ahead of the frontend, which
  is fine: the frontend is pinned to the previous contract until its own PR lands, and the
  generated types make the mismatch a build error rather than a runtime surprise.
- Squash-merge means the PR title becomes the commit message on `main`, so a PR that
  does two unrelated things produces one commit that describes neither. That is the real
  cost of mixing scope here, not reviewer convenience.

## Protection for `main`

Protection is a **ruleset**, not classic branch protection: the configuration is
committed at `.github/rulesets/main.json`, so it is version-controlled and
reviewable rather than living as GitHub UI state. Rulesets are free on public
repositories.

Apply it with `just protect-main`, which also sets the merge settings. The recipe
is **idempotent** — it creates the ruleset if absent and updates it in place
otherwise — so re-run it after any edit to `main.json`:

```bash
just protect-main
```

**`main.json` always reflects what is live.** Do not list a rule there that is not
applied; that drift is the thing the committed-config approach exists to prevent.

### Repository security settings

Separate from the ruleset, and all free on a public repository. Verified enabled
2026-11-26:

| Setting | State | Replaces |
| --- | --- | --- |
| `secret_scanning` | enabled | a `gitleaks` CI step |
| `secret_scanning_push_protection` | enabled | — it **rejects the push**, rather than failing CI once the secret is already in remote history |
| Dependabot alerts | enabled | — |
| Dependabot **security updates** | enabled | opens fix pull requests automatically; separate from the version updates in `dependabot.yml` |
| `secret_scanning_non_provider_patterns` | disabled | accepted by the API but does not take effect; needs the web UI or is unavailable on a free public repo |
| `secret_scanning_validity_checks` | disabled | same |

These were **off** until 2026-11-26 even though
[ADR 0004](../decisions/0004-verification-layers.md) cited them as the reason not to run
`gitleaks`. See that ADR's Revision section.

### Currently enforced

- a pull request before merging, 0 required approvals, squash as the only allowed
  merge method;
- conversation resolution before merging;
- linear history;
- no force pushes (`non_fast_forward`) and no branch deletion.

There are no bypass actors, so the rules apply to the repository admin too. All
changes to `main`, including your own, go through a pull request.

### Staged rollout of the required CI checks

Checks are added to `main.json` incrementally, each in the pull request that makes it
pass, by appending to the `rules` array and re-running `just protect-main`. Requiring a
check that can never report would block every merge, which is why they were all absent
at first: none could pass before `uv.lock`, prettier and vitest existed, and before each
place CI runs pytest or vitest had at least one test (both fail on zero tests).

| Check | Required since | Made green by |
| --- | --- | --- |
| `backend` | 2026-11-26 | bootstrap 4a — deps, ruff/mypy/pytest config, first tests |
| `docker` | 2026-11-26 | green from the start; the images build |
| `frontend` | 2026-11-26 | bootstrap 4b — dev deps, formatting, first vitest test |
| `integration` | **not yet** | needs bootstrap 4c (Alembic), which waits on `core/config.py` |

`strict_required_status_checks_policy` is `true`: a branch must be up to date with `main`
before it merges. For sequential solo work that costs nothing, and it is what catches two
pull requests that pass separately but break together.

Adding `integration` is tracker row C5. When it lands, that is the end state: four
required checks, strict.

**Side effect worth knowing:** `just merge` (`gh pr merge --auto`) used to fail
intermittently with exit 1, because `--auto` is rejected when there are no required checks
to wait for. Now that there are, auto-merge works as intended.

## Labels

Sixteen labels, **nine applied automatically**. The only three ever clicked by hand are the
three that *do* something.

### Why this is smaller than a standard taxonomy

A pull request here already carries its type and area in machine-readable form: the type in
the Conventional Commit prefix (`feat:`, `fix:`, `chore:`), the area in the changed paths.
And there are no issues — every label sits on a pull request. Hand-applying `type:feature`
to a pull request titled `feat: …` is duplicate data entry, which is the one thing every
label guide warns against: **don't label what another field already holds.**

So a label earns its place here only by being **automatic** (no triage cost) or a **control**
(it changes what happens).

### Automatic — `actions/labeler` from changed paths

| Label | Paths |
| --- | --- |
| `area:backend` | `backend/**` |
| `area:frontend` | `frontend/**` |
| `area:docs` | `docs/**`, `*.md`, `**/AGENTS.md` |
| `area:ci` | `.github/**`, `justfile`, `compose.yaml`, `scripts/**`, `.mcp.json` |

Config is `.github/labeler.yml`, run by the `label` job in `ci.yml` with `sync-labels: true`
so a label is removed again when the paths stop matching. It only touches labels defined in
that file, so the manual ones survive.

Dependabot maintains its own five automatically — `dependencies`, `python:uv`, `javascript`,
`docker`, `github_actions`. Left alone.

### Manual — three controls

| Label | Meaning |
| --- | --- |
| `run:e2e` | Run the Playwright end-to-end suite on this pull request. A **switch**, not a description — this is how end-to-end verification stays on demand rather than on every PR |
| `needs:decision` | Waiting on a decision. Applied when a blocking question is raised, so unanswered pull requests are filterable |
| `blocked` | Cannot merge pending something external |

### Kept for when issues start

`bug`, `enhancement`, `good first issue`, `help wanted`. The last two carry *platform*
meaning — GitHub surfaces them in contributor discovery — so they stay even while unused.

### Removed, and one renamed

`duplicate`, `invalid`, `wontfix` and `question` are gone: GitHub's close reasons ("not
planned") cover all four, and with no issues they were noise. `documentation` was
**renamed** to `area:docs` rather than deleted and recreated, because GitHub renames in
place and keeps existing assignments.

### Colours

The `area:*` labels share a blue family, so the eye reads the family before the word. The
three controls deliberately are *not* a family: they use traffic-light semantics — purple
for a switch, amber for waiting, red for stopped — because they signal state rather than
category.

### Deferred

`type:*` waits until there is a release and a `.github/release.yml` to consume it: GitHub's
auto-generated release notes group by **label**, not by commit prefix, which is the point at
which type labels start paying for themselves. They should then be derived from the commit
prefix, not applied by hand.

`priority:*` is not used at all. With one developer and [`../tracker.md`](../tracker.md)
already ordering the work, priority is expressed by what gets picked up next.

## Why squash-only, not rebase

`required_linear_history` blocks **merge commits only** — squash and rebase both satisfy
it, because both produce single-parent commits. So linear history was never the reason to
pick one over the other. Squash-only is chosen for a different reason:

- **CI only ever tests the branch tip.** With a rebase merge, each branch commit lands on
  `main` individually having never been verified in isolation, which makes `git bisect`
  unreliable. With squash, every commit on `main` is exactly a state that passed all CI
  checks.
- **One commit per PR = one commit per milestone.** `main` becomes the milestone log,
  which is the same granularity the project already works in.
- **No discipline needed on the branch.** Commit `wip` and `fix typo` freely; it collapses
  into one well-named commit. Rebase would move the burden from "write one good PR title"
  to "every commit message must be good forever".
- **Nothing is lost.** GitHub keeps every branch commit in the PR's Commits tab
  permanently, even after a squash merge — so atomic commits are still practised and still
  reviewable a year later. Only `main` is collapsed.

If a PR contains genuinely distinct logical changes worth separating on `main`, split it
into two PRs rather than switching to rebase.

**If you ever do enable rebase, change both places or merging breaks entirely:**
`gh repo edit --enable-rebase-merge` *and* add `"rebase"` to `allowed_merge_methods` in
`main.json`, then `just protect-main`. GitHub blocks the merge when the repository setting
and the ruleset disagree about a method.

## Differences from `shuhari-cli`

| | `shuhari-cli` | this repo |
| --- | --- | --- |
| Mechanism | classic branch protection | ruleset committed at `.github/rulesets/main.json` |
| Merge methods | squash and rebase | squash only |
| Required checks | `ci` | `backend`, `frontend`, `docker` (and `integration` after 4c) |

Everything else — public, PR-required, 0 approvals, linear history, conversation
resolution, no force pushes — is the same.
