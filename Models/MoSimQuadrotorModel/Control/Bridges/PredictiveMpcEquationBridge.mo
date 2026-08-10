within MoSimQuadrotorModel.Control.Bridges;
model PredictiveMpcEquationBridge
  "Shared equation kernel copied from the P4 graphical predictive-controller cores"

  // Algorithm variants follow build_mpc_graphical_mil.py:
  // 1 robust, 2 adaptive, 3 tube, 4 explicit gain scheduled, 5 iLQR, 6 MPPI.
  parameter Integer algorithm_variant(min = 1, max = 6) = 1;
  parameter Real sample_time_s = 0.01;
  parameter Real horizon_s = 0.25;
  parameter Real position_weight[3] = {1.0, 1.0, 1.2};
  parameter Real velocity_weight[3] = {0.08, 0.08, 0.10};
  parameter Real control_weight[3] = {0.002, 0.002, 0.003};
  parameter Real acceleration_limit[3] = {4.0, 4.0, 2.5};
  parameter Real increment_limit[3] = {1.2, 1.2, 0.8};
  parameter Real robust_bound[3] = {0.25, 0.25, 0.20};
  parameter Real tube_position_gain[3] = {0.35, 0.35, 0.45};
  parameter Real tube_velocity_gain[3] = {0.18, 0.18, 0.25};
  parameter Real adaptive_rate = 0.08;
  parameter Real adaptive_scale_min = 0.75;
  parameter Real adaptive_scale_max = 1.25;
  parameter Real schedule_error_threshold = 0.75;
  parameter Real ilqr_step_size = 0.65;
  parameter Real mppi_temperature = 0.30;
  parameter Real mppi_noise_scale[3] = {0.35, 0.35, 0.25};
  parameter Real gravity_mps2 = 9.80665;
  parameter Real roll_from_lateral_acceleration = -0.10197162129779283;
  parameter Real pitch_from_lateral_acceleration = 0.10197162129779283;
  parameter Real tilt_limit_rad = 0.5235987755982988;
  parameter Real normalized_thrust_scale = 0.03772949988018335;

  input Real position[3];
  input Real velocity[3];
  input Real reference_position[3];
  input Real reference_velocity[3];
  input Real reference_acceleration[3];
  input Real enable;

  output Real desired_acceleration_out[3]
    "World acceleration command after P4 gravity compensation";
  output Real unconstrained_acceleration_out[3];
  output Real auxiliary_out[3];
  output Real solver_cost_out;
  output Real solver_iterations_out;
  output Real desired_roll_rad_out;
  output Real desired_pitch_rad_out;
  output Real normalized_thrust_out;

protected
  discrete Real previous_acceleration[3](each start = 0, each fixed = true);
  discrete Real adaptive_scale_memory(start = 1, fixed = true);
  Real position_error[3];
  Real velocity_error[3];
  Real denominator[3];
  Real linear_acceleration[3];
  Real robust_acceleration[3];
  Real adaptive_acceleration[3];
  Real tube_acceleration[3];
  Real scheduled_acceleration[3];
  Real ilqr_acceleration[6, 3];
  Real ilqr_position_prediction[5, 3];
  Real ilqr_velocity_prediction[5, 3];
  Real ilqr_gradient[5, 3];
  Real mppi_candidate[7, 3];
  Real mppi_cost[7, 3];
  Real mppi_minimum_cost[3];
  Real mppi_weight[7, 3];
  Real mppi_weighted_candidate[7, 3];
  Real mppi_solution[3];
  Real selected_core_acceleration[3];
  Real constrained_acceleration[3];
  Real absolute_limited_acceleration[3];
  Real selected_acceleration_limit[3];
  Real adaptive_scale_candidate;
  Real adaptive_scale;
  Real schedule[3];
  Real stage_cost[3];
  Real desired_roll_rad;
  Real desired_pitch_rad;
  Real normalized_thrust;
  Boolean enabled;

equation
  position_error = reference_position - position;
  velocity_error = reference_velocity - velocity;
  for axis in 1:3 loop
    denominator[axis] = 0.5 * position_weight[axis] * horizon_s ^ 4
      + 2 * velocity_weight[axis] * horizon_s ^ 2 + 2 * control_weight[axis];
    linear_acceleration[axis] = position_weight[axis] * horizon_s ^ 2
      / denominator[axis] * position_error[axis]
      + 2 * velocity_weight[axis] * horizon_s / denominator[axis]
      * velocity_error[axis]
      + 2 * control_weight[axis] / denominator[axis]
      * previous_acceleration[axis];

    robust_acceleration[axis] = linear_acceleration[axis] + robust_bound[axis]
      * Modelica.Math.tanh(4 * (position_error[axis]
        + horizon_s * velocity_error[axis]));
    tube_acceleration[axis] = linear_acceleration[axis]
      + tube_position_gain[axis] * position_error[axis]
      + tube_velocity_gain[axis] * velocity_error[axis];
    schedule[axis] = min(max(abs(position_error[axis])
      / schedule_error_threshold, 0), 1);
    scheduled_acceleration[axis] = linear_acceleration[axis] + schedule[axis]
      * (tube_position_gain[axis] * position_error[axis]
        + tube_velocity_gain[axis] * velocity_error[axis]);
    adaptive_acceleration[axis] = linear_acceleration[axis] * adaptive_scale;

    ilqr_acceleration[1, axis] = linear_acceleration[axis];
    for iteration in 1:5 loop
      ilqr_position_prediction[iteration, axis] = position_error[axis]
        + horizon_s * velocity_error[axis]
        - 0.5 * horizon_s ^ 2 * ilqr_acceleration[iteration, axis];
      ilqr_velocity_prediction[iteration, axis] = velocity_error[axis]
        - horizon_s * ilqr_acceleration[iteration, axis];
      ilqr_gradient[iteration, axis] = -position_weight[axis] * horizon_s ^ 2
        * ilqr_position_prediction[iteration, axis]
        - 2 * velocity_weight[axis] * horizon_s
        * ilqr_velocity_prediction[iteration, axis]
        + 2 * control_weight[axis] * ilqr_acceleration[iteration, axis];
      ilqr_acceleration[iteration + 1, axis] = ilqr_acceleration[iteration, axis]
        - ilqr_step_size / denominator[axis] * ilqr_gradient[iteration, axis];
    end for;

    for sample in 1:7 loop
      mppi_candidate[sample, axis] = linear_acceleration[axis]
        + (sample - 4) * 0.5 * mppi_noise_scale[axis];
      mppi_cost[sample, axis] = position_weight[axis]
        * (position_error[axis] + horizon_s * velocity_error[axis]
          - 0.5 * horizon_s ^ 2 * mppi_candidate[sample, axis]) ^ 2
        + velocity_weight[axis]
        * (velocity_error[axis] - horizon_s * mppi_candidate[sample, axis]) ^ 2
        + control_weight[axis] * mppi_candidate[sample, axis] ^ 2;
    end for;
    mppi_minimum_cost[axis] = min(mppi_cost[1, axis], min(mppi_cost[2, axis],
      min(mppi_cost[3, axis], min(mppi_cost[4, axis], min(mppi_cost[5, axis],
      min(mppi_cost[6, axis], mppi_cost[7, axis]))))));
    for sample in 1:7 loop
      mppi_weight[sample, axis] = Modelica.Math.exp(-(mppi_cost[sample, axis]
        - mppi_minimum_cost[axis]) / mppi_temperature);
      mppi_weighted_candidate[sample, axis] = mppi_weight[sample, axis]
        * mppi_candidate[sample, axis];
    end for;
    mppi_solution[axis] = (mppi_weighted_candidate[1, axis]
      + mppi_weighted_candidate[2, axis] + mppi_weighted_candidate[3, axis]
      + mppi_weighted_candidate[4, axis] + mppi_weighted_candidate[5, axis]
      + mppi_weighted_candidate[6, axis] + mppi_weighted_candidate[7, axis])
      / (mppi_weight[1, axis] + mppi_weight[2, axis] + mppi_weight[3, axis]
        + mppi_weight[4, axis] + mppi_weight[5, axis] + mppi_weight[6, axis]
        + mppi_weight[7, axis]);

    selected_core_acceleration[axis] = if algorithm_variant == 1 then 
      robust_acceleration[axis] else if algorithm_variant == 2 then 
      adaptive_acceleration[axis] else if algorithm_variant == 3 then 
      tube_acceleration[axis] else if algorithm_variant == 4 then 
      scheduled_acceleration[axis] else if algorithm_variant == 5 then 
      ilqr_acceleration[6, axis] else mppi_solution[axis];
    unconstrained_acceleration_out[axis] = selected_core_acceleration[axis]
      + reference_acceleration[axis];
    selected_acceleration_limit[axis] = if algorithm_variant == 3 then 
      max(0.1, acceleration_limit[axis] - robust_bound[axis]) 
      else acceleration_limit[axis];
    absolute_limited_acceleration[axis] = min(max(
      unconstrained_acceleration_out[axis], -selected_acceleration_limit[axis]),
      selected_acceleration_limit[axis]);
    constrained_acceleration[axis] = min(max(absolute_limited_acceleration[axis],
      previous_acceleration[axis] - increment_limit[axis]),
      previous_acceleration[axis] + increment_limit[axis]);
    desired_acceleration_out[axis] = if axis == 3 then 
      constrained_acceleration[axis] + gravity_mps2 else constrained_acceleration[axis];
    auxiliary_out[axis] = if algorithm_variant == 1 then robust_bound[axis] 
      else if algorithm_variant == 2 then adaptive_scale 
      else if algorithm_variant == 3 then selected_acceleration_limit[axis] 
      else if algorithm_variant == 4 then schedule[axis] 
      else if algorithm_variant == 6 then mppi_minimum_cost[axis] else 0;
    stage_cost[axis] = position_weight[axis]
      * (position_error[axis] + horizon_s * velocity_error[axis]
        - 0.5 * horizon_s ^ 2 * constrained_acceleration[axis]) ^ 2
      + velocity_weight[axis]
      * (velocity_error[axis] - horizon_s * constrained_acceleration[axis]) ^ 2
      + control_weight[axis] * constrained_acceleration[axis] ^ 2;
  end for;

  adaptive_scale_candidate = min(max(adaptive_scale_memory + adaptive_rate
    * sample_time_s / 3 * (position_error[1] * velocity_error[1]
      + position_error[2] * velocity_error[2]
      + position_error[3] * velocity_error[3]), adaptive_scale_min),
    adaptive_scale_max);
  adaptive_scale = if algorithm_variant == 2 then adaptive_scale_candidate else 1;
  when sample(sample_time_s, sample_time_s) then
    if enable >= 0.5 then
      for axis in 1:3 loop
        previous_acceleration[axis] = constrained_acceleration[axis];
      end for;
      adaptive_scale_memory = adaptive_scale_candidate;
    else
      for axis in 1:3 loop
        previous_acceleration[axis] = 0;
      end for;
      adaptive_scale_memory = 1;
    end if;
  end when;

  desired_roll_rad = min(max(roll_from_lateral_acceleration
    * desired_acceleration_out[2], -tilt_limit_rad), tilt_limit_rad);
  desired_pitch_rad = min(max(pitch_from_lateral_acceleration
    * desired_acceleration_out[1], -tilt_limit_rad), tilt_limit_rad);
  normalized_thrust = min(max(normalized_thrust_scale
    * desired_acceleration_out[3], 0), 1);
  solver_cost_out = if algorithm_variant == 6 then mppi_minimum_cost[1]
    + mppi_minimum_cost[2] + mppi_minimum_cost[3] else stage_cost[1]
    + stage_cost[2] + stage_cost[3];
  solver_iterations_out = if algorithm_variant == 5 then 5 
    else if algorithm_variant == 6 then 7 else 0;
  enabled = enable >= 0.5;
  desired_roll_rad_out = if enabled then desired_roll_rad else 0;
  desired_pitch_rad_out = if enabled then desired_pitch_rad else 0;
  normalized_thrust_out = if enabled then normalized_thrust else 0;

  annotation(__MWORKS(version = "26.3.0"));
end PredictiveMpcEquationBridge;