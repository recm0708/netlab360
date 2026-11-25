"""Arranque exclusivo del servicio web dedicado, con recuperación conservadora."""
from contextlib import contextmanager
import fcntl
import os
import stat

from . import broker_client, jobs, storage
from .main import create_app


@contextmanager
def dedicated_app(directory, port=9145):
    """No recuperar trabajos mientras otro proceso conserve la instancia."""
    broker_client.check_identity()
    storage.inspect(directory)
    lock_path = directory / "web-instance.lock"
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
            raise ValueError("UNSAFE_WEB_INSTANCE_LOCK")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        jobs.recover_interrupted(directory)
        yield create_app(directory, job_transport=broker_client.request,
                         job_stream=broker_client.request_stream, console_port=port)
    finally:
        os.close(fd)
