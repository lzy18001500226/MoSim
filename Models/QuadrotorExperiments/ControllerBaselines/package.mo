within QuadrotorExperiments;
package ControllerBaselines
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "控制器基线与对比模型（兼容旧平铺类名的分类入口）"
  extends Modelica.Icons.Package;

  model AntiWindupFeedforwardCore
    "AWFF 控制器核心"
    extends MoSimQuadrotorModel.Controllers.Baselines.AntiWindupFeedforwardController;
    annotation(__MWORKS(hide=true));
  end AntiWindupFeedforwardCore;

  model Example1AWFFBaseline
    "阶跃爬升：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1AWFFBaseline;

  model Example2AWFFBaseline
    "螺旋爬升：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2AWFFBaseline;

  model Example2HelixTunedAWFFBaseline
    "螺旋爬升：调参 AWFF 控制器基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAWFFBaseline;

  model Example3AWFFBaseline
    "8 字任务：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example3AWFFBaseline;

  model Example1ImprovedPIDBaseline
    "阶跃爬升：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1ImprovedPIDBaseline;

  model Example1EnhancedPIDBaseline
    "阶跃爬升：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1EnhancedPIDBaseline;

  model Example2ImprovedPIDBaseline
    "螺旋爬升：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example2ImprovedPIDBaseline;

  model Example2EnhancedPIDBaseline
    "螺旋爬升：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2EnhancedPIDBaseline;

  model Example2HelixTunedEnhancedPIDBaseline
    "螺旋爬升：调参增强 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedEnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedEnhancedPIDBaseline;

  model Example3ImprovedPIDBaseline
    "8 字任务：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example3ImprovedPIDBaseline;

  model Example3EnhancedPIDBaseline
    "8 字任务：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example3EnhancedPIDBaseline;
  annotation(__MWORKS(hide=true));

end ControllerBaselines;