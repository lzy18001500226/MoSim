within MoSimQuadrotorModel.Control.Interfaces;
partial model PartialBodyRateThrustController
  "Offline BODY_RATE_THRUST controller contract"

  Modelica.Blocks.Interfaces.RealInput position_ref[3];
  Modelica.Blocks.Interfaces.RealInput velocity_ref[3]
    "Reference translational velocity in m/s";
  Modelica.Blocks.Interfaces.RealInput acceleration_ref[3]
    "Reference translational acceleration in m/s2";
  Modelica.Blocks.Interfaces.RealInput position_mea[3];
  Modelica.Blocks.Interfaces.RealInput velocity_mea[3]
    "Runner-owned filtered translational velocity in m/s";
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3];
  Modelica.Blocks.Interfaces.RealOutput body_rate_ref[3];
  Modelica.Blocks.Interfaces.RealOutput collective_thrust_delta
    "Collective thrust increment about hover in N";
  annotation(__MWORKS(version="26.3.0"));
end PartialBodyRateThrustController;