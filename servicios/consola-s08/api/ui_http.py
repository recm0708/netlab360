"""Rutas visuales explícitas y comprobación de identidad antes de servir la consola."""
from pathlib import Path
from importlib.resources import files
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, Response

from . import sessions
from .auth_http import COOKIE

UI = Path(__file__).resolve().parents[1] / "ui"
PAGES = ("/home", "/topology", "/wan", "/lan", "/services", "/lacp", "/sdn", "/diagnostics", "/observability", "/intelligence", "/incidents", "/copilot", "/system", "/administration", "/debug")
HTML_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; base-uri 'none'; form-action 'none'; "
            "frame-ancestors 'none'; object-src 'none'")


# Plotly genera estilos SVG/CSS dinámicos. Limitamos esta excepción a observabilidad.
DEBUG_CSP = HTML_CSP.replace("frame-ancestors", "frame-src 'self'; frame-ancestors")
PLOT_CSP = HTML_CSP.replace("style-src 'self';", "style-src 'self' 'unsafe-inline'; img-src data: blob:;")

@lru_cache(maxsize=1)
def plotly_asset():
    """Leer solamente el recurso distribuido con la dependencia científica."""
    asset = files("plotly").joinpath("package_data", "plotly.min.js")
    content = asset.read_bytes()
    if not 0 < len(content) <= 30 * 1024 * 1024:
        raise ValueError("INVALID_PLOTLY_ASSET")
    return content


def register_ui(app: FastAPI, directory) -> None:
    """Publicar solo páginas y archivos conocidos; ninguna ruta ejecuta acciones."""
    def authenticated(request: Request) -> bool:
        return sessions.resolve(directory, request.cookies.get(COOKIE)) is not None

    def page(filename: str, csp=HTML_CSP) -> Response:
        return Response((UI / filename).read_text(encoding="utf-8"),
                        media_type="text/html",
                        headers={"Content-Security-Policy": csp})

    @app.get("/", include_in_schema=False)
    def index(request: Request):
        return RedirectResponse("/home" if authenticated(request) else "/login", status_code=303)

    @app.get("/login", include_in_schema=False)
    def login(request: Request):
        if authenticated(request):
            return RedirectResponse("/home", status_code=303)
        return page("login.html")

    def console(request: Request):
        identity = sessions.resolve(directory, request.cookies.get(COOKIE))
        if identity is None:
            return RedirectResponse("/login", status_code=303)
        # La reserva de diagnóstico técnico no amplía los permisos existentes.
        if request.url.path == "/debug" and identity["role"] != "OPERATOR":
            raise HTTPException(403)
        csp = {"/observability": PLOT_CSP, "/debug": DEBUG_CSP}.get(request.url.path, HTML_CSP)
        return page("index.html", csp)

    for path in PAGES:
        app.add_api_route(path, console, methods=["GET"], include_in_schema=False)

    @app.get("/ui/static/styles.css", include_in_schema=False)
    def stylesheet():
        return Response((UI / "static/styles.css").read_text(encoding="utf-8"),
                        media_type="text/css")

    @app.get("/ui/static/app.js", include_in_schema=False)
    def javascript():
        return Response((UI / "static/app.js").read_text(encoding="utf-8"),
                        media_type="text/javascript")

    @app.get("/ui/static/login.js", include_in_schema=False)
    def login_script():
        return Response((UI / "static/login.js").read_text(encoding="utf-8"),
                        media_type="text/javascript")

    @app.get("/ui/static/plotly.js", include_in_schema=False)
    def plotly_script(request: Request):
        if not authenticated(request):
            raise HTTPException(401)
        try:
            content = plotly_asset()
        except (ImportError, OSError, ValueError):
            raise HTTPException(503) from None
        return Response(content, media_type="text/javascript")

    @app.get("/ui/static/history.js", include_in_schema=False)
    def history_script():
        return Response((UI / "static/history.js").read_text(encoding="utf-8"),
                        media_type="text/javascript")

    @app.get("/ui/static/topology.js", include_in_schema=False)
    def topology_script():
        return Response((UI / "static/topology.js").read_text(encoding="utf-8"),
                        media_type="text/javascript")
