"""Contrato acotado de progreso real de contenido y respuesta final del broker."""
import math

from .content_executor import PROFILES
from .transfer_executor import PROFILES as IPERF_PROFILES

STREAM_ACTIONS = frozenset(("test.content.tcp", "test.iperf.tcp", "test.iperf.udp"))

MAX_EVENTS = 256
MAX_FRAME = 262144


def sample(value, profile, previous=None):
    """Aceptar únicamente contadores de aplicación crecientes y tiempo medido."""
    if profile in IPERF_PROFILES:
        return iperf_sample(value, profile, previous)
    if type(value) is not dict or set(value) != {"role", "bytes", "elapsed_s"}:
        raise ValueError("INVALID_PROGRESS")
    role, total, elapsed = value["role"], value["bytes"], value["elapsed_s"]
    target = PROFILES.get(profile)
    if (role not in ("sender", "receiver") or target is None
            or type(total) is not int or not 0 < total <= target
            or type(elapsed) not in (int, float) or not math.isfinite(elapsed)
            or not 0 < elapsed <= 700):
        raise ValueError("INVALID_PROGRESS")
    if previous is not None and (previous["role"] != role or total <= previous["bytes"]
                                 or elapsed <= previous["elapsed_s"]):
        raise ValueError("NON_MONOTONIC_PROGRESS")
    base_bytes = previous["bytes"] if previous else 0
    base_time = previous["elapsed_s"] if previous else 0
    rate = (total - base_bytes) * 8 / (elapsed - base_time) / 1e6
    if not math.isfinite(rate):
        raise ValueError("INVALID_PROGRESS_RATE")
    return {"role": role, "bytes": total, "elapsed_s": elapsed, "mbps": round(rate, 3)}

def iperf_sample(value, profile, previous=None):
    """Validar intervalos nativos, incluidos intervalos sin bytes y excedentes medidos."""
    fields = {"role", "bytes", "elapsed_s", "mbps", "interval_bytes", "start_s"}
    if type(value) is not dict or set(value) != fields:
        raise ValueError("INVALID_IPERF_PROGRESS")
    role, total, elapsed = value["role"], value["bytes"], value["elapsed_s"]
    start, interval, rate = value["start_s"], value["interval_bytes"], value["mbps"]
    _, _, _, bitrate, _, timeout = IPERF_PROFILES[profile]
    if (role not in ("sender", "receiver") or type(total) is not int
            or type(interval) is not int or not 0 <= interval <= total <= bitrate * timeout // 4
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in (start, elapsed, rate))
            or not 0 <= start < elapsed <= timeout or rate < 0):
        raise ValueError("INVALID_IPERF_PROGRESS")
    if previous is not None:
        if (previous["role"] != role or elapsed <= previous["elapsed_s"]
                or start + 0.02 < previous["elapsed_s"]
                or total != previous["bytes"] + interval):
            raise ValueError("NON_MONOTONIC_IPERF_PROGRESS")
    elif total != interval:
        raise ValueError("INVALID_IPERF_INITIAL_COUNTER")
    return dict(value)
