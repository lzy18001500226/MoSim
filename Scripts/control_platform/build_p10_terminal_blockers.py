#!/usr/bin/env python3
"""Build reproducible P10 blockers for unavailable mu and Neural-SMC routes."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718"


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def mu_blocker(created_at: str) -> dict:
    audit_path = RESULT / "mu_synthesis/SYSLAB_MU_CAPABILITY_AUDIT.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    dynamic_available = bool(audit["dynamic_mu_controller_synthesis_available"])
    return {
        "schema": "mosim.p10_mworks_gap.terminal_blocker.v1",
        "status": "blocked" if not dynamic_available else "reopen_required",
        "created_at": created_at,
        "controller": "mu_synthesis",
        "blocked_stage": "controller_synthesis_before_mworks",
        "missing_capability": "dynamic musyn or MuSynthesis controller synthesis",
        "available_but_insufficient": ["cmsclsyn constant-matrix scaling", "mussv mu analysis"],
        "evidence": relative(audit_path),
        "evidence_sha256": sha256(audit_path),
        "reopen_gate": "Install or provide a licensed/reproducible dynamic mu-synthesis implementation, then freeze the synthesized controller and restart at graphical MWORKS MIL.",
        "forbidden_substitution": "Do not label constant-matrix cmsclsyn/mussv analysis as a dynamic mu-synthesis controller.",
        "evidence_ladder": {
            "controller_synthesis": "blocked",
            "graphical_sysblock_fixture": "blocked_upstream",
            "check_model": "not_run",
            "simulate_model": "not_run",
            "official_generate_model_code": "not_run",
            "generated_c_sil": "not_run",
            "generated_c_gazebo": "not_run",
        },
    }


def neural_smc_blocker(created_at: str) -> dict:
    roots = [
        ROOT / "Config/control_platform",
        ROOT / "Config/profiles",
        ROOT / "Scripts/control_platform",
        ROOT / "Scripts/tests",
        ROOT / "Models",
        ROOT / "Results/control_platform/p3_sliding_mode_source_20260716",
        ROOT / "Results/control_platform/p3_sliding_mode_mworks_20260716",
        ROOT / "Results/control_platform/classic_controller_closeout_20260717",
    ]
    text_hits: list[str] = []
    artifact_hits: list[str] = []
    artifact_suffixes = {".onnx", ".pt", ".pth", ".h5", ".npz", ".npy", ".mat", ".csv"}
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            lowered = path.name.lower().replace("-", "_")
            if "neural_smc" not in lowered and not ("neural" in lowered and "smc" in lowered):
                continue
            text_hits.append(relative(path))
            if path.suffix.lower() in artifact_suffixes:
                artifact_hits.append(relative(path))
    source_gate = ROOT / "Results/control_platform/p3_sliding_mode_source_20260716/P3_SLIDING_MODE_SOURCE_GATE.json"
    return {
        "schema": "mosim.p10_mworks_gap.terminal_blocker.v1",
        "status": "blocked" if not artifact_hits else "manual_review_required",
        "created_at": created_at,
        "controller": "neural_smc",
        "blocked_stage": "frozen_learning_asset_before_mworks",
        "scan_roots": [relative(path) for path in roots],
        "neural_smc_named_files": text_hits,
        "candidate_dataset_or_weight_artifacts": artifact_hits,
        "missing_requirements": [
            "frozen Neural-SMC training dataset with provenance",
            "trained model or fixed-size bounded inference weights with hash",
            "deterministic fallback and reset tests",
            "independent safety benchmark against a non-neural SMC baseline",
        ],
        "prior_source_gate": relative(source_gate),
        "prior_source_gate_sha256": sha256(source_gate),
        "reopen_gate": "Provide all four missing requirements, then implement deterministic fixed-size inference and restart at source/lifecycle and graphical MWORKS MIL.",
        "forbidden_substitution": "Do not use an untrained zero residual, P9 Neural Residual, or another SMC variant as Neural-SMC evidence.",
        "evidence_ladder": {
            "frozen_training_asset": "blocked",
            "deterministic_inference": "not_run",
            "graphical_sysblock_fixture": "blocked_upstream",
            "check_model": "not_run",
            "simulate_model": "not_run",
            "official_generate_model_code": "not_run",
            "generated_c_sil": "not_run",
            "generated_c_gazebo": "not_run",
        },
    }


def main() -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    mu = mu_blocker(created_at)
    neural = neural_smc_blocker(created_at)
    write(RESULT / "mu_synthesis/TERMINAL_BLOCKER.json", mu)
    write(RESULT / "neural_smc/TERMINAL_BLOCKER.json", neural)
    summary = {
        "schema": "mosim.p10_mworks_gap.terminal_blockers.v1",
        "status": "closed_with_blockers",
        "created_at": created_at,
        "controllers": {
            "mu_synthesis": mu["status"],
            "neural_smc": neural["status"],
        },
        "blockers": [
            "Results/control_platform/p10_mworks_gap_closeout_20260718/mu_synthesis/TERMINAL_BLOCKER.json",
            "Results/control_platform/p10_mworks_gap_closeout_20260718/neural_smc/TERMINAL_BLOCKER.json",
        ],
    }
    write(RESULT / "P10_TERMINAL_BLOCKERS.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if mu["status"] == "blocked" and neural["status"] == "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
