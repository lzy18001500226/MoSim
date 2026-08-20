within MoSimQuadrotorModel.Guidance.Trajectories;
model MultiModeTrajectory
  "Parameter-driven multi-scenario trajectory reference.
   scenario_mode: 0=ClimbTrajectory  1=HoverHold  2=StepResponse
                  3=Figure8  4=SpiralAscent  5=OpenBlocksAvoidance"
  extends PartialTrajectory;

  // ── scenario selector ──────────────────────────────────────────────────
  parameter Integer scenario_mode(min = 0, max = 5) = 0
    "Active trajectory: 0 Climb 1 Hover 2 Step 3 Fig8 4 Spiral 5 OpenBlocks";

  // ── OpenBlocksAvoidance sub-block (mode=5) ─────────────────────────────
  MoSimQuadrotorModel.Guidance.Trajectories.OpenBlocksPx4CtrlReference openblocks_ref 
    annotation(Placement(transformation(origin = {0, -90}, extent = {{-20, -15}, {20, 15}})));

  // ── HoverHold parameters (mode=1) ──────────────────────────────────────
  parameter Real target_altitude_m(unit = "m") = 2.0;
  parameter Real takeoff_duration_s(unit = "s") = 5.0;
  parameter Real hold_duration_s(unit = "s") = 30.0;

  // ── StepResponse parameters (mode=2) ───────────────────────────────────
  parameter Real hover_altitude_m(unit = "m") = 2.0;
  parameter Real step_time_s(unit = "s") = 15.0;
  parameter Real x_step_m(unit = "m") = 1.0;
  parameter Real y_step_m(unit = "m") = -1.0;

  // ── Figure8 parameters (mode=3) ────────────────────────────────────────
  parameter Real altitude_m(unit = "m") = 2.0;
  parameter Real x_amplitude_m(unit = "m") = 2.0;
  parameter Real y_amplitude_m(unit = "m") = 1.0;
  parameter Real angular_rate_rad_s(unit = "rad/s") = 0.35;

  // ── SpiralAscent parameters (mode=4) ───────────────────────────────────
  parameter Real radius_m(unit = "m") = 1.5;
  parameter Real spiral_omega(unit = "rad/s") = 0.3;
  parameter Real climb_rate_m_s(unit = "m/s") = 0.15;

protected
  // Figure-8: time elapsed since takeoff_duration_s
  Real tau_f8;
  // Spiral: phase angle
  Real theta_sp;

equation
  tau_f8 = max(0.0, time - takeoff_duration_s);
  theta_sp = spiral_omega * time;

  // ── position_command ───────────────────────────────────────────────────
  // X
  position_command[1] =
    if scenario_mode == 1 then 0.0 
    else if scenario_mode == 2 then (if time >= step_time_s then x_step_m else 0.0) 
    else if scenario_mode == 3 then (if time < takeoff_duration_s then 0.0 else x_amplitude_m * sin(angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then radius_m * sin(theta_sp) 
    else if scenario_mode == 5 then openblocks_ref.position_command[1] 
    else min(10.0, max(0.0, time - 20.0));  // mode=0: ClimbTrajectory x ramp [20,30]

  // Y
  position_command[2] =
    if scenario_mode == 1 then 0.0 
    else if scenario_mode == 2 then (if time >= step_time_s then y_step_m else 0.0) 
    else if scenario_mode == 3 then (if time < takeoff_duration_s then 0.0 else y_amplitude_m * sin(2.0 * angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then radius_m * (cos(theta_sp) - 1.0) 
    else if scenario_mode == 5 then openblocks_ref.position_command[2] 
    else min(10.0, max(0.0, time - 30.0));  // mode=0: ClimbTrajectory y ramp [30,40]

  // Z
  position_command[3] =
    if scenario_mode == 1 then 
      (if time < takeoff_duration_s then (target_altitude_m / takeoff_duration_s) * time else target_altitude_m) 
    else if scenario_mode == 2 then 
      (if time < takeoff_duration_s then (hover_altitude_m / takeoff_duration_s) * time else hover_altitude_m) 
    else if scenario_mode == 3 then 
      (if time < takeoff_duration_s then (altitude_m / takeoff_duration_s) * time else altitude_m) 
    else if scenario_mode == 4 then climb_rate_m_s * time 
    else if scenario_mode == 5 then openblocks_ref.position_command[3] 
    else min(10.0, 2.0 * time) + min(5.0, max(0.0, (5.0 / 3.0) * (time - 10.0)));  // mode=0 Climb z

  // ── velocity_command ───────────────────────────────────────────────────
  velocity_command[1] =
    if scenario_mode == 3 then 
      (if time < takeoff_duration_s then 0.0 else x_amplitude_m * angular_rate_rad_s * cos(angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then radius_m * spiral_omega * cos(theta_sp) 
    else if scenario_mode == 5 then openblocks_ref.velocity_command[1] 
    else 0.0;

  velocity_command[2] =
    if scenario_mode == 3 then 
      (if time < takeoff_duration_s then 0.0 else 2.0 * y_amplitude_m * angular_rate_rad_s * cos(2.0 * angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then -(radius_m * spiral_omega) * sin(theta_sp) 
    else if scenario_mode == 5 then openblocks_ref.velocity_command[2] 
    else 0.0;

  velocity_command[3] =
    if scenario_mode == 1 then (if time < takeoff_duration_s then target_altitude_m / takeoff_duration_s else 0.0) 
    else if scenario_mode == 2 then (if time < takeoff_duration_s then hover_altitude_m / takeoff_duration_s else 0.0) 
    else if scenario_mode == 3 then (if time < takeoff_duration_s then altitude_m / takeoff_duration_s else 0.0) 
    else if scenario_mode == 4 then climb_rate_m_s 
    else if scenario_mode == 5 then openblocks_ref.velocity_command[3] 
    else 0.0;

  // ── acceleration_command ───────────────────────────────────────────────
  acceleration_command[1] =
    if scenario_mode == 3 then 
      (if time < takeoff_duration_s then 0.0 else -(x_amplitude_m * angular_rate_rad_s ^ 2) * sin(angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then -(radius_m * spiral_omega ^ 2) * sin(theta_sp) 
    else if scenario_mode == 5 then openblocks_ref.acceleration_command[1] 
    else 0.0;

  acceleration_command[2] =
    if scenario_mode == 3 then 
      (if time < takeoff_duration_s then 0.0 else -(4.0 * y_amplitude_m * angular_rate_rad_s ^ 2) * sin(2.0 * angular_rate_rad_s * tau_f8)) 
    else if scenario_mode == 4 then -(radius_m * spiral_omega ^ 2) * cos(theta_sp) 
    else if scenario_mode == 5 then openblocks_ref.acceleration_command[2] 
    else 0.0;

  acceleration_command[3] =
    if scenario_mode == 5 then openblocks_ref.acceleration_command[3] 
    else 0.0;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end MultiModeTrajectory;