#!/usr/bin/env python3
"""Write the px4ctrl generated-C SIL report and export a hash-bound source set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "Results" / "control_platform" / "px4ctrl_codegen_sil_v1"
GENERATED_DIR = (
    RESULT_DIR
    / "generated_c"
    / "MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock"
)
NATIVE_DIR = RESULT_DIR / "native"
EXPORT_DIR = ROOT / "src" / "control" / "codegen" / "px4ctrl"

EXPORTED_SOURCES = [
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c",
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h",
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h",
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_extern_include.h",
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_data.c",
    "mwb_types.h",
    "mwb_runtime.h",
    "mwb_main.c",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def copy_normalized_text(source: Path, target: Path) -> None:
    """Archive generated source with Git-safe text formatting only."""
    text = source.read_text(encoding="utf-8", errors="strict")
    normalized = "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"
    target.write_bytes(normalized.encode("utf-8"))


def shared_library_evidence() -> dict[str, Any]:
    library = NATIVE_DIR / "libpx4ctrl_graphical_generated.so"
    if not library.is_file():
        raise FileNotFoundError(library)
    wsl_library = "/mnt/c/Users/HP/Desktop/MoSim/" + relative(library)
    symbol = subprocess.run(
        ["wsl", "bash", "-lc", f"nm -D --defined-only {wsl_library} | grep MosimPx4ctrlGeneratedGraphStepScalar"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    deps = subprocess.run(
        ["wsl", "bash", "-lc", f"ldd {wsl_library}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    result = {
        "platform": "WSL Linux",
        "artifact": relative(library),
        "sha256": sha256(library),
        "exported_symbol": symbol.stdout.strip(),
        "symbol_check_returncode": symbol.returncode,
        "ldd": deps.stdout.strip(),
        "ldd_returncode": deps.returncode,
        "pass": symbol.returncode == 0 and "MosimPx4ctrlGeneratedGraphStepScalar" in symbol.stdout and deps.returncode == 0 and "not found" not in deps.stdout,
    }
    return result


def main() -> int:
    build = read_json(RESULT_DIR / "logs" / "MODEL_BUILD_MANIFEST.json")
    fixture = read_json(RESULT_DIR / "logs" / "FIXTURE_SIL_RESULT.json")
    raw_c = read_json(RESULT_DIR / "logs" / "RAW_C_SIL_RESULT.json")
    closed_loop = read_json(RESULT_DIR / "logs" / "CLOSED_LOOP_SIL_RESULT.json")
    shared = shared_library_evidence()

    direct_pass = bool(
        fixture.get("pass")
        and float(fixture["graphical_vs_cfunction"]["max_abs"]) <= 1e-12
        and raw_c.get("ok")
        and float(raw_c["comparison"]["max_abs_error"]) <= 1e-12
    )
    closed_pass = bool(closed_loop.get("pass"))
    passed = bool(direct_pass and closed_pass and shared["pass"])
    if not passed:
        raise RuntimeError("refusing code export because one or more SIL gates failed")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_hashes: dict[str, str] = {}
    for name in EXPORTED_SOURCES:
        source = GENERATED_DIR / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = EXPORT_DIR / name
        copy_normalized_text(source, target)
        export_hashes[name] = sha256(target)
    source_wrapper = NATIVE_DIR / "px4ctrl_graphical_generated_shared.c"
    target_wrapper = EXPORT_DIR / source_wrapper.name
    copy_normalized_text(source_wrapper, target_wrapper)
    export_hashes[target_wrapper.name] = sha256(target_wrapper)

    manifest = {
        "schema": "mosim.px4ctrl_codegen_export.v1",
        "generated_graphical_model": build["generated_model"],
        "generated_c_hashes": build["generated_c_hashes"],
        "exported_files": export_hashes,
        "export_normalization": "LF line endings and trailing horizontal whitespace removed after MWORKS code generation; executable tokens are unchanged.",
        "cfunction_interface": build["interface"],
        "shared_library_evidence": shared,
        "sil_result": relative(RESULT_DIR / "logs" / "CLOSED_LOOP_SIL_RESULT.json"),
        "claim_boundary": "This source set passed MWORKS graphical-to-C SIL only. Gazebo/PX4 integration is a separate runtime gate.",
    }
    (EXPORT_DIR / "CODEGEN_MANIFEST.json").write_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )

    position = closed_loop["differences"]["position"]
    attitude = closed_loop["differences"]["attitude"]
    rotor = closed_loop["differences"]["rotor_command"]
    report = f'''# PX4CTRL Generated-C SIL Equivalence Report

## Verdict

**PASS**. The MWORKS graphical model, MWORKS CFunction envelope, standalone generated-C runtime, and 50 s whole-aircraft generated-C Runner meet the requested numerical thresholds.

This report proves the MWORKS graphical-to-generated-C chain only. It does not claim Gazebo, PX4, ROS, MAVROS, or flight-runtime equivalence.

## Code Generation

- Source graphical model: `{build["generated_model"]}`
- Generated C source hash: `{build["generated_c_hashes"]["source"]}`
- Graphical model hash: `{closed_loop["source_hashes"]["graphical_model"]}`
- CFunction model hash: `{closed_loop["source_hashes"]["cfunction_model"]}`
- Generated runner hash: `{closed_loop["source_hashes"]["generated_runner"]}`
- Sample period: `0.01 s`, double precision
- Export archive normalization: LF line endings and trailing horizontal whitespace only

## Compilation

- C99 generated-source compile and nonzero runtime harness: pass (`{relative(RESULT_DIR / "logs" / "RAW_C_SIL_RESULT.json")}`)
- Shared object: `{shared["artifact"]}`
- Shared object SHA-256: `{shared["sha256"]}`
- Exported entry point: `{shared["exported_symbol"]}`
- Dynamic dependencies resolved: `{shared["pass"]}`

## Direct SIL

| Comparison | Inputs | Maximum absolute difference | Verdict |
| --- | ---: | ---: | --- |
| Graphical Sysblock vs MWORKS CFunction | 4 nonzero vectors, 8 outputs | {fixture["graphical_vs_cfunction"]["max_abs"]:.3e} | PASS |
| Graphical Sysblock vs standalone generated C | 4 nonzero vectors, 8 outputs | {raw_c["comparison"]["max_abs_error"]:.3e} | PASS |

## 50 s Whole-Aircraft SIL

Both runners used their unmodified model annotation: Dassl, `0..50 s`, tolerance `1e-4`, output interval `0.01 s`; each returned 5001 samples.

| Signal family | Metric | Observed | Threshold | Verdict |
| --- | --- | ---: | ---: | --- |
| Position | aggregate RMSE (m) | {position["aggregate_rmse"]:.3e} | < 1.0e-6 | PASS |
| Attitude | maximum absolute difference (rad) | {attitude["aggregate_max_abs"]:.3e} | < 1.0e-8 | PASS |
| Rotor command | maximum absolute difference (rad/s) | {rotor["aggregate_max_abs"]:.3e} | < 1.0e-6 | PASS |

## Artifacts

- Generated C: `{relative(GENERATED_DIR)}`
- Native CFunction wrapper: `{relative(NATIVE_DIR / "px4ctrl_graphical_generated_wrapper.c")}`
- 50 s raw baseline: `{relative(Path(closed_loop["baseline"]["raw_csv"]))}`
- 50 s raw generated-C runner: `{relative(Path(closed_loop["generated_cfunction"]["raw_csv"]))}`
- Closed-loop metrics: `{relative(RESULT_DIR / "logs" / "CLOSED_LOOP_SIL_RESULT.json")}`
- Exported source set: `{relative(EXPORT_DIR)}`

## Runtime Handoff Boundary

The next and only remaining evidence layer is a separate Gazebo/PX4 integration run that calls this hash-bound generated entry point through the px4ctrl runtime interface. That run must verify coordinate frames, units, scheduling, initialization, and actuator command mapping under the intended Gazebo scenario.
'''
    (RESULT_DIR / "SIL_EQUIVALENCE_REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    status = {
        "schema": "mosim.px4ctrl_codegen_sil_status.v1",
        "status": "passed",
        "report": relative(RESULT_DIR / "SIL_EQUIVALENCE_REPORT.md"),
        "export_manifest": relative(EXPORT_DIR / "CODEGEN_MANIFEST.json"),
        "shared_library": shared,
        "direct_sil_pass": direct_pass,
        "closed_loop_sil_pass": closed_pass,
        "gazebo_boundary": "not run in this thread",
    }
    (RESULT_DIR / "SIL_EQUIVALENCE_STATUS.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
