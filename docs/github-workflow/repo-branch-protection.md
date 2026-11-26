# GitHub workflow and branch protection

> **Last updated:** 2026-11-26 12:44 IST

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

The four CI checks are **not yet required**, because none can pass until there is a
`uv.lock`, prettier and vitest installed, and at least one test in each place CI runs
pytest or vitest (both fail on zero tests). Requiring a check that never reports
blocks every merge.

They get added to `main.json` incrementally, each in the same pull request that makes
it pass, by appending to the `rules` array and re-running `just protect-main`:

```json
{
  "type": "required_status_checks",
  "parameters": {
    "strict_required_status_checks_policy": true,
    "required_status_checks": [
      { "context": "backend" },
      { "context": "integration" },
      { "context": "frontend" },
      { "context": "docker" }
    ]
  }
}
```

The target end state is all four required and strict (the branch must be up to date
with `main` before merging).

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
