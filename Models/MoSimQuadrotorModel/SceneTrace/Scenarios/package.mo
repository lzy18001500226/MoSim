within MoSimQuadrotorModel.SceneTrace;
package Scenarios
  "UE 场景与轨迹表驱动烟测（审查入口）"
  extends Modelica.Icons.Package;

  model UEFactoryLinearMPC
    "Factory 场景：线性 MPC 烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end UEFactoryLinearMPC;

  model UEFactoryTraceTable
    "Factory 场景：轨迹表驱动烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end UEFactoryTraceTable;

  model UEDerelictLinearMPC
    "Derelict 场景：线性 MPC 烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEDerelictLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end UEDerelictLinearMPC;
  annotation(__MWORKS(version="26.3.0"));

end Scenarios;
