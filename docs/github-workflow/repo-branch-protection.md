# GitHub workflow and branch protection

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

Applied once with `just protect-main`, which also sets the merge settings:

```bash
just protect-main
```

The ruleset requires:

- a pull request before merging, 0 required approvals, squash as the only
  allowed merge method;
- conversation resolution before merging;
- the four CI checks `backend`, `integration`, `frontend` and `docker`, strict
  (the branch must be up to date with `main` before merging);
- linear history;
- no force pushes (`non_fast_forward`) and no branch deletion.

### Ordering

`just protect-main` must run **after** CI is green on `main`. The four required
checks cannot pass until bootstrap steps 4–5 and milestone 1 exist (there is no
`uv.lock`, no source and no tests before then), and a ruleset naming checks that
never report would block every merge. The bootstrap commit is therefore pushed to
an unprotected `main`, with CI red, and protection is applied later.

## Differences from `shuhari-cli`

| | `shuhari-cli` | this repo |
| --- | --- | --- |
| Mechanism | classic branch protection | ruleset committed at `.github/rulesets/main.json` |
| Merge methods | squash and rebase | squash only |
| Required checks | `ci` | `backend`, `integration`, `frontend`, `docker` |

Everything else — public, PR-required, 0 approvals, linear history, conversation
resolution, no force pushes, no AI authorship — is the same.
