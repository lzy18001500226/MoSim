#!/usr/bin/env python3
"""Materialize the px4ctrl generated-C CFunction and SIL fixtures.

Run this file inside an already-authorized Sysplorer session.  It never edits
the px4ctrl graphical model or its gains.  It derives the CFunction body from
the files emitted by MWORKS GenerateModelCode, then creates project-local
evidence models under the task result directory.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results" / "control_platform" / "px4ctrl_codegen_sil_v1"
GENERATED_DIR = (
    RESULT_DIR
    / "generated_c"
    / "MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock"
)
MODEL_DIR = RESULT_DIR / "models"
RAW_DIR = RESULT_DIR / "raw"
LOG_DIR = RESULT_DIR / "logs"

GRAPHICAL_MODEL = (
    "MoSimQuadrotorModel.Control.Implementations.Sysblocks."
    "PX4CTRL_Original_OuterLoop_Graphical_Sysblock"
)
CFUNCTION_MODEL = "PX4CTRL_Generated_CFunction_Sysblock"
ADAPTER_MODEL = "Px4CtrlGeneratedCodeAttitudeThrustAdapter"
RUNNER_MODEL = "Px4CtrlGeneratedCodeFormalRunner"
GRAPHICAL_FIXTURE = "PX4CTRL_Graphical_SIL_Reference_Fixture"
CFUNCTION_FIXTURE = "PX4CTRL_Generated_CFunction_SIL_Fixture"

INPUTS = [
    "ref_px", "px", "ref_vx", "vx", "ref_ax",
    "ref_py", "py", "ref_vy", "vy", "ref_ay",
    "ref_pz", "pz", "ref_vz", "vz", "ref_az",
    "yaw_mea", "ref_yaw",
]
OUTPUTS = [
    "desired_acc_x", "desired_acc_y", "desired_acc_z", "roll_cmd",
    "pitch_cmd", "yaw_cmd", "collective_thrust_n", "normalized_thrust",
]

TEST_CASES = [
    {
        "ref_px": 1.2, "px": -0.4, "ref_vx": 0.3, "vx": -0.1, "ref_ax": 0.05,
        "ref_py": -0.8, "py": 0.25, "ref_vy": -0.2, "vy": 0.15, "ref_ay": -0.04,
        "ref_pz": 1.7, "pz": 0.9, "ref_vz": 0.1, "vz": -0.05, "ref_az": 0.02,
        "yaw_mea": 0.35, "ref_yaw": -0.12,
    },
    {
        "ref_px": -0.6, "px": 0.3, "ref_vx": -0.2, "vx": 0.14, "ref_ax": -0.06,
        "ref_py": 0.7, "py": -0.5, "ref_vy": 0.18, "vy": -0.09, "ref_ay": 0.08,
        "ref_pz": 0.4, "pz": 0.65, "ref_vz": -0.12, "vz": 0.07, "ref_az": -0.03,
        "yaw_mea": -0.55, "ref_yaw": 0.27,
    },
    {
        "ref_px": 0.15, "px": 0.2, "ref_vx": 0.0, "vx": 0.04, "ref_ax": 0.11,
        "ref_py": 0.3, "py": 0.1, "ref_vy": 0.05, "vy": -0.03, "ref_ay": -0.09,
        "ref_pz": 1.0, "pz": 1.25, "ref_vz": 0.2, "vz": 0.1, "ref_az": 0.04,
        "yaw_mea": 0.9, "ref_yaw": 0.0,
    },
    {
        "ref_px": 0.0, "px": 0.0, "ref_vx": 0.0, "vx": 0.0, "ref_ax": 0.0,
        "ref_py": 0.0, "py": 0.0, "ref_vy": 0.0, "vy": 0.0, "ref_ay": 0.0,
        "ref_pz": 0.0, "pz": 0.0, "ref_vz": 0.0, "vz": 0.0, "ref_az": 0.0,
        "yaw_mea": 0.0, "ref_yaw": 0.0,
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def modelica_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def remove_include_guard(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#ifndef\s+[A-Za-z_][A-Za-z0-9_]*$", stripped):
            continue
        if re.match(r"^#define\s+[A-Za-z_][A-Za-z0-9_]*$", stripped):
            continue
        if stripped.startswith("#endif"):
            continue
        lines.append(line)
    return "\n".join(lines)


def flatten_generated_c() -> tuple[str, dict[str, str]]:
    required = {
        "types": GENERATED_DIR / "mwb_types.h",
        "runtime": GENERATED_DIR / "mwb_runtime.h",
        "header": GENERATED_DIR / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h",
        "private": GENERATED_DIR / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h",
        "source": GENERATED_DIR / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c",
        "data": GENERATED_DIR / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_data.c",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"generated code is incomplete: {missing}")

    # CFunction simulation units already include MWORKS' Mwb* typedefs.  The
    # generated mwb_types.h would redeclare incompatible aliases there, so the
    # mechanical envelope retains only generated model declarations and code.
    fragments: list[str] = ["#include <math.h>"]
    for key in ("header", "private"):
        fragment = remove_include_guard(required[key].read_text(encoding="utf-8"))
        fragment = "\n".join(
            line for line in fragment.splitlines()
            if not line.strip().startswith("#include")
            and line.strip() not in {"void Step(void);", "void Init(void);"}
        )
        fragments.append(fragment)
    source = "\n".join(
        line for line in required["source"].read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("#include")
    )
    source = source.replace(
        "void Step(void)",
        "static void MosimPx4ctrlGeneratedGraphStep(void)",
        1,
    ).replace(
        "void Init(void)",
        "static void MosimPx4ctrlGeneratedGraphInit(void)",
        1,
    )
    fragments.append(source)

    arguments = ",\n  ".join(f"double {name}" for name in INPUTS)
    output_arguments = ",\n  ".join(f"double *{name}" for name in OUTPUTS)
    assignments = "\n  ".join(
        f"graphical_sysblockGbIn.{name} = {name};" for name in INPUTS
    )
    outputs = "\n  ".join(
        f"*{name} = agraphical_sysblockGbOut.{name};" for name in OUTPUTS
    )
    fragments.append(
        "\n".join(
            [
                "void MosimPx4ctrlGeneratedGraphStepScalar(",
                f"  {arguments},",
                f"  {output_arguments})",
                "{",
                "  static int mosim_px4ctrl_generated_initialized = 0;",
                "  if (!mosim_px4ctrl_generated_initialized) {",
                "    MosimPx4ctrlGeneratedGraphInit();",
                "    mosim_px4ctrl_generated_initialized = 1;",
                "  }",
                f"  {assignments}",
                "  MosimPx4ctrlGeneratedGraphStep();",
                f"  {outputs}",
                "}",
            ]
        )
    )
    flattened = "\n\n".join(fragments).strip() + "\n"
    # A standalone Sysblock and a Modelica composite compile external C against
    # different MWORKS type headers.  Normalize only generated primitive type
    # aliases so the exact generated arithmetic compiles in both units.
    for generated_type, c_type in {
        "MwbDouble": "double",
        "MwbInt32": "int",
        "MwbInt8": "signed char",
    }.items():
        flattened = re.sub(rf"\b{generated_type}\b", c_type, flattened)
    return flattened, {key: sha256(path) for key, path in required.items()}


def port_arrangement(names: list[str]) -> str:
    return ", ".join(names)


def port_labels(names: list[str]) -> str:
    return ",".join(f'label(text="{name}",instance="{name}")' for name in names)


def c_port_decl(direction: str, name: str) -> str:
    kind = "Inport" if direction == "input" else "Outport"
    return (
        f"    SysplorerEmbeddedCoder.Port.{kind} {name} "
        "annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref=\"double\"),"
        "Dimension(dimensionType=DimensionType.none)=1)),"
        "Placement(transformation(origin={0,0},extent={{-10,-10},{10,10}})));"
    )


def outer_port_decl(direction: str, name: str, index: int) -> str:
    kind = "Inport" if direction == "input" else "Outport"
    x = -260 if direction == "input" else 260
    y = 210 - index * 26
    return (
        f"  SysplorerEmbeddedCoder.Port.{kind} {name} "
        f"annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-8,-8}},{{8,8}}}})),"
        "__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref=\"double\"),"
        "Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group=\"D1\")=0.01)));"
    )


def build_cfunction_model(include_code: str) -> str:
    function_args = ",".join(INPUTS + OUTPUTS)
    c_inputs = "\n".join(
        f"      input SysplorerEmbeddedCoder.Types.Auto {name} annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref=\"double\"),Dimension(dimensionType=DimensionType.none)=1)));"
        for name in INPUTS
    )
    c_outputs = "\n".join(
        f"      output SysplorerEmbeddedCoder.Types.Auto {name} annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref=\"double\"),Dimension(dimensionType=DimensionType.none)=1)));"
        for name in OUTPUTS
    )
    c_ports = "\n".join(
        [*(c_port_decl("input", name) for name in INPUTS), *(c_port_decl("output", name) for name in OUTPUTS)]
    )
    outer_ports = "\n".join(
        [*(outer_port_decl("input", name, index) for index, name in enumerate(INPUTS)), *(outer_port_decl("output", name, index) for index, name in enumerate(OUTPUTS))]
    )
    input_connects = "\n".join(
        f"  connect({name}, cFunction.{name});" for name in INPUTS
    )
    output_connects = "\n".join(
        f"  connect(cFunction.{name}, {name});" for name in OUTPUTS
    )
    return f'''model {CFUNCTION_MODEL}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left({port_arrangement(INPUTS)}), Right({port_arrangement(OUTPUTS)})),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.02,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-300,-220}},{{300,240}}}},grid={{2,2}})));

  CFunction cFunction annotation(__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
{outer_ports}

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left({port_arrangement(INPUTS)}), Right({port_arrangement(OUTPUTS)})),PortLabels(labelType="CustomType",labels({port_labels(INPUTS + OUTPUTS)})),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true));
    function func_CFunction
{c_inputs}
{c_outputs}
    external "C" MosimPx4ctrlGeneratedGraphStepScalar({function_args})
      annotation(Include="{modelica_escape(include_code)}");
    end func_CFunction;

{c_ports}
  equation
    ({", ".join(OUTPUTS)}) = func_CFunction({", ".join(INPUTS)});
  end CFunction;

equation
{input_connects}
{output_connects}
end {CFUNCTION_MODEL};
'''


def build_adapter_model() -> str:
    assignments = "\n  ".join(
        [
            "core.ref_px = position_ref[1];", "core.px = position_mea[1];",
            "core.ref_vx = velocity_ref[1];", "core.vx = velocity_mea[1];",
            "core.ref_ax = acceleration_ref[1];", "core.ref_py = position_ref[2];",
            "core.py = position_mea[2];", "core.ref_vy = velocity_ref[2];",
            "core.vy = velocity_mea[2];", "core.ref_ay = acceleration_ref[2];",
            "core.ref_pz = position_ref[3];", "core.pz = position_mea[3];",
            "core.ref_vz = velocity_ref[3];", "core.vz = velocity_mea[3];",
            "core.ref_az = acceleration_ref[3];", "core.yaw_mea = attitude_mea[3];",
            "core.ref_yaw = 0;",
        ]
    )
    return f'''model {ADAPTER_MODEL}
  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real hover_collective_thrust_n = 4 * profile.mworks_visual_thrust_coefficient * profile.mworks_hover_visual_rotor_speed_rad_s ^ 2;
  {CFUNCTION_MODEL} core;

equation
  {assignments}
  attitude_ref[1] = -core.roll_cmd;
  attitude_ref[2] = core.pitch_cmd;
  attitude_ref[3] = core.yaw_cmd;
  collective_thrust_delta = core.collective_thrust_n - hover_collective_thrust_n;
end {ADAPTER_MODEL};
'''


def build_runner_model() -> str:
    original = (ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal" / "Px4CtrlFormalRunner.mo").read_text(encoding="utf-8")
    if "Px4CtrlAttitudeThrustAdapter controller" not in original:
        raise RuntimeError("unexpected Px4CtrlFormalRunner controller declaration")
    rewritten = original.replace("within MoSimQuadrotorModel.Experiment.Runners.Formal;\n", "", 1)
    rewritten = rewritten.replace("model Px4CtrlFormalRunner", f"model {RUNNER_MODEL}", 1)
    rewritten = rewritten.replace(
        "MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter controller",
        f"{ADAPTER_MODEL} controller",
        1,
    )
    rewritten = rewritten.replace("end Px4CtrlFormalRunner;", f"end {RUNNER_MODEL};", 1)
    return rewritten


def write_models() -> dict[str, Any]:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    include_code, generated_hashes = flatten_generated_c()
    paths = {
        CFUNCTION_MODEL: MODEL_DIR / f"{CFUNCTION_MODEL}.mo",
        ADAPTER_MODEL: MODEL_DIR / f"{ADAPTER_MODEL}.mo",
        RUNNER_MODEL: MODEL_DIR / f"{RUNNER_MODEL}.mo",
    }
    texts = {
        CFUNCTION_MODEL: build_cfunction_model(include_code),
        ADAPTER_MODEL: build_adapter_model(),
        RUNNER_MODEL: build_runner_model(),
    }
    for name, path in paths.items():
        path.write_text(texts[name], encoding="utf-8", newline="\n")
    wrapper_path = RESULT_DIR / "native" / "px4ctrl_graphical_generated_wrapper.c"
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    wrapper_path.write_text(include_code, encoding="utf-8", newline="\n")
    standalone_wrapper = "\n".join(
        [
            '#include "mwb_types.h"',
            '#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h"',
            '#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h"',
            '#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c"',
            "",
            "#if defined(_WIN32)",
            "#define MOSIM_PX4CTRL_EXPORT __declspec(dllexport)",
            "#else",
            "#define MOSIM_PX4CTRL_EXPORT __attribute__((visibility(\"default\")))",
            "#endif",
            "",
            "MOSIM_PX4CTRL_EXPORT void MosimPx4ctrlGeneratedGraphStepScalar(",
            "  " + ",\n  ".join(f"double {name}" for name in INPUTS) + ",",
            "  " + ",\n  ".join(f"double *{name}" for name in OUTPUTS) + ")",
            "{",
            "  static int mosim_px4ctrl_generated_initialized = 0;",
            "  if (!mosim_px4ctrl_generated_initialized) {",
            "    Init();",
            "    mosim_px4ctrl_generated_initialized = 1;",
            "  }",
            "  " + "\n  ".join(f"graphical_sysblockGbIn.{name} = {name};" for name in INPUTS),
            "  Step();",
            "  " + "\n  ".join(f"*{name} = agraphical_sysblockGbOut.{name};" for name in OUTPUTS),
            "}",
            "",
        ]
    )
    shared_wrapper_path = RESULT_DIR / "native" / "px4ctrl_graphical_generated_shared.c"
    shared_wrapper_path.write_text(standalone_wrapper, encoding="utf-8", newline="\n")
    manifest = {
        "schema": "mosim.px4ctrl_codegen_sil_models.v1",
        "generated_model": GRAPHICAL_MODEL,
        "generated_c_dir": str(GENERATED_DIR),
        "generated_c_hashes": generated_hashes,
        "flattened_wrapper_sha256": sha256(wrapper_path),
        "models": {name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()},
        "wrapper": str(wrapper_path),
        "shared_library_wrapper": str(shared_wrapper_path),
        "shared_library_wrapper_sha256": sha256(shared_wrapper_path),
        "interface": {"inputs": INPUTS, "outputs": OUTPUTS, "sample_time_s": 0.01},
        "claim_boundary": "The wrapper is a mechanical CFunction envelope around MWORKS generated C. It changes only symbol visibility and Init/Step invocation, not controller equations or parameters.",
    }
    (LOG_DIR / "MODEL_BUILD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def add(model: str, type_name: str, block: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, model, block, x, y, 28, 24):
        raise RuntimeError(f"AddComponent failed: {block} ({type_name})")


def connect(model: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def build_fixture(name: str, controller: str) -> Path:
    if not ModelingPy.ClassExist(name):
        if not ModelingPy.NewModel(name, "Sysblock", "px4ctrl generated C SIL fixture"):
            raise RuntimeError(f"NewModel failed: {name}")
    if not ModelingPy.OpenModel(name, "diagram"):
        raise RuntimeError(f"OpenModel failed: {name}")
    for component in list(ModelingPy.GetComponents(name)):
        if not ModelingPy.RemoveComponent(name, component):
            raise RuntimeError(f"RemoveComponent failed: {name}.{component}")
    for index, port in enumerate(INPUTS):
        source = f"{port}_source"
        add(name, "SysplorerEmbeddedCoder.Sources.Constant", source, -220, 210 - index * 26)
        if not ModelingPy.SetParamValue(f"{source}.k", "0"):
            raise RuntimeError(f"SetParamValue failed: {source}.k")
    add(name, controller, "controller", 0, 0)
    for index, port in enumerate(OUTPUTS):
        add(name, "SysplorerEmbeddedCoder.Port.Outport", port, 220, 110 - index * 28)
    for port in INPUTS:
        connect(name, f"{port}_source.y", f"controller.{port}")
    for port in OUTPUTS:
        connect(name, f"controller.{port}", port)
    target = MODEL_DIR / f"{name}.mo"
    saved = ModelingPy.SaveModel(name) if target.exists() else ModelingPy.SaveModelAs(name, str(MODEL_DIR), name)
    if not saved:
        raise RuntimeError(f"SaveModel failed: {name}")
    if not ModelingPy.CheckModel(name):
        raise RuntimeError(f"CheckModel failed: {name}")
    return target


def run_fixture_cases(model: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, values in enumerate(TEST_CASES):
        # SetParamValue operates on the active Sysplorer diagram.  The two
        # fixtures share source instance names, so activate the requested one
        # before each vector and force its parameter update into translation.
        if not ModelingPy.OpenModel(model, "diagram"):
            raise RuntimeError(f"OpenModel failed: {model}")
        for port in INPUTS:
            if not ModelingPy.SetParamValue(f"{port}_source.k", repr(values[port])):
                raise RuntimeError(f"SetParamValue failed: {model}.{port}_source.k")
        if not ModelingPy.CheckModel(model):
            raise RuntimeError(f"CheckModel failed after parameter update: {model}, case={index}")
        simulated = ModelingPy.SimulateModelEx(model, {"stopTime": 0.02, "interval": 0.01})
        if not simulated:
            raise RuntimeError(f"SimulateModelEx failed: {model}, case={index}")
        columns = [list(values) for values in ModelingPy.GetVarsValues(OUTPUTS)]
        if not all(column for column in columns):
            raise RuntimeError(f"empty fixture output: {model}, case={index}")
        outputs = {name: float(values[-1]) for name, values in zip(OUTPUTS, columns)}
        if not all(math.isfinite(value) for value in outputs.values()):
            raise RuntimeError(f"non-finite fixture output: {model}, case={index}")
        rows.append({"index": index, "time_s": index * 0.01, "inputs": values, "outputs": outputs})
    return rows


def max_difference(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    if len(left) != len(right):
        raise RuntimeError("fixture sample count mismatch")
    per_output = {name: 0.0 for name in OUTPUTS}
    for lhs, rhs in zip(left, right):
        for name in OUTPUTS:
            per_output[name] = max(per_output[name], abs(float(lhs["outputs"][name]) - float(rhs["outputs"][name])))
    return {"per_output_max_abs": per_output, "max_abs": max(per_output.values())}


def main() -> dict[str, Any]:
    for directory in (MODEL_DIR, RAW_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    manifest = write_models()
    required_models = (CFUNCTION_MODEL, ADAPTER_MODEL, RUNNER_MODEL)
    missing_models = [name for name in required_models if not ModelingPy.ClassExist(name)]
    if missing_models:
        raise RuntimeError(
            "generated evidence models must be loaded through the MCP model_manager before this script runs: "
            + ", ".join(missing_models)
        )
    cfunction_check = ModelingPy.CheckModel(CFUNCTION_MODEL)
    if not cfunction_check:
        raise RuntimeError(f"CheckModel failed: {CFUNCTION_MODEL}")
    graphical_fixture_path = build_fixture(GRAPHICAL_FIXTURE, GRAPHICAL_MODEL)
    cfunction_fixture_path = build_fixture(CFUNCTION_FIXTURE, CFUNCTION_MODEL)
    graphical_rows = run_fixture_cases(GRAPHICAL_FIXTURE)
    cfunction_rows = run_fixture_cases(CFUNCTION_FIXTURE)
    comparison = max_difference(graphical_rows, cfunction_rows)
    graphical_ref = {
        "schema": "mosim.px4ctrl_graphical_reference.v1",
        "source_label": "MWORKS_GRAPHICAL_SYSBLOCK",
        "model": GRAPHICAL_MODEL,
        "fixture": GRAPHICAL_FIXTURE,
        "rows": [{"time_s": row["time_s"], "outputs": row["outputs"]} for row in graphical_rows],
    }
    runtime_schema = {
        "input_global": "graphical_sysblockGbIn",
        "output_global": "agraphical_sysblockGbOut",
        "input_fields": INPUTS,
        "output_fields": OUTPUTS,
        "input_sequence": TEST_CASES,
    }
    (RAW_DIR / "graphical_reference.json").write_text(json.dumps(graphical_ref, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (RAW_DIR / "runtime_schema.json").write_text(json.dumps(runtime_schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (RAW_DIR / "fixture_comparison.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["case", *[f"graphical_{name}" for name in OUTPUTS], *[f"cfunction_{name}" for name in OUTPUTS]])
        for graphical, cfunction in zip(graphical_rows, cfunction_rows):
            writer.writerow([graphical["index"], *[graphical["outputs"][name] for name in OUTPUTS], *[cfunction["outputs"][name] for name in OUTPUTS]])
    evidence = {
        "schema": "mosim.px4ctrl_codegen_sil_fixture.v1",
        "build_manifest": str(LOG_DIR / "MODEL_BUILD_MANIFEST.json"),
        "graphical_fixture_path": str(graphical_fixture_path),
        "cfunction_fixture_path": str(cfunction_fixture_path),
        "cfunction_check_model": bool(cfunction_check),
        "case_count": len(TEST_CASES),
        "graphical_vs_cfunction": comparison,
        "threshold": 1e-12,
        "pass": comparison["max_abs"] <= 1e-12,
    }
    (LOG_DIR / "FIXTURE_SIL_RESULT.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": evidence["pass"], "evidence": str(LOG_DIR / "FIXTURE_SIL_RESULT.json"), "max_abs": comparison["max_abs"], "runner_model": str(MODEL_DIR / f"{RUNNER_MODEL}.mo")}


RUN_SCRIPT_RESULT = main()
