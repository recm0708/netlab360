"""Instalación explícita de recursos Swagger UI, sin ejecutar scripts de npm."""
import argparse
import base64
from hashlib import sha512, sha256
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler

from . import storage

VERSION = "5.34.1"
REGISTRY = "https://registry.npmjs.org/swagger-ui-dist"
TARBALL = REGISTRY + "/-/swagger-ui-dist-" + VERSION + ".tgz"
ASSETS = {"swagger-ui-bundle.js": "text/javascript", "swagger-ui.css": "text/css"}
MAX_BYTES = 30 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    """No seguimos redirecciones a otros orígenes."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download(url, limit):
    if url not in (REGISTRY + "/" + VERSION, TARBALL):
        raise ValueError("INVALID_ASSET_URL")
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(url, timeout=30) as response:
        raw = response.read(limit + 1)
    if not 0 < len(raw) <= limit:
        raise ValueError("INVALID_DOWNLOAD_SIZE")
    return raw


def extract(raw, integrity):
    """Verificamos el paquete antes de leer dos miembros explícitos."""
    expected = "sha512-" + base64.b64encode(sha512(raw).digest()).decode("ascii")
    if integrity != expected:
        raise ValueError("INVALID_PACKAGE_INTEGRITY")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for name in ASSETS:
            member = archive.getmember("package/" + name)
            if not member.isfile() or not 0 < member.size <= MAX_BYTES:
                raise ValueError("INVALID_ASSET_MEMBER")
            with archive.extractfile(member) as stream:
                result[name] = stream.read(MAX_BYTES + 1)
            if len(result[name]) != member.size:
                raise ValueError("INVALID_ASSET_SIZE")
    return result


def folder(directory):
    path = directory / "swagger-ui"
    storage._owned_directory(path, private=True)
    return path


def asset(directory, name):
    if name not in ASSETS:
        raise ValueError("INVALID_ASSET")
    path = folder(directory) / name
    storage._owned_database(path)
    with path.open("rb") as stream:
        content = stream.read(MAX_BYTES + 1)
    if not 0 < len(content) <= MAX_BYTES:
        raise ValueError("INVALID_ASSET_SIZE")
    return content


def install(directory):
    storage.inspect(directory)
    metadata = json.loads(download(REGISTRY + "/" + VERSION, 1024 * 1024))
    if (metadata["name"] != "swagger-ui-dist" or metadata["version"] != VERSION
            or metadata["dist"]["tarball"] != TARBALL):
        raise ValueError("INVALID_PACKAGE_METADATA")
    integrity = metadata["dist"]["integrity"]
    files = extract(download(TARBALL, MAX_BYTES), integrity)
    target = directory / "swagger-ui"
    if target.exists() or target.is_symlink():
        folder(directory)
        for name, content in files.items():
            if asset(directory, name) != content:
                raise ValueError("EXISTING_ASSET_DIFFERS")
    else:
        with tempfile.TemporaryDirectory(prefix=".swagger-", dir=directory) as tmp:
            stage = Path(tmp) / "assets"
            stage.mkdir(mode=0o700)
            for name, content in files.items():
                with (stage / name).open("xb") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write(content)
            stage.rename(target)
    return {"version": VERSION, "registry_integrity": integrity,
            "files": {name: sha256(content).hexdigest() for name, content in files.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install",))
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.directory), sort_keys=True))


if __name__ == "__main__":
    main()
