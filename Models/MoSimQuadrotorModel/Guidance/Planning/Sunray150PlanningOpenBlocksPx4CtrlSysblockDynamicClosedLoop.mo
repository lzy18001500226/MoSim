within MoSimQuadrotorModel.Guidance.Planning;
model Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop
  "PX4CTRL whole-aircraft tracking of dynamic OpenBlocks A* path from MAT file"

  parameter Real initial_position_m[3](each unit = "m") = {-41, -26, 1.5}
    "Match the first OpenBlocks reference point at the sampled controller boundary";

  extends MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner(
    redeclare model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksDynamicReference,
    plant(initial_position_m = initial_position_m));
  // The graphical PX4CTRL outer loop owns its 100 Hz sample boundary. Do not
  // retain EquationBridge-only UnitDelay modifiers on this graphical route.

  OpenBlocksMapTruthDisplay navigationDisplay(
    n_segments = 54,
    p_x = {-41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, -41, 41},
    p_y = {-26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, -26, 26},
    p_z = {1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5},
    segment_duration = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1})
    "Canonical full-map truth with a separate 6 m local sensing overlay." annotation(Placement(transformation(extent={{-15,-46},{15,-6}})));

equation
  connect(plant.position, navigationDisplay.actual_position);
  connect(reference.position_command, navigationDisplay.reference_position);

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 300,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(hide=true,version="26.3.0"));
end Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop;
