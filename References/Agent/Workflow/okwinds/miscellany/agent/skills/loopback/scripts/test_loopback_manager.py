import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
MANAGER = SCRIPT_DIR / "loopback-manager.py"


def run_manager(args, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(MANAGER), *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def write_state(cwd: Path, *, active=True, iteration=1, max_iterations=0, completion_promise=None, prompt="noop"):
    codex_dir = cwd / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    promise_yaml = "null" if completion_promise is None else json.dumps(completion_promise)
    content = (
        "---\n"
        f"active: {str(active).lower()}\n"
        f"iteration: {iteration}\n"
        f"max_iterations: {max_iterations}\n"
        f"completion_promise: {promise_yaml}\n"
        'started_at: "2026-02-10T00:00:00Z"\n'
        "---\n\n"
        f"{prompt}\n"
    )
    (codex_dir / "loopback.local.md").write_text(content)


class LoopbackManagerTests(unittest.TestCase):
    def test_check_allows_iteration_equal_max(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            write_state(cwd, iteration=3, max_iterations=3)
            p = run_manager(["check"], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("CONTINUE: Iteration 3", p.stdout)

    def test_advance_stops_at_max_after_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            write_state(cwd, iteration=3, max_iterations=3)
            out_file = cwd / ".codex" / "out.log"
            out_file.write_text("not done\n")

            p = run_manager(["advance", "--output-file", str(out_file)], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
            self.assertTrue(data["stop"])
            self.assertIn("max_iterations_reached", data["reason"])

            status = run_manager(["status"], cwd=cwd)
            self.assertIn("Active: False", status.stdout)
            self.assertIn("Final Iteration: 3", status.stdout)

    def test_advance_stops_on_completion_promise(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            write_state(cwd, iteration=1, max_iterations=20, completion_promise="DONE")
            out_file = cwd / ".codex" / "out.log"
            out_file.write_text("ok\n<promise>DONE</promise>\n")

            p = run_manager(["advance", "--output-file", str(out_file)], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
            self.assertTrue(data["stop"])
            self.assertIn("completion_promise_detected", data["reason"])

            status = run_manager(["status"], cwd=cwd)
            self.assertIn("Active: False", status.stdout)
            self.assertIn("Final Iteration: 1", status.stdout)

    def test_set_session_updates_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            write_state(cwd, iteration=1, max_iterations=2)

            p = run_manager(["set-session", "--session-id", "019c480b-fcdf-7ef3-876b-ec0ed2166f1b"], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("OK", p.stdout)

            info = run_manager(["info", "--json"], cwd=cwd)
            self.assertEqual(info.returncode, 0, info.stderr)
            data = json.loads(info.stdout)
            self.assertEqual(data["session_id"], "019c480b-fcdf-7ef3-876b-ec0ed2166f1b")


if __name__ == "__main__":
    unittest.main()
