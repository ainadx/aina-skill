#!/usr/bin/env python3
"""Seed a bundled golden starter into a workspace. Self-contained — copies from
this plugin's ./starters/<name>, no engine dependency.

Usage:
  python3 seed_starter.py <workspace_dir> <framework>   # framework: fastapi | nextjs
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
STARTERS = PLUGIN_ROOT / "starters"

# framework → starter directory name
FRAMEWORK_TO_STARTER = {
    "fastapi": "fastapi-htmx",
    # "nextjs": "nextjs",   # add when a Next.js starter is bundled
}
_SKIP = {"__pycache__", ".venv", "venv", ".git", ".env", "node_modules", ".DS_Store"}


def seed(ws: Path, framework: str):
    name = FRAMEWORK_TO_STARTER.get(framework or "")
    src = STARTERS / name if name else None
    if not src or not src.is_dir():
        return None
    ws.mkdir(parents=True, exist_ok=True)
    copied = 0
    for p in src.rglob("*"):
        if any(part in _SKIP for part in p.parts):
            continue
        rel = p.relative_to(src)
        dest = ws / rel
        if p.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            copied += 1
    return {"starter": name, "framework": framework, "files": copied}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: seed_starter.py <workspace_dir> <framework>", file=sys.stderr)
        return 2
    ws = Path(sys.argv[1]).expanduser().resolve()
    result = seed(ws, sys.argv[2])
    if result is None:
        print(json.dumps({"seeded": False, "framework": sys.argv[2],
                          "note": "no bundled starter for this framework"}))
        return 0
    print(json.dumps({"seeded": True, "workspace": str(ws), **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
