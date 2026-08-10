within MoSimQuadrotorModel.Control;
package Baselines
  "正式运行器使用的离线默认控制律与通用控制器核心"
  extends Modelica.Icons.Package;

  model AntiWindupFeedforwardCore
    "AWFF 控制器核心"
    extends MoSimQuadrotorModel.Control.Baselines.AntiWindupFeedforwardController;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end AntiWindupFeedforwardCore;

  annotation(__MWORKS(version="26.3.0"));

end Baselines;