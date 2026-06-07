within MoSimQuadrotorModel;
package Missions
  "正式任务场景（从QuadrotorExperiments.OfficialScenarios迁移的主线入口）"

  extends Modelica.Icons.Package;

  model Example1AWFF
    "阶跃爬升：AWFF Sysblock 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example1AWFF;
    annotation(__MWORKS(hide=false));
  end Example1AWFF;

  model Example1INDI
    "阶跃爬升：INDI / L1 组合控制闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example1INDI;
    annotation(__MWORKS(hide=false));
  end Example1INDI;

  model Example1L1
    "阶跃爬升：L1 残差补偿闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example1L1;
    annotation(__MWORKS(hide=false));
  end Example1L1;

  model Example1LinearMPC
    "阶跃爬升：线性 MPC 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example1LinearMPC;
    annotation(__MWORKS(hide=false));
  end Example1LinearMPC;

  model Example1PlanarFigure8Trail
    "阶跃起飞后平面 8 字轨迹留痕审查"
    extends QuadrotorExperiments.OfficialScenarios.Example1PlanarFigure8Trail;
    annotation(__MWORKS(hide=false));
  end Example1PlanarFigure8Trail;

  model Example1HelicalFigure8Trail
    "阶跃起飞后螺旋 8 字轨迹留痕审查"
    extends QuadrotorExperiments.OfficialScenarios.Example1HelicalFigure8Trail;
    annotation(__MWORKS(hide=false));
  end Example1HelicalFigure8Trail;

  model Example2AWFF
    "螺旋爬升：AWFF Sysblock 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example2AWFF;
    annotation(__MWORKS(hide=false));
  end Example2AWFF;

  model Example2HelixTunedAWFF
    "螺旋爬升：调参 AWFF Sysblock 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example2HelixTunedAWFF;
    annotation(__MWORKS(hide=false));
  end Example2HelixTunedAWFF;

  model Example2INDI
    "螺旋爬升：INDI / L1 组合控制闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example2INDI;
    annotation(__MWORKS(hide=false));
  end Example2INDI;

  model Example2HelixTunedINDI
    "螺旋爬升：调参 INDI / L1 组合控制闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example2HelixTunedINDI;
    annotation(__MWORKS(hide=false));
  end Example2HelixTunedINDI;

  model Example2LinearMPC
    "螺旋爬升：线性 MPC 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example2LinearMPC;
    annotation(__MWORKS(hide=false));
  end Example2LinearMPC;

  model Example3AWFF
    "8 字任务：AWFF Sysblock 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example3AWFF;
    annotation(__MWORKS(hide=false));
  end Example3AWFF;

  model Example3INDI
    "8 字任务：INDI / L1 组合控制闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example3INDI;
    annotation(__MWORKS(hide=false));
  end Example3INDI;

  model Example3L1
    "8 字任务：L1 残差补偿闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example3L1;
    annotation(__MWORKS(hide=false));
  end Example3L1;

  model Example3LinearMPC
    "8 字任务：线性 MPC 闭环"
    extends QuadrotorExperiments.OfficialScenarios.Example3LinearMPC;
    annotation(__MWORKS(hide=false));
  end Example3LinearMPC;
end Missions;
