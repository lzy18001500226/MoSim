# MWORKS Controller Code Generation Workflow

Date: 2026-06-02

Purpose: verify and reuse MWORKS/Sysplorer/Sysblock controller code generation
for the MoSim C/C++ controller runtime path.

## 1. Key Result

MWORKS/Sysplorer supports Sysblock model code generation through the official
Python API:

```text
GetModelCodeGenerationOptions(modelName)
SetModelCodeGenerationOptions(modelName, options)
GenerateModelCode(modelName)
```

This is separate from `TranslateModel(modelName)`. The current Sysplorer MCP
`translate_model` wrapper only calls `TranslateModel(modelName)` and ignores
`code_folder`, `code_type`, `build_type`, `run_to`, and `config_json`; it is not
the right proof for project-local C/C++ export.

## 2. Verified Probe

Probe model:

```text
Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo.mo
```

Output:

```text
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo/
```

Generated files:

```text
AWFF_PID_Sysblock_Demo.c
AWFF_PID_Sysblock_Demo.h
AWFF_PID_Sysblock_Demo_data.c
AWFF_PID_Sysblock_Demo_extern_include.h
AWFF_PID_Sysblock_Demo_private.h
ExternalCResource.json
ExternalResources.xml
motrace.json
mwb_main.c
mwb_runtime.h
mwb_types.h
```

Observed generated runtime shape:

```text
Init()
Step()
global input struct:  awff_pid_sysblock_demoGbIn
global output struct: awff_pid_sysblock_demoGbOut
sample time:          0.01 s
```

The generated C sources compiled with:

```bash
gcc -std=c99 -Wall -Wextra -pedantic -c \
  AWFF_PID_Sysblock_Demo.c \
  AWFF_PID_Sysblock_Demo_data.c \
  mwb_main.c
```

Temporary `.o` files were removed after the compile probe. The generated C/H
files and `motrace.json` remain as local evidence.

The reusable project check is:

```bash
python3 Scripts/mworks/check_codegen_runtime.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --compile \
  --expect-sample-time 0.01 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json
```

This check records:

```text
schema:                  mosim.mworks_codegen_runtime_check.v1
runtime adapter shape:   global_struct_input_output_init_step
functions:               Init, Step
input fields:            z_error
output fields:           thrust_cmd
sample_time_s:           0.01
compile status:          gcc C99 compile ok
SIL requirement:         true
```

With `--run-smoke`, the check also builds a temporary C harness that includes
the generated headers, calls `Init()`, writes one input field, calls `Step()`,
and records the output field plus generated runtime time. For the current PID
probe, the smoke sequence verifies:

```text
input global/field:   awff_pid_sysblock_demoGbIn.z_error
output global/field:  awff_pid_sysblock_demoGbOut.thrust_cmd
input sequence:       0.1, 0.2, -0.1
runtime times:        0.01, 0.02, 0.03
```

The compile and runtime-smoke probes run in temporary directories so generated
evidence folders are not polluted by `.o`, `.obj`, `.exe`, or harness files.

## 3. Minimal Script Pattern

Use `mcp__sysplorer.call_code(mode="run_script")` or a future dedicated MCP
tool. Do not use `ClearAll` or `ChangeDirectory`.

```python
import os
import mworks.sysplorer as ModelingPy

model_name = "AWFF_PID_Sysblock_Demo"
model_path = r"C:\Users\HP\Desktop\MoSim\Models\QuadrotorControllerBlocks\AWFF_PID_Sysblock_Demo.mo"
out_dir = r"C:\Users\HP\Desktop\MoSim\Results\codegen_probe\AWFF_PID_Sysblock_Demo_api"

os.makedirs(out_dir, exist_ok=True)

ModelingPy.LoadLibrary("SysplorerEmbeddedCoder")
ModelingPy.OpenModelFile(model_path)
assert ModelingPy.CheckModel(model_name)

options = ModelingPy.GetModelCodeGenerationOptions(model_name)
options["CodePlatform.OutPath"] = {"output": out_dir}
assert ModelingPy.SetModelCodeGenerationOptions(model_name, options)
assert ModelingPy.GenerateModelCode(model_name)
```

## 4. MoSim Runtime Policy

The generated code is accepted as a controller-runtime candidate only after a
SIL equivalence gate:

```text
same input sequence
  -> MWORKS/Sysblock output
  -> generated C/C++ output
  -> sample-by-sample tolerance check
```

Required evidence for every exported controller:

```text
model_name
model_source_path
codegen_api_version or MWORKS version
generated_code_hash
codegen_options_snapshot
adapter_type
compile_status
sil_equivalence_status
external_runtime_status
```

Before equivalence passes, generated or external C/C++ results cannot replace
MWORKS/Sysplorer simulation evidence.

Pre-SIL gate:

```text
generated files present
  -> check_codegen_runtime.py summary ok
  -> generated C compiles without temp artifacts
  -> temporary Init/Step harness runs on a small input sequence
  -> interface/sample-time snapshot saved
  -> only then build ControllerRuntime wrapper
```

Zero-input SIL smoke gate:

```bash
python3 Scripts/mworks/check_codegen_sil_equivalence.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --input-sequence 0,0,0 \
  --tolerance 1e-12 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json
```

Current status: `zero_input_sil_smoke` passes for the PID demo. This is useful
as a startup/reference check but not a complete SIL proof. The Sysplorer result
variable discovery for this model exposes internal variables such as
`cmd_sum.y`, not the outport name `AWFF_PID_Sysblock_Demo.thrust_cmd`.

Nonzero constant-input SIL gate:

```text
MWORKS/Sysblock constant reference model
  -> z_error = 0.1
  -> result variable cmd_sum.y
  -> generated C runtime input sequence 0.1,0.1,0.1,0.1
  -> output-order sample comparison
```

Reference model:

```text
Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo_SIL_Constant.mo
```

Evidence:

```text
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
```

Command:

```bash
python3 Scripts/mworks/check_codegen_sil_equivalence.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --input-sequence 0.1,0.1,0.1,0.1 \
  --mworks-reference-json Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json \
  --tolerance 1e-5 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
```

Current result: `nonzero_input_sil_smoke` passes for the PID demo with
`max_abs_error = 8.934736470678217e-07`, below the `1e-5` tolerance. The
tolerance accounts for the current generated-code option `real_as_float=true`.
MWORKS reports the first Sysblock output at `t=0`; the generated C harness
records outputs after `Step()`, so runtime timestamps are one sample later while
output order matches.

Remaining stronger SIL gate:

```text
MWORKS/Sysblock time-varying input injection
  -> same input sequence as generated C runtime
  -> compare output sample-by-sample
  -> save input trace, MWORKS output, generated C output, tolerance, max error
```

Do not claim a generated controller is MoSim runtime-authoritative until the
target controller's own nonzero/time-varying SIL gate passes. The current
constant-input PID demo proves the architecture path is viable; it does not
finish SIL for all controllers.

## 5. Required MCP Improvement

Add a project MCP tool for code generation instead of overloading
`translate_model`.

Minimum tool surface:

```text
get_code_generation_options(model_name)
set_code_generation_options(model_name, options)
generate_model_code(model_name, output_dir)
summarize_generated_code(output_dir)
```

The tool must expose whether `GenerateModelCode` succeeded and list generated
files under the requested project-local output directory.

## 6. Architecture Implication

MoSim should reuse the RflySim-style role split, but replace the motion/control
authority with MWORKS:

```text
MWORKS/Sysblock
  -> controller design, plant solve, truth, formal metrics, code generation

C/C++ ControllerRuntime
  -> generated controller wrapper, SIL, ROS2/PX4/V6X deployable adapter

UE / MoSimSceneLibrary
  -> rendering, camera, collision and sensor oracle

ROS2 / RViz2
  -> LiDAR/IMU/TF, FAST-LIO, local 3D map, planner review
```

Do not resume hand-built point-cloud/grid demos as the product route. The next
implementation path is generated-controller SIL plus continuous MWORKS state
and sensor contracts.

## 7. 2026-06-02 Source Check

External and local checks support this route:

- MathWorks Simulink Coder officially generates and executes C/C++ code from
  Simulink models, Stateflow charts, and MATLAB functions for real-time,
  non-real-time, rapid-prototyping, and HIL-style workflows:
  `https://www.mathworks.com/products/simulink-coder.html`.
- RflySim's documented split is CopterSim for kinematic simulation,
  Unreal/RflySim3D for high-fidelity scene simulation, QGroundControl for
  mission/monitoring, PX4PSP for MATLAB/Simulink-based firmware-level automatic
  code generation, and Python/ROS interface libraries for upper-layer AI
  validation: `https://rflysim.com/doc/en/1/Intro.html`.
- PX4 ROS2 Offboard is a continuous streamed-control contract. PX4 requires
  repeated `OffboardControlMode`/setpoint traffic and drops out of offboard
  mode if the proof-of-life stream falls below about 2Hz:
  `https://docs.px4.io/main/en/ros2/offboard_control`.
- AirSim is a C++/Unreal simulator with PX4/ArduPilot SIL/HIL support and
  ROS/ROS2 wrappers. This is useful as a bridge/API reference, but it should
  not replace MWORKS as MoSim's controller and plant-solver authority:
  `https://github.com/microsoft/AirSim` and
  `https://microsoft.github.io/AirSim/airsim_ros_pkgs/`.

MoSim decision: copy the architecture pattern, not the solver. MWORKS owns
solver, controller design, truth, metrics, and code generation. UE owns
rendering and scene/sensor oracle. ROS2 owns middleware, FAST-LIO, 3D map,
planner state, and RViz2 review.
