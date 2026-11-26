"""Pruebas del alcance Viewer, respuestas JSON y denegación explícita."""
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
import sys
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/s08"))
import aprovisionar_grafana_viewer as V
from ejecutar_paneles_grafana import decode_payload, fetch, PROM


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.user = {"login": V.LOGIN, "isGrafanaAdmin": False, "isDisabled": False}
        self.orgs = [{"orgId": 1, "role": "Viewer"}]
        self.dashboard = {"dashboard": {"uid": V.DASH, "editable": False,
                                       "panels": list(range(10))},
                          "meta": {"canEdit": False, "canSave": False}}

    def test_viewer(self):
        V.validate_role(self.user, self.orgs, self.dashboard)

    def test_privilege_escalation(self):
        for role in ("Admin", "Editor"):
            with self.subTest(role=role), self.assertRaises(AssertionError):
                V.validate_role(self.user, [{"orgId": 1, "role": role}], self.dashboard)
        self.user["isGrafanaAdmin"] = True
        with self.assertRaises(AssertionError):
            V.validate_role(self.user, self.orgs, self.dashboard)

    def test_edit_denied(self):
        for key in ("canEdit", "canSave"):
            self.dashboard["meta"][key] = True
            with self.assertRaises(AssertionError):
                V.validate_role(self.user, self.orgs, self.dashboard)
            self.dashboard["meta"][key] = False

    def test_json_list(self):
        self.assertEqual(decode_payload(b'[{"id":1}]', list), [{"id": 1}])
        with self.assertRaises(ValueError):
            decode_payload(b'[{"id":1}]')
        for raw in (b'{}', b'[1]'):
            with self.assertRaises(AssertionError):
                decode_payload(raw, list)

    def test_credentials_only_grafana(self):
        with self.assertRaises(AssertionError):
            fetch(PROM + "/api/v1/query", "not-a-real-secret")

    def test_denied(self):
        def error(code):
            raise HTTPError("http://127.0.0.1:3000", code, "", {}, BytesIO(b""))
        self.assertEqual(V.denied(lambda: error(403)), 403)
        with self.assertRaises(HTTPError):
            V.denied(lambda: error(500))
        with self.assertRaises(ValueError):
            V.denied(lambda: {})

    def test_password_validation_codes(self):
        good = "A" * 20
        V.validate_password(good, good, "B" * 20)
        for password, repeated, admin, code in (
            (good, "different", "", "PASSWORD_MISMATCH"),
            ("short", "short", "", "PASSWORD_TOO_SHORT"),
            (good + " ", good + " ", "", "PASSWORD_EDGE_WHITESPACE"),
            (good, good, good, "PASSWORD_MUST_BE_INDEPENDENT"),
        ):
            with self.subTest(code=code), self.assertRaisesRegex(V.PasswordInputError, "^" + code + "$"):
                V.validate_password(password, repeated, admin)

    def test_retry_password_without_disclosure(self):
        good = "Z" * 20
        with patch.object(V.getpass, "getpass", side_effect=["short", "short", good, good]), patch("builtins.print") as output:
            self.assertEqual(V.password_prompt("admin"), good)
            self.assertNotIn(good, str(output.call_args_list))
            self.assertIn("PASSWORD_TOO_SHORT", str(output.call_args_list))

    def test_password_attempt_limit(self):
        with patch.object(V.getpass, "getpass", return_value="short"), patch("builtins.print"):
            with self.assertRaisesRegex(V.PasswordInputError, "^PASSWORD_ATTEMPTS_EXHAUSTED$"):
                V.password_prompt("admin")


if __name__ == "__main__":
    unittest.main()
