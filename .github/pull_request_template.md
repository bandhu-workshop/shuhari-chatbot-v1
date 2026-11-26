<!--
Title = the squash commit subject on main. Conventional prefix, imperative, <= 72 chars.

Keep this body under ~15 lines. If a rationale needs more than one line, it belongs in
docs/decisions/ as an ADR and this links to it -- a PR body is the worst place to store
reasoning, because nobody reads git history looking for it.

Note: `just draft` uses `gh pr create --fill`, so the COMMIT MESSAGE becomes this body.
Write the commit message in this shape and the PR matches automatically.
-->

**What**
-

**Why** <!-- only where it is not obvious from the diff; one line each, or link an ADR -->
-

**Verified**
-

**Deferred** <!-- delete if nothing was left out on purpose -->
-

<!--
Before marking ready:
- [ ] `just check` passes (`just check-all` for DB, Docker or build changes)
- [ ] Migration included and reviewed, if anything in models/ changed
- [ ] Eval case added and `just eval` shows no regression, if behaviour changed
- [ ] Docs updated in this PR, if a convention, command or decision changed
- [ ] Labelled (area:* is automatic; add run:e2e / needs:decision / blocked if they apply)
-->
