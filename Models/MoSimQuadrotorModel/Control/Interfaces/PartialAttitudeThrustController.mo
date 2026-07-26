within MoSimQuadrotorModel.Control.Interfaces;
partial model PartialAttitudeThrustController
  "Offline ATTITUDE_THRUST controller contract; attitude is roll/pitch/yaw in rad"

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput attitude_ref[3];
  Modelica.Blocks.Interfaces.RealOutput collective_thrust_delta;
  annotation(__MWORKS(version="26.3.0"));
end PartialAttitudeThrustController;