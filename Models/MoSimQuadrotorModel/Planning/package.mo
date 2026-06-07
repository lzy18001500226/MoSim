within MoSimQuadrotorModel;
package Planning
  "规划与地图场景（局部感知、重规划、轨迹跟踪和地图审查）"

  extends Modelica.Icons.Package;

  model QuinticReference
    "五次多项式参考轨迹"
    extends QuadrotorExperiments.PlanningScenarios.QuinticReference;
    annotation(__MWORKS(hide=false));
  end QuinticReference;

  model NavigationDisplay
    "规划/导航显示与局部地图审查支撑"
    extends QuadrotorExperiments.PlanningScenarios.NavigationDisplay;
    annotation(__MWORKS(hide=false));
  end NavigationDisplay;

  model OpenBlocksAWFF
    "开放障碍场：AWFF 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.OpenBlocksAWFF;
    annotation(__MWORKS(hide=false));
  end OpenBlocksAWFF;

  model OpenBlocksLinearMPC
    "开放障碍场：线性 MPC 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.OpenBlocksLinearMPC;
    annotation(__MWORKS(hide=false));
  end OpenBlocksLinearMPC;

  model OpenBlocksColorMapReview
    "开放障碍场：颜色地图审查"
    extends QuadrotorExperiments.PlanningScenarios.OpenBlocksColorMapReview;
    annotation(__MWORKS(hide=false));
  end OpenBlocksColorMapReview;

  model CorridorGateAWFF
    "走廊门控场：AWFF 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.CorridorGateAWFF;
    annotation(__MWORKS(hide=false));
  end CorridorGateAWFF;

  model CorridorGateLinearMPC
    "走廊门控场：线性 MPC 规划闭环"
    extends QuadrotorExperiments.PlanningScenarios.CorridorGateLinearMPC;
    annotation(__MWORKS(hide=false));
  end CorridorGateLinearMPC;
end Planning;
