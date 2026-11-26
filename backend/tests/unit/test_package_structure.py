"""The layered package structure of `backend/AGENTS.md` -> Layout, enforced.

Tracker row B5. These tests need no application code, which is why they are the first
tests in the repo: pytest fails a CI job when it collects nothing, and a layout that is
only described in a Markdown file drifts from the one on disk.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "shuhari"

# Every package in backend/AGENTS.md -> Layout. Add a row here when a layer is added.
LAYER_PACKAGES = [
    "shuhari",
    "shuhari.core",
    "shuhari.api",
    "shuhari.api.v1",
    "shuhari.api.v1.routes",
    "shuhari.db",
    "shuhari.models",
    "shuhari.schemas",
    "shuhari.ai",
    "shuhari.ai.agents",
    "shuhari.ai.agents.chatbot",
    "shuhari.ai.agents.research",
    "shuhari.ai.tools",
    "shuhari.ai.mcp",
    "shuhari.ai.memory",
    "shuhari.ai.sessions",
    "shuhari.ai.observability",
    "shuhari.ai.evaluation",
    "shuhari.ai.evaluation.graders",
]

# core/ holds cross-cutting concerns that every other layer reads. It must not depend
# on them, or settings and logging cannot be imported without dragging in the app.
OUTER_LAYERS = ("api", "db", "models", "schemas", "ai")


@pytest.mark.parametrize("module", LAYER_PACKAGES)
def test_layer_package_is_importable(module: str) -> None:
    """A missing __init__.py or a broken import in any layer fails here first."""
    assert importlib.import_module(module) is not None


def test_layer_package_list_matches_disk() -> None:
    """Catches a package added to the tree but not documented above, and vice versa."""
    on_disk = {
        "shuhari." + str(p.parent.relative_to(SRC)).replace("/", ".")
        for p in SRC.rglob("__init__.py")
    }
    on_disk = {m.replace("shuhari..", "shuhari") for m in on_disk}
    assert on_disk == set(LAYER_PACKAGES)


def test_prompts_is_data_not_a_package() -> None:
    """ai/prompts/ holds .md templates loaded at runtime; making it a package would
    invite importing prompts as code, and would package them into the wheel."""
    assert (SRC / "ai" / "prompts").is_dir()
    assert not (SRC / "ai" / "prompts" / "__init__.py").exists()


def test_core_does_not_import_outer_layers() -> None:
    """`core` is the innermost layer. Enforces 'don't reach across layers' in the one
    direction that is unambiguous: nothing in core/ may import api, db, models,
    schemas or ai."""
    offenders: list[str] = []
    for path in (SRC / "core").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            for name in names:
                parts = name.split(".")
                if parts[:1] == ["shuhari"] and len(parts) > 1 and parts[1] in OUTER_LAYERS:
                    offenders.append(f"{path.name} imports {name}")
    assert not offenders, "core/ must not depend on outer layers: " + "; ".join(offenders)
