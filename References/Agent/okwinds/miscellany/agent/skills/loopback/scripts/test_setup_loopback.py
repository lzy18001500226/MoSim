import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SETUP = SCRIPT_DIR / "setup-loopback.sh"


def run_setup(args, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SETUP), *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        env={
            # Keep environment minimal and deterministic.
            "PATH": str(Path("/usr/bin")) + ":" + str(Path("/bin")) + ":" + str(Path("/usr/sbin")) + ":" + str(Path("/sbin")),
        },
    )


class SetupLoopbackGuideTests(unittest.TestCase):
    def test_guide_prints_steps_and_does_not_create_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            # NOTE: `--no-run` is here to make the pre-fix behavior safe (otherwise the
            # script may launch the driver). After the fix, `--guide` should exit early
            # and ignore other flags.
            p = run_setup(["--no-run", "--guide"], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("Loopback", p.stdout)
            self.assertIn("Step 1", p.stdout)

            self.assertFalse((cwd / ".codex" / "loopback.local.md").exists())

    def test_missing_stop_contract_fails_without_allow_infinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            p = run_setup(["--no-run", "Do something"], cwd=cwd)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("stop", p.stderr.lower() + p.stdout.lower())
            self.assertFalse((cwd / ".codex" / "loopback.local.md").exists())

    def test_allow_infinite_allows_missing_stop_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            p = run_setup(["--no-run", "--allow-infinite", "Do something"], cwd=cwd)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue((cwd / ".codex" / "loopback.local.md").exists())

    def test_fresh_and_reuse_session_mutual_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)

            p = run_setup(
                [
                    "--no-run",
                    "--completion-promise",
                    "DONE",
                    "--fresh-session",
                    "--reuse-session",
                    "Do something",
                ],
                cwd=cwd,
            )
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("exclusive", p.stderr.lower() + p.stdout.lower())
            self.assertFalse((cwd / ".codex" / "loopback.local.md").exists())


if __name__ == "__main__":
    unittest.main()
