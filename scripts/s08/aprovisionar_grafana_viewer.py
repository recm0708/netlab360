#!/usr/bin/env python3
"""Crear una cuenta Viewer local y acreditar su acceso sin exponer contraseñas."""
import getpass
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ejecutar_paneles_grafana import BASE, DASH, PROM, UID, fetch, run

LOGIN = "netlab360-viewer"
ADMIN = "netlab360-admin"


def password_prompt():
    """Exigir entrada oculta en terminal y una contraseña independiente."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        password = getpass.getpass("Nueva contraseña Viewer (mínimo 20 caracteres): ")
        repeated = getpass.getpass("Confirmar contraseña Viewer: ")
    if password != repeated or len(password) < 20 or password != password.strip():
        raise ValueError("PASSWORD_INVALID_OR_MISMATCH")
    return password


def denied(call, allowed=(403,)):
    """Aceptar solo códigos de denegación explícitos, nunca fallos de transporte."""
    try:
        call()
    except HTTPError as error:
        if error.code not in allowed:
            raise
        return error.code
    raise ValueError("UNEXPECTED_ACCESS")


def validate_role(user, organizations, dashboard):
    """Comprobar identidad local, organización única y ausencia de edición."""
    assert user["login"] == LOGIN and user["isGrafanaAdmin"] is False
    assert user["isDisabled"] is False
    assert [(o["orgId"], o["role"]) for o in organizations] == [(1, "Viewer")]
    assert dashboard["dashboard"]["uid"] == DASH
    assert dashboard["dashboard"]["editable"] is False
    assert len(dashboard["dashboard"]["panels"]) == 10
    assert dashboard["meta"]["canEdit"] is False
    assert dashboard["meta"]["canSave"] is False


def members(admin):
    """Capturar identidades y roles, excluyendo campos volátiles de último acceso."""
    return sorted((u["userId"], u["login"], u["role"])
                  for u in fetch(BASE + "/api/org/users", admin, expected=list))


def provision(root, admin):
    """Crear una identidad nueva y revertir solo esa identidad si falla la aceptación."""
    lookup = BASE + "/api/users/lookup?" + urlencode({"loginOrEmail": LOGIN})
    dash_url = BASE + "/api/dashboards/uid/" + DASH
    admin_user = fetch(BASE + "/api/user", admin)
    assert admin_user["login"] == ADMIN and admin_user["isGrafanaAdmin"] is True
    denied(lambda: fetch(lookup, admin), (404,))
    sources = fetch(BASE + "/api/datasources", admin, expected=list)
    assert len(sources) == 1 and sources[0]["uid"] == UID
    assert sources[0]["url"] == PROM and sources[0]["type"] == "prometheus"
    flags = fetch(PROM + "/api/v1/status/flags")["data"]
    for flag in ("web.enable-admin-api", "web.enable-lifecycle", "web.enable-remote-write-receiver", "web.enable-otlp-receiver"):
        assert flags[flag] == "false", flag
    before = members(admin)
    dash_before = fetch(dash_url, admin)["dashboard"]
    password = password_prompt()
    if password == admin:
        raise ValueError("PASSWORD_MUST_BE_INDEPENDENT")
    created_id = None
    try:
        result = fetch(BASE + "/api/admin/users", admin, {
            "name": "NETLAB360 Viewer", "email": "netlab360-viewer@example.invalid",
            "login": LOGIN, "password": password, "OrgId": 1})
        created_id = result["id"]
        assert type(created_id) is int and created_id > 0
        user = fetch(lookup, admin)
        assert user["id"] == created_id
        me = fetch(BASE + "/api/user", password, username=LOGIN)
        assert me["login"] == LOGIN and me["id"] == created_id
        organizations = fetch(BASE + "/api/user/orgs", password, username=LOGIN, expected=list)
        dashboard = fetch(dash_url, password, username=LOGIN)
        validate_role(user, organizations, dashboard)
        anonymous = denied(lambda: fetch(dash_url), (401, 403))
        admin_status = denied(lambda: fetch(BASE + "/api/admin/settings", password, username=LOGIN))
        users_status = denied(lambda: fetch(BASE + "/api/users", password, username=LOGIN))
        run(root / "grafana-viewer-paneles.json", password, username=LOGIN)
        assert members(admin) == sorted(before + [(created_id, LOGIN, "Viewer")])
        assert fetch(dash_url, admin)["dashboard"] == dash_before
        assert fetch(BASE + "/api/datasources", admin, expected=list) == sources
        with (root / "grafana-viewer-acceso.json").open("x", encoding="utf-8") as handle:
            json.dump({"login": LOGIN, "id": created_id, "org_id": 1, "role": "Viewer",
                       "admin": False, "can_edit": False, "can_save": False,
                       "anonymous_status": anonymous, "admin_status": admin_status,
                       "users_status": users_status, "existing_members_preserved": True,
                       "dashboard_preserved": True, "datasource_preserved": True}, handle, indent=2)
        print("GRAFANA_VIEWER=OK ROL=Viewer PANEL=10/10 CONSULTAS=19/19 PUNTOS=571/571")
        print("ADMINISTRACION_DENEGADA=2/2 EDICION_DASHBOARD=NO")
    except BaseException:
        if type(created_id) is int and created_id > 0:
            current = fetch(lookup, admin)
            assert current["id"] == created_id and current["login"] == LOGIN
            fetch(BASE + f"/api/admin/users/{created_id}", admin, method="DELETE")
            denied(lambda: fetch(lookup, admin), (404,))
            assert members(admin) == before
            print("CUENTA_NUEVA_REVERTIDA=OK")
        else:
            print("CREACION_NO_CONFIRMADA=REVISAR_INVENTARIO_ANTES_DE_REINTENTAR")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: aprovisionar_grafana_viewer.py DIRECTORIO_EVIDENCIAS")
    try:
        provision(Path(sys.argv[1]), sys.stdin.readline().strip())
    except Exception as error:
        print("VIEWER_ERROR=" + type(error).__name__, file=sys.stderr)
        if isinstance(error, HTTPError):
            print("HTTP_STATUS=" + str(error.code), file=sys.stderr)
        raise SystemExit(1)
