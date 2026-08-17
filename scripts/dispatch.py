#!/usr/bin/env python3
"""Dispatch a task to one of the coding agents (OpenCode/DeepSeek or Antigravity).

Minimal orchestration helper for the 3-agent setup described in
scripts/agent-orchestration.md. Not a server — a thin CLI wrapper so Hermes
can delegate without remembering flags.

Usage:
    python scripts/dispatch.py opencode "Add Alembic migrations" [--background]
    python scripts/dispatch.py antigravity "Add gitignore for build dirs"

OpenCode uses the free DeepSeek model by default.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKTREES = {
    "opencode": REPO_ROOT.parent / "flowmind-agent-opencode",
    "antigravity": REPO_ROOT.parent / "flowmind-agent-antigravity",
}

OPENCODE_MODEL = "opencode/deepseek-v4-flash-free"

# Resolve binaries explicitly: npm global bins may not be on Python's PATH.
OPENCODE_BIN = (
    Path(os.environ.get("OPENCODE_BIN", "")).expanduser()
    if os.environ.get("OPENCODE_BIN") else None
) or shutil.which("opencode") or r"C:\Users\Usuario\AppData\Roaming\npm\opencode"
ANTIGRAVITY_BIN = (
    Path(os.environ.get("AGY_BIN", "")).expanduser()
    if os.environ.get("AGY_BIN") else None
) or shutil.which("agy") or r"C:\Users\Usuario\AppData\Local\agy\bin\agy"


def run_opencode(task: str, worktree: Path, background: bool) -> int:
    cmd = [
        str(OPENCODE_BIN), "run", task,
        "-m", OPENCODE_MODEL,
        "--dir", str(worktree),
    ]
    if background:
        # launch detached; caller polls via process tool
        subprocess.Popen(cmd, cwd=worktree)  # noqa: S603
        print(f"[dispatch] opencode launched in background @ {worktree}")
        return 0
    return subprocess.call(cmd, cwd=worktree)  # noqa: S603


def run_antigravity(task: str, worktree: Path) -> int:
    # agy uses --add-dir to register a workspace dir (no --dir flag).
    # Run with cwd in the worktree and add it to the workspace.
    cmd = [str(ANTIGRAVITY_BIN), "--print", task, "--add-dir", str(worktree)]
    return subprocess.call(cmd, cwd=worktree)  # noqa: S603


def main() -> int:
    ap = argparse.ArgumentParser(description="Dispatch a task to a coding agent.")
    ap.add_argument("agent", choices=["opencode", "antigravity"])
    ap.add_argument("task", help="Task description / prompt for the agent")
    ap.add_argument("--background", action="store_true",
                    help="Launch opencode detached (do not wait)")
    args = ap.parse_args()

    worktree = WORKTREES.get(args.agent)
    if not worktree or not worktree.exists():
        print(f"[dispatch] ERROR: worktree not found: {worktree}", file=sys.stderr)
        return 2

    if args.agent == "opencode":
        return run_opencode(args.task, worktree, args.background)
    return run_antigravity(args.task, worktree)


if __name__ == "__main__":
    raise SystemExit(main())
