import json
import tempfile
import unittest
from pathlib import Path

from gate import Log, risk, run


class GateTest(unittest.TestCase):
    def setUp(self):
        self.log = Log(Path(tempfile.mkdtemp()) / "audit.log")
        self.calls = []

    def act(self, step):
        self.calls.append(step)
        return f"done: {step}"

    def test_no_action_without_approval(self):
        self.assertEqual(run("a, b", lambda s: False, self.act, self.log), [])
        self.assertEqual(self.calls, [])
        self.assertEqual([e["event"] for e in self.log.entries()], ["planned", "approval", "stopped"])

    def test_acts_after_approval(self):
        run("a, b", lambda s: True, self.act, self.log)
        self.assertEqual(self.calls, ["a", "b"])
        self.assertTrue(self.log.verify())

    def test_approval_sees_full_plan_before_any_action(self):
        seen = []
        run("a, b", lambda s: seen.append((list(s), list(self.calls))) or True, self.act, self.log)
        self.assertEqual(seen, [(["a", "b"], [])])

    def test_edit_breaks_chain(self):
        run("a, b", lambda s: True, self.act, self.log)
        lines = self.log.path.read_text().splitlines()
        e = json.loads(lines[1]); e["data"]["approved"] = False
        lines[1] = json.dumps(e, sort_keys=True)
        self.log.path.write_text("\n".join(lines) + "\n")
        self.assertFalse(self.log.verify())

    def test_deleted_line_breaks_chain(self):
        run("a, b", lambda s: True, self.act, self.log)
        lines = self.log.path.read_text().splitlines()
        del lines[2]
        self.log.path.write_text("\n".join(lines) + "\n")
        self.assertFalse(self.log.verify())

    def test_risk_flags_world_changing_steps(self):
        self.assertEqual(risk("send 2400 reminder emails"), "write")
        self.assertEqual(risk("read open invoices"), "read")
        self.assertEqual(risk(""), "read")

    def test_planned_entry_lists_write_steps(self):
        run("read a, delete b", lambda s: False, self.act, self.log)
        self.assertEqual(self.log.entries()[0]["data"]["writes"], ["delete b"])

    def test_ungated_acts_without_asking_and_logs_it(self):
        asked = []
        run("a, b", lambda s: asked.append(s) or False, self.act, self.log, gated=False)
        self.assertEqual(asked, [])
        self.assertEqual(self.calls, ["a", "b"])
        self.assertIsNone(self.log.entries()[1]["data"]["approved"])
        self.assertTrue(self.log.verify())


if __name__ == "__main__":
    unittest.main()
