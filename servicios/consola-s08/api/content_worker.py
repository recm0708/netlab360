"""Emisor y receptor TCP de contenido reproducible, ejecutados sin privilegios."""
import argparse
import hashlib
import json
import os
import socket
import time

PORT = 5202
BLOCK = 65536
VOLUMES = (100_000_000, 500_000_000, 1_000_000_000, 2_000_000_000, 5_000_000_000)
BITRATE = 100_000_000
HQ = "10.70.20.20"
DESTINATIONS = ("10.71.20.20", "10.72.20.20")


def send_stream(conn, volume, bitrate, clock=time.monotonic, pause=time.sleep):
    """Generar bloques deterministas, medir bytes entregados al socket y SHA-256."""
    digest = hashlib.sha256()
    sent = 0
    start = clock()
    while sent < volume:
        size = min(BLOCK, volume - sent)
        data = hashlib.shake_256(b"NETLAB360_CONTENT_V1" + sent.to_bytes(8, "big")).digest(size)
        # Pacing basado en bytes acumulados; no permite recuperar una ráfaga atrasada.
        tick = clock()
        conn.sendall(data)
        digest.update(data)
        sent += size
        delay = size * 8 / bitrate - (clock() - tick)
        if delay > 0:
            pause(delay)
    conn.shutdown(socket.SHUT_WR)
    return {"bytes": sent, "sha256": digest.hexdigest(), "duration_s": clock() - start}


def receive_stream(conn, volume, clock=time.monotonic):
    """Calcular el hash de los bytes realmente recibidos y exigir EOF exacto."""
    digest = hashlib.sha256()
    received = 0
    start = clock()
    while received < volume:
        data = conn.recv(min(BLOCK, volume - received))
        if not data:
            raise ValueError("PREMATURE_EOF")
        digest.update(data)
        received += len(data)
    if conn.recv(1):
        raise ValueError("EXCESS_CONTENT")
    return {"bytes": received, "sha256": digest.hexdigest(), "duration_s": clock() - start}


def main():
    """Aceptar solo roles, identidades y tamaños del laboratorio; sin archivos grandes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("sender", "receiver"), required=True)
    parser.add_argument("--site", choices=DESTINATIONS, required=True)
    parser.add_argument("--volume", type=int, choices=VOLUMES, required=True)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("ROOT_FORBIDDEN")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        if args.role == "sender":
            sock.bind((HQ, 0))
            sock.connect((args.site, PORT))
            result = send_stream(sock, args.volume, BITRATE)
        else:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((args.site, PORT))
            sock.listen(1)
            conn, peer = sock.accept()
            with conn:
                conn.settimeout(10)
                if peer[0] != HQ:
                    raise ValueError("UNAUTHORIZED_PEER")
                result = receive_stream(conn, args.volume)
    result.update(role=args.role, site=args.site, uid=os.geteuid(), target_bytes=args.volume)
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
