#!/usr/bin/env python3
"""Mechanical documentation checks. Stdlib only, no dependencies.

Run with `just docs-audit`. Part of `just check`, so doc drift fails the build
instead of relying on anyone remembering to look.

Checks:
  1. Every tracked Markdown doc carries a `Last updated:` stamp under its H1.
  2. No stamp is dated in the future.
  3. Every relative Markdown link to a repo file resolves.
  4. A doc whose content changed has its stamp changed in the same change.

Check 4 is what makes the stamps mean something. A stamp that is merely *present* says
nothing; "is it current?" used to be a human check, which by this project's own rules is
the wrong kind of check. Comparing the stamp's time to the commit's time does not work --
the stamp is written minutes before the commit, so every doc looks stale. The exact
question is instead: did the change that touched this doc also touch its stamp line? That
has no tolerance to tune and no false positives.

Links inside fenced code blocks are ignored: docs/blueprint.md embeds whole copies of
other files, whose links are relative to where those files will live, not to the
blueprint. A link inside a fence is sample text, not a link.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files that legitimately carry no stamp: a template, and the CLAUDE.md shims whose
# entire content is "@AGENTS.md".
NO_STAMP = {
    ".github/pull_request_template.md",
    "CLAUDE.md",
    "backend/CLAUDE.md",
    "frontend/CLAUDE.md",
}

STAMP = re.compile(r"^> \*\*Last updated:\*\* (\d{4}-\d{2}-\d{2})", re.MULTILINE)
STAMP_LINE = "**Last updated:**"
LINK = re.compile(r"\[[^\]]*\]\(([^)#]+?)(?:#[^)]*)?\)")
FENCE = re.compile(r"^(`{3,}|~{3,})")


def outside_fences(lines: list[str]) -> list[str]:
    """Drop fenced-code lines. A fence closes on a marker at least as long as its opener."""
    kept: list[str] = []
    marker: str | None = None
    for line in lines:
        m = FENCE.match(line)
        if marker is None:
            if m:
                marker = m.group(1)
            else:
                kept.append(line)
        elif m and m.group(1)[0] == marker[0] and len(m.group(1)) >= len(marker):
            marker = None
    return kept


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return out.stdout


def tracked_markdown() -> list[Path]:
    return [ROOT / line for line in git("ls-files", "*.md").splitlines() if line]


def stamp_was_updated(rel: str) -> bool | None:
    """Did the change that last touched this doc also touch its stamp line?

    Looks at uncommitted changes first, so the problem is caught *before* the commit,
    which is when it is still cheap to fix. Falls back to the last commit that touched
    the file, which is what runs in CI on a clean checkout.

    Returns None when there is nothing to judge: no changes and no history.
    """
    for diff in (
        git("diff", "HEAD", "--unified=0", "--", rel),
        None,  # sentinel: fall back to the last commit
    ):
        if diff is None:
            sha = git("log", "-1", "--format=%H", "--", rel).strip()
            if not sha:
                return None
            diff = git("show", "--format=", "--unified=0", sha, "--", rel)
        if not diff.strip():
            continue
        return any(
            line.startswith("+") and STAMP_LINE in line for line in diff.split("\n")
        )
    return None


def main() -> int:
    today = dt.date.today()
    problems: list[str] = []

    for path in tracked_markdown():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text()
        lines = text.split("\n")

        if rel not in NO_STAMP:
            head = "\n".join(lines[:8])
            match = STAMP.search(head)
            if not match:
                problems.append(f"{rel}: no 'Last updated' stamp in the first 8 lines")
            else:
                stamped = dt.date.fromisoformat(match.group(1))
                if stamped > today:
                    problems.append(f"{rel}: stamp {stamped} is in the future")
                elif stamp_was_updated(rel) is False:
                    problems.append(
                        f"{rel}: content changed but the 'Last updated' stamp did not"
                    )

        for target in LINK.findall("\n".join(outside_fences(lines))):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                problems.append(f"{rel}: broken link -> {target}")

    if problems:
        print(f"docs audit: {len(problems)} problem(s)\n")
        for p in problems:
            print(f"  {p}")
        return 1

    print(f"docs audit: {len(tracked_markdown())} docs, all clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
