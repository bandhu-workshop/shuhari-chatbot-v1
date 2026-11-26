# GitHub workflow and branch protection

> **Last updated:** 2026-11-26 16:02 IST

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
- Never add a `Co-Authored-By: Claude …` (or any AI) trailer to commit messages,
  and never mention Claude/AI authorship in commits or PR descriptions. Claude/AI
  must never appear as a GitHub contributor on this repo — commit authorship stays
  solely with the human developer.
- Use the `git`/`gh` CLI for all GitHub operations.

## Daily flow

```bash
just branch feat/session-store   # fresh main, new branch
# ... work, commit ...
just pr                          # push + open a PR filled from commits
just merge                       # squash-merge automatically once CI is green
just sync                        # back to main
```

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
| Required checks | `ci` | `backend`, `integration`, `frontend`, `docker` |

Everything else — public, PR-required, 0 approvals, linear history, conversation
resolution, no force pushes, no AI authorship — is the same.
