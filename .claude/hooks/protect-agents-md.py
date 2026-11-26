#!/usr/bin/env python3
"""Block shell mutations of any AGENTS.md. Those files are human territory.

This covers the Bash escape hatch only. The hard guarantee for the file-writing tools is
`permissions.deny` in .claude/settings.json -- declarative, with no script to go wrong.
This hook exists because `sed -i AGENTS.md`, or a python heredoc calling write_text, would
otherwise walk straight past that.

Why this is Python and not a grep one-liner: the first version matched the whole command
string, so writing *any* file whose contents mentioned AGENTS.md was refused -- it blocked
the creation of localdev/AGENTS-delta.md on its first real use. A hook that stops real work
is worse than no hook, so the matching has to distinguish the target of a write from the
text being written.

Two passes, because the two cases need opposite treatment:
  - Outside heredocs: a shell mutator (>, sed -i, tee, mv ...) aimed at AGENTS.md.
  - Inside heredocs:  a program write call (write_text, open(..., "w")) naming AGENTS.md.
    Heredoc bodies cannot be scanned with the shell-mutator patterns, because prose
    legitimately contains both "AGENTS.md" and ">".

Reads stay allowed: cat, grep, head, sed -n, wc, git log.
"""

from __future__ import annotations

import json
import re
import sys

# AGENTS.md as the target of a shell mutation, in the command itself.
SHELL_MUTATION = re.compile(
    r"(?:>>?|\btee\b|\bsed\s+-i|\bperl\s+-i|\btruncate\b|\brm\b|\bmv\b|\bcp\b|\bdd\b)"
    r"[^;&|]*?(?:^|[\s/'\"])AGENTS\.md",
    re.MULTILINE,
)

# A program opening AGENTS.md for writing, inside a heredoc body.
PROGRAM_WRITE = re.compile(
    r"AGENTS\.md[^\n]{0,80}?(?:write_text|writelines|truncate)"
    r"|(?:write_text|open)\s*\([^)]{0,80}?AGENTS\.md"
    r"|AGENTS\.md[^\n]{0,40}?['\"][wa]['\"]",
)

HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

REASON = (
    "AGENTS.md files are human-owned and the agent must not modify them "
    "(.claude/settings.json). Propose the wording in your reply and let the human apply "
    "it. Every other doc -- docs/, README.md, localdev/ -- is fair game."
)


def split_heredocs(command: str) -> tuple[str, str]:
    """Return (code outside heredoc bodies, concatenated heredoc bodies)."""
    outside: list[str] = []
    inside: list[str] = []
    marker: str | None = None
    for line in command.split("\n"):
        if marker is not None:
            if line.strip() == marker:
                marker = None
            else:
                inside.append(line)
            continue
        outside.append(line)
        found = HEREDOC_START.search(line)
        if found:
            marker = found.group(2)
    return "\n".join(outside), "\n".join(inside)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Never block because the hook itself could not parse its input.

    command = (payload.get("tool_input") or {}).get("command") or ""
    if "AGENTS.md" not in command:
        return 0

    outside, inside = split_heredocs(command)
    if SHELL_MUTATION.search(outside) or PROGRAM_WRITE.search(inside):
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": REASON,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
