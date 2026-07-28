within MoSimQuadrotorModel.Vehicle;
package Dynamics
  "Hidden compatibility aliases for the pre-cleanup Vehicle.Dynamics namespace"

  extends Modelica.Icons.Package;

  model ActuatorCommandMapper
    extends MoSimQuadrotorModel.Vehicle.ActuatorCommandMapper;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end ActuatorCommandMapper;

  model ActuatorMappedWrapperSurface
    extends MoSimQuadrotorModel.Vehicle.ActuatorMappedWrapperSurface;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end ActuatorMappedWrapperSurface;

  model OptionalDampingGyroLayer
    extends MoSimQuadrotorModel.Vehicle.OptionalDampingGyroLayer;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end OptionalDampingGyroLayer;

  model PhysicalWrenchAdapter
    extends MoSimQuadrotorModel.Vehicle.PhysicalWrenchAdapter;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end PhysicalWrenchAdapter;

  model RotorActuatorCore
    extends MoSimQuadrotorModel.Vehicle.RotorActuatorCore;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end RotorActuatorCore;

  model WrapperSurface
    extends MoSimQuadrotorModel.Vehicle.WrapperSurface;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end WrapperSurface;

  model HoverSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.HoverSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end HoverSmoke;

  model YawStepSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.YawStepSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end YawStepSmoke;

  model PhysicalWrenchHoverSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchHoverSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end PhysicalWrenchHoverSmoke;

  model PhysicalWrenchYawStepSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.PhysicalWrenchYawStepSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end PhysicalWrenchYawStepSmoke;

  model RotorEffectivenessSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.RotorEffectivenessSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end RotorEffectivenessSmoke;

  model WrapperHoverSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperHoverSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end WrapperHoverSmoke;

  model WrapperYawStepSmoke
    extends MoSimQuadrotorModel.Vehicle.LegacyDiagnostics.WrapperYawStepSmoke;
    annotation(__MWORKS(hide=true,version="26.3.0"));
  end WrapperYawStepSmoke;

  annotation(__MWORKS(hide=true,version="26.3.0"));
end Dynamics;
