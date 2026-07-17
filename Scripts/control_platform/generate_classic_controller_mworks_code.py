#!/usr/bin/env python3
"""Run official Sysplorer code generation for the classic controller bridge."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks"
MODEL_NAME = "MoSim_Classic_CFunction_Sysblock"
MODEL_PATH = RESULT_DIR / "models" / f"{MODEL_NAME}.mo"
CODEGEN_ROOT = RESULT_DIR / "codegen"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_generated_text(code_dir: Path) -> None:
    text_suffixes = {".c", ".h", ".json", ".xml"}
    for path in sorted(item for item in code_dir.rglob("*") if item.is_file()):
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        normalized = "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"
        path.write_text(normalized, encoding="utf-8", newline="\n")


def main() -> dict:
    CODEGEN_ROOT.mkdir(parents=True, exist_ok=True)
    if not ModelingPy.ClassExist(MODEL_NAME):
        if not ModelingPy.OpenModelFile(str(MODEL_PATH)):
            raise RuntimeError(f"OpenModelFile failed for {MODEL_PATH}")
    if not ModelingPy.CheckModel(MODEL_NAME):
        raise RuntimeError(f"CheckModel failed: {ModelingPy.GetLastErrors()}")

    options = ModelingPy.GetModelCodeGenerationOptions(MODEL_NAME)
    options["CodePlatform.OutPath"] = {"output": str(CODEGEN_ROOT)}
    if not ModelingPy.SetModelCodeGenerationOptions(MODEL_NAME, options):
        raise RuntimeError(f"SetModelCodeGenerationOptions failed: {ModelingPy.GetLastErrors()}")
    if not ModelingPy.GenerateModelCode(MODEL_NAME):
        raise RuntimeError(f"GenerateModelCode failed: {ModelingPy.GetLastErrors()}")

    code_dir = CODEGEN_ROOT / MODEL_NAME
    normalize_generated_text(code_dir)
    files = {
        str(path.relative_to(code_dir)).replace("\\", "/"): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(code_dir.rglob("*"))
        if path.is_file()
    }
    required = {
        f"{MODEL_NAME}.c",
        f"{MODEL_NAME}.h",
        f"{MODEL_NAME}_data.c",
        f"{MODEL_NAME}_private.h",
        "extern_inc/momodel_extern_ince1.c",
    }
    missing = sorted(required - files.keys())
    manifest = {
        "schema": "mosim.classic_controller.mworks_codegen_manifest.v1",
        "status": "passed" if not missing else "failed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "MWORKS_MCP_LIVE",
        "official_api": "ModelingPy.GenerateModelCode",
        "model_name": MODEL_NAME,
        "model_path": str(MODEL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "model_sha256": sha256(MODEL_PATH),
        "codegen_options": options,
        "generated_code_dir": str(code_dir.relative_to(ROOT)).replace("\\", "/"),
        "generated_file_count": len(files),
        "generated_files": files,
        "missing_required_files": missing,
        "archive_normalization": "LF line endings and trailing horizontal whitespace removed after GenerateModelCode; executable tokens are unchanged.",
        "claim_ceiling": "Official MWORKS-generated C archive only; generated-C SIL and external runtime remain separate gates.",
    }
    manifest_path = RESULT_DIR / "MWORKS_CODEGEN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    if missing:
        raise RuntimeError(f"generated archive missing required files: {missing}")
    return {"ok": True, "manifest": str(manifest_path), "generated_file_count": len(files)}


RUN_SCRIPT_RESULT = main()
