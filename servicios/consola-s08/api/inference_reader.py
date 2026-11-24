"""Inferencia S06 de alcance HQ, mediante el gateway NOC y contrato S07."""
from __future__ import annotations

import importlib

from . import readers, prometheus_reader

adapter = importlib.import_module(prometheus_reader.PACKAGE + ".adaptadores_noc")
PATH = "/api/v1/s06/diagnostics"


def project(payload, received, transport):
    """Conservar abstención y procedencia, sin elevar predicciones a incidentes."""
    root = readers.obj(payload)
    if transport == "OK" and (
            root.get("schema") != "NETLAB360_S06_047_NOC_AI_ADAPTER_V1"
            or root.get("mode") != "READ_ONLY_EXPLORATORY"
            or root.get("network_mutations_authorized") is not False
            or root.get("production_deployment_authorized") is not False
            or root.get("graph_s05_independent") is not True):
        transport = "INVALID"
    rows = []
    for event in adapter.ia_events(root if transport == "OK" else None, received):
        details = {**event["details"], "ground_truth": "UNKNOWN",
                   "production_deployment_authorized": False}
        row = readers.observation("IA_S06", event["resource_id"],
                                  "HQ_CLIENT_EGRESS_NETWORK_STATE", received, transport,
                                  event["observed_at_utc"], event["state"], details)
        if transport == "OK" and row["quality"] != event["quality"]:
            row.update(quality=event["quality"], state="UNKNOWN", details={})
        rows.append(row)
    return rows


def collect():
    """Consultar exclusivamente el gateway existente; no activar modelos ni ping."""
    payload, received, transport = readers._fetch_fixed(9130, PATH, readers.MAX_BYTES)
    return project(payload, received, transport)
