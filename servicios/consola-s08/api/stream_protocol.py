"""Contrato acotado de progreso real de contenido y respuesta final del broker."""
import math

from .content_executor import PROFILES

MAX_EVENTS = 256
MAX_FRAME = 262144


def sample(value, profile, previous=None):
    """Aceptar únicamente contadores de aplicación crecientes y tiempo medido."""
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
