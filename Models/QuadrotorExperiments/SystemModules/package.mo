within QuadrotorExperiments;
package SystemModules
  "Sunray150 系统组成模块（架构图与接口支撑）"
  extends Modelica.Icons.Package;

  block PerceptionInterface
    "感知接口模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.PerceptionInterfaceModule;
    annotation(__MWORKS(hide=false));
  end PerceptionInterface;

  block FlightController
    "V6X 飞控模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.V6XFlightControllerModule;
    annotation(__MWORKS(hide=false));
  end FlightController;

  block MissionComputer
    "ORIN NX 任务计算机模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.ORINNXMissionComputerModule;
    annotation(__MWORKS(hide=false));
  end MissionComputer;

  block Supervisor
    "系统监督与模式管理模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.SystemSupervisorModule;
    annotation(__MWORKS(hide=false));
  end Supervisor;

  block BatteryPower
    "电池与供电模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.BatteryPowerModule;
    annotation(__MWORKS(hide=false));
  end BatteryPower;

  block ESCDrive
    "电调驱动模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.ESCDriveModule;
    annotation(__MWORKS(hide=false));
  end ESCDrive;

  block AWFFController
    "AWFF 控制器接口模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.AWFFControllerModule;
    annotation(__MWORKS(hide=false));
  end AWFFController;

  model MotorDrive
    "电机驱动模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.MotorDriveModule;
    annotation(__MWORKS(hide=false));
  end MotorDrive;

  model AirframeSensor
    "机体与传感器模块"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock.Sunray150AirframeSensorModule;
    annotation(__MWORKS(hide=false));
  end AirframeSensor;

end SystemModules;
