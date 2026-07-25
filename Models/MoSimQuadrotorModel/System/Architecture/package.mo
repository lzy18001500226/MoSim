within MoSimQuadrotorModel.System;
package Architecture
  "完整系统图形化架构与失效模式烟测（非最终性能证据）"
  extends Modelica.Icons.Package;

  model CompleteSystemGraphical
    "Sunray150 完整系统图形化架构"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGraphical_Sysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end CompleteSystemGraphical;

  model GPSDropout
    "完整系统：GPS 丢失烟测"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGPSDropoutSysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end GPSDropout;

  model BatteryLow
    "完整系统：低电量烟测"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemBatteryLowSysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end BatteryLow;

  model OffboardLoss
    "完整系统：Offboard 心跳丢失烟测"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemOffboardLossSysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end OffboardLoss;

  model MissionFailure
    "完整系统：任务不可行烟测"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemMissionFailureSysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end MissionFailure;

  model GeofenceBreach
    "完整系统：地理围栏越界烟测"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGeofenceBreachSysblock;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end GeofenceBreach;
  annotation(__MWORKS(version="26.3.0"));

end Architecture;