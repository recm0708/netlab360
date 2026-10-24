"""Pruebas offline del playbook de compliance sobre FRR live (sin Docker/sudo)."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAY = ROOT/"ansible/s03/compliance-frr.yml"

class TestS03AnsibleCompliance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.play=yaml.safe_load(PLAY.read_text(encoding="utf-8"))[0]
        cls.tasks=cls.play["tasks"]

    def test_scope_is_three_router_inventory(self):
        self.assertEqual(self.play["hosts"],"routers")
        self.assertEqual(self.play["connection"],"local")
        self.assertFalse(self.play["gather_facts"])
        self.assertFalse(self.play.get("become",False),
                         "No habilitar elevacion para todo el playbook")

    def test_become_only_on_observation_command(self):
        privileged=[t for t in self.tasks if t.get("become",False)]
        self.assertEqual(len(privileged),1)
        task=privileged[0]
        self.assertIn("ansible.builtin.command",task)
        self.assertEqual(task["become_method"],"sudo")
        # Sudo-rs (Ubuntu 26.04) imprime un prompt no compatible con
        # Ansible 2.20. El fallback aplica solo al auditor read-only.
        self.assertEqual(task["vars"]["ansible_become_exe"],"/usr/bin/sudo.ws")
        self.assertFalse(task["changed_when"])
        self.assertEqual(task["environment"]["HOME"],
                         "{{ lookup('ansible.builtin.env', 'HOME') }}")

    def test_command_targets_compliance_only(self):
        task=next(t for t in self.tasks if "ansible.builtin.command" in t)
        argv=task["ansible.builtin.command"]["argv"]
        self.assertEqual(argv[0],"python3")
        self.assertIn("--router",argv)
        self.assertIn("s03_script",argv[1])
        self.assertTrue(task["check_mode"] is False)
        self.assertEqual(task["failed_when"],"s03_auditoria.rc != 0")

    def test_no_mutating_ansible_modules(self):
        prohibited={"ansible.builtin.shell","ansible.builtin.copy",
                    "ansible.builtin.template","ansible.builtin.file",
                    "ansible.builtin.service","ansible.builtin.systemd"}
        for task in self.tasks:
            self.assertTrue(prohibited.isdisjoint(task))


if __name__=="__main__":
    unittest.main()
