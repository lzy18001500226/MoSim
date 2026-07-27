within MoSimQuadrotorModel.Control.Adapters;
model DfbcHighOrderAttitudeThrustAdapter
  "Selected graphical high-order DFBC law through an equation bridge at ATTITUDE_THRUST"

  extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;

  parameter MoSimQuadrotorModel.Parameters.Sunray150VirtualPx4Classic profile;
  parameter Real sample_time_s = 0.01;
  parameter Real hover_speed = profile.mworks_hover_visual_rotor_speed_rad_s;
  parameter Real lift_coefficient = profile.mworks_visual_thrust_coefficient;
  parameter Real collective_thrust_slope = 8 * lift_coefficient * hover_speed;
  parameter Real normalized_thrust_scale = 0.03772949988018335
    "Copied from the selected graphical DFBC output adapter";
  parameter Real max_collective_thrust_delta_n = 30.0 * collective_thrust_slope;

  MoSimQuadrotorModel.Control.Bridges.DfbcHighOrderEquationBridge core(sample_time_s = sample_time_s);
  Modelica.Blocks.Continuous.Derivative body_rate_estimator[3](
    each k = 1,
    each T = 0.02,
    each initType = Modelica.Blocks.Types.Init.InitialOutput,
    each y_start = 0);

  Real desired_collective_thrust_n
    "DFBC normalized thrust includes its own gravity compensation";
  Real roll_ref;

equation
  connect(attitude_mea, body_rate_estimator.u);

  core.position_x = position_mea[1];
  core.position_y = position_mea[2];
  core.position_z = position_mea[3];
  core.velocity_x = velocity_mea[1];
  core.velocity_y = velocity_mea[2];
  core.velocity_z = velocity_mea[3];
  core.reference_position_x = position_ref[1];
  core.reference_position_y = position_ref[2];
  core.reference_position_z = position_ref[3];
  core.reference_velocity_x = 0;
  core.reference_velocity_y = 0;
  core.reference_velocity_z = 0;
  core.reference_acceleration_x = 0;
  core.reference_acceleration_y = 0;
  core.reference_acceleration_z = 0;
  core.body_rate_x = body_rate_estimator[1].y;
  core.body_rate_y = body_rate_estimator[2].y;
  core.body_rate_z = body_rate_estimator[3].y;
  core.dt = sample_time_s;
  core.enable = 1;

  roll_ref = core.desired_roll_rad_out;
  // The DFBC bridge emits ENU/FLU roll; the shared MWORKS allocator uses the opposite roll sense.
  attitude_ref[1] = -roll_ref;
  attitude_ref[2] = core.desired_pitch_rad_out;
  attitude_ref[3] = 0;
  desired_collective_thrust_n = core.normalized_thrust_out / normalized_thrust_scale;
  collective_thrust_delta = min(max(
    desired_collective_thrust_n - 4 * lift_coefficient * hover_speed ^ 2,
    -max_collective_thrust_delta_n), max_collective_thrust_delta_n);

  annotation(__MWORKS(version = "26.3.0"));
end DfbcHighOrderAttitudeThrustAdapter;
