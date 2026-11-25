"""Documentación OpenAPI de operador y recursos Swagger locales."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from . import sessions, swagger_assets
from .auth_http import COOKIE

CSP = ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "connect-src 'self'; img-src data:; font-src 'self' data:; "
       "base-uri 'none'; form-action 'none'; frame-ancestors 'none'; object-src 'none'")

PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NETLAB360 | Documentación API</title>
<link rel="stylesheet" href="/docs/assets/swagger-ui.css">
</head><body>
<header><p><a href="/debug">Volver al diagnóstico técnico</a></p>
<p>Documentación interactiva. Las consultas GET respetan los permisos y límites del servidor.
Las operaciones de sesión se muestran únicamente como referencia.</p></header>
<div id="swagger-ui"></div>
<script src="/docs/assets/swagger-ui-bundle.js"></script>
<script src="/docs/init.js"></script>
</body></html>"""

INIT = """/* Inicialización local de Swagger UI: sin destinos ni escrituras libres. */
SwaggerUIBundle({
  url: "/openapi.json",
  dom_id: "#swagger-ui",
  deepLinking: true,
  validatorUrl: null,
  persistAuthorization: false,
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
        data = app.openapi()
        return JSONResponse(data)

    @app.get("/docs", include_in_schema=False)
    def docs(request: Request):
        authorize(request)
        try:
            for name in swagger_assets.ASSETS:
                swagger_assets.asset(directory, name)
        except (OSError, ValueError):
            raise HTTPException(503) from None
        return HTMLResponse(PAGE, headers={"Content-Security-Policy": CSP})

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
