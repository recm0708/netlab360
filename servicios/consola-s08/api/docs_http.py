"""Documentación OpenAPI de operador y recursos Swagger locales."""
from copy import deepcopy

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pathlib import Path

from .history_reader import GROUPS, WINDOWS
from .debug_http import CATALOG
from . import sessions, swagger_assets
from .auth_http import COOKIE

CSP = ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "connect-src 'self'; img-src data:; font-src 'self' data:; "
       "base-uri 'none'; form-action 'none'; frame-ancestors 'self'; object-src 'none'")

PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NETLAB360 | Documentación API</title>
<link rel="stylesheet" href="/ui/static/styles.css">
<link rel="stylesheet" href="/docs/assets/swagger-ui.css">
<link rel="stylesheet" href="/docs/theme.css">
</head><body>
<header class="docs-heading"><strong>Documentación interactiva</strong>
<p>Sesión de operador activa. No necesita introducir una clave adicional. Expanda una consulta GET, pulse Try it out y Execute. Las operaciones de sesión se documentan sin ejecutarlas aquí.</p></header>
<div id="swagger-ui"></div>
<script src="/docs/assets/swagger-ui-bundle.js"></script>
<script src="/docs/init.js"></script>
</body></html>"""

INIT = """/* Inicialización local de Swagger UI: sin destinos ni escrituras libres. */
if (window.parent !== window) {
  try {
    const theme = window.parent.document.documentElement.dataset.theme;
    if (["light", "dark"].includes(theme)) document.documentElement.dataset.theme = theme;
  } catch { /* El marco conserva la paleta predeterminada. */ }
}
SwaggerUIBundle({
  url: "/openapi.json",
  dom_id: "#swagger-ui",
  deepLinking: true,
  validatorUrl: null,
  queryConfigEnabled: false,
  persistAuthorization: false,
  withCredentials: true,
  showMutatedRequest: false,
  docExpansion: "list",
  supportedSubmitMethods: ["get"],
  tryItOutEnabled: false,
  requestInterceptor: request => {
    const url = new URL(request.url, location.origin);
    if (url.origin !== location.origin || url.username || url.password ||
        (request.method || "GET").toUpperCase() !== "GET") {
      throw new Error("Consulta no autorizada");
    }
    request.credentials = "same-origin";
    return request;
  }
});
"""


def register_docs(app: FastAPI, directory):
    """Mantenemos la documentación deshabilitada en modo de arranque."""
    def authorize(request):
        actor = sessions.resolve(directory, request.cookies.get(COOKIE))
        if actor is None:
            raise HTTPException(401)
        if actor["role"] != "OPERATOR":
            raise HTTPException(403)

    @app.get("/openapi.json", include_in_schema=False)
    def schema(request: Request):
        authorize(request)
        # El esquema describe las rutas registradas, no concede permisos.
        data = deepcopy(app.openapi())
        data["servers"] = [{"url": "/"}]
        data.setdefault("components", {}).setdefault("securitySchemes", {})["SessionCookie"] = {
            "type": "apiKey", "in": "cookie", "name": COOKIE,
            "description": "Sesión iniciada en NETLAB360; el navegador envía su cookie."
        }
        public = {"/healthz", "/api/v1/capabilities", "/api/v1/auth/login"}
        for path, operations in data["paths"].items():
            for method, operation in operations.items():
                if method not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    continue
                if path.startswith("/api/v1/auth/"):
                    tag = "Identidad y sesión"
                elif path.startswith("/api/v1/history/") or path in ("/api/v1/metrics", "/api/v1/alerts"):
                    tag = "Observabilidad"
                elif path.startswith("/api/v1/debug/"):
                    tag = "Diagnóstico técnico"
                elif path in ("/api/v1/diagnostics", "/api/v1/advisory"):
                    tag = "Diagnóstico y consulta asesora"
                elif path in ("/api/v1/topology", "/api/v1/sources"):
                    tag = "Infraestructura"
                else:
                    tag = "Sistema"
                operation["tags"] = [tag]
                allowed = {}
                if path == "/api/v1/history/{group}/{window}":
                    allowed = {"group": list(GROUPS), "window": list(WINDOWS)}
                elif path == "/api/v1/debug/probe/{key}":
                    allowed = {"key": [item[0] for item in CATALOG]}
                for parameter in operation.get("parameters", []):
                    if parameter["in"] == "path" and parameter["name"] in allowed:
                        parameter.setdefault("schema", {})["enum"] = allowed[parameter["name"]]
                if path not in public:
                    operation["security"] = [{"SessionCookie": []}]
                    responses = operation.setdefault("responses", {})
                    responses.setdefault("401", {"description": "Sesión no válida"})
                    responses.setdefault("403", {"description": "Permiso insuficiente"})
                if method != "get":
                    operation["description"] = (
                        operation.get("description", "") +
                        "\n\nOperación documentada; no ejecutable desde Swagger UI."
                    ).strip()
        return JSONResponse(data)

    @app.get("/docs", include_in_schema=False)
    def docs(request: Request):
        authorize(request)
        if not request.query_params:
            return RedirectResponse("/debug?tab=docs", status_code=303)
        if list(request.query_params.multi_items()) != [("embedded", "1")]:
            raise HTTPException(400)
        try:
            for name in swagger_assets.ASSETS:
                swagger_assets.asset(directory, name)
        except (OSError, ValueError):
            raise HTTPException(503) from None
        return HTMLResponse(PAGE, headers={"Content-Security-Policy": CSP})

    @app.get("/docs/theme.css", include_in_schema=False)
    def stylesheet(request: Request):
        authorize(request)
        path = Path(__file__).resolve().parents[1] / "ui/static/swagger-theme.css"
        return Response(path.read_text(encoding="utf-8"), media_type="text/css")

    @app.get("/docs/init.js", include_in_schema=False)
    def initializer(request: Request):
        authorize(request)
        return Response(INIT, media_type="text/javascript")

    @app.get("/docs/assets/{name}", include_in_schema=False)
    def resource(request: Request, name: str):
        authorize(request)
        if name not in swagger_assets.ASSETS:
            raise HTTPException(404)
        try:
            content = swagger_assets.asset(directory, name)
        except (OSError, ValueError):
            raise HTTPException(503) from None
        return Response(content, media_type=swagger_assets.ASSETS[name])
