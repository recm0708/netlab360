"""Catálogo de sondas y cálculo provisional basado en observaciones, no en SLA."""
from .probe_catalog import ROUTES, ENDPOINTS, HTTP_PORT, HTTP_PATH

CADENCE_S = 10
WINDOWS_MIN = (5, 15, 60)
TARGET_PCT = 99
PROBES = {
    "hq-s1-icmp": ("HQ_A_S1", "icmp_v4"),
    "hq-s2-icmp": ("HQ_A_S2", "icmp_v4"),
    "s2-hq-icmp": ("S2_A_FRONTAL_HQ", "icmp_v4"),
    "s2-hq-tcp": ("S2_A_FRONTAL_HQ", "tcp_v4"),
    "s2-hq-http": ("S2_A_FRONTAL_HQ", "http_service"),
}


def probe(identifier):
    """Derivar destino literal y contexto de las rutas autorizadas."""
    if type(identifier) is not str or identifier not in PROBES:
        raise ValueError("INVALID_OBSERVATION_SELECTION")
    route, module = PROBES[identifier]
    pair = ROUTES[route]
    src, dst = ENDPOINTS[pair.origin], ENDPOINTS[pair.destination]
    target = dst.address
    if module == "tcp_v4":
        target += f":{HTTP_PORT}"
    elif module == "http_service":
        target = f"http://{target}:{HTTP_PORT}{HTTP_PATH}"
    return {"id": identifier, "route": route, "origin": pair.origin,
            "namespace": src.namespace, "module": module, "target": target}


def summarize(minutes, scrape_count, scrape_ok, probe_count, probe_ok):
    """Separar fallos medidos de ausencia de evidencia; presupuesto provisional."""
    if type(minutes) is not int or minutes not in WINDOWS_MIN:
        raise ValueError("INVALID_SLO_WINDOW")
    counts = (scrape_count, scrape_ok, probe_count, probe_ok)
    if any(type(n) is not int or n < 0 for n in counts):
        raise ValueError("INVALID_SLO_COUNTS")
    if not 0 <= probe_ok <= probe_count <= scrape_ok <= scrape_count:
        raise ValueError("INCONSISTENT_SLO_COUNTS")
    nominal = minutes * 60 // CADENCE_S
    failed = probe_count - probe_ok
    allowance = probe_count * (100 - TARGET_PCT) // 100
    pct = 100 * probe_ok / probe_count if probe_count else None
    burn = (failed / probe_count) / ((100 - TARGET_PCT) / 100) if probe_count else None
    quality = ("ABSENT" if not scrape_count else "PARTIAL"
               if scrape_count != nominal or probe_count != scrape_count else "OBSERVED")
    return {"window_minutes": minutes, "target_pct": TARGET_PCT,
            "cadence_s": CADENCE_S, "nominal_slots": nominal,
            "scrape_count": scrape_count, "scrape_ok": scrape_ok,
            "probe_count": probe_count, "probe_ok": probe_ok,
            "probe_fail": failed, "unobserved_scrapes": scrape_count - probe_count,
            "nominal_shortfall": max(0, nominal - scrape_count),
            "observed_availability_pct": pct, "allowed_failures_observed": allowance,
            "remaining_budget_observed": allowance - failed if probe_count else None,
            "burn_rate_observed": burn, "quality": quality,
            "meets_observed_target": pct >= TARGET_PCT if pct is not None and quality == "OBSERVED" else None,
            "assessment": "PROVISIONAL_LAB_TARGET"}
