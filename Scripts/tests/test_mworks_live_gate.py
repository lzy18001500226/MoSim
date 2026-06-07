#!/usr/bin/env python3
"""Regression checks for the MWORKS live-session gate checker."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_mworks_live_gate.py"


def run_checker(packet_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(packet_path), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_live_task_requires_explicit_sentinel_and_screenshot_gate(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-GATE-SMOKE",
        "mworks_live_gate": {
            "live_mworks_touched": True,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first live step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "activation_state_observation",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "license_api_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_window_evidence_touched",
                "mworks_phase_screenshots",
                "mworks_phase_observations",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "live")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_live_task_rejects_missing_window_evidence_gate(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-MISSING-WINDOW-EVIDENCE",
        "mworks_live_gate": {
            "live_mworks_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first live step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "activation_state_observation",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "license_api_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_phase_screenshots",
                "mworks_phase_observations",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "live")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "department_task_missing_window_evidence_gate" in reasons


def test_department_task_rejects_required_return_fields_missing_observation(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-TASK-MISSING-OBSERVATION",
        "mworks_live_gate": {
            "live_mworks_touched": False,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first business step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_window_evidence_touched",
                "mworks_phase_screenshots",
                "mworks_phase_observations",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    findings = {(finding["reason"], finding["message"]) for finding in report["findings"]}
    assert ("missing_required_return_field", "activation_state_observation") in findings


def test_department_task_requires_engineering_outputs(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-TASK-JSON-ONLY",
        "mworks_live_gate": {
            "live_mworks_touched": False,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first business step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "activation_state_observation",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_window_evidence_touched",
                "mworks_phase_screenshots",
                "mworks_phase_observations",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
            "expected_engineering_outputs": [
                "Results/agent_packets/returns/MWORKS-DEPARTMENT-TASK-JSON-ONLY.json",
                "PROGRESS.md ledger update",
            ],
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "expected_outputs_not_engineering_evidence" in reasons
    assert "json_only_expected_outputs" in reasons


def test_department_task_accepts_diagnostic_only_json_outputs(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-TASK-DIAGNOSTIC-ONLY",
        "mworks_live_gate": {
            "live_mworks_touched": False,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first business step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "activation_state_observation",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_window_evidence_touched",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
            "engineering_output_mode": "preflight_drill_only",
            "expected_engineering_outputs": [
                "sentinel classification JSON",
                "background screenshot manifest",
                "return packet",
            ],
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "department")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_live_return_rejects_missing_background_screenshot(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-RETURN-MISSING-SCREENSHOT",
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "activation_state_observation": "sentinel clean; screenshot/window title observed education marker before live work",
        "license_state": "education_verified",
        "will_not_click_activation_login": True,
        "mworks_phase_screenshots": [{"phase": "check_model", "status": "captured"}],
        "mworks_phase_observations": "after check_model screenshot capture the education window title was still visible",
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "live")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_required_mworks_return_field" in reasons
    assert "missing_background_screenshot" in reasons


def test_live_return_rejects_missing_phase_screenshots(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-RETURN-MISSING-PHASE-SCREENSHOTS",
        "status": "completed",
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel clean; screenshot/window title observed education marker before live work, but no activation API probe was recorded",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_live_phase_screenshots" in reasons
    assert "missing_live_phase_observations" in reasons


def test_live_return_accepts_phase_screenshots_and_observations(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-RETURN-PHASE-SCREENSHOTS",
        "status": "completed",
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel clean; screenshot/window title observed education marker and license API version probe was recorded before live work",
        "license_state": "license_api_recorded_education_version_only",
        "license_api_before": {
            "source": "ModelingPy.License(ltype='info')",
            "value": {"许可证版本": "教育版"},
            "activation_proof_limit": "version_only_no_account_activation_claim",
        },
        "will_not_click_activation_login": True,
        "mworks_phase_screenshots": [
            {"phase": "after_check_model", "status": "captured"},
            {"phase": "after_simulate_plot", "status": "captured"},
        ],
        "mworks_phase_observations": [
            "after check_model screenshot capture, window title stayed in education mode",
            "after simulate/plot screenshot capture, result plot window was visible and no activation dialog appeared",
        ],
        "actual_engineering_outputs": [
            "References/MWORKS/QuadrotorModel/package.mo",
            "check_model passed",
            "SimulateModel data=true",
            "native_result/Result.msr",
        ],
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_live_return_rejects_education_window_without_activation_api(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-RETURN-EDU-WINDOW-ONLY",
        "status": "completed",
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel clean; screenshot/window title observed Sysplorer education marker before live work",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
        "mworks_phase_screenshots": [{"phase": "after_check_model", "status": "captured"}],
        "mworks_phase_observations": ["after check_model screenshot capture, window title stayed in education mode"],
        "actual_engineering_outputs": ["check_model passed"],
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_live_activation_api_evidence" in reasons
    assert "unverified_activation_state_not_returned_as_blocker" in reasons


def test_live_blocker_marked_live_still_requires_api_probe(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-LIVE-BLOCKER-ACTIVATION-UNVERIFIED",
        "status": "blocked",
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel clean and screenshot capture observed Sysplorer education window title, but no activation API proof was available",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
        "mworks_phase_screenshots": [{"phase": "preflight", "status": "not_started_due_to_activation_unverified"}],
        "mworks_phase_observations": ["no check_model phase ran because activation API proof was unavailable"],
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_live_activation_api_evidence" in reasons


def test_department_completed_return_rejects_json_only_outputs(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-RETURN-JSON-ONLY",
        "status": "completed",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel and screenshot capture observed one education-mode window title before business work",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
        "actual_engineering_outputs": [
            "Results/agent_packets/returns/MWORKS-DEPARTMENT-RETURN-JSON-ONLY.json",
            "PROGRESS.md",
        ],
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "json_only_mworks_return" in reasons


def test_mworks_department_static_task_requires_window_evidence_gate(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-STATIC-TASK",
        "mworks_live_gate": {
            "live_mworks_touched": False,
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "department_task_missing_window_evidence_gate" in reasons


def test_mworks_department_window_evidence_return_required_even_when_static(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-STATIC-RETURN",
        "live_mworks_touched": False,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "department_return_missing_window_evidence_flag" in reasons


def test_static_return_accepts_false_live_flag(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-STATIC-RETURN",
        "live_mworks_touched": False,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "static")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_window_evidence_task_requires_full_gate_even_without_live_mcp(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-WINDOW-EVIDENCE-TASK",
        "mworks_live_gate": {
            "live_mworks_touched": False,
            "mworks_window_evidence_touched": True,
        },
    }
    packet_path = tmp_path / "task.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "task", "--expect", "auto")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_required_gate_field" in reasons
    assert "required_boolean_not_true" in reasons


def test_static_return_with_sentinel_requires_window_evidence_flag(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-SENTINEL-RETURN-MISSING-EVIDENCE-FLAG",
        "live_mworks_touched": False,
        "activation_sentinel_before": {"status": "incident_detected"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "screenshot/window title showed mixed education and demo markers",
        "license_state": "mixed_education_and_demo_blocked",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "auto")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_window_evidence_flag" in reasons


def test_window_evidence_blocker_passes_with_required_fields(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-WINDOW-EVIDENCE-BLOCKER",
        "status": "blocked",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "incident_detected"},
        "gui_sentinel_before": {"status": "incident_detected"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": {
            "sentinel_status": "incident_detected",
            "observed_window_title_or_screenshot": "sentinel and screenshot capture observed mixed education and demo window titles",
        },
        "license_state": "mixed_education_and_demo_blocked",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "auto")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True

    department_completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert department_completed.returncode == 0, department_completed.stdout + department_completed.stderr


def test_window_evidence_return_rejects_missing_activation_state_observation(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-WINDOW-EVIDENCE-MISSING-OBSERVATION",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_activation_state_observation" in reasons


def test_department_static_return_requires_activation_state_observation(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-STATIC-MISSING-OBSERVATION",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_activation_state_observation" in reasons


def test_department_return_rejects_vague_activation_observation(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-VAGUE-OBSERVATION",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "ok",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "vague_activation_state_observation" in reasons


def test_department_return_rejects_empty_sentinel_or_screenshot_placeholders(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-EMPTY-SENTINEL-SCREENSHOT",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {},
        "gui_sentinel_before": "",
        "background_screenshot_before": {},
        "activation_state_observation": "sentinel and screenshot evidence were unavailable before any MWORKS work",
        "license_state": "sentinel_unavailable_blocked",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "empty_sentinel_reference" in reasons
    assert "missing_background_screenshot" in reasons


def test_department_return_rejects_unclassified_license_state(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-UNCLASSIFIED-LICENSE",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel was clean and the captured window title was checked before business work",
        "license_state": "looks_fine",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "unclassified_license_state" in reasons


def test_department_return_rejects_observation_without_evidence_source(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-OBSERVATION-WITHOUT-SOURCE",
        "status": "completed",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "clean"},
        "gui_sentinel_before": {"status": "clean"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "The current activation state is acceptable before business work begins.",
        "license_state": "education_window_observed_activation_unverified",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "activation_state_observation_missing_evidence_source" in reasons


def test_department_return_rejects_blocking_license_state_as_completed(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-BLOCKING-LICENSE-AS-COMPLETED",
        "status": "completed",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "incident_detected"},
        "gui_sentinel_before": {"status": "incident_detected"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel and screenshot capture observed mixed education/demo window titles before business work",
        "license_state": "mixed_education_and_demo_blocked",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "blocking_license_state_not_returned_as_blocker" in reasons


def test_department_blocker_accepts_blocking_license_state(tmp_path: Path) -> None:
    packet = {
        "request_id": "MWORKS-DEPARTMENT-BLOCKING-LICENSE-BLOCKER",
        "status": "blocked",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": True,
        "activation_sentinel_before": {"status": "incident_detected"},
        "gui_sentinel_before": {"status": "incident_detected"},
        "background_screenshot_before": {"status": "captured"},
        "activation_state_observation": "sentinel and screenshot capture observed one education window title plus one demo window title before business work",
        "license_state": "mixed_education_and_demo_blocked",
        "will_not_click_activation_login": True,
    }
    packet_path = tmp_path / "return.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path, "--kind", "return", "--expect", "department")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
