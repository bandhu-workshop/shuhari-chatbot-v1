#!/usr/bin/env python3
"""Route shell mutations of any AGENTS.md to a human confirmation prompt.

Those files are human-owned, but not frozen: the agent may change one *after* the human
says yes in that prompt, for that one edit. Not easy, still possible.

This covers the Bash escape hatch only. The declarative half is `permissions.ask` in
.claude/settings.json, which puts the file-writing tools behind the same prompt with no
script to go wrong. This hook exists because `sed -i` on one of these files, or a python
heredoc calling write_text, would otherwise walk straight past it and write silently.

"ask" rather than "deny" because a deny has no release valve: the agent cannot comply even
when the human wants the edit, so every change becomes a copy-paste chore -- while the
part that actually protects the file, a human reading the exact diff before it lands, is
what the prompt already provides.

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

# A quoted string that *ends* at AGENTS.md -- i.e. a path argument, not prose that happens
# to name the file. The closing quote is the whole point: without it, `write_text("the
# AGENTS.md files are human-owned")` looks identical to `write_text` on the file itself,
# and the hook prompts on a command that writes somewhere else entirely.
PATH_ARG = r"['\"][^'\"\n]{0,120}?AGENTS\.md['\"]"

# A program opening AGENTS.md for writing, inside a heredoc body.
PROGRAM_WRITE = re.compile(
    rf"(?:write_text|writelines|truncate|open)\s*\(\s*{PATH_ARG}"  # open("AGENTS.md", ...)
    rf"|{PATH_ARG}[^\n]{{0,30}}?(?:write_text|writelines|truncate)"  # Path(...).write_text()
    rf"|{PATH_ARG}\s*,\s*['\"][wa]",  # open(..., "w") with the mode split off
)

HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

REASON = (
    "This command writes to a human-owned instruction file, so the human confirms the "
    "edit (.claude/settings.json -> permissions.ask). To approve it they need the exact "
    "change: show the old wording, the new wording, and why the rule belongs there. If "
    "the answer is no, put the proposed wording in your reply instead. Every other doc "
    "-- docs/, README.md, localdev/ -- needs no prompt."
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
                    "permissionDecision": "ask",
                    "permissionDecisionReason": REASON,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
