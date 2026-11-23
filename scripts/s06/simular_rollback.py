#!/usr/bin/env python3
"""S06-037: simulador puro de seguridad y rollback (NO modifica la red).

Ejercita autorizacion, exclusividad, watchdog logico, TTL, propiedad de
qdisc y fallos. El tiempo es virtual; ninguno de estos casos demuestra
que un ejecutor root-owned o un rollback systemd real ya funcionen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys

ROOT = Path.home() / "netlab360-bootstrap/s06/rollback-simulaciones"
SCHEMA = "NETLAB360_S06_ROLLBACK_SIM_V1"
TARGET = {"namespace": "nl360-s02-h-hq-120",
          "device": "eth0", "ip": "10.70.20.20/24",
          "gateway": "10.70.20.1"}
MANAGEMENT = {"ip": "192.168.47.40/24", "gateway": "192.168.47.2"}
ALLOWED_TTL = (10, 60)
CASES = (
    "success", "expired_ttl", "controller_crash", "apply_failure",
    "foreign_owner", "rollback_failure", "double_restore",
    "no_approval", "watchdog_missing", "concurrency",
    "wrong_target", "wrong_qdisc", "wrong_management", "bad_ttl",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Refusal(Exception):
    """Gate de seguridad no cumplido; no se realizo accion."""


class Slot:
    def __init__(self):
        self.owner = None

    def acquire(self, token: str) -> None:
        if self.owner is not None:
            raise Refusal("active_operation_exists")
        self.owner = token

    def release(self, token: str) -> None:
        if self.owner != token:
            raise Refusal("slot_not_owned")
        self.owner = None


class Trial:
    def __init__(self, slot: Slot | None = None, *, token: str = "demo-s06-037"):
        self.slot = slot if slot is not None else Slot()
        self.token = token
        self.state = "NEW"
        self.clock = 0
        self.expires_at = None
        self.watchdog_armed = False
        self.effective_qdisc = {"kind": "noqueue", "owner": None}
        self.applied_by = None
        self.events = []
        self.log("created")

    def log(self, event: str, **details) -> None:
        self.events.append({"virtual_seconds": self.clock, "event": event,
                            "state": self.state, "details": details})

    def approve(self, *, operator_role: str = "operator", approved: bool = True,
                management: dict | None = None, target: dict | None = None,
                original_qdisc: str = "noqueue", ttl: int = 30) -> None:
        if self.state != "NEW":
            raise Refusal("already_started")
        if operator_role != "operator" or approved is not True:
            raise Refusal("human_approval_required")
        if management is None:
            management = MANAGEMENT
        if target is None:
            target = TARGET
        if management != MANAGEMENT:
            raise Refusal("management_not_in_reference")
        if target != TARGET:
            raise Refusal("target_not_allowlisted")
        if original_qdisc != "noqueue":
            raise Refusal("preexisting_qdisc_not_owned")
        if type(ttl) is not int or not ALLOWED_TTL[0] <= ttl <= ALLOWED_TTL[1]:
            raise Refusal("ttl_out_of_policy")
        self.slot.acquire(self.token)
        self.expires_at = self.clock + ttl
        self.state = "APPROVED"
        self.log("approval_recorded", ttl=ttl, scenario="simulated_only")

    def arm_watchdog(self, *, success: bool = True) -> None:
        if self.state != "APPROVED":
            raise Refusal("approve_before_watchdog")
        if not success:
            self.state = "ABORTED"
            self.slot.release(self.token)
            self.log("watchdog_arm_failed_no_change")
            return
        self.watchdog_armed = True
        self.state = "ARMED"
        self.log("watchdog_armed_simulated", deadline=self.expires_at)

    def apply(self, *, fail_before_change: bool = False) -> None:
        if self.state != "ARMED" or not self.watchdog_armed:
            raise Refusal("must_arm_watchdog_before_apply")
        if fail_before_change:
            self.state = "ABORTED"
            self.slot.release(self.token)
            self.log("apply_failed_before_change")
            return
        self.effective_qdisc = {"kind": "netem", "owner": self.token}
        self.applied_by = self.token
        self.state = "ACTIVE"
        self.log("synthetic_qdisc_change", kind="netem", no_real_network=True)

    def lose_controller(self) -> None:
        if self.state != "ACTIVE":
            raise Refusal("no_controller_to_lose")
        self.log("controller_crash_simulated")

    def restore(self, *, caller: str = "watchdog",
                restore_success: bool = True) -> None:
        if self.state == "RESTORED":
            self.log("restore_idempotent")
            return
        if self.state not in ("ACTIVE", "RESTORE_PENDING"):
            raise Refusal("restore_not_permitted_from_state")
        if caller not in ("watchdog", "operator"):
            raise Refusal("unauthorized_restorer")
        self.state = "RESTORE_PENDING"
        self.log("restore_requested", caller=caller)
        if self.effective_qdisc != {"kind": "netem", "owner": self.token}:
            self.state = "ESCALATED"
            self.log("foreign_qdisc_not_deleted")
            return
        if not restore_success:
            self.state = "ESCALATED"
            self.log("rollback_failed_escalated")
            return
        self.effective_qdisc = {"kind": "noqueue", "owner": None}
        self.state = "RESTORED"
        self.slot.release(self.token)
        self.log("owned_qdisc_restored_simulated", no_real_network=True)

    def advance(self, seconds: int) -> None:
        if type(seconds) is not int or seconds < 0:
            raise ValueError("virtual_clock_invalid")
        self.clock += seconds
        self.log("virtual_time_advanced", seconds=seconds)
        if (self.state == "ACTIVE" and self.watchdog_armed
                and self.expires_at is not None
                and self.clock >= self.expires_at):
            self.log("watchdog_deadline_reached")
            self.restore(caller="watchdog")


def run_case(case: str) -> dict:
    if case not in CASES:
        raise ValueError("unknown_simulation")
    slot = Slot()
    x = Trial(slot)
    refused = None
    if case == "no_approval":
        try:
            x.approve(operator_role="viewer")
        except Refusal as exc:
            refused = str(exc)
    elif case == "wrong_target":
        try:
            x.approve(target={**TARGET, "device": "ens33"})
        except Refusal as exc:
            refused = str(exc)
    elif case == "wrong_qdisc":
        try:
            x.approve(original_qdisc="netem")
        except Refusal as exc:
            refused = str(exc)
    elif case == "wrong_management":
        try:
            x.approve(management={**MANAGEMENT, "gateway": "192.168.47.3"})
        except Refusal as exc:
            refused = str(exc)
    elif case == "bad_ttl":
        try:
            x.approve(ttl=3600)
        except Refusal as exc:
            refused = str(exc)
    else:
        x.approve(ttl=30)
        if case == "watchdog_missing":
            try:
                x.apply()
            except Refusal as exc:
                refused = str(exc)
        elif case == "concurrency":
            contender = Trial(slot, token="other-experiment")
            try:
                contender.approve()
            except Refusal as exc:
                refused = str(exc)
        else:
            x.arm_watchdog()
            if case == "apply_failure":
                x.apply(fail_before_change=True)
            else:
                x.apply()
                if case == "success":
                    x.restore(caller="operator")
                elif case == "expired_ttl":
                    x.advance(31)
                elif case == "controller_crash":
                    x.lose_controller()
                    x.advance(31)
                elif case == "foreign_owner":
                    x.effective_qdisc = {"kind": "netem", "owner": "another"}
                    x.advance(31)
                elif case == "rollback_failure":
                    x.restore(restore_success=False)
                elif case == "double_restore":
                    x.restore()
                    x.restore()

    expected = {
        "success": "RESTORED", "expired_ttl": "RESTORED",
        "controller_crash": "RESTORED", "apply_failure": "ABORTED",
        "foreign_owner": "ESCALATED", "rollback_failure": "ESCALATED",
        "double_restore": "RESTORED", "no_approval": "NEW",
        "watchdog_missing": "APPROVED", "concurrency": "APPROVED",
        "wrong_target": "NEW", "wrong_qdisc": "NEW",
        "wrong_management": "NEW", "bad_ttl": "NEW",
    }
    if x.state != expected[case]:
        raise AssertionError(f"Unexpected simulation state {case}: {x.state}")
    if case in ("foreign_owner", "rollback_failure"):
        if slot.owner != x.token:
            raise AssertionError("Escalated operation lost protected lock")
    if case in ("success", "expired_ttl", "controller_crash", "double_restore"):
        if x.effective_qdisc != {"kind": "noqueue", "owner": None}:
            raise AssertionError("Simulated owned qdisc not restored")
    if case in ("no_approval", "wrong_target", "wrong_qdisc",
                "wrong_management", "bad_ttl") and slot.owner is not None:
        raise AssertionError("Refused operation has acquired slot")

    return {
        "schema": SCHEMA, "scenario": case, "outcome": x.state,
        "expected_outcome": expected[case],
        "refusal": refused, "virtual_seconds": x.clock,
        "watchdog_armed_simulated": x.watchdog_armed,
        "qdisc_simulated": x.effective_qdisc, "slot_owned": slot.owner,
        "events": x.events,
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "network_changes_executed": False,
        "real_rollback_implemented": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--save-report", action="store_true")
    options = parser.parse_args()
    if not options.all and not options.case:
        parser.error("Usar --all o --case")
    if options.all and options.case:
        parser.error("No combinar --all con --case")
    os.umask(0o077)

    scenarios = CASES if options.all else (options.case,)
    reports = [run_case(s) for s in scenarios]
    for entry in reports:
        print(f"S06_037_ESCENARIO={entry['scenario']} "
              f"RESULTADO_SIMULADO={entry['outcome']}")
    if options.save_report:
        name = ("S06_037_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                + "_" + secrets.token_hex(3))
        folder = ROOT / name
        folder.mkdir(mode=0o700, parents=True, exist_ok=False)
        path = folder / "simulacion_rollback.json"
        payload = {
            "schema": SCHEMA, "generated_at_utc": utc(),
            "tests": len(reports), "type": "offline_virtual_clock",
            "network_changes_executed": False,
            "real_rollback_implemented": False,
            "results": reports,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        print("S06_037_REPORTE_JSON=" + str(path))
        print("S06_037_REPORTE_INTEGRIDAD=" +
              hashlib.sha256(path.read_bytes()).hexdigest())
    print(f"S06_037_SIMULACIONES_VALIDADAS={len(reports)}")
    print("S06_037_NETEM_EJECUTADO=NO")
    print("S06_037_ROLLBACK_REAL=NO_IMPLEMENTADO")
    print("S06_037_SIMULACIONES=OK")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, Refusal, AssertionError) as exc:
        print("S06_037_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
