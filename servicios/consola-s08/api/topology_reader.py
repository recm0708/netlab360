"""Proyección autenticable del grafo NOC, sin acceso privilegiado ni mutaciones."""
from . import readers
from .contracts import source_metadata

SITES = ("HQ", "S1", "S2")
VLANS = {site: tuple(100*i+j for j in (10, 20, 30))
         for i, site in enumerate(SITES, 1)}
NODES = {**{f"R-{site}": (site, "router") for site in SITES},
         **{f"SW-{site}": (site, "switch") for site in SITES},
         **{f"H-{site}-{vid}": (site, "host") for site in SITES for vid in VLANS[site]},
         "BACKEND_HQ": ("HQ", "server"), "FRONTAL_HQ": ("HQ", "server"),
         "BACKEND_S1": ("S1", "server")}
LINKS = {**{f"TRUNK-{s}": (f"R-{s}", f"SW-{s}", "lan") for s in SITES},
         **{f"ACCESS-{s}-{v}": (f"SW-{s}", f"H-{s}-{v}", "access")
            for s in SITES for v in VLANS[s]},
         **{f"WAN-{role}-HQ-{s}": ("R-HQ", f"R-{s}", "wan")
            for s in ("S1", "S2") for role in ("PRIMARIA", "RESPALDO")},
         "S05-HA-ACCESO-HQ": ("SW-HQ", "BACKEND_HQ", "access"),
         "S05-HA-ACCESO-S1": ("SW-S1", "BACKEND_S1", "access"),
         "S05-HA-ACCESO-FRONTAL": ("SW-HQ", "FRONTAL_HQ", "access"),
         "S05-HA-HTTP-PRINCIPAL": ("FRONTAL_HQ", "BACKEND_HQ", "redundancy"),
         "S05-HA-HTTP-RESPALDO": ("FRONTAL_HQ", "BACKEND_S1", "redundancy")}
WAN_GATEWAYS = {"WAN-PRIMARIA-HQ-S1": "10.78.0.2",
                "WAN-RESPALDO-HQ-S1": "10.78.0.6",
                "WAN-PRIMARIA-HQ-S2": "10.78.0.10",
                "WAN-RESPALDO-HQ-S2": "10.78.0.14"}


def bounded(value, limit=180):
    """No reenviar metadatos arbitrarios, controles ni textos extensos."""
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError("INVALID_TEXT")
    return value


def enum(value, options):
    if value not in options:
        raise ValueError("INVALID_VALUE")
    return value


def indexed(rows, expected):
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError("INVALID_INVENTORY")
    result = {}
    for row in rows:
        key = row["id"]
        if key not in expected or key in result:
            raise ValueError("INVALID_ID")
        result[key] = row
    return result


def meta(received, transport, stamp):
    return source_metadata(source="NOC_S05", received_at_utc=received,
                           transport=transport, observed_at_utc=stamp)


def project(payload, received, transport):
    """Conservar inventario y separar vigencia, FIB, HTTP y estado administrativo."""
    root = readers.obj(payload)
    result = {"project": "NETLAB360", "schema_version": 1,
              "source": "NOC", "network_mutations_authorized": False,
              "traffic_measured": False, "nodes": [], "links": []}
    generation = meta(received, transport, root.get("observed_at_utc"))
    result["graph"] = generation
    result["telemetry"] = meta(received, "UNAVAILABLE", None)
    result["http"] = meta(received, "UNAVAILABLE", None)
    result["routing_available"] = False
    result["warning_count"] = 0
    if transport != "OK":
        return result
    try:
        if root["project"] != "NETLAB360" or root["phase"] != "S05" or type(root["schema_version"]) is not int or root["schema_version"] != 1:
            raise ValueError("INVALID_SOURCE")
        nodes = indexed(root["nodes"], NODES)
        links = indexed(root["links"], LINKS)
        tele, routing, ha = (root[key] for key in ("telemetry", "routing", "ha_service"))
        if routing["traffic_measured"] is not False:
            raise ValueError("INVALID_SCOPE")
        warnings = root["source_warnings"]
        if not isinstance(warnings, list) or len(warnings) > 32:
            raise ValueError("INVALID_WARNINGS")
        result["warning_count"] = len(warnings)
        result["telemetry"] = meta(received, "OK" if tele["available"] is True else "UNAVAILABLE", tele["last_sample_utc"])
        result["http"] = meta(received, "OK" if ha["available"] is True else "UNAVAILABLE", ha["observed_at_utc"])
        current = generation["quality"] == "VALID"
        fresh = current and result["telemetry"]["quality"] == "VALID"
        fresh_ha = current and result["http"]["quality"] == "VALID"
        # La FIB es una lectura asociada a la generación, no un contador de tráfico.
        fib = fresh and routing["available"] is True
        result["routing_available"] = fib
        for key, row in nodes.items():
            site, kind = NODES[key]
            if (row["site"], row["type"]) != (site, kind):
                raise ValueError("INVALID_NODE")
            status = enum(row["status"], ("running", "offline", "unknown") if kind in ("router", "server")
                          else ("namespace-present", "offline", "unknown"))
            verified = fresh if kind == "router" else fresh_ha if kind == "server" else current and root["namespaces_observable"] is True
            entry = {"id": key, "site": site, "type": kind, "label": bounded(row["label"], 80),
                     "detail": bounded(row["detail"]), "status": status if verified else "unknown",
                     "scope": {"router": "CONTAINER_ONLY", "switch": "NAMESPACE_ONLY",
                               "host": "NAMESPACE_ONLY", "server": "HTTP_FROM_S2"}[kind]}
            if kind == "host":
                entry["vlan"] = int(key.rsplit("-", 1)[1])
                if row["vlan"] != entry["vlan"]:
                    raise ValueError("INVALID_VLAN")
                entry["gateway"] = bounded(row["gateway"], 45)
                admin = enum(row["vlan_admin"], ("admin-up", "admin-down", "unknown"))
                entry["vlan_admin"] = admin if fresh else "unknown"
            if kind == "server":
                selection = enum(row["application_selection"], ("selected", "standby", "unknown"))
                entry["application_selection"] = selection if fresh_ha else "unknown"
            result["nodes"].append(entry)
        for key, row in links.items():
            a, b, kind = LINKS[key]
            if (row["from"], row["to"], row["type"]) != (a, b, kind):
                raise ValueError("INVALID_LINK")
            status = enum(row["status"], ("admin-up", "admin-down", "offline", "running", "unknown"))
            entry = {"id": key, "from": a, "to": b, "type": kind,
                     "role": bounded(row["role"], 48), "detail": bounded(row["detail"]),
                     "status": "unknown", "scope": "INVENTORY_ONLY"}
            if kind == "wan":
                expected_role = "primary" if "PRIMARIA" in key else "backup"
                if row["role"] != expected_role or status not in ("admin-up", "admin-down", "offline", "unknown"):
                    raise ValueError("INVALID_WAN")
                entry.update(status=status if fresh else "unknown", scope="ADMIN_STATE_ONLY",
                             a=bounded(row["a"], 45), b=bounded(row["b"], 45))
                selection = enum(row["route_selection"], ("selected", "standby", "unavailable", "unknown"))
                gateway = row.get("route_gateway")
                if selection == "selected" and (gateway != WAN_GATEWAYS[key] or status != "admin-up"):
                    raise ValueError("INVALID_FIB")
                entry.update(route_selection=selection if fib else "unknown",
                             route_gateway=gateway if fib and selection == "selected" else None)
                # El texto original incluye afirmaciones de ruta: separamos la parte estática.
                entry["detail"] = entry["detail"].split(" · ruta", 1)[0]
            elif kind == "redundancy":
                if status not in ("running", "offline", "unknown"):
                    raise ValueError("INVALID_HTTP")
                selection = enum(row["application_selection"], ("selected", "standby", "unknown"))
                entry.update(status=status if fresh_ha else "unknown", scope="HTTP_FROM_S2",
                             application_selection=selection if fresh_ha else "unknown")
            result["links"].append(entry)
        return result
    except (KeyError, TypeError, ValueError, AttributeError):
        result.update(nodes=[], links=[], graph=meta(received, "INVALID", None),
                      telemetry=meta(received, "INVALID", None), http=meta(received, "INVALID", None),
                      routing_available=False, warning_count=0)
        return result


def collect():
    """Reutilizar exclusivamente la ruta NOC local ya delimitada."""
    return project(*readers.fetch("NOC_S05"))
