#!/usr/bin/env python3
"""Classify a build request as backend- vs frontend-heavy and print the golden
stack profile. Self-contained (stdlib only) — no engine dependency.

Usage:
  python3 classify_stack.py --text "an admin dashboard to manage orders" [--archetype internal-tool]
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# Golden profiles: framework drives which starter the seeder copies.
GOLDEN_PROFILES = {
    "backend": {"runtime": "python", "framework": "fastapi", "ui": "htmx", "hosting": "vps"},
    "frontend": {"runtime": "node", "framework": "nextjs", "ui": "shadcn", "hosting": "vercel"},
}

_BACKEND = [
    "dashboard", "admin", "internal tool", "back office", "back-office", "crud",
    "database", "records", "report", "reporting", "data entry", "spreadsheet",
    "table of", "api", "rest", "pipeline", "workflow", "etl", "automation",
    "automate", "tracker", "tracking", "inventory", "management", "manage",
    "ops", "operations", "monitoring", "queue", "scheduler", "scheduling",
    "billing", "invoicing", "invoice", "accounting", "portal", "intranet",
    "python", "ml ", "machine learning", "model training", "scraper",
    "integration", "sync", "cron", "batch", "backend", "data tool", "analytics tool",
]
_FRONTEND = [
    "landing page", "landing", "marketing site", "marketing page", "portfolio",
    "interactive", "animation", "animated", "realtime", "real-time", "chat",
    "messaging", "game", "canvas", "editor", "wysiwyg", "drag and drop",
    "drag-and-drop", "page builder", "spa", "single page", "rich ui",
    "rich interface", "mobile app", "pwa", "social feed", "feed", "video player",
    "audio player", "interactive map", "visualization", "3d", "three.js",
    "micro-interaction", "polished marketing",
]
_ARCHETYPE_BIAS = {"internal-tool": 3, "content-site": -3, "ai-app": 1, "utility": -1, "saas": 0}


def classify(text: str, archetype: str = "saas"):
    t = re.sub(r"\s+", " ", (text or "").lower())
    b = sum(1 for s in _BACKEND if s in t)
    f = sum(1 for s in _FRONTEND if s in t)
    bias = _ARCHETYPE_BIAS.get(archetype, 0)
    score = b - f + bias
    lean = "frontend" if score < 0 else "backend"  # ties → backend (reliable server-rendered)
    return lean, {
        "lean": lean, "score": score, "backend_hits": b, "frontend_hits": f,
        "archetype_bias": bias,
        "reason": f"{b} backend vs {f} frontend signal(s)"
                  + (f" + archetype bias {bias:+d}" if bias else "") + f" → {lean}",
        "profile": GOLDEN_PROFILES[lean],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--archetype", default="saas")
    args = ap.parse_args()
    _, detail = classify(args.text, args.archetype)
    print(json.dumps(detail, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
