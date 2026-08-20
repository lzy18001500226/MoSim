within MoSimQuadrotorModel.Experiment.Px4Ctrl;
model OpenBlocksLocalPerceptionDisplaySmoke
  "Static native-3D smoke case for the OpenBlocks 9 m local perception display"

  parameter Real actual_position_m[3] = {-8.0, 0.0, 1.0}
    "Pose near the first wall group so the local window contains ground and wall geometry";
  parameter Real reference_position_m[3] = {-6.0, 2.0, 1.0};

  MoSimQuadrotorModel.Environment.Maps.OpenBlocksLocalPerceptionDisplay nav_display;

equation
  nav_display.actual_position = actual_position_m;
  nav_display.reference_position = reference_position_m;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.1,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end OpenBlocksLocalPerceptionDisplaySmoke;