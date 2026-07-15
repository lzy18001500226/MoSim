from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_capability_index.py"
INDEX = ROOT / "Config" / "capabilities" / "capability_index.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_capability_index", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_capability_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_capability_index_passes() -> None:
    completed = run_checker(INDEX)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["capability_count"] >= 10


def test_rejects_authority_grant_language() -> None:
    checker = load_checker()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    index["capabilities"][0]["stop_actions"].append("permission granted; may restart")
    report = checker.validate_index(index)
    assert report["ok"] is False
    assert any(finding["reason"] == "capability_claims_authority" for finding in report["findings"])


def test_rejects_missing_required_capability_id() -> None:
    checker = load_checker()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    index["capabilities"] = [
        capability
        for capability in index["capabilities"]
        if capability["id"] != "review.evidence_gate"
    ]
    report = checker.validate_index(index)
    assert report["ok"] is False
    assert any(
        finding["reason"] == "missing_required_capability_ids"
        for finding in report["findings"]
    )


def test_rejects_empty_required_lists() -> None:
    checker = load_checker()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    index["capabilities"][0]["owner_docs"] = []
    report = checker.validate_index(index)
    assert report["ok"] is False
    assert any(finding["reason"] == "empty_required_list" for finding in report["findings"])


def main() -> int:
    test_current_capability_index_passes()
    test_rejects_authority_grant_language()
    test_rejects_missing_required_capability_id()
    test_rejects_empty_required_lists()
    print("[OK] capability index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
