within MoSimQuadrotorModel.ExperimentRunner.Interfaces;
partial model PartialRotorCommandController
  "Offline ROTOR_COMMAND controller contract"

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4];
  annotation(__MWORKS(version="26.3.0"));
end PartialRotorCommandController;