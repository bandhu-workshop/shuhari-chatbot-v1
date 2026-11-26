#!/usr/bin/env python3
"""Run the AGENTS.md guard hook over a case suite and print decision vs expectation."""

import json
import subprocess
import sys
from pathlib import Path

HOOK = str(Path(__file__).with_name("protect-agents-md.py"))
TARGET = "AGENTS" + ".md"  # assembled so this harness is not itself a match

# (label, command, expected decision: "ask" or None)
CASES = [
    # --- should prompt: a write aimed at the protected file ---
    ("redirect overwrite", f'echo hi > {TARGET}', "ask"),
    ("redirect append", f'echo hi >> backend/{TARGET}', "ask"),
    ("sed -i", f'sed -i "s/a/b/" frontend/{TARGET}', "ask"),
    ("perl -i", f'perl -i -pe "s/a/b/" {TARGET}', "ask"),
    ("tee", f'echo hi | tee {TARGET}', "ask"),
    ("mv over it", f'mv draft.md {TARGET}', "ask"),
    ("cp over it", f'cp /dev/null {TARGET}', "ask"),
    ("rm", f'rm {TARGET}', "ask"),
    ("truncate", f'truncate -s 0 {TARGET}', "ask"),
    ("heredoc write_text", f'python3 - <<EOF\nPath("{TARGET}").write_text("x")\nEOF', "ask"),
    ("heredoc open w", f'python3 - <<EOF\nopen("{TARGET}", "w").write("x")\nEOF', "ask"),

    # --- should NOT prompt: reads and unrelated work ---
    ("cat", f'cat {TARGET}', None),
    ("grep", f'grep -n Layout backend/{TARGET}', None),
    ("head", f'head -20 {TARGET}', None),
    ("sed -n", f'sed -n "1,30p" {TARGET}', None),
    ("wc", f'wc -l {TARGET}', None),
    ("git log", f'git log --oneline -- {TARGET}', None),
    ("git diff", f'git diff {TARGET}', None),
    ("unrelated write", 'echo hi > docs/tracker.md', None),
    (
        "prose mentions it, writes elsewhere",
        f'python3 - <<EOF\nPath("notes.md").write_text("the {TARGET} files are human-owned")\nEOF',
        None,
    ),
    (
        "commit message mentions it",
        f'git commit -m "docs: explain why {TARGET} is human-owned"',
        None,
    ),
]


def decide(command: str) -> str | None:
    out = subprocess.run(
        [HOOK],
        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    if not out:
        return None
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


def main() -> int:
    failures = 0
    for label, command, expected in CASES:
        got = decide(command)
        ok = got == expected
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {label:38} expected={expected!s:5} got={got!s}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} as expected")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
