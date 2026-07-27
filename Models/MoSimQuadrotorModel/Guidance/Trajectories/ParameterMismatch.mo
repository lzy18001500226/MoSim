within MoSimQuadrotorModel.Guidance.Trajectories;
model ParameterMismatch
  "ClimbPath reference with a configurable mass and inertia mismatch contract"

  extends MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  parameter Real mismatch_fraction(min = 0, max = 1) = 0.20
    "Magnitude of the mass and inertia bias";
  parameter Boolean use_negative_bias = false
    "False applies +20 percent; true applies -20 percent";
  parameter Real mass_scale = if use_negative_bias then
    1 - mismatch_fraction else 1 + mismatch_fraction;
  parameter Real inertia_scale[3] = {mass_scale, mass_scale, mass_scale}
    "Principal-inertia scale read by a Runner when this scenario is bound";

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end ParameterMismatch;
