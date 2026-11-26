"""Piloto HTTP real aislado: contenido en vivo, cancelación y recuperación de historial."""
import argparse
from contextlib import contextmanager
from http.client import HTTPConnection
import json
from pathlib import Path
import secrets
import sys
import threading
import time

ORIGIN = "http://127.0.0.1:9145"
JOBS = "/api/v1/jobs"


def emit(kind, **data):
    print(json.dumps({"kind": kind, **data}, allow_nan=False), flush=True)


def request(method, path, *, auth=None, body=None, csrf=True, origin=ORIGIN, html=False):
    """No registrar cabeceras de identidad ni contraseñas."""
    headers = {"Host": "127.0.0.1:9145"}
    if auth:
        headers["Cookie"] = auth["cookie"]
    if method == "POST":
        headers["Origin"] = origin
        if auth and csrf:
            headers["X-CSRF-Token"] = auth["csrf"]
    if body is not None:
        body = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    conn = HTTPConnection("127.0.0.1", 9145, timeout=10)
    try:
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        raw = response.read(2_100_000)
        return response.status, raw.decode() if html else json.loads(raw), response.getheader("Set-Cookie")
    finally:
        conn.close()


def login(user, password):
    status, data, cookie = request("POST", "/api/v1/auth/login",
                                  body={"username": user, "password": password})
    assert status == 200 and cookie, status
    return {"cookie": cookie.split(";", 1)[0], "csrf": data["csrf_token"]}


@contextmanager
def server_context(directory):
    import uvicorn
    from api.service_runtime import dedicated_app
    with dedicated_app(directory, port=9145) as app:
        config = uvicorn.Config(app, host="127.0.0.1", port=9145, loop="asyncio", http="h11",
                                ws="none", lifespan="off", proxy_headers=False, server_header=False,
                                access_log=False, log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                assert thread.is_alive() and time.monotonic() < deadline, "SERVER_NOT_READY"
                time.sleep(0.1)
            yield
        finally:
            server.should_exit = True
            thread.join(30)
            assert not thread.is_alive(), "SERVER_NOT_STOPPED"


def execute(selection, operator, other, *, cancel=False):
    status, initial, _ = request("POST", JOBS, auth=operator, body=selection)
    assert status == 202 and initial["status"] == "QUEUED", status
    identifier = initial["job_id"]
    url = JOBS + "/" + identifier
    assert request("GET", url, auth=other)[0] == 404
    states = ["QUEUED"]
    observed_roles = set()
    asked = False
    deadline = time.monotonic() + 110
    while time.monotonic() < deadline:
        status, job, _ = request("GET", url, auth=operator)
        assert status == 200, status
        current = job["status"]
        if current != states[-1]:
            states.append(current)
        data = job["data"]
        assert data.get("execution_quality") != "UNCERTAIN", job
        if current == "RUNNING":
            observed_roles.update(p["role"] for p in data.get("progress", []) if p["bytes"] > 0)
            if cancel and observed_roles == {"sender", "receiver"} and not asked:
                assert request("POST", JOBS, auth=operator, body=selection)[0] == 409
                assert request("POST", url+"/cancel", auth=other)[0] == 404
                status, pending, _ = request("POST", url+"/cancel", auth=operator)
                assert status == 200 and pending["data"]["cancel_requested"] is True
                asked = True
        if current in ("SUCCEEDED", "CANCELLED", "FAILED"):
            break
        time.sleep(0.25)
    else:
        raise AssertionError("JOB_DEADLINE")
    if cancel:
        assert asked and current == "CANCELLED" and data["cleanup_verified"] is True
        assert data["result"] is None
        assert observed_roles == {"sender", "receiver"}
    else:
        assert current == "SUCCEEDED", job
        m = data["result"]["measurement"]
        assert m["status"] == "OK", m
        if selection["action"] == "test.content.tcp":
            assert observed_roles == {"sender", "receiver"}
            assert m["bytes_sent"] == m["bytes_received"] == 100000000
            assert m["content_integrity_verified"] is True and m["sender_sha256"] == m["receiver_sha256"]
        else:
            assert observed_roles == {"sender", "receiver"}
            assert m["bytes_sent"] > 0 and m["bytes_received"] > 0
            assert all("interval_bytes" in point for point in data["progress"])
            for role in ("sender", "receiver"):
                points = [p for p in data["progress"] if p["role"] == role]
                assert len(points) == len(m[role + "_intervals"])
                assert points[-1]["bytes"] == sum(p["bytes"] for p in m[role + "_intervals"])
    emit("real_job", job=job, states=states, roles_observed_while_running=sorted(observed_roles))
    return identifier


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deps", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--iperf", action="store_true", help="Validar TCP/UDP y cancelación iPerf3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(args.deps))
    sys.path.insert(0, str(root / "servicios/consola-s08"))
    from api import jobs, security, storage
    directory = args.state
    assert not directory.exists()
    storage.initialize(directory)
    storage.migrate(directory)
    storage.migrate_v3(directory)
    password = secrets.token_urlsafe(32)
    for username, role in (("operator","OPERATOR"),("other","OPERATOR"),("viewer","VIEWER")):
        security.create_user(directory,username,password,role)
    with server_context(directory):
        assert request("GET","/healthz")[1]["mode"] == "AUTHENTICATED_JOBS"
        assert request("GET",JOBS+"/catalog")[0] == 401
        operator, other, viewer = [login(name,password) for name in ("operator","other","viewer")]
        status, page, _ = request("GET","/diagnostics",auth=operator,html=True)
        assert status == 200 and 'id="jobs-view"' in page
        assert request("GET","/ui/static/jobs.js",html=True)[0] == 200
        status, catalog, _ = request("GET",JOBS+"/catalog",auth=operator)
        assert status == 200 and len(catalog["selections"]) == 34
        assert sum(row["live_progress"] for row in catalog["selections"]) == 24
        assert sum(row["active_cancel"] for row in catalog["selections"]) == 24
        content = {"action":"test.content.tcp","route":"HQ_A_S1","profile":"content-100mb"}
        assert request("POST",JOBS,auth=viewer,body=content)[0] == 403
        assert request("POST",JOBS,auth=operator,body=content,csrf=False)[0] == 403
        assert request("POST",JOBS,auth=operator,body=content,origin="http://127.0.0.1:9140")[0] == 403
        assert request("POST",JOBS,auth=operator,body=dict(content,route="192.168.47.2"))[0] == 400
        tcp = {"action":"test.iperf.tcp","route":"HQ_A_S1","profile":"tcp-10s"}
        if args.iperf:
            ids = [execute(tcp,operator,other),
                   execute({"action":"test.iperf.udp","route":"HQ_A_S2","profile":"udp-10s"},operator,other),
                   execute(dict(tcp,profile="tcp-500mb",route="HQ_A_S2"),operator,other,cancel=True),
                   execute(content,operator,other)]
        else:
            ids = [execute(content,operator,other),
                   execute(dict(content,profile="content-500mb",route="HQ_A_S2"),operator,other,cancel=True),
                   execute(tcp,operator,other)]
        assert len(set(ids)) == (4 if args.iperf else 3)
        assert request("GET",JOBS,auth=other)[1]["jobs"] == []
        assert {row["job_id"] for row in request("GET",JOBS,auth=operator)[1]["jobs"]} == set(ids)
        for auth in (operator,other,viewer):
            assert request("POST","/api/v1/auth/logout",auth=auth)[0] == 200
    # Registro de cola sintético separado: no se despacha ni se cuenta como medición.
    queued = jobs.enqueue(directory,"operator",content,stream_enabled=True)
    with server_context(directory):
        operator = login("operator",password)
        rows = request("GET",JOBS,auth=operator)[1]["jobs"]
        assert {row["job_id"] for row in rows} == set(ids) | {queued["job_id"]}
        assert request("GET",JOBS+"/"+queued["job_id"],auth=operator)[1]["status"] == "CANCELLED"
        for identifier in ids:
            assert request("GET",JOBS+"/"+identifier,auth=operator)[0] == 200
        assert request("POST","/api/v1/auth/logout",auth=operator)[0] == 200
    emit("acceptance", real_jobs=len(ids), completed=len(ids)-1, cancelled_under_load=1, history_reopened=len(ids),
         synthetic_queue_recovery=1, storage=storage.inspect(directory), browser_visual_verified=False)


if __name__ == "__main__":
    main()
