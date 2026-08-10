within MoSimQuadrotorModel.Control.Bridges;
model DfbcHighOrderBodyRateEquationBridge
  "High-order DFBC bridge with the direct graphical body-rate projection"

  // The G5 high-order attitude/body-rate diagrams share their translational
  // high-order surface path. Reuse the checked equation bridge and retain the
  // body-rate graph's final gains and saturation limits exactly.
  extends MoSimQuadrotorModel.Control.Bridges.DfbcHighOrderEquationBridge;

  parameter Real body_rate_from_acceleration[3] = {0.72, 0.72, 0.55};
  parameter Real body_rate_limit[3] = {6.0, 6.0, 3.0};

  output Real desired_body_rate_out[3];

protected
  Real desired_body_rate[3];

equation
  desired_body_rate[1] = min(max(body_rate_from_acceleration[1]
    * desired_acceleration_x_out, -body_rate_limit[1]), body_rate_limit[1]);
  desired_body_rate[2] = min(max(body_rate_from_acceleration[2]
    * desired_acceleration_y_out, -body_rate_limit[2]), body_rate_limit[2]);
  // Vertical acceleration belongs to collective thrust, not yaw-rate demand.
  // The formal trajectory keeps a fixed yaw reference, so retain zero yaw rate.
  desired_body_rate[3] = 0;
  desired_body_rate_out = if enable >= 0.5 then desired_body_rate else {0, 0, 0};

  annotation(__MWORKS(version = "26.3.0"));
end DfbcHighOrderBodyRateEquationBridge;