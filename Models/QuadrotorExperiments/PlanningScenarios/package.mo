within QuadrotorExperiments;
package PlanningScenarios
  "规划避障与轨迹生成场景（兼容旧平铺类名的分类入口）"
  extends Modelica.Icons.Package;

  model QuinticReference
    "五次多项式参考轨迹"
    extends QuadrotorExperiments.PlanningScenarios.PlannedQuinticReference;
    annotation(__MWORKS(hide=false));
  end QuinticReference;

  model NavigationDisplay
    "规划/导航显示与局部地图审查支撑"
    extends QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay;
    annotation(__MWORKS(hide=false));
  end NavigationDisplay;

  model OpenBlocksAWFF
    "开放障碍场：AWFF 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false));
  end OpenBlocksAWFF;

  model OpenBlocksLinearMPC
    "开放障碍场：线性 MPC 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false));
  end OpenBlocksLinearMPC;

  model OpenBlocksColorMapReview
    "开放障碍场：颜色地图审查"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview;
    annotation(__MWORKS(hide=false));
  end OpenBlocksColorMapReview;

  model CorridorGateAWFF
    "走廊门控场：AWFF 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false));
  end CorridorGateAWFF;

  model CorridorGateLinearMPC
    "走廊门控场：线性 MPC 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false));
  end CorridorGateLinearMPC;

end PlanningScenarios;
