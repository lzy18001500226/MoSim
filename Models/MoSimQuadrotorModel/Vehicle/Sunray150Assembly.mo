within MoSimQuadrotorModel.Vehicle;
model Sunray150Assembly
  "Canonical Sunray150 physical assembly shared by every offline Runner"

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real initial_rotor_speed[4] = {
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s,
    profile.mworks_hover_visual_rotor_speed_rad_s,
    -profile.mworks_hover_visual_rotor_speed_rad_s};
  parameter Real rotor_effectiveness[4] = {1, 1, 1, 1};
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real reaction_moment_ratio = profile.moment_constant_ratio_m;
  parameter Real yaw_reaction_direction[4] = -profile.mworks_yaw_direction
    "Aerodynamic reaction torque opposes the recorded rotor spin direction";
  parameter Real gust_force[3] = {0, 0, 0};
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 0;
  parameter Real mass_scale(min = 0.01) = 1
    "Plant-only body mass scale for parameter-mismatch experiments";
  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1}
    "Plant-only diagonal inertia scale for parameter-mismatch experiments";
  parameter Real fault_start_s(unit = "s") = 1e9
    "Scheduled motor-fault start time; default is disabled over formal horizons";
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;

  Modelica.Blocks.Interfaces.RealInput rotor_command[4];
  Modelica.Blocks.Interfaces.RealOutput position[3];
  Modelica.Blocks.Interfaces.RealOutput attitude[3];
  Modelica.Blocks.Interfaces.RealOutput rotor_speed[4];

  MoSimQuadrotorModel.Vehicle.Dynamics.PhysicalWrenchAdapter physical(
    profile = profile,
    initial_rotor_speed = initial_rotor_speed,
    lift_coefficient = lift_coefficient,
    reaction_moment_ratio = reaction_moment_ratio,
    yaw_reaction_direction = yaw_reaction_direction,
    thrust_effectiveness = rotor_effectiveness,
    reaction_moment_effectiveness = rotor_effectiveness,
    mass_scale = mass_scale,
    inertia_scale = inertia_scale,
    fault_start_s = fault_start_s,
    fault_rotor_index = fault_rotor_index,
    fault_rotor_effectiveness = fault_rotor_effectiveness);
  MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors;
  Modelica.Mechanics.MultiBody.Forces.WorldForce gust(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
    animation = false);
  Real rotor_thrust[4](each unit = "N");
  Real rotor_yaw_reaction_moment[4](each unit = "N.m");
  Real applied_reaction_yaw_moment(unit = "N.m");

equation
  gust.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[1] else 0;
  gust.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[2] else 0;
  gust.force[3] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then gust_force[3] else 0;

  connect(gust.frame_b, physical.body.frame_a);
  connect(physical.body.frame_a, sensors.frame_a);

  for i in 1:4 loop
    physical.wrapper.motor_command[i] = rotor_command[i];
    rotor_speed[i] = physical.wrapper.dynamics.omega[i];
    rotor_thrust[i] = physical.wrapper.dynamics.thrust[i];
    rotor_yaw_reaction_moment[i] = physical.wrapper.dynamics.yaw_reaction_moment[i];
  end for;
  applied_reaction_yaw_moment = physical.applied_yaw_torque_body;

  position = sensors.PosMea;
  attitude = sensors.AngleMea;

  annotation(Icon(graphics = {Text(extent = {{-92, 20}, {92, -20}}, textString = "Sunray150整机/动画")}),
    Diagram(coordinateSystem(extent = {{-200, -120}, {200, 120}})),
    __MWORKS(version="26.3.0"));
end Sunray150Assembly;
