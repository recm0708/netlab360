"""Catálogo cerrado para pruebas activas; no ejecuta comandos ni modifica red."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    namespace: str
    address: str
    gateway: str
    interface: str = "eth0"


@dataclass(frozen=True)
class Route:
    origin: str
    destination: str


@dataclass(frozen=True)
class Profile:
    packets: int = 0
    hops: int = 0
    duration_s: int = 0
    bitrate_bps: int = 0
    timeout_s: int = 0


# Identidades comprobadas en el inventario operacional.
ENDPOINTS = {
    "HQ": Endpoint("nl360-s02-h-hq-120", "10.70.20.20", "10.70.20.1"),
    "S1": Endpoint("nl360-s02-h-s1-220", "10.71.20.20", "10.71.20.1"),
    "S2": Endpoint("nl360-s02-h-s2-320", "10.72.20.20", "10.72.20.1"),
    "FRONTAL_HQ": Endpoint("nl360-s05-ha-fe", "10.70.20.23", "10.70.20.1"),
}
ROUTES = {
    "HQ_A_S1": Route("HQ", "S1"),
    "HQ_A_S2": Route("HQ", "S2"),
    "S2_A_FRONTAL_HQ": Route("S2", "FRONTAL_HQ"),
}
PROFILES = {
    "test.ping.short": Profile(packets=4, timeout_s=10),
    "test.ping.long": Profile(packets=20, timeout_s=30),
    "test.traceroute": Profile(hops=12, timeout_s=30),
    "test.http": Profile(timeout_s=5),
    "test.iperf.tcp": Profile(duration_s=10, bitrate_bps=20_000_000, timeout_s=25),
    "test.iperf.udp": Profile(duration_s=10, bitrate_bps=20_000_000, timeout_s=25),
}
HTTP_PATH = "/api/v1/service"
HTTP_PORT = 8080
IPERF_PORT = 5201
MAX_CONCURRENT_ACTIVE_TESTS = 1


def resolve(action: str, route: str) -> tuple[Endpoint, Endpoint, Profile]:
    """Aceptar exclusivamente identificadores enumerados, nunca IP o URL libre."""
    if type(action) is not str or type(route) is not str:
        raise ValueError("INVALID_PROBE_SELECTION")
    if action not in PROFILES or route not in ROUTES:
        raise ValueError("INVALID_PROBE_SELECTION")
    if action == "test.http" and route != "S2_A_FRONTAL_HQ":
        raise ValueError("INVALID_PROBE_SELECTION")
    if action.startswith("test.iperf.") and route not in ("HQ_A_S1", "HQ_A_S2"):
        raise ValueError("INVALID_PROBE_SELECTION")
    pair = ROUTES[route]
    return ENDPOINTS[pair.origin], ENDPOINTS[pair.destination], PROFILES[action]


def catalog() -> list[dict]:
    """Publicar combinaciones permitidas como candidatos, no pruebas ejecutables."""
    from dataclasses import asdict

    rows = []
    for action in PROFILES:
        for route in ROUTES:
            try:
                origin, destination, profile = resolve(action, route)
            except ValueError:
                continue
            rows.append({"action": action, "route": route,
                         "source": asdict(origin), "destination": asdict(destination),
                         "limits": asdict(profile), "execution_enabled": False})
    return rows
