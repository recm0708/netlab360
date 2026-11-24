"""Autenticación HTTP S08 sobre bases privadas temporales y cuentas sintéticas."""
from contextlib import closing
import importlib.util
from pathlib import Path
import os
import sqlite3
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi","pydantic","httpx","uvicorn"))

if AVAILABLE:
    from fastapi.testclient import TestClient
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location(
        "netlab360_s08_auth",package / "__init__.py",
        submodule_search_locations=[str(package)])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_auth import storage, security, sessions
    from netlab360_s08_auth.main import create_app

ORIGIN = "http://127.0.0.1:9140"
PASS = "synthetic test phrase only"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/auth/me"
LOGOUT = "/api/v1/auth/logout"
OPERATOR = "/api/v1/auth/operator-check"


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 con dependencias y usuario sin root")
class AuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.directory = Path(temp.name) / "estado"
        storage.initialize(cls.directory)
        storage.migrate(cls.directory)
        security.create_user(cls.directory,"viewer",PASS,"VIEWER")
        security.create_user(cls.directory,"operator",PASS,"OPERATOR")
        cls.path = cls.directory / storage.DB_NAME

    def setUp(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("DELETE FROM sessions")
            db.commit()
        self.client = TestClient(create_app(self.directory),base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def login(self, user="viewer", password=PASS):
        return self.client.post(LOGIN,json={"username":user,"password":password},
                                headers={"Origin":ORIGIN})

    def test_capabilities(self):
        body = self.client.get("/api/v1/capabilities").json()
        self.assertIs(body["authentication_enabled"],True)
        self.assertIs(body["persistence_enabled"],True)
        self.assertIs(body["network_mutations_authorized"],False)

    def test_missing_session(self):
        self.assertEqual(self.client.get(ME).status_code,401)

    def test_login_cookie_and_identity(self):
        result = self.login()
        self.assertEqual(result.status_code,200)
        self.assertNotIn("token",result.json())
        header = result.headers["set-cookie"].lower()
        for field in ("httponly","samesite=strict","max-age=28800","path=/"):
            self.assertIn(field,header)
        self.assertEqual(self.client.get(ME).json()["role"],"VIEWER")

    def test_wrong_password_and_unknown(self):
        for user in ("viewer","unknown"):
            result = self.login(user,"wrong")
            self.assertEqual(result.status_code,401)
            self.assertNotIn("wrong",result.text)

    def test_origin_required(self):
        for origin in (None,"https://evil.invalid","http://localhost:9140"):
            headers = {} if origin is None else {"Origin":origin}
            self.assertEqual(self.client.post(LOGIN,json={"username":"viewer","password":PASS},
                                              headers=headers).status_code,403)

    def test_invalid_payload_not_echoed(self):
        result = self.client.post(LOGIN,json={"username":3,"password":"SECRET_MARKER"},
                                  headers={"Origin":ORIGIN})
        self.assertEqual(result.status_code,400)
        self.assertNotIn("SECRET_MARKER",result.text)

    def test_body_limit_and_media_type(self):
        self.assertEqual(self.client.post(LOGIN,content=b"x"*4097,
            headers={"Origin":ORIGIN,"Content-Type":"application/json"}).status_code,413)
        self.assertEqual(self.client.post(LOGIN,data={"password":PASS},
            headers={"Origin":ORIGIN}).status_code,415)

    def test_role_check(self):
        self.assertEqual(self.login().status_code,200)
        self.assertEqual(self.client.get(OPERATOR).status_code,403)
        self.assertEqual(self.login("operator").status_code,200)
        result = self.client.get(OPERATOR)
        self.assertEqual(result.status_code,200)
        self.assertIs(result.json()["network_mutations_authorized"],False)

    def test_logout_csrf_and_revocation(self):
        result = self.login()
        csrf = result.json()["csrf_token"]
        token = self.client.cookies.get("netlab360_session")
        for headers in ({"Origin":ORIGIN},{"Origin":ORIGIN,"X-CSRF-Token":"wrong"},
                        {"X-CSRF-Token":csrf}):
            self.assertEqual(self.client.post(LOGOUT,headers=headers).status_code,403)
        self.assertEqual(self.client.get(ME).status_code,200)
        self.assertEqual(self.client.post(LOGOUT,headers={"Origin":ORIGIN,
                         "X-CSRF-Token":csrf}).status_code,200)
        self.client.cookies.set("netlab360_session",token)
        self.assertEqual(self.client.get(ME).status_code,401)

    def test_expiration_and_future(self):
        issued = sessions.issue(self.directory,"viewer",now=100)
        self.assertIsNone(sessions.resolve(self.directory,issued["token"],now=99))
        self.assertIsNotNone(sessions.resolve(self.directory,issued["token"],now=459))
        self.assertIsNone(sessions.resolve(self.directory,issued["token"],now=460))

    def test_resume_does_not_extend_or_rotate(self):
        a = self.login().json()
        for headers in ({"Origin": ORIGIN}, {"Origin": "https://evil.invalid",
                         "X-Netlab360-Resume": "1"}, {"X-Netlab360-Resume": "1"}):
            self.assertEqual(self.client.post("/api/v1/auth/resume",headers=headers).status_code,403)
        r = self.client.post("/api/v1/auth/resume",headers={"Origin":ORIGIN,"X-Netlab360-Resume":"1"})
        self.assertEqual(r.status_code,200)
        b = r.json()
        for key in ("csrf_token","warning_at","expires_at","absolute_expires_at","username","role"):
            self.assertEqual(a[key],b[key])
        self.assertNotIn("token",b)
        self.assertEqual(b["expires_at"]-b["warning_at"],60)

    def test_idle_warning_and_confirmation(self):
        a = sessions.issue(self.directory,"viewer",now=100)
        token, csrf = a["token"], a["csrf_token"]
        self.assertEqual((a["warning_at"],a["expires_at"]),(400,460))
        self.assertEqual(sessions.resume(self.directory,token,now=399)["expires_at"],460)
        self.assertEqual(sessions.touch(self.directory,token,csrf,now=400)["expires_at"],460)
        b = sessions.touch(self.directory,token,csrf,confirmed=True,now=459)
        self.assertEqual((b["warning_at"],b["expires_at"]),(759,819))
        self.assertIsNone(sessions.resolve(self.directory,token,now=819))
        self.assertIsNone(sessions.touch(self.directory,token,csrf,confirmed=True,now=819))

    def test_activity_and_absolute_limit(self):
        a = sessions.issue(self.directory,"viewer",now=100)
        token, csrf = a["token"],a["csrf_token"]
        for now in range(350,28900,250):
            b = sessions.touch(self.directory,token,csrf,confirmed=True,now=now)
            self.assertIsNotNone(b)
            self.assertLessEqual(b["expires_at"],28900)
        self.assertEqual(b["expires_at"],28900)
        self.assertIsNone(sessions.resolve(self.directory,token,now=28900))

    def test_http_activity_requires_origin_and_csrf(self):
        a = self.login().json()
        for path in ("/api/v1/auth/activity","/api/v1/auth/continue"):
            self.assertEqual(self.client.post(path,headers={"Origin":ORIGIN}).status_code,403)
            self.assertEqual(self.client.post(path,headers={"X-CSRF-Token":a["csrf_token"]}).status_code,403)
            r = self.client.post(path,headers={"Origin":ORIGIN,"X-CSRF-Token":a["csrf_token"]})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json()["absolute_expires_at"],a["absolute_expires_at"])

    def test_legacy_session_rejected(self):
        a = sessions.issue(self.directory,"viewer")
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE sessions SET csrf_digest=?",(b"x"*32,))
            db.commit()
        self.assertIsNone(sessions.resolve(self.directory,a["token"]))
        self.assertIsNone(sessions.resume(self.directory,a["token"]))

    def test_session_replacement_and_digest_only(self):
        a = sessions.issue(self.directory,"viewer")
        b = sessions.issue(self.directory,"viewer")
        self.assertIsNone(sessions.resolve(self.directory,a["token"]))
        self.assertIsNotNone(sessions.resolve(self.directory,b["token"]))
        data = self.path.read_bytes()
        self.assertNotIn(b["token"].encode(),data)
        self.assertNotIn(b["csrf_token"].encode(),data)

    def test_disabled_account_revokes_access(self):
        self.assertEqual(self.login().status_code,200)
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE users SET enabled=0 WHERE username='viewer'")
            db.commit()
        try:
            self.assertEqual(self.client.get(ME).status_code,401)
        finally:
            with closing(sqlite3.connect(self.path)) as db:
                db.execute("UPDATE users SET enabled=1 WHERE username='viewer'")
                db.commit()

    def test_rate_limit(self):
        for _ in range(8):
            self.assertEqual(self.login("viewer","wrong").status_code,401)
        result = self.login()
        self.assertEqual(result.status_code,429)
        self.assertEqual(result.headers["retry-after"],"60")

    def test_bootstrap_has_no_auth_routes(self):
        with TestClient(create_app(),base_url=ORIGIN) as client:
            self.assertEqual(client.post(LOGIN).status_code,404)

    def test_network_mutations_unavailable(self):
        self.assertEqual(self.login("operator").status_code,200)
        self.assertEqual(self.client.post("/api/v1/actions").status_code,404)
        self.assertEqual(self.client.post("/api/v1/rfcs").status_code,404)


if __name__ == "__main__":
    unittest.main()
