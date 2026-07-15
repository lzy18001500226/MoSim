from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_capability_resolution.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_capability_resolution", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_capability_resolution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_resolution() -> dict:
    return {
        "required": True,
        "capability_index_consulted": True,
        "consulted_index_path": "Docs/Index/capability_index.md",
        "matched_capability_ids": ["desktop.window.capture_evidence"],
        "matched_capabilities": ["Desktop window screenshot evidence"],
        "existing_assets_to_reuse": [
            "Docs/Skills/Desktop/window-capture-evidence/SKILL.md",
            "Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers",
        ],
        "searched_existing_assets": [
            "Docs/Index/capability_index.md",
            "Docs/Skills/",
            "Scripts/",
        ],
        "create_new_assets": [],
        "reason_existing_assets_insufficient": "",
        "do_not_recreate": ["window screenshot skill"],
        "unresolved_capabilities": [],
        "notes": "Capability resolution is routing evidence, not permission.",
    }


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


def test_template_and_visible_thread_packet_pass_strict() -> None:
    template_result = run_checker(ROOT / "Config/protocol/templates/capability_resolution.json")
    assert template_result.returncode == 0, template_result.stdout + template_result.stderr

    packet_result = run_checker(ROOT / "Config/protocol/templates/visible_thread_dispatch_packet.json", "--strict")
    assert packet_result.returncode == 0, packet_result.stdout + packet_result.stderr
    report = json.loads(packet_result.stdout)
    assert report["ok"] is True


def test_valid_resolution_passes() -> None:
    checker = load_checker()
    report = checker.validate_packet({"capability_resolution": valid_resolution()}, strict=True)
    assert report["ok"], report


def test_rejects_new_skill_without_existing_asset_search(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = {"capability_resolution": valid_resolution()}
    resolution = payload["capability_resolution"]
    resolution["capability_index_consulted"] = False
    resolution["searched_existing_assets"] = ["Scripts/"]
    resolution["existing_assets_to_reuse"] = []
    resolution["matched_capability_ids"] = []
    resolution["matched_capabilities"] = []
    resolution["create_new_assets"] = ["Docs/Skills/Desktop/new-window-capture/SKILL.md"]
    resolution["reason_existing_assets_insufficient"] = ""
    resolution["do_not_recreate"] = []

    path = tmp_path / "packet.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    completed = run_checker(path, "--strict")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "capability_index_not_consulted" in reasons
    assert "missing_existing_asset_search" in reasons
    assert "new_asset_without_insufficiency_reason" in reasons


def test_rejects_capability_resolution_as_permission(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = {"capability_resolution": valid_resolution()}
    payload["capability_resolution"]["notes"] = "Permission granted; may click and may restart."
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    completed = run_checker(path, "--strict")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert any(
        finding["reason"] == "capability_resolution_claims_authority"
        for finding in report["findings"]
    )


def main() -> int:
    test_template_and_visible_thread_packet_pass_strict()
    test_valid_resolution_passes()
    temp = ROOT / ".tmp" / "capability_resolution_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_rejects_new_skill_without_existing_asset_search(temp / "new_skill")
        test_rejects_capability_resolution_as_permission(temp / "permission")
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
    print("[OK] capability resolution tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
