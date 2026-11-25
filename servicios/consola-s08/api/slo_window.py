"""Evaluación de ventanas con timestamps reales de scrape, sin imputar ausencias."""
import math

from . import slo_contract as S


def samples(rows, start, end):
    """Normalizar una serie binaria y rechazar timestamps ambiguos."""
    if not isinstance(rows, list) or len(rows) > 400:
        raise ValueError("INVALID_WINDOW_SERIES")
    result = {}
    for item in rows:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("INVALID_WINDOW_SAMPLE")
        timestamp, value = item
        if (type(timestamp) not in (float, int) or not math.isfinite(timestamp)
                or not start < timestamp <= end or type(value) not in (str, int, float)):
            raise ValueError("INVALID_WINDOW_SAMPLE")
        if isinstance(value, str) and value not in ("0", "1"):
            raise ValueError("INVALID_WINDOW_VALUE")
        value = float(value)
        if value not in (0, 1):
            raise ValueError("INVALID_WINDOW_VALUE")
        # Prometheus representa los timestamps con precisión de milisegundos.
        key = round(timestamp * 1000)
        if key in result:
            raise ValueError("DUPLICATE_WINDOW_TIMESTAMP")
        result[key] = int(value)
    return result


def evaluate(identifier, minutes, end, up, probes):
    """Emparejar muestras por timestamp y comprobar cobertura de cada intervalo."""
    S.probe(identifier)
    if type(minutes) is not int or minutes not in S.WINDOWS_MIN:
        raise ValueError("INVALID_SLO_WINDOW")
    if type(end) not in (int, float) or not math.isfinite(end) or end <= minutes * 60:
        raise ValueError("INVALID_WINDOW_END")
    start = end - minutes * 60
    scrape = samples(up, start, end)
    probe = samples(probes, start, end)
    if any(scrape.get(key) != 1 for key in probe):
        raise ValueError("UNPAIRED_PROBE_SAMPLE")
    row = S.summarize(minutes, len(scrape), sum(scrape.values()), len(probe), sum(probe.values()))
    slots = {}
    for key in scrape:
        # Ventana (inicio, fin]: un scrape por intervalo nominal de diez segundos.
        slot = math.ceil((key / 1000 - start) / S.CADENCE_S) - 1
        slots[slot] = slots.get(slot, 0) + 1
    missing = row["nominal_slots"] - len(slots)
    duplicate = sum(count - 1 for count in slots.values())
    row.update(probe_id=identifier, window_start_unix=start, window_end_unix=end,
               missing_slots=missing, duplicate_slots=duplicate,
               latest_scrape_unix=max(scrape) / 1000 if scrape else None)
    if missing or duplicate:
        row["quality"] = "PARTIAL" if scrape else "ABSENT"
        row["meets_observed_target"] = None
    return row
