within MoSimQuadrotorModel.Control.Bridges;
model BacksteppingBaselineEquationBridge
  "Readable backstepping outer-loop law from the graphical baseline"

  parameter Real position_gain[3] = {1.1, 1.1, 1.3};
  parameter Real virtual_velocity_gain[3] = {1.8, 1.8, 2.0};
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;
  parameter Real normalized_thrust_scale = 0.03772949988018335;
  parameter Real collective_thrust_from_normalized = 17.745945945945948;

  input Real position_x;
  input Real position_y;
  input Real position_z;
  input Real velocity_x;
  input Real velocity_y;
  input Real velocity_z;
  input Real reference_position_x;
  input Real reference_position_y;
  input Real reference_position_z;
  input Real reference_velocity_x;
  input Real reference_velocity_y;
  input Real reference_velocity_z;
  input Real reference_acceleration_x;
  input Real reference_acceleration_y;
  input Real reference_acceleration_z;
  input Real dt "Retained for the graphical-core boundary";
  input Real enable;

  output Real desired_acceleration_x_out;
  output Real desired_acceleration_y_out;
  output Real desired_acceleration_z_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;
  output Real collective_thrust_n_out;

protected
  Real position_error[3];
  Real velocity_error[3];
  Real virtual_velocity_error[3];
  Real desired_acceleration[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Real collective_thrust_n;
  Boolean enabled;
equation
  position_error = {reference_position_x - position_x,
    reference_position_y - position_y, reference_position_z - position_z};
  velocity_error = {reference_velocity_x - velocity_x,
    reference_velocity_y - velocity_y, reference_velocity_z - velocity_z};
  for axis in 1:3 loop
    virtual_velocity_error[axis] = velocity_error[axis]
      + position_gain[axis] * position_error[axis];
    desired_acceleration[axis] = (if axis == 3 then reference_acceleration_z
      else if axis == 2 then reference_acceleration_y else reference_acceleration_x)
      + position_gain[axis] * velocity_error[axis]
      + virtual_velocity_gain[axis] * virtual_velocity_error[axis]
      + (if axis == 3 then gravity_mps2 else 0);
  end for;

  desired_roll_rad = min(max(roll_from_lateral_acceleration
    * desired_acceleration[2], -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration
    * desired_acceleration[1], -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(normalized_thrust_scale
    * desired_acceleration[3], 0.0), 1.0);
  collective_thrust_n = collective_thrust_from_normalized * normalized_thrust;

  enabled = enable >= 0.5;
  desired_acceleration_x_out = if enabled then desired_acceleration[1] else 0;
  desired_acceleration_y_out = if enabled then desired_acceleration[2] else 0;
  desired_acceleration_z_out = if enabled then desired_acceleration[3] else 0;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;
  collective_thrust_n_out = if enabled then collective_thrust_n else 0;

  annotation(__MWORKS(version = "26.3.0"));
end BacksteppingBaselineEquationBridge;
