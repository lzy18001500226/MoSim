import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EXTRACTOR = SCRIPT_DIR / "extract_codex_json.py"


class ExtractCodexJsonTests(unittest.TestCase):
    def test_extracts_thread_id_and_agent_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            thread_file = cwd / "thread.txt"

            sample = "\n".join(
                [
                    '{"type":"thread.started","thread_id":"abc-123"}',
                    '{"type":"turn.started"}',
                    '{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"Hello"}}',
                    '{"type":"item.completed","item":{"id":"item_1","type":"agent_message","text":"World\\n"}}',
                ]
            )

            p = subprocess.run(
                ["python3", str(EXTRACTOR), "--thread-id-file", str(thread_file)],
                input=sample,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(thread_file.read_text(), "abc-123")
            self.assertEqual(p.stdout, "Hello\nWorld\n")


if __name__ == "__main__":
    unittest.main()

