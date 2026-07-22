within QuadrotorExperiments;
package SceneTraceScenarios
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "UE 场景与轨迹表驱动烟测（兼容旧平铺类名的分类入口）"
  extends Modelica.Icons.Package;

  model UEFactoryLinearMPC
    "Factory 场景：线性 MPC 烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end UEFactoryLinearMPC;

  model UEFactoryTraceTable
    "Factory 场景：轨迹表驱动烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end UEFactoryTraceTable;

  model UEDerelictLinearMPC
    "Derelict 场景：线性 MPC 烟测"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEDerelictLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end UEDerelictLinearMPC;
  annotation(__MWORKS(hide=true));

end SceneTraceScenarios;