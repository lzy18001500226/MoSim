within MoSimQuadrotorModel.Guidance.Planning;
package Scenarios
  "规划避障与轨迹生成场景（审查入口）"
  extends Modelica.Icons.Package;

  model QuinticReference
    "五次多项式参考轨迹"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.PlannedQuinticReference;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end QuinticReference;

  model NavigationDisplay
    "规划/导航显示与局部地图审查支撑"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.PlanningNavigationDisplay;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end NavigationDisplay;

  model OpenBlocksAWFF
    "开放障碍场：AWFF 规划闭环"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksAWFF;

  model OpenBlocksLinearMPC
    "开放障碍场：线性 MPC 规划闭环"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksLinearMPC;

  model OpenBlocksColorMapReview
    "开放障碍场：颜色地图审查"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.Sunray150PlanningOpenBlocksColorMapReview;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksColorMapReview;

  model OpenBlocksThreeUavFormation
    "开放障碍场：三机可重构编队整机闭环"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.ThreeUavOpenBlocksReconfigurableFormationLinearMPC;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OpenBlocksThreeUavFormation;

  model CorridorGateAWFF
    "走廊门控场：AWFF 规划闭环"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CorridorGateAWFF;

  model CorridorGateLinearMPC
    "走廊门控场：线性 MPC 规划闭环"
    extends MoSimQuadrotorModel.Guidance.Planning.Scenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CorridorGateLinearMPC;
  annotation(__MWORKS(version="26.3.0"));

end Scenarios;
