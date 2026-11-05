"""Public platform-level PWA asset routes."""

import base64
from pathlib import Path

from fastapi import APIRouter, Depends, Response

import app as core
from fastapi.responses import HTMLResponse


router = APIRouter()


def _read_pwa_asset(filename: str) -> str:
    """Read one fixed, public PWA asset; callers cannot choose a filesystem path."""
    asset_path = Path(__file__).resolve().parents[1] / "static" / filename
    return asset_path.read_text(encoding="utf-8")


@router.get("/manifest.webmanifest")
def pwa_manifest():
    return Response(_read_pwa_asset("manifest.webmanifest"), media_type="application/manifest+json")


@router.get("/service-worker.js")
def pwa_service_worker():
    return Response(
        _read_pwa_asset("service-worker.js"),
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@router.get("/offline.html")
def pwa_offline_page():
    return HTMLResponse(_read_pwa_asset("offline.html"))


@router.get("/app-icon.svg")
def pwa_app_icon():
    return Response(_read_pwa_asset("app-icon.svg"), media_type="image/svg+xml")


@router.get("/apple-touch-icon.png")
def pwa_apple_touch_icon():
    encoded = _read_pwa_asset("apple-touch-icon.png.b64").strip()
    return Response(base64.b64decode(encoded, validate=True), media_type="image/png")


@router.get("/setup/health")
def setup_health(u: dict = Depends(core.user)):
    core._require_firm_setup_runtime()
    core.require_admin(u)
    return core._setup_health_report()
