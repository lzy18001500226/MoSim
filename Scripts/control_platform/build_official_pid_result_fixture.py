#!/usr/bin/env python3
"""Build a thin fixed-input fixture around the existing Official PID block."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720"
    / "G9_CORE_COMPARISON/official_pid/models"
    / "MoSim_OFFICIAL_PID_REPORT_MIL.mo"
)

MODEL = r'''model MoSim_OFFICIAL_PID_REPORT_MIL "Official PID fixed-input report fixture"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.5,StoreEventValue=0),Diagram(coordinateSystem(extent={{-260,-100},{260,100}},grid={2,2})));
  SysplorerEmbeddedCoder.Sources.Constant altitude_error(k=0.15) annotation(Placement(transformation(origin={-200,20},extent={{-24,-18},{24,18}})));
  MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_PID_Sysblock_Demo official_pid annotation(Placement(transformation(origin={0,20},extent={{-45,-35},{45,35}})));
  SysplorerEmbeddedCoder.Port.Outport thrust_command annotation(Placement(transformation(origin={210,20},extent={{-24,-18},{24,18}})));
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(altitude_error.y,official_pid.z_error) annotation(Line(points={{-176,20},{-45,20}},color={0,0,0}));
  connect(official_pid.thrust_cmd,thrust_command) annotation(Line(points={{45,20},{186,20}},color={0,0,0}));
end MoSim_OFFICIAL_PID_REPORT_MIL;
'''


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(MODEL, encoding="utf-8", newline="\n")
    print(OUTPUT.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
