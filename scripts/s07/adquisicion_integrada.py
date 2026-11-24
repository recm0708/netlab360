"""Adquisición integrada de S07 y evaluación de vigencia, sin acciones de red."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import math
import time

import adaptadores_noc as noc
import adaptador_prometheus as prom
import adaptador_frr as frr
from contrato_eventos import SOURCES, normalize_batch, utc
from almacen_eventos import checked_event, stream_key

EXPECTED = {"NOC_S05":19, "IA_S06":2, "PROMETHEUS_S04":23, "FRR_S02":14}
WINDOW_SCHEMA = "NETLAB360_S07_WINDOW_V1"
MAX_DURATION = 30
MAX_SPAN = 60


def now():
    return datetime.now(timezone.utc).isoformat()


def assess(event, as_of):
    """Evaluar vigencia sin cambiar identidad, calidad o estado históricos."""
    e = checked_event(event)
    end = utc(as_of)
    if utc(e["received_at_utc"]) > end:
        return "AFTER_WINDOW", None
    if e["quality"] != "VALID":
        return e["quality"], None
    age = (end - utc(e["observed_at_utc"])).total_seconds()
    if age < 0:
        return "FUTURE", round(age, 3)
    if age > SOURCES[e["source"]]["max_age"]:
        return "STALE", round(age, 3)
    return "ELIGIBLE", round(age, 3)


def evaluate_window(batch, started, ended, elapsed):
    start, end = utc(started), utc(ended)
    duration = (end-start).total_seconds()
    if (type(elapsed) not in (float,int) or not math.isfinite(elapsed)
            or elapsed < 0 or duration < 0 or abs(duration-elapsed)>2):
        raise ValueError("WINDOW_CLOCK_INVALID")
    if (batch.get("schema")!="NETLAB360_S07_EVENT_BATCH_V1"
            or batch.get("mode")!="READ_ONLY"
            or batch.get("network_mutations_authorized") is not False):
        raise ValueError("WINDOW_BATCH_INVALID")
    events = [checked_event(e) for e in batch["events"]]
    if (Counter(e["source"] for e in events)!=EXPECTED
            or len({stream_key(e) for e in events})!=sum(EXPECTED.values())
            or len({e["event_id"] for e in events})!=sum(EXPECTED.values())):
        raise ValueError("WINDOW_INVENTORY_INVALID")
    rows, valid_times = [], []
    for e in events:
        if not start <= utc(e["received_at_utc"]) <= end:
            raise ValueError("RECEPTION_OUTSIDE_WINDOW")
        status, age = assess(e, ended)
        if status == "ELIGIBLE":
            valid_times.append(utc(e["observed_at_utc"]))
        rows.append({"event_id":e["event_id"],"source":e["source"],
                     "subject":e["subject"],"resource_id":e["resource_id"],
                     "eligibility":status,"age_at_end_seconds":age})
    span = (max(valid_times)-min(valid_times)).total_seconds() if valid_times else None
    bounded = (elapsed<=MAX_DURATION and duration<=MAX_DURATION
               and span is not None and span<=MAX_SPAN)
    return {"schema":WINDOW_SCHEMA,"mode":"READ_ONLY","started_at_utc":start.isoformat(),
            "ended_at_utc":end.isoformat(),"elapsed_seconds":round(elapsed,6),
            "observation_span_seconds":round(span,6) if span is not None else None,
            "temporal_gate":bounded,"simultaneous_measurement":False,
            "by_eligibility":dict(Counter(r["eligibility"] for r in rows)),
            "rows":rows,"network_mutations_authorized":False}


def collect():
    started = now()
    tick = time.monotonic()
    raw_frr, batch_frr = frr.collect()  # Las guardas de propiedad/gestión deben aprobarse.
    events = list(batch_frr["events"])
    sources = dict(batch_frr["sources"])
    raw = {"FRR_S02":raw_frr}
    for source, reader, projector in (
        ("NOC_S05",lambda:noc.read_source("NOC_S05"),noc.graph_events),
        ("IA_S06",lambda:noc.read_source("IA_S06"),noc.ia_events),
        ("PROMETHEUS_S04",prom.read_prometheus,prom.project),
    ):
        payload, received, status = reader()
        raw[source] = {"payload":payload,"received_at_utc":received,"transport":status}
        if source=="PROMETHEUS_S04":
            raw[source]["query"]=prom.QUERY
        sources[source]=status
        events.extend(projector(payload,received))
    frr.management()
    ended = now()
    elapsed = time.monotonic()-tick
    batch = normalize_batch(events)
    batch.update(mode="READ_ONLY",sources=sources)
    window = evaluate_window(batch,started,ended,elapsed)
    return {"raw":raw,"batch":batch,"window":window}


def main():
    result=collect()
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=="__main__":
    main()
