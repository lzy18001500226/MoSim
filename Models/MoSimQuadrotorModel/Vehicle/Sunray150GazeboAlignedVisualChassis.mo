within MoSimQuadrotorModel.Vehicle;
model Sunray150GazeboAlignedVisualChassis
  "Official QuadChassis physics with Gazebo-aligned Sunray150 propeller visuals"

  extends MoSimQuadrotorModel.Vehicle.Mechanics.QuadChassis(
    propellers1(
      length = 0.001,
      width = 0.001,
      height = 0.001,
      lengthDirection = {0, -1, 0},
      widthDirection = {-1, 0, 0}),
    propellers2(
      length = 0.001,
      width = 0.001,
      height = 0.001,
      lengthDirection = {0, -1, 0},
      widthDirection = {-1, 0, 0}),
    propellers3(
      length = 0.001,
      width = 0.001,
      height = 0.001,
      lengthDirection = {0, -1, 0},
      widthDirection = {-1, 0, 0}),
    propellers4(
      length = 0.001,
      width = 0.001,
      height = 0.001,
      lengthDirection = {0, -1, 0},
      widthDirection = {-1, 0, 0}));

  annotation(__MWORKS(version="26.3.0"));
end Sunray150GazeboAlignedVisualChassis;
