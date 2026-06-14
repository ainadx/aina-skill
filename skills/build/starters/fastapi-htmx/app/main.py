"""<APP_NAME> — FastAPI + HTMX golden starter.

Server-rendered (Jinja2) admin/dashboard shell. No client build step, no CDN:
styling is the committed design system at static/css/app.css, interactivity is
vendored HTMX (static/js/htmx.min.js). Generated apps extend this — add routes,
replace the demo data layer, fill in the pages — but keep the shell so every
app inherits the professional chrome and deploys cleanly to the VPS/Fly.

Run locally:  uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_NAME = os.environ.get("APP_NAME", "Acme Console")
APP_TAGLINE = os.environ.get("APP_TAGLINE", "A clean starting point for your app.")

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Inline SVG icons (stroke=currentColor) so the nav has no external asset deps.
_ICONS = {
    "grid": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>',
    "list": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="3.5" cy="6" r="1.2"/><circle cx="3.5" cy="12" r="1.2"/><circle cx="3.5" cy="18" r="1.2"/></svg>',
    "map": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M9 3 4 5v16l5-2 6 2 5-2V3l-5 2-6-2Z"/><line x1="9" y1="3" x2="9" y2="19"/><line x1="15" y1="5" x2="15" y2="21"/></svg>',
}

NAV = [
    {"key": "dashboard", "label": "Dashboard", "href": "/", "icon": _ICONS["grid"]},
    {"key": "items", "label": "Items", "href": "/items", "icon": _ICONS["list"]},
    {"key": "roadmap", "label": "Roadmap", "href": "/roadmap", "icon": _ICONS["map"]},
]


def ctx(request: Request, active: str, **extra):
    return {
        "request": request,
        "app_name": APP_NAME,
        "app_tagline": APP_TAGLINE,
        "nav": NAV,
        "active": active,
        **extra,
    }


# ── Demo data layer (replace with your real models/DB) ────────────────────
_ITEMS: list[dict] = [
    {"id": 1, "name": "Acme onboarding flow", "status": "active", "owner": "Dana"},
    {"id": 2, "name": "Billing reconciliation", "status": "review", "owner": "Priya"},
    {"id": 3, "name": "Q3 analytics export", "status": "done", "owner": "Marco"},
]
_NEXT_ID = [4]

STATS = [
    {"label": "Total items", "value": "128", "delta": "+12%", "dir": "up"},
    {"label": "Active", "value": "34", "delta": "+4", "dir": "up"},
    {"label": "In review", "value": "9", "delta": "-2", "dir": "down"},
    {"label": "Avg. cycle", "value": "2.4d", "delta": "-0.3d", "dir": "up"},
]

# Roadmap surface — every generated app advertises what's built vs. coming.
ROADMAP = [
    {"title": "Core dashboard + items", "state": "done", "note": "Shipped in v0.1"},
    {"title": "Search & filters", "state": "progress", "note": "In this iteration"},
    {"title": "Auth & roles", "state": "planned", "note": "Next iteration"},
    {"title": "Exports & reporting", "state": "planned", "note": "Backlog"},
]


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "pages/dashboard.html", ctx(request, "dashboard", stats=STATS, items=_ITEMS[:5]))


@app.get("/items", response_class=HTMLResponse)
def items_page(request: Request):
    return templates.TemplateResponse(request, "pages/items.html", ctx(request, "items", items=_ITEMS))


@app.post("/items", response_class=HTMLResponse)
def create_item(request: Request, name: str = Form(...), owner: str = Form("—")):
    item = {"id": _NEXT_ID[0], "name": name.strip() or "Untitled", "status": "active", "owner": owner.strip() or "—"}
    _NEXT_ID[0] += 1
    _ITEMS.append(item)
    html = templates.get_template("partials/item_row.html").render(ctx(request, "items", item=item))
    return HTMLResponse(html, headers={"X-Toast": f"Added '{item['name']}'"})


@app.delete("/items/{item_id}", response_class=HTMLResponse)
def delete_item(item_id: int):
    global _ITEMS
    _ITEMS = [i for i in _ITEMS if i["id"] != item_id]
    return HTMLResponse("", headers={"X-Toast": "Item removed"})


@app.get("/roadmap", response_class=HTMLResponse)
def roadmap_page(request: Request):
    return templates.TemplateResponse(request, "pages/roadmap.html", ctx(request, "roadmap", roadmap=ROADMAP))


@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "ok"
