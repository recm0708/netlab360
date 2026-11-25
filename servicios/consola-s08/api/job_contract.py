"""Contrato cerrado de trabajos S08; no inicia procesos ni otorga privilegios."""
from dataclasses import dataclass

from . import content_executor, probe_executor, transfer_executor
from .probe_catalog import resolve


@dataclass(frozen=True)
class Selection:
    action: str
    route: str
    profile: str
    deadline_s: int

    def parameters(self):
        return {"action": self.action, "route": self.route, "profile": self.profile}


def select(payload):
    """Aceptar únicamente identificadores enumerados y calcular límites en servidor."""
    if type(payload) is not dict or set(payload) != {"action", "route", "profile"}:
        raise ValueError("INVALID_JOB_PARAMETERS")
    action, route, profile = (payload[k] for k in ("action", "route", "profile"))
    if any(type(x) is not str or len(x) > 64 for x in (action, route, profile)):
        raise ValueError("INVALID_JOB_PARAMETERS")
    if action in probe_executor.ACTIONS and profile == "default":
        _, _, limits = resolve(action, route)
        deadline = limits.timeout_s + 25
    elif action in ("test.iperf.tcp", "test.iperf.udp"):
        _, _, _, _, _, receiver_timeout = transfer_executor.commands(profile, route)
        if transfer_executor.PROFILES[profile][0].lower() != action.rsplit(".", 1)[1]:
            raise ValueError("PROFILE_PROTOCOL_MISMATCH")
        deadline = receiver_timeout + 35
    elif action == "test.content.tcp" and profile in content_executor.PROFILES and route in transfer_executor.ROUTES:
        volume = content_executor.PROFILES[profile]
        deadline = int(volume * 8 / content_executor.BITRATE * 1.5) + 65
    else:
        raise ValueError("INVALID_JOB_SELECTION")
    return Selection(action, route, profile, deadline)


def catalog():
    """Publicar las selecciones aceptables sin afirmar disponibilidad del ejecutor."""
    rows = []
    for action in probe_executor.ACTIONS:
        for route in ("HQ_A_S1", "HQ_A_S2", "S2_A_FRONTAL_HQ"):
            try:
                rows.append(select({"action": action, "route": route, "profile": "default"}))
            except ValueError:
                continue
    for profile, limits in transfer_executor.PROFILES.items():
        for route in transfer_executor.ROUTES:
            rows.append(select({"action": "test.iperf." + limits[0].lower(), "route": route,
                                "profile": profile}))
    for profile in content_executor.PROFILES:
        for route in transfer_executor.ROUTES:
            rows.append(select({"action": "test.content.tcp", "route": route, "profile": profile}))
    return [dict(row.parameters(), deadline_s=row.deadline_s, execution_enabled=False) for row in rows]
