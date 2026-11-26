"""Entrada de servicio instalada exclusivamente en una ruta propiedad de root."""
import os
from pathlib import Path
import pwd
import socket
import stat
import sys

ROOT = Path("/usr/local/libexec/netlab360/s08-broker")
API_FILES = (
    "__init__.py", "probe_catalog.py", "probe_executor.py", "transfer_executor.py",
    "content_executor.py", "content_worker.py", "job_contract.py", "probe_broker.py", "broker_transfer.py",
    "broker_stream.py", "stream_protocol.py", "iperf_native.py",
)


def trusted(path, directory=False):
    info = path.lstat()
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    if not kind(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise RuntimeError("UNTRUSTED_INSTALLATION")


def main():
    if os.geteuid() != 0 or Path(__file__) != ROOT / "entry.py":
        raise RuntimeError("INSTALLED_ROOT_SERVICE_REQUIRED")
    for parent in reversed(ROOT.parents):
        trusted(parent, True)
    trusted(ROOT, True)
    trusted(ROOT / "entry.py")
    trusted(ROOT / "api", True)
    if {item.name for item in (ROOT / "api").iterdir()} != set(API_FILES):
        raise RuntimeError("UNEXPECTED_PACKAGE_CONTENT")
    for name in API_FILES:
        trusted(ROOT / "api" / name)
    # El intérprete aislado solo importa desde la copia instalada, nunca desde HOME.
    sys.path.insert(0, str(ROOT))
    from api.probe_broker import serve
    from api.broker_transfer import execute

    allowed_uid = pwd.getpwnam("netlab360-s08-api").pw_uid
    if allowed_uid <= 0:
        raise RuntimeError("INVALID_SERVICE_IDENTITY")
    worker = pwd.getpwnam("netlab360-s08-worker")
    if min(worker.pw_uid, worker.pw_gid) <= 0 or worker.pw_uid == allowed_uid:
        raise RuntimeError("INVALID_WORKER_IDENTITY")
    with socket.socket(fileno=os.dup(0)) as conn:
        serve(conn, allowed_uid, transfer=lambda selection: execute(selection, worker.pw_uid, worker.pw_gid),
              worker=(worker.pw_uid, worker.pw_gid))


if __name__ == "__main__":
    main()
