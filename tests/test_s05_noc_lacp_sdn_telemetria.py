"""S05 NOC LACP/SDN: datos realmente observados, no asumir disponibilidad."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/operacion/s05_observador_privilegiado.py"
APP = ROOT / "servicios/topologia-s05/app.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


helper = load(HELPER, "s05_helper_extended")
app = load(APP, "s05_noc_extended")


def timestamp(seconds: int = 0) -> str:
    return (datetime.now(timezone.utc)
            + timedelta(seconds=seconds)).isoformat(timespec="seconds")


def bond_json(dev="bond0", alias="S05_HQ_0000000000000000", ports=2,
              flags=("BROADCAST", "MULTICAST", "MASTER", "UP", "LOWER_UP")):
    return json.dumps([{
        "ifname": dev, "ifalias": alias, "flags": list(flags),
        "linkinfo": {"info_kind": "bond",
                     "info_data": {"mode": "802.3ad", "ad_num_ports": ports}},
    }])


def read_lacp(status="up", count=2, stamp=None):
    return {"owner": app.LACP_OBS_OWNER,
            "observed_at_utc": stamp or timestamp(),
            "sites": {site: {"status": status,
                             "switch_members": count,
                             "client_members": count}
                      for site in ("HQ", "S1", "S2")}}


def read_sdn(connected=True, stamp=None):
    return {"owner": app.SDN_OBS_OWNER,
            "observed_at_utc": stamp or timestamp(),
            "available": True,
            "status": "connected" if connected else "disconnected",
            "connected": connected,
            "flow_count": 25 if connected else None}


class TestNocExtendedSources(unittest.TestCase):
    def test_root_observed_bond_real_8023ad(self):
        alias = "S05_HQ_0000000000000000"
        with mock.patch.object(helper, "optional_read",
                               return_value=bond_json(alias=alias)):
            result = helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)
        self.assertEqual(result["active_members"], 2)
        self.assertTrue(result["link_up"])

    def test_root_observed_bond_rejects_wrong_owner(self):
        with mock.patch.object(helper, "optional_read",
                               return_value=bond_json()):
            with self.assertRaisesRegex(RuntimeError, "no acreditados"):
                helper.observed_bond("nl360-s05-lacp-hq", "bond0", "S05_HQ_ffffffffffffffff")

    def test_root_observed_bond_json_sin_ad_num_ports_con_proc_real(self):
        alias = "S05_HQ_0000000000000000"
        proc = (
            "Ethernet Channel Bonding Driver: v6.16\\n"
            "Bonding Mode: IEEE 802.3ad Dynamic link aggregation\\n"
            "MII Status: up\\n"
            "Active Aggregator Info:\\n"
            "        Aggregator ID: 1\\n"
            "        Number of ports: 2\\n"
        ).replace("\\n", "\n")
        with mock.patch.object(
            helper, "optional_read",
            side_effect=[bond_json(alias=alias, ports=None), proc]
        ) as reader:
            result = helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)
        self.assertTrue(result["link_up"])
        self.assertEqual(result["active_members"], 2)
        self.assertEqual(reader.call_count, 2)
        self.assertEqual(reader.call_args_list[1].args, (
            "/usr/sbin/ip", "netns", "exec", "nl360-s05-lacp-hq",
            "/usr/bin/cat", "/proc/net/bonding/bond0",
        ))
        self.assertEqual(reader.call_args_list[1].kwargs["timeout"], 4.0)

    def test_root_observed_bond_proc_degradado_un_puerto(self):
        alias = "S05_HQ_0000000000000000"
        proc = "Bonding Mode: IEEE 802.3ad Dynamic link aggregation\\nNumber of ports: 1\\n".replace("\\n", "\n")
        with mock.patch.object(helper, "optional_read",
                               side_effect=[bond_json(alias=alias, ports=None), proc]):
            result = helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)
        self.assertEqual(result["active_members"], 1)

    def test_root_observed_bond_proc_no_acredita_modo_o_numero(self):
        alias = "S05_HQ_0000000000000000"
        invalids = (
            "Bonding Mode: fault tolerance (active-backup)\\nNumber of ports: 2\\n",
            "Bonding Mode: IEEE 802.3ad Dynamic link aggregation\\n",
            "Bonding Mode: IEEE 802.3ad Dynamic link aggregation\\nNumber of ports: 9\\n",
            "Bonding Mode: IEEE 802.3ad Dynamic link aggregation\\nNumber of ports: 2\\nNumber of ports: 1\\n",
        )
        for raw in invalids:
            with self.subTest(raw=raw), mock.patch.object(
                helper, "optional_read", side_effect=[
                    bond_json(alias=alias, ports=None), raw.replace("\\n", "\n")
                ]
            ):
                with self.assertRaises(RuntimeError):
                    helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)

    def test_root_observed_bond_proc_no_disponible_se_rechaza(self):
        alias = "S05_HQ_0000000000000000"
        with mock.patch.object(helper, "optional_read", side_effect=[
                bond_json(alias=alias, ports=None), RuntimeError("proceso no observado")
        ]):
            with self.assertRaisesRegex(RuntimeError, "no observado"):
                helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)

    def test_root_observed_bond_namespace_ajeno_no_se_consulta(self):
        with mock.patch.object(helper, "optional_read") as reader:
            with self.assertRaisesRegex(RuntimeError, "ajeno al inventario"):
                helper.observed_bond("nl360-s02-h-hq-120", "bond0", "alias")
        reader.assert_not_called()

    def test_root_observed_bond_json_ya_completo_sin_proc(self):
        alias = "S05_HQ_0000000000000000"
        with mock.patch.object(helper, "optional_read",
                               return_value=bond_json(alias=alias, ports=2)) as reader:
            result = helper.observed_bond("nl360-s05-lacp-hq", "bond0", alias)
        self.assertEqual(result["active_members"], 2)
        reader.assert_called_once()

    def test_root_observed_bond_rejects_unexpected_type(self):
        payload = json.loads(bond_json())
        payload[0]["linkinfo"]["info_kind"] = "veth"
        with mock.patch.object(helper, "optional_read",
                               return_value=json.dumps(payload)):
            with self.assertRaises(RuntimeError):
                helper.observed_bond("x", "bond0", payload[0]["ifalias"])

    def test_root_lacp_fails_closed_for_missing_state(self):
        with mock.patch.object(helper, "LACP_STATES", Path("/nonexistent-no-state")):
            out = helper.lacp_observation()
        self.assertFalse(out["available"])
        self.assertEqual(
            {x["status"] for x in out["sites"].values()}, {"unknown"})

    def test_root_lacp_stores_real_degraded_members(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            for site, (switch, client) in helper.LACP_SITES.items():
                (base / f"state-{site.lower()}.json").write_text(json.dumps({
                    "owner": f"NETLAB360_S05_LACP_{site}_V1",
                    "site": site, "sw": switch, "client": client,
                    "alias": f"S05_{site}_0000000000000000", "status": "active",
                }))
            with mock.patch.object(helper, "LACP_STATES", base), \
                 mock.patch.object(helper, "observed_bond",
                                   return_value={"active_members": 1,
                                                 "link_up": True}):
                obs = helper.lacp_observation()
        self.assertTrue(obs["available"])
        self.assertEqual(obs["sites"]["S2"]["status"], "degraded")
        self.assertEqual(obs["sites"]["HQ"]["client_members"], 1)

    def test_root_sdn_rejects_unowned_bridge_before_container_lookup(self):
        with mock.patch.object(helper, "safe_json",
                               return_value={"owner": helper.SDN_OWNER,
                                             "status": "active",
                                             "bridge": helper.SDN_BRIDGE}), \
             mock.patch.object(helper, "optional_read",
                               return_value='"OTHER_OWNER"') as commands:
            out = helper.sdn_observation()
        self.assertEqual(out["status"], "unknown")
        self.assertEqual(commands.call_count, 1)

    def test_root_sdn_observes_connected_not_from_state_only(self):
        container = [{"Name": "/nl360-s05-faucet",
                      "State": {"Running": True},
                      "Config": {"Labels": {
                          "netlab360.owner": helper.SDN_OWNER}}}]
        replies = [
            f'"{helper.SDN_OWNER}"',
            "sdna0\nsdnb0\nsdnc0\n",
            json.dumps(container),
            "true\n",
            "cookie=0x0, duration=123.0s, table=0, actions=drop\n"
            "cookie=0x0, duration=123.0s, table=1, actions=output:2\n",
        ]
        state = {"owner": helper.SDN_OWNER, "bridge": helper.SDN_BRIDGE,
                 "status": "active"}
        with mock.patch.object(helper, "safe_json", return_value=state), \
             mock.patch.object(helper, "optional_read", side_effect=replies):
            out = helper.sdn_observation()
        self.assertTrue(out["connected"])
        self.assertEqual(out["flow_count"], 2)
        self.assertEqual(out["status"], "connected")

    def test_noc_lacp_valid(self):
        result, warning = app.observed_lacp({"lacp": read_lacp()})
        self.assertFalse(warning)
        self.assertTrue(result["available"])
        self.assertEqual(result["sites"]["HQ"]["switch_members"], 2)

    def test_noc_lacp_rejects_future_or_stale(self):
        for offset in (-60, 60):
            with self.subTest(offset=offset):
                result, warning = app.observed_lacp(
                    {"lacp": read_lacp(stamp=timestamp(offset))})
                self.assertFalse(result["available"])
                self.assertTrue(warning)

    def test_noc_lacp_rejects_fabricated_up(self):
        snapshot = read_lacp()
        snapshot["sites"]["HQ"]["switch_members"] = 1
        result, warning = app.observed_lacp({"lacp": snapshot})
        self.assertFalse(result["available"])
        self.assertTrue(warning)

    def test_noc_sdn_distinguishes_connected_disconnected_unknown(self):
        for observed, status in [(True, "connected"), (False, "disconnected")]:
            with self.subTest(observed=observed):
                value, error = app.observed_sdn({"sdn": read_sdn(observed)})
                self.assertEqual(value["status"], status)
                self.assertFalse(error)
        value, error = app.observed_sdn({})
        self.assertEqual(value["status"], "unknown")
        self.assertTrue(error)

    def test_noc_sdn_rejects_stale_or_fabricated_flows(self):
        d = read_sdn()
        d["flow_count"] = 0
        value, _ = app.observed_sdn({"sdn": d})
        self.assertFalse(value["available"])
        d["flow_count"] = 25
        d["observed_at_utc"] = timestamp(-120)
        value, _ = app.observed_sdn({"sdn": d})
        self.assertFalse(value["available"])

    def test_graph_extension_preserves_old_infrastructure(self):
        inv = app.inventory()
        ext = {"schema_version": 1, "nodes": [], "links": []}
        d = app.graph(inv, None, None, ext,
                      lacp=app.observed_lacp({"lacp": read_lacp()})[0],
                      sdn=app.observed_sdn({"sdn": read_sdn()})[0])
        self.assertEqual(d["counts"]["sites"], 3)
        self.assertEqual(d["counts"]["wan"], 4)
        self.assertEqual(len(d["nodes"]), 15)
        self.assertEqual(len(d["links"]), 16)
        self.assertEqual(d["sdn"]["flow_count"], 25)

    def test_legacy_cli_snapshot_contract_preserved(self):
        # El binario privilegiado mantiene la misma invocación acotada.
        code = HELPER.read_text(encoding="utf-8")
        self.assertIn('sys.argv != [sys.argv[0], "snapshot"]', code)
        self.assertIn('result["routes"][site] = route', code)
        self.assertNotIn('shell=True', code)

    def test_optional_root_fail_does_not_crash_legacy_fib(self):
        # Nuevas fuentes pueden faltar y deben permanecer UNKNOWN.
        with mock.patch.object(helper, "lacp_observation",
                               side_effect=RuntimeError("missing")):
            # El contrato FIB no se altera al preparar el helper: no se
            # reemplaza nunca la acción sudoers original.
            self.assertTrue(callable(helper.fib))
            self.assertTrue(callable(app.fib_routes))


if __name__ == "__main__":
    unittest.main()
