from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_pre_submit_readiness_inventory.py"
MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_pre_submit_readiness_inventory", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_pre_submit_readiness_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path, manifest: Path = MANIFEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--manifest",
            str(manifest.relative_to(ROOT) if manifest.is_relative_to(ROOT) else manifest),
            "--output-dir",
            str(output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_inventory_builds(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["candidate_paths_ready"] is True
    inventory = json.loads((tmp_path / "pre_submit_readiness_inventory.json").read_text(encoding="utf-8"))
    assert inventory["status"] == "static_inventory_not_final_submission_acceptance"
    assert inventory["summary"]["candidate_row_count"] >= 10
    assert inventory["summary"]["live_claim_blocker_count"] >= 1


def test_inventory_records_missing_candidate_files(tmp_path: Path) -> None:
    builder = load_builder()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["candidate_rows"][0]["metrics_file"] = "Results/missing/metrics.json"
    bad_manifest = tmp_path / "bad_manifest.json"
    tmp_path.mkdir(parents=True, exist_ok=True)
    bad_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    inventory = builder.build_inventory(bad_manifest)
    assert inventory["summary"]["candidate_paths_ready"] is False
    assert inventory["missing_candidate_files"]


def main() -> int:
    temp = ROOT / ".tmp" / "pre_submit_readiness_inventory_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_inventory_builds(temp / "current")
        test_inventory_records_missing_candidate_files(temp / "missing")
    finally:
        if temp.exists():
            for item in sorted(temp.glob("**/*"), key=lambda path: len(path.parts), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            temp.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
    print("[OK] pre-submit readiness inventory tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
