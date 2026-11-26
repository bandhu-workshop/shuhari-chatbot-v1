# Roadmap

> **Last updated:** 2026-11-26 13:44 IST

The wider Shuhari arc. For current position and the per-milestone breakdown, see
[tracker.md](./tracker.md) — this file holds only the shape across projects.

## Project 1 — this repo: a chatbot on Google ADK

Learn every component of a modern assistant by building it on a mature framework, one
working end-to-end slice at a time, with tracing and evals from the first slice.

Milestones 0–7, from bootstrap to "evaluate and improve". Detail in
[tracker.md](./tracker.md); the original specification in
[blueprint.md](./blueprint.md).

**Status:** in progress — milestone 0 (bootstrap).

## Project 2 — the same thing from scratch

Rebuild the parts ADK provided, without ADK: the agent loop, tool dispatch, session and
memory handling, the eval harness. The point is that Project 1 teaches what those pieces
*do*, so Project 2 can be about how they work rather than what they are.

**Status:** not yet specified. It should not be specified until Project 1 reaches
milestone 7, because what is worth rebuilding will only be clear by then.

## Why this order

守破離 — *shu* learn the form, *ha* break it, *ri* leave it. Project 1 is shu: follow a
framework's conventions and learn why they exist. Project 2 is ha. The naming of this
repo is not decoration; it is the method.
