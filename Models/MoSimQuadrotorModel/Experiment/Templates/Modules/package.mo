within MoSimQuadrotorModel.Experiment.Templates;
package Modules
  "Sunray150 系统组成模块（架构图与接口支撑）"
  extends Modelica.Icons.Package;

  block PerceptionInterface
    "感知接口模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.PerceptionInterfaceModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end PerceptionInterface;

  block FlightController
    "V6X 飞控模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.V6XFlightControllerModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end FlightController;

  block MissionComputer
    "ORIN NX 任务计算机模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.ORINNXMissionComputerModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end MissionComputer;

  block Supervisor
    "系统监督与模式管理模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.SystemSupervisorModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Supervisor;

  block BatteryPower
    "电池与供电模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.BatteryPowerModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end BatteryPower;

  block ESCDrive
    "电调驱动模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.ESCDriveModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end ESCDrive;

  block Px4CtrlController
    "px4ctrl 控制器与离线控制分配模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.Px4CtrlControllerModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Px4CtrlController;

  model MotorDrive
    "电机驱动模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.MotorDriveModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end MotorDrive;

  model AirframeSensor
    "机体与传感器模块"
    extends MoSimQuadrotorModel.Experiment.Templates.Architecture.Sunray150CompleteSystemGraphical_Sysblock.Sunray150AirframeSensorModule;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end AirframeSensor;
  annotation(__MWORKS(version="26.3.0"));

end Modules;
