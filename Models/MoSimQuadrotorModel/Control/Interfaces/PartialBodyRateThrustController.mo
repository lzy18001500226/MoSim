within MoSimQuadrotorModel.Control.Interfaces;
partial model PartialBodyRateThrustController
  "Offline BODY_RATE_THRUST controller contract"

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput body_rate_ref[3];
  Modelica.Blocks.Interfaces.RealOutput collective_thrust_delta;
  annotation(__MWORKS(version="26.3.0"));
end PartialBodyRateThrustController;