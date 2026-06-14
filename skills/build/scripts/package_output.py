#!/usr/bin/env python3
"""Package a finished build directory into the chosen output. Self-contained.

Usage:
  python3 package_output.py <build_dir> <mode> [--org ORG] [--name NAME] [--private]
    mode: folder | zip | git-repo
Prints a JSON result: {ok, mode, path|zip|repo_url, ...}.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd, cwd):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("mode", choices=["folder", "zip", "git-repo"])
    ap.add_argument("--org", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args()

    bd = Path(args.build_dir).expanduser().resolve()
    if not bd.is_dir():
        print(json.dumps({"ok": False, "error": f"build dir not found: {bd}"}))
        return 1
    name = args.name or bd.name

    if args.mode == "folder":
        print(json.dumps({"ok": True, "mode": "folder", "path": str(bd)}))
        return 0

    if args.mode == "zip":
        archive = shutil.make_archive(str(bd), "zip", root_dir=str(bd))
        print(json.dumps({"ok": True, "mode": "zip", "zip": archive, "path": str(bd)}))
        return 0

    # git-repo
    owner = args.org.strip()
    name_with_owner = f"{owner}/{name}" if owner else name
    steps = []
    for label, cmd in [
        ("git init", ["git", "init", "-b", "main"]),
        ("git add", ["git", "add", "-A"]),
        ("git commit", ["git", "-c", "user.email=aina@local", "-c", "user.name=AiNa",
                        "commit", "-m", f"AiNa build: {name}"]),
    ]:
        code, out, err = _run(cmd, bd)
        steps.append({"step": label, "ok": code == 0, "err": err[-200:]})
        if code != 0 and label != "git init":  # re-init is fine if already a repo
            pass
    vis = "--private" if args.private else "--public"
    code, out, err = _run(
        ["gh", "repo", "create", name_with_owner, vis, "--source", str(bd),
         "--remote", "origin", "--push"], bd)
    steps.append({"step": "gh repo create + push", "ok": code == 0, "err": err[-300:]})
    if code != 0:
        print(json.dumps({"ok": False, "mode": "git-repo", "error": err[-300:], "steps": steps}))
        return 1
    print(json.dumps({"ok": True, "mode": "git-repo",
                      "repo_url": f"https://github.com/{name_with_owner}", "steps": steps}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
