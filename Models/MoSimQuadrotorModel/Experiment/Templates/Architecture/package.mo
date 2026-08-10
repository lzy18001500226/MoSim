within MoSimQuadrotorModel.Experiment.Templates;
package Architecture
  "完整系统图形化架构；历史失效模式 Smoke 隐藏保留"
  extends Modelica.Icons.Package;

  model CompleteSystemGraphical
    "Sunray150 完整系统图形化架构"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CompleteSystemGraphical;

  model GPSDropout
    "完整系统：GPS 丢失烟测"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGPSDropout;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end GPSDropout;

  model BatteryLow
    "完整系统：低电量烟测"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemBatteryLow;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end BatteryLow;

  model OffboardLoss
    "完整系统：Offboard 心跳丢失烟测"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemOffboardLoss;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end OffboardLoss;

  model MissionFailure
    "完整系统：任务不可行烟测"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemMissionFailure;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end MissionFailure;

  model GeofenceBreach
    "完整系统：地理围栏越界烟测"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGeofenceBreach;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end GeofenceBreach;
  annotation(__MWORKS(hide=true,version="26.3.0"));

end Architecture;