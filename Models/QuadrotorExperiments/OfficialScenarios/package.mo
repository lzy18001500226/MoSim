within QuadrotorExperiments;
package OfficialScenarios
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "官方任务与控制器闭环场景（兼容旧平铺类名的分类入口）"
  extends Modelica.Icons.Package;

  model Example1AWFF
    "阶跃爬升：AWFF Sysblock 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example1AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1AWFF;

  model Example1INDI
    "阶跃爬升：INDI / L1 组合控制闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example1INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1INDI;

  model Example1L1
    "阶跃爬升：L1 残差补偿闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example1L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1L1;

  model Example1LinearMPC
    "阶跃爬升：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example1LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1LinearMPC;

  model Example1PlanarFigure8Trail
    "阶跃起飞后平面 8 字轨迹留痕审查"
    extends MoSimQuadrotorModel.Missions.Official.Example1PlanarFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1PlanarFigure8Trail;

  model Example1HelicalFigure8Trail
    "阶跃起飞后螺旋 8 字轨迹留痕审查"
    extends MoSimQuadrotorModel.Missions.Official.Example1HelicalFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1HelicalFigure8Trail;

  model Example2AWFF
    "螺旋爬升：AWFF Sysblock 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example2AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2AWFF;

  model Example2HelixTunedAWFF
    "螺旋爬升：调参 AWFF Sysblock 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example2HelixTunedAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAWFF;

  model Example2INDI
    "螺旋爬升：INDI / L1 组合控制闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example2INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2INDI;

  model Example2HelixTunedINDI
    "螺旋爬升：调参 INDI / L1 组合控制闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example2HelixTunedINDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedINDI;

  model Example2LinearMPC
    "螺旋爬升：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example2LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2LinearMPC;

  model Example3AWFF
    "8 字任务：AWFF Sysblock 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example3AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3AWFF;

  model Example3INDI
    "8 字任务：INDI / L1 组合控制闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example3INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3INDI;

  model Example3L1
    "8 字任务：L1 残差补偿闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example3L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3L1;

  model Example3LinearMPC
    "8 字任务：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Missions.Official.Example3LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3LinearMPC;
  annotation(__MWORKS(hide=true));

end OfficialScenarios;