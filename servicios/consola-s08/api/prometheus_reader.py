"""Proyección de métricas S04 reutilizando el adaptador validado de S07."""
from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
from urllib.parse import urlsplit

from . import readers

# Cargamos el paquete propio por ruta relativa al repositorio, sin añadir
# directorios globales a sys.path ni resolver módulos desde el cliente.
PACKAGE = "_netlab360_s08_shared_s07"
DIRECTORY = Path(__file__).resolve().parents[3] / "scripts/s07"
if PACKAGE not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        PACKAGE, DIRECTORY / "__init__.py", submodule_search_locations=[str(DIRECTORY)])
    if spec is None or spec.loader is None:
        raise ImportError("S07_SHARED_PACKAGE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(PACKAGE, None)
        raise

adapter = importlib.import_module(PACKAGE + ".adaptador_prometheus")
endpoint = urlsplit(adapter.URL)
if (endpoint.scheme, endpoint.netloc, endpoint.path) != (
        "http", "127.0.0.1:9091", "/api/v1/query"):
    raise ValueError("INVALID_PROMETHEUS_ENDPOINT")
PATH = endpoint.path + "?" + endpoint.query


def project(payload, received, transport):
    """Mantener la calidad temporal y la semántica S07 en el contrato S08."""
    root = readers.obj(payload)
    data = readers.obj(root.get("data"))
    if transport == "OK" and (root.get("status") != "success"
            or root.get("warnings") or data.get("resultType") != "matrix"
            or not isinstance(data.get("result"), list)):
        transport = "INVALID"

    events = adapter.project(root if transport == "OK" else None, received)
    rows = []
    for event in events:
        resource = event["resource_id"]
        scope = {
            "S04-EXPORTER": "SCRAPE_AVAILABILITY",
            "S04-COLLECTOR": "COLLECTOR_READ",
            "MULTISEDE": "ROUTER_EXISTENCE_ONLY",
        }.get(resource)
        if scope is None:
            scope = "ADMIN_STATE_ONLY" if event["subject"] in ("WAN", "VLAN") else "CONTAINER_RUNNING_ONLY"
        # Un scrape ausente no convierte un transporte HTTP correcto en error.
        row = readers.observation("PROMETHEUS_S04", resource, scope, received,
                                  transport, event["observed_at_utc"], event["state"],
                                  event["details"])
        if transport == "OK" and event["quality"] != row["quality"]:
            row.update(quality=event["quality"], state="UNKNOWN", details={})
        rows.append(row)
    return rows


def collect():
    """Consultar la única expresión PromQL autorizada con timestamps de scrape."""
    payload, received, transport = readers._fetch_fixed(9091, PATH, adapter.MAX_BYTES)
    return project(payload, received, transport)
