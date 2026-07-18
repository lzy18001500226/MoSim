within MoSimQuadrotorModel.ExperimentRunner.Interfaces;
partial model PartialWrenchController
  "Offline WRENCH controller contract in body FLU"

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput body_force[3];
  Modelica.Blocks.Interfaces.RealOutput body_torque[3];
end PartialWrenchController;
