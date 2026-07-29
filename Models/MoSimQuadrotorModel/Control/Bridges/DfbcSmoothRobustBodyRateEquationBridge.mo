within MoSimQuadrotorModel.Control.Bridges;
model DfbcSmoothRobustBodyRateEquationBridge
  "Smooth-robust DFBC bridge with the graphical body-rate output projection"

  // The body-rate and attitude graphical variants share the same translational
  // smooth-robust path. This class retains that path and replaces only the
  // final graphical projection with its published body-rate gains and limits.
  extends MoSimQuadrotorModel.Control.Bridges.DfbcSmoothRobustAttitudeEquationBridge;

  parameter Real body_rate_from_acceleration[3] = {0.72, 0.72, 0.55};
  parameter Real body_rate_limit[3] = {6.0, 6.0, 3.0};

  output Real desired_body_rate_out[3];

protected
  Real desired_body_rate[3];

equation
  for axis in 1:2 loop
    desired_body_rate[axis] = min(max(body_rate_from_acceleration[axis]
      * desired_acceleration_out[axis], -body_rate_limit[axis]),
      body_rate_limit[axis]);
    desired_body_rate_out[axis] = if enable >= 0.5 then
      desired_body_rate[axis] else 0;
  end for;
  // The vertical acceleration channel produces collective thrust. It must not
  // be projected into yaw rate when the formal trajectory holds yaw at zero.
  desired_body_rate[3] = 0;
  desired_body_rate_out[3] = 0;

  annotation(__MWORKS(version = "26.3.0"));
end DfbcSmoothRobustBodyRateEquationBridge;
