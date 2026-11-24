"""Publicación explícita de la estructura visual sin exponer el árbol del repositorio."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response

UI = Path(__file__).resolve().parents[1] / "ui"
HTML_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; base-uri 'none'; form-action 'none'; "
            "frame-ancestors 'none'; object-src 'none'")


def register_ui(app: FastAPI) -> None:
    """Servir tres recursos fijos; el HTML público no contiene datos privados."""
    @app.get("/", include_in_schema=False)
    def index():
        return Response((UI / "index.html").read_text(encoding="utf-8"),
                        media_type="text/html",
                        headers={"Content-Security-Policy": HTML_CSP})

    @app.get("/ui/static/styles.css", include_in_schema=False)
    def stylesheet():
        return Response((UI / "static/styles.css").read_text(encoding="utf-8"),
                        media_type="text/css")

    @app.get("/ui/static/app.js", include_in_schema=False)
    def javascript():
        return Response((UI / "static/app.js").read_text(encoding="utf-8"),
                        media_type="text/javascript")
