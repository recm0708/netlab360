"""Decodificación acotada de los eventos nativos iPerf3 de cada extremo."""
import json

from . import transfer_executor as T


class NativeStream:
    """Conservar intervalos locales y reconstruir el resultado sin imputar muestras."""

    def __init__(self, profile, route, role):
        self.src, self.dst, _, _, client_timeout, server_timeout = T.commands(profile, route)
        if role not in ("sender", "receiver"):
            raise ValueError("INVALID_STREAM_ROLE")
        self.profile, self.route, self.role = profile, route, role
        self.deadline = max(client_timeout, server_timeout)
        self.document = {"intervals": []}
        self.bytes = 0

    def feed(self, frame):
        """Procesar una trama completa; devolver solo progreso observado."""
        if type(frame) is not dict or type(frame.get("data")) is not dict:
            raise ValueError("INVALID_NATIVE_FRAME")
        event, data = frame.get("event"), frame["data"]
        if "end" in self.document:
            raise ValueError("FRAME_AFTER_END")
        if event == "start":
            if "start" in self.document:
                raise ValueError("DUPLICATE_NATIVE_START")
            local, remote = ((self.src, self.dst) if self.role == "sender"
                             else (self.dst, self.src))
            connections = data["connected"]
            if (data["test_start"]["protocol"] != T.PROFILES[self.profile][0]
                    or len(connections) != 1
                    or connections[0]["local_host"] != local.address
                    or connections[0]["remote_host"] != remote.address):
                raise ValueError("NATIVE_IDENTITY_MISMATCH")
            self.document["start"] = data
            return None
        if "start" not in self.document:
            raise ValueError("NATIVE_START_REQUIRED")
        if event == "interval":
            rows = self.document["intervals"]
            normalized = T.intervals({"intervals": [*rows, data]})[-1]
            if normalized["end_s"] > self.deadline:
                raise ValueError("NATIVE_INTERVAL_DEADLINE")
            rows.append(data)
            self.bytes += normalized["bytes"]
            return {"role": self.role, "bytes": self.bytes,
                    "elapsed_s": normalized["end_s"], "mbps": normalized["mbps"],
                    "interval_bytes": normalized["bytes"],
                    "start_s": normalized["start_s"]}
        if event == "end":
            if not self.document["intervals"]:
                raise ValueError("NATIVE_INTERVAL_REQUIRED")
            self.document["end"] = data
            return None
        raise ValueError("UNEXPECTED_NATIVE_EVENT")

    def finish(self):
        """No tratar un flujo truncado como resultado completo."""
        if "end" not in self.document:
            raise ValueError("NATIVE_END_REQUIRED")
        return self.document


def replay(path, profile, route, role):
    """Leer evidencia NDJSON acotada conservando la identidad de cada extremo."""
    with path.open("rb") as handle:
        raw = handle.read(T.MAX_JSON + 1)
    if len(raw) > T.MAX_JSON:
        raise ValueError("NATIVE_OUTPUT_LIMIT")
    stream = NativeStream(profile, route, role)
    samples = []
    for line in raw.splitlines():
        if line.strip():
            sample = stream.feed(json.loads(line))
            if sample is not None:
                samples.append(sample)
    return stream.finish(), samples


def replay_pair(sender, receiver, profile, route):
    """Aplicar el mismo contrato final aceptado anteriormente a ambos extremos."""
    tx, tx_samples = replay(sender, profile, route, "sender")
    rx, rx_samples = replay(receiver, profile, route, "receiver")
    return {"measurement": T.parse_results(profile, route, tx, rx),
            "sender_samples": tx_samples, "receiver_samples": rx_samples}
