within;
package QuadrotorExperiments
  "Project-local experiment models for official quadrotor comparisons"

  extends Modelica.Icons.Package;
  annotation(uses(
    Modelica(version = "4.0.0.TY.1"),
    QuadrotorModel));

  function saturate
    input Real u;
    input Real limit;
    output Real y;
  algorithm
    y := if u > limit then limit else if u < -limit then -limit else u;
  end saturate;

  model AntiWindupFeedforwardController
    "Project-owned PID controller with conditional integration and reference feedforward"
    parameter Real kp_x = 1.65;
    parameter Real ki_x = 0.0;
    parameter Real kd_x = 1.0;
    parameter Real kp_y = 1.65;
    parameter Real ki_y = 0.0;
    parameter Real kd_y = 1.0;
    parameter Real kp_z = 8.0;
    parameter Real ki_z = 6.0;
    parameter Real kd_z = 4.0;
    parameter Real kp_roll = 14.142;
    parameter Real kd_roll = 1.70;
    parameter Real kp_pitch = 14.142;
    parameter Real kd_pitch = 1.70;
    parameter Real kp_yaw = 5.0;
    parameter Real roll_pitch_cmd_limit = 12 / 57.3;
    parameter Real attitude_cmd_limit = 6.5;
    parameter Real yaw_cmd_limit = 6.5;
    parameter Real output_limit = 20.0;
    parameter Real reference_feedforward_z = 0.35;
    parameter Real reference_filter_T = 0.20;
    parameter Real position_derivative_filter_T = 0.05;
    parameter Real altitude_derivative_filter_T = 0.08;
    parameter Real attitude_derivative_filter_T = 0.03;

    Modelica.Blocks.Interfaces.RealInput position_command[3];
    Modelica.Blocks.Interfaces.RealInput position[3];
    Modelica.Blocks.Interfaces.RealInput angle[3];
    Modelica.Blocks.Interfaces.RealOutput y;
    Modelica.Blocks.Interfaces.RealOutput y1;
    Modelica.Blocks.Interfaces.RealOutput y2;
    Modelica.Blocks.Interfaces.RealOutput y3;

    Real ex;
    Real ey;
    Real ez;
    Real e_roll;
    Real e_pitch;
    Real e_yaw;
    Real ex_filter(start = 0, fixed = true);
    Real ey_filter(start = 0, fixed = true);
    Real ez_filter(start = 0, fixed = true);
    Real e_roll_filter(start = 0, fixed = true);
    Real e_pitch_filter(start = 0, fixed = true);
    Real dex;
    Real dey;
    Real dez;
    Real d_roll;
    Real d_pitch;
    Real ix(start = 0, fixed = true);
    Real iy(start = 0, fixed = true);
    Real iz(start = 0, fixed = true);
    Real x_cmd_raw;
    Real y_cmd_raw;
    Real z_cmd_raw;
    Real x_cmd;
    Real y_cmd;
    Real z_cmd;
    Real roll_cmd_raw;
    Real pitch_cmd_raw;
    Real yaw_cmd_raw;
    Real roll_cmd;
    Real pitch_cmd;
    Real yaw_cmd;
    Real z_ref_filter(start = 0, fixed = true);
    Real z_ref_rate;
    Real common;
    Real yaw_mix;
    Real pitch_mix;
    Real roll_mix;
    Real u1_raw;
    Real u2_raw;
    Real u3_raw;
    Real u4_raw;

  equation
    ex = position_command[1] - position[1];
    ey = position_command[2] - position[2];
    ez = position_command[3] - position[3];

    der(z_ref_filter) = (position_command[3] - z_ref_filter) / reference_filter_T;
    z_ref_rate = (position_command[3] - z_ref_filter) / reference_filter_T;

    der(ex_filter) = (ex - ex_filter) / position_derivative_filter_T;
    der(ey_filter) = (ey - ey_filter) / position_derivative_filter_T;
    der(ez_filter) = (ez - ez_filter) / altitude_derivative_filter_T;
    dex = (ex - ex_filter) / position_derivative_filter_T;
    dey = (ey - ey_filter) / position_derivative_filter_T;
    dez = (ez - ez_filter) / altitude_derivative_filter_T;

    x_cmd_raw = kp_x * ex + ki_x * ix + kd_x * dex;
    y_cmd_raw = kp_y * ey + ki_y * iy + kd_y * dey;
    z_cmd_raw = kp_z * ez + ki_z * iz + kd_z * dez + reference_feedforward_z * z_ref_rate;
    x_cmd = saturate(0.1 * x_cmd_raw, roll_pitch_cmd_limit);
    y_cmd = saturate(0.1 * y_cmd_raw, roll_pitch_cmd_limit);
    z_cmd = z_cmd_raw;

    der(ix) = if abs(0.1 * x_cmd_raw) < roll_pitch_cmd_limit or ex * x_cmd_raw < 0 then ex else 0;
    der(iy) = if abs(0.1 * y_cmd_raw) < roll_pitch_cmd_limit or ey * y_cmd_raw < 0 then ey else 0;
    der(iz) = if abs(z_cmd_raw) < output_limit or ez * z_cmd_raw < 0 then ez else 0;

    e_pitch = x_cmd - angle[2];
    e_roll = y_cmd + angle[1];
    e_yaw = -angle[3];

    der(e_pitch_filter) = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
    der(e_roll_filter) = (e_roll - e_roll_filter) / attitude_derivative_filter_T;
    d_pitch = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
    d_roll = (e_roll - e_roll_filter) / attitude_derivative_filter_T;

    pitch_cmd_raw = kp_pitch * e_pitch + kd_pitch * d_pitch;
    roll_cmd_raw = kp_roll * e_roll + kd_roll * d_roll;
    yaw_cmd_raw = kp_yaw * e_yaw;
    pitch_cmd = saturate(pitch_cmd_raw, attitude_cmd_limit);
    roll_cmd = saturate(roll_cmd_raw, attitude_cmd_limit);
    yaw_cmd = saturate(yaw_cmd_raw, yaw_cmd_limit);

    common = z_cmd;
    yaw_mix = 0.707 * yaw_cmd;
    pitch_mix = 0.707 * pitch_cmd;
    roll_mix = 0.707 * roll_cmd;

    u1_raw = common + (-yaw_mix - pitch_mix + roll_mix);
    u2_raw = -(common + (yaw_mix - pitch_mix - roll_mix));
    u3_raw = common + (-yaw_mix + pitch_mix - roll_mix);
    u4_raw = -(common + (yaw_mix + pitch_mix + roll_mix));

    y = saturate(u1_raw, output_limit);
    y1 = saturate(u2_raw, output_limit);
    y2 = saturate(u3_raw, output_limit);
    y3 = saturate(u4_raw, output_limit);
  end AntiWindupFeedforwardController;

  partial model Example1ProjectControllerBase
    "Project-owned Example1 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1ProjectControllerBase;

  partial model Example2ProjectControllerBase
    "Project-owned Example2 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.CirclePath climbePath(ramp(height = 20), sine(f = 0.05), cosine(f = 0.05, startTime = 10, phase = 0));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2ProjectControllerBase;

  partial model Example3ProjectControllerBase
    "Project-owned Example3 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.EightPath climbePath;
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3ProjectControllerBase;

  model Example1AntiWindupFeedforwardPID
    "Example1 with project-owned anti-windup and reference-feedforward controller"
    extends Example1ProjectControllerBase;
  end Example1AntiWindupFeedforwardPID;

  model Example2AntiWindupFeedforwardPID
    "Example2 with project-owned anti-windup and reference-feedforward controller"
    extends Example2ProjectControllerBase;
  end Example2AntiWindupFeedforwardPID;

  model Example2HelixTunedAntiWindupFeedforwardPID
    "Example2 AWFF PID with helix-specific lateral command authority"
    extends Example2ProjectControllerBase(
      controller3_2(
        roll_pitch_cmd_limit = 15 / 57.3,
        attitude_cmd_limit = 7.0,
        yaw_cmd_limit = 7.0));
  end Example2HelixTunedAntiWindupFeedforwardPID;

  model Example3AntiWindupFeedforwardPID
    "Example3 with project-owned anti-windup and reference-feedforward controller"
    extends Example3ProjectControllerBase;
  end Example3AntiWindupFeedforwardPID;

  model Example1Mass20AntiWindupFeedforwardPID
    "Example1 AWFF PID with +20% central body mass perturbation"
    extends Example1ProjectControllerBase(
      quadChassisTest17_1.body(m = 1.2));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20AntiWindupFeedforwardPID;

  partial model Example1WindGustBase
    "Example1 with lateral world-frame gust force connected to the chassis body"
    extends QuadrotorModel.Examples.Example1;

    parameter Real gust_force_x_N = 0.22;
    parameter Real gust_force_y_N = -0.10;
    parameter Real gust_start_s = 15.0;
    parameter Real gust_duration_s = 4.0;
    parameter Real gust_sine_amplitude_x_N = 0.08;
    parameter Real gust_sine_amplitude_y_N = 0.04;
    parameter Real gust_sine_frequency_Hz = 1.2;

    Modelica.Mechanics.MultiBody.Forces.WorldForce gustForce(
      resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
      animation = false);

  equation
    gustForce.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then
      gust_force_x_N + gust_sine_amplitude_x_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s))
      else 0;
    gustForce.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then
      gust_force_y_N + gust_sine_amplitude_y_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s))
      else 0;
    gustForce.force[3] = 0;
    connect(gustForce.frame_b, quadChassisTest17_1.body.frame_b);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1WindGustBase;

  partial model Example1WindGustProjectControllerBase
    "Example1 project controller clone with lateral world-frame gust force"
    extends Example1ProjectControllerBase;

    parameter Real gust_force_x_N = 0.22;
    parameter Real gust_force_y_N = -0.10;
    parameter Real gust_start_s = 15.0;
    parameter Real gust_duration_s = 4.0;
    parameter Real gust_sine_amplitude_x_N = 0.08;
    parameter Real gust_sine_amplitude_y_N = 0.04;
    parameter Real gust_sine_frequency_Hz = 1.2;

    Modelica.Mechanics.MultiBody.Forces.WorldForce gustForce(
      resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
      animation = false);

  equation
    gustForce.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then
      gust_force_x_N + gust_sine_amplitude_x_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s))
      else 0;
    gustForce.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then
      gust_force_y_N + gust_sine_amplitude_y_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s))
      else 0;
    gustForce.force[3] = 0;
    connect(gustForce.frame_b, quadChassisTest17_1.body.frame_b);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1WindGustProjectControllerBase;

  model Example1WindGustAntiWindupFeedforwardPID
    "Example1 AWFF PID with lateral gust disturbance"
    extends Example1WindGustProjectControllerBase;
  end Example1WindGustAntiWindupFeedforwardPID;

  model Example1Rotor1Loss15AntiWindupFeedforwardPID
    "Example1 AWFF PID with rotor 1 lift efficiency reduced to 85%"
    extends Example1ProjectControllerBase(
      quadChassisTest17_1.gain2(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15AntiWindupFeedforwardPID;

  model Example1ImprovedPID
    "Example1 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example1(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1ImprovedPID;

  model Example1EnhancedPID
    "Example1 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example1(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1EnhancedPID;

  model Example1Mass20PID
    "Example1 baseline PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20PID;

  model Example1Mass20ImprovedPID
    "Example1 improved PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20ImprovedPID;

  model Example1Mass20EnhancedPID
    "Example1 enhanced PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20EnhancedPID;

  model Example1WindGustPID
    "Example1 baseline PID with lateral gust disturbance"
    extends Example1WindGustBase;
  end Example1WindGustPID;

  model Example1WindGustImprovedPID
    "Example1 improved PID with lateral gust disturbance"
    extends Example1WindGustBase(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
  end Example1WindGustImprovedPID;

  model Example1WindGustEnhancedPID
    "Example1 enhanced PID with lateral gust disturbance"
    extends Example1WindGustBase(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
  end Example1WindGustEnhancedPID;

  model Example1Rotor1Loss15PID
    "Example1 baseline PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15PID;

  model Example1Rotor1Loss15ImprovedPID
    "Example1 improved PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15ImprovedPID;

  model Example1Rotor1Loss15EnhancedPID
    "Example1 enhanced PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15EnhancedPID;

  model Example1Rotor2Loss15PID
    "Example1 baseline PID with rotor 2 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain3(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor2Loss15PID;

  model Example1Rotor3Loss15PID
    "Example1 baseline PID with rotor 3 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain4(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor3Loss15PID;

  model Example1Rotor4Loss15PID
    "Example1 baseline PID with rotor 4 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain5(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor4Loss15PID;

  model Example2ImprovedPID
    "Example2 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2ImprovedPID;

  model Example2EnhancedPID
    "Example2 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2EnhancedPID;

  model Example2HelixTunedEnhancedPID
    "Example2 enhanced PID with helix-specific lateral command authority"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 15 / 57.3, uMin = -15 / 57.3),
      controller3_2.limiter2(uMax = 15 / 57.3, uMin = -15 / 57.3),
      controller3_2.limiter3(uMax = 7.0, uMin = -7.0),
      controller3_2.limiter4(uMax = 7.0, uMin = -7.0),
      controller3_2.limiter5(uMax = 7.0, uMin = -7.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2HelixTunedEnhancedPID;

  model Example3ImprovedPID
    "Example3 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example3(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3ImprovedPID;

  model Example3EnhancedPID
    "Example3 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example3(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3EnhancedPID;
model Sunray150CompleteSystemGraphical_Sysblock
  "Sunray150 complete graphical system with project AWFF Sysblock data flow"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  block GPSInterfaceBlock
    "Graphical GPS/GNSS data interface: measured position to navigation position"
    Modelica.Blocks.Interfaces.RealInput position_raw[3]
      annotation (Placement(transformation(origin = {-110, 20}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3]
      annotation (Placement(transformation(origin = {110, 20}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-10, -10}, {10, 10}})));
  equation
    position_est = position_raw;
    health = 1;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {40, 90, 180}, fillColor = {245, 250, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 12}, extent = {{-58, -42}, {58, 42}}, fileName = "modelica://QuadrotorModel/Resources/Images/GPS.png"),
        Text(origin = {0, -72}, extent = {{-80, 15}, {80, -15}}, textString = "GPS", textColor = {40, 90, 180})}));
  end GPSInterfaceBlock;

  block Mid360InterfaceBlock
    "Graphical Mid360 perception interface: estimated pose to local-map status"
    Modelica.Blocks.Interfaces.RealInput position_est[3]
      annotation (Placement(transformation(origin = {-110, 20}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput local_position[3]
      annotation (Placement(transformation(origin = {110, 20}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_margin
      annotation (Placement(transformation(origin = {110, -25}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -60}, extent = {{-10, -10}, {10, 10}})));
  equation
    local_position = position_est;
    obstacle_margin = 5.0;
    health = 1;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 120, 120}, fillColor = {240, 255, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 15}, extent = {{-58, -40}, {58, 40}}, fileName = "modelica://QuadrotorModel/Resources/Images/MId360.png"),
        Text(origin = {0, -72}, extent = {{-80, 15}, {80, -15}}, textString = "Mid360", textColor = {0, 120, 120})}));
  end Mid360InterfaceBlock;

  block V6XFlightControllerInterfaceBlock
    "Graphical V6X/PX6C flight-controller state interface"
    Modelica.Blocks.Interfaces.RealInput gps_position[3]
      annotation (Placement(transformation(origin = {-110, 55}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput attitude_raw[3]
      annotation (Placement(transformation(origin = {-110, 10}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4]
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3]
      annotation (Placement(transformation(origin = {110, 55}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput attitude_est[3]
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4]
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-10, -10}, {10, 10}})));
  equation
    position_est = gps_position;
    attitude_est = attitude_raw;
    motor_speed_est = motor_speed_raw;
    health = 1;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 13}, extent = {{-58, -42}, {58, 42}}, fileName = "modelica://QuadrotorModel/Resources/Images/V6X.png"),
        Text(origin = {0, -72}, extent = {{-85, 15}, {85, -15}}, textString = "V6X / PX6C", textColor = {100, 70, 20})}));
  end V6XFlightControllerInterfaceBlock;

  block ORINNXMissionComputerInterfaceBlock
    "Graphical ORIN NX mission computer: trajectory/perception/state to control references"
    Modelica.Blocks.Interfaces.RealInput mission_position[3]
      annotation (Placement(transformation(origin = {-110, 60}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput aircraft_position[3]
      annotation (Placement(transformation(origin = {-110, 15}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput lidar_position[3]
      annotation (Placement(transformation(origin = {-110, -30}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput obstacle_margin
      annotation (Placement(transformation(origin = {-110, -70}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput reference_position[3]
      annotation (Placement(transformation(origin = {110, 50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput yaw_reference
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput z_reference_rate
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-10, -10}, {10, 10}})));
  equation
    reference_position = mission_position;
    yaw_reference = 0;
    z_reference_rate = 0;
    health = if obstacle_margin >= 0 then 1 else 0;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 15}, extent = {{-58, -42}, {58, 42}}, fileName = "modelica://QuadrotorModel/Resources/Images/ORIN_NX.jpg"),
        Text(origin = {0, -72}, extent = {{-80, 15}, {80, -15}}, textString = "ORIN NX", textColor = {80, 80, 80})}));
  end ORINNXMissionComputerInterfaceBlock;

  QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1))
    annotation (Placement(transformation(origin = {-350, 170}, extent = {{-18, -18}, {18, 18}})));
  QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1
    annotation (Placement(transformation(origin = {235, 0}, extent = {{-36, -36}, {36, 36}})));
  QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)))
    annotation (Placement(transformation(origin = {105, 135}, extent = {{-18, -18}, {18, 18}})));
  QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)))
    annotation (Placement(transformation(origin = {105, 45}, extent = {{-18, -18}, {18, 18}})));
  QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)))
    annotation (Placement(transformation(origin = {105, -45}, extent = {{-18, -18}, {18, 18}})));
  QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)))
    annotation (Placement(transformation(origin = {105, -135}, extent = {{-18, -18}, {18, 18}})));
  QuadrotorModel.Sensors.Sensors sensors1_1
    annotation (Placement(transformation(origin = {235, -125}, extent = {{-24, -24}, {24, 24}})));
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4]
    annotation (Placement(transformation(origin = {170, -205}, extent = {{-12, -12}, {12, 12}})));
  Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {-90, 160}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {-90, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {-90, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {-90, -110}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor1_hover_sum
    annotation (Placement(transformation(origin = {35, 135}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor2_hover_sum
    annotation (Placement(transformation(origin = {35, 45}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor3_hover_sum
    annotation (Placement(transformation(origin = {35, -45}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add motor4_hover_sum
    annotation (Placement(transformation(origin = {35, -135}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale)
    annotation (Placement(transformation(origin = {-35, 130}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale)
    annotation (Placement(transformation(origin = {-35, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale)
    annotation (Placement(transformation(origin = {-35, -50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale)
    annotation (Placement(transformation(origin = {-35, -140}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Feedback x_error
    annotation (Placement(transformation(origin = {-250, 175}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Feedback y_error
    annotation (Placement(transformation(origin = {-250, 125}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Feedback z_error
    annotation (Placement(transformation(origin = {-250, 75}, extent = {{-10, -10}, {10, 10}})));

  AWFF_FullControllerFlatGraphical_Sysblock controller3_2
    annotation (Placement(transformation(origin = {-80, 20}, extent = {{-32, -48}, {32, 48}})));
  GPSInterfaceBlock gps_receiver
    annotation (Placement(transformation(origin = {-285, -65}, extent = {{-28, -28}, {28, 28}})));
  Mid360InterfaceBlock mid360_lidar
    annotation (Placement(transformation(origin = {-285, -150}, extent = {{-28, -28}, {28, 28}})));
  V6XFlightControllerInterfaceBlock v6x_flight_controller
    annotation (Placement(transformation(origin = {-185, -55}, extent = {{-34, -34}, {34, 34}})));
  ORINNXMissionComputerInterfaceBlock orin_nx_computer
    annotation (Placement(transformation(origin = {-285, 95}, extent = {{-34, -34}, {34, 34}})));

equation
  connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a)
    annotation (Line(origin = {170, 105}, points = {{-47, 30}, {20, 30}, {20, -82}, {47, -82}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1)
    annotation (Line(origin = {170, 40}, points = {{-47, 5}, {18, 5}, {18, -6}, {47, -6}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2)
    annotation (Line(origin = {170, -40}, points = {{-47, -5}, {18, -5}, {18, 6}, {47, 6}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3)
    annotation (Line(origin = {170, -105}, points = {{-47, -30}, {20, -30}, {20, 82}, {47, 82}}, color = {95, 95, 95}, thickness = 0.5));
  connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a)
    annotation (Line(origin = {235, -70}, points = {{0, -34}, {0, -31}}, color = {95, 95, 95}, thickness = 0.5));

  connect(climbePath.position_command[1], orin_nx_computer.mission_position[1])
    annotation (Line(origin = {-330, 150}, points = {{-2, 20}, {8, 20}, {8, -35}, {7, -35}}, color = {0, 0, 127}));
  connect(climbePath.position_command[2], orin_nx_computer.mission_position[2])
    annotation (Line(origin = {-330, 142}, points = {{-2, 28}, {16, 28}, {16, -27}, {7, -27}}, color = {0, 0, 127}));
  connect(climbePath.position_command[3], orin_nx_computer.mission_position[3])
    annotation (Line(origin = {-330, 134}, points = {{-2, 36}, {24, 36}, {24, -19}, {7, -19}}, color = {0, 0, 127}));

  connect(sensors1_1.PosMea[1], gps_receiver.position_raw[1])
    annotation (Line(origin = {-35, -95}, points = {{246, -30}, {-285, -30}, {-285, 36}, {-278, 36}}, color = {0, 0, 127}));
  connect(sensors1_1.PosMea[2], gps_receiver.position_raw[2])
    annotation (Line(origin = {-35, -102}, points = {{246, -23}, {-277, -23}, {-277, 43}, {-278, 43}}, color = {0, 0, 127}));
  connect(sensors1_1.PosMea[3], gps_receiver.position_raw[3])
    annotation (Line(origin = {-35, -109}, points = {{246, -16}, {-269, -16}, {-269, 50}, {-278, 50}}, color = {0, 0, 127}));
  connect(gps_receiver.position_est[1], v6x_flight_controller.gps_position[1])
    annotation (Line(origin = {-235, -28}, points = {{-19, -31}, {16, -31}, {16, 1}, {13, 1}}, color = {0, 0, 127}));
  connect(gps_receiver.position_est[2], v6x_flight_controller.gps_position[2])
    annotation (Line(origin = {-235, -35}, points = {{-19, -24}, {24, -24}, {24, 8}, {13, 8}}, color = {0, 0, 127}));
  connect(gps_receiver.position_est[3], v6x_flight_controller.gps_position[3])
    annotation (Line(origin = {-235, -42}, points = {{-19, -17}, {32, -17}, {32, 15}, {13, 15}}, color = {0, 0, 127}));

  connect(gps_receiver.position_est[1], mid360_lidar.position_est[1])
    annotation (Line(origin = {-270, -112}, points = {{16, 53}, {16, -32}, {-47, -32}}, color = {0, 0, 127}));
  connect(gps_receiver.position_est[2], mid360_lidar.position_est[2])
    annotation (Line(origin = {-262, -112}, points = {{8, 53}, {8, -32}, {-55, -32}}, color = {0, 0, 127}));
  connect(gps_receiver.position_est[3], mid360_lidar.position_est[3])
    annotation (Line(origin = {-254, -112}, points = {{0, 53}, {0, -32}, {-63, -32}}, color = {0, 0, 127}));

  connect(mid360_lidar.local_position[1], orin_nx_computer.lidar_position[1])
    annotation (Line(origin = {-230, -58}, points = {{-24, -86}, {17, -86}, {17, 143}, {-18, 143}}, color = {0, 0, 127}));
  connect(mid360_lidar.local_position[2], orin_nx_computer.lidar_position[2])
    annotation (Line(origin = {-222, -58}, points = {{-32, -86}, {9, -86}, {9, 143}, {-26, 143}}, color = {0, 0, 127}));
  connect(mid360_lidar.local_position[3], orin_nx_computer.lidar_position[3])
    annotation (Line(origin = {-214, -58}, points = {{-40, -86}, {1, -86}, {1, 143}, {-34, 143}}, color = {0, 0, 127}));
  connect(mid360_lidar.obstacle_margin, orin_nx_computer.obstacle_margin)
    annotation (Line(origin = {-230, -55}, points = {{-24, -102}, {25, -102}, {25, 126}, {-18, 126}}, color = {0, 0, 127}));

  connect(v6x_flight_controller.position_est[1], orin_nx_computer.aircraft_position[1])
    annotation (Line(origin = {-230, 15}, points = {{82, -51}, {96, -51}, {96, 85}, {-18, 85}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.position_est[2], orin_nx_computer.aircraft_position[2])
    annotation (Line(origin = {-222, 15}, points = {{74, -51}, {88, -51}, {88, 85}, {-26, 85}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.position_est[3], orin_nx_computer.aircraft_position[3])
    annotation (Line(origin = {-214, 15}, points = {{66, -51}, {80, -51}, {80, 85}, {-34, 85}}, color = {0, 0, 127}));

  connect(orin_nx_computer.reference_position[1], x_error.u1)
    annotation (Line(origin = {-248, 148}, points = {{0, -36}, {0, 27}, {-14, 27}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.position_est[1], x_error.u2)
    annotation (Line(origin = {-200, 55}, points = {{52, -91}, {70, -91}, {70, 120}, {-50, 120}}, color = {0, 0, 127}));
  connect(orin_nx_computer.reference_position[2], y_error.u1)
    annotation (Line(origin = {-248, 120}, points = {{0, -8}, {0, 5}, {-14, 5}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.position_est[2], y_error.u2)
    annotation (Line(origin = {-208, 40}, points = {{60, -76}, {78, -76}, {78, 85}, {-42, 85}}, color = {0, 0, 127}));
  connect(orin_nx_computer.reference_position[3], z_error.u1)
    annotation (Line(origin = {-248, 92}, points = {{0, 20}, {0, -17}, {-14, -17}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.position_est[3], z_error.u2)
    annotation (Line(origin = {-216, 25}, points = {{68, -61}, {86, -61}, {86, 50}, {-34, 50}}, color = {0, 0, 127}));

  connect(x_error.y, controller3_2.x_error)
    annotation (Line(origin = {-165, 140}, points = {{-74, 35}, {53, 35}, {53, -88}}, color = {0, 0, 127}));
  connect(y_error.y, controller3_2.y_error)
    annotation (Line(origin = {-165, 110}, points = {{-74, 15}, {53, 15}, {53, -70}}, color = {0, 0, 127}));
  connect(z_error.y, controller3_2.z_error)
    annotation (Line(origin = {-165, 80}, points = {{-74, -5}, {53, -5}, {53, -52}}, color = {0, 0, 127}));
  connect(orin_nx_computer.z_reference_rate, controller3_2.z_ref_rate)
    annotation (Line(origin = {-155, 35}, points = {{-93, 45}, {43, 45}, {43, -19}}, color = {0, 0, 127}));
  connect(sensors1_1.AngleMea[1], v6x_flight_controller.attitude_raw[1])
    annotation (Line(origin = {-15, -82}, points = {{226, -43}, {-232, -43}, {-232, 30}}, color = {0, 0, 127}));
  connect(sensors1_1.AngleMea[2], v6x_flight_controller.attitude_raw[2])
    annotation (Line(origin = {-23, -86}, points = {{234, -39}, {-224, -39}, {-224, 34}}, color = {0, 0, 127}));
  connect(sensors1_1.AngleMea[3], v6x_flight_controller.attitude_raw[3])
    annotation (Line(origin = {-31, -90}, points = {{242, -35}, {-216, -35}, {-216, 38}}, color = {0, 0, 127}));
  connect(speedSensor[1].w, v6x_flight_controller.motor_speed_raw[1])
    annotation (Line(origin = {0, -180}, points = {{182, -25}, {-245, -25}, {-245, 109}}, color = {0, 0, 127}));
  connect(speedSensor[2].w, v6x_flight_controller.motor_speed_raw[2])
    annotation (Line(origin = {-8, -186}, points = {{190, -19}, {-237, -19}, {-237, 115}}, color = {0, 0, 127}));
  connect(speedSensor[3].w, v6x_flight_controller.motor_speed_raw[3])
    annotation (Line(origin = {-16, -192}, points = {{198, -13}, {-229, -13}, {-229, 121}}, color = {0, 0, 127}));
  connect(speedSensor[4].w, v6x_flight_controller.motor_speed_raw[4])
    annotation (Line(origin = {-24, -198}, points = {{206, -7}, {-221, -7}, {-221, 127}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.attitude_est[1], controller3_2.roll_mea)
    annotation (Line(origin = {-130, -20}, points = {{-18, -32}, {18, -32}, {18, 28}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.attitude_est[2], controller3_2.pitch_mea)
    annotation (Line(origin = {-130, -34}, points = {{-18, -18}, {18, -18}, {18, 14}}, color = {0, 0, 127}));
  connect(v6x_flight_controller.attitude_est[3], controller3_2.yaw_mea)
    annotation (Line(origin = {-130, -48}, points = {{-18, -4}, {18, -4}, {18, 0}}, color = {0, 0, 127}));
  connect(orin_nx_computer.yaw_reference, controller3_2.yaw_ref)
    annotation (Line(origin = {-155, -30}, points = {{-93, 30}, {43, 30}, {43, -30}}, color = {0, 0, 127}));

  connect(controller3_2.y, motor1_delta_scale.u)
    annotation (Line(origin = {-65, 75}, points = {{17, -19}, {15, -19}, {15, 55}}, color = {0, 0, 127}));
  connect(motor1_delta_scale.y, motor1_hover_sum.u1)
    annotation (Line(origin = {0, 132}, points = {{-24, -2}, {23, -2}, {23, 9}}, color = {0, 0, 127}));
  connect(hover_u1.y, motor1_hover_sum.u2)
    annotation (Line(origin = {-28, 150}, points = {{-51, 10}, {51, 10}, {51, -9}}, color = {0, 0, 127}));
  connect(motor1_hover_sum.y, actuator1_1.u)
    annotation (Line(origin = {70, 135}, points = {{-24, 0}, {17, 0}}, color = {0, 0, 127}));
  connect(controller3_2.y1, motor2_delta_scale.u)
    annotation (Line(origin = {-95, 30}, points = {{-28, -2}, {45, -2}, {45, 10}}, color = {0, 0, 127}));
  connect(motor2_delta_scale.y, motor2_hover_sum.u1)
    annotation (Line(origin = {0, 42}, points = {{-24, -2}, {23, -2}, {23, 9}}, color = {0, 0, 127}));
  connect(hover_u2.y, motor2_hover_sum.u2)
    annotation (Line(origin = {-28, 60}, points = {{-51, 10}, {51, 10}, {51, -9}}, color = {0, 0, 127}));
  connect(motor2_hover_sum.y, actuator1_2.u)
    annotation (Line(origin = {70, 45}, points = {{-24, 0}, {17, 0}}, color = {0, 0, 127}));
  connect(controller3_2.y2, motor3_delta_scale.u)
    annotation (Line(origin = {-95, -30}, points = {{-28, 2}, {45, 2}, {45, -20}}, color = {0, 0, 127}));
  connect(motor3_delta_scale.y, motor3_hover_sum.u1)
    annotation (Line(origin = {0, -48}, points = {{-24, -2}, {23, -2}, {23, 9}}, color = {0, 0, 127}));
  connect(hover_u3.y, motor3_hover_sum.u2)
    annotation (Line(origin = {-28, -30}, points = {{-51, 10}, {51, 10}, {51, -9}}, color = {0, 0, 127}));
  connect(motor3_hover_sum.y, actuator1_3.u)
    annotation (Line(origin = {70, -45}, points = {{-24, 0}, {17, 0}}, color = {0, 0, 127}));
  connect(controller3_2.y3, motor4_delta_scale.u)
    annotation (Line(origin = {-95, -75}, points = {{-28, 19}, {45, 19}, {45, -65}}, color = {0, 0, 127}));
  connect(motor4_delta_scale.y, motor4_hover_sum.u1)
    annotation (Line(origin = {0, -138}, points = {{-24, -2}, {23, -2}, {23, 9}}, color = {0, 0, 127}));
  connect(hover_u4.y, motor4_hover_sum.u2)
    annotation (Line(origin = {-28, -120}, points = {{-51, 10}, {51, 10}, {51, -9}}, color = {0, 0, 127}));
  connect(motor4_hover_sum.y, actuator1_4.u)
    annotation (Line(origin = {70, -135}, points = {{-24, 0}, {17, 0}}, color = {0, 0, 127}));

  connect(actuator1_1.flange_a, speedSensor[1].flange)
    annotation (Line(origin = {140, -35}, points = {{-17, 170}, {30, 170}, {30, -170}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_2.flange_a, speedSensor[2].flange)
    annotation (Line(origin = {130, -80}, points = {{-7, 125}, {40, 125}, {40, -125}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_3.flange_a, speedSensor[3].flange)
    annotation (Line(origin = {120, -125}, points = {{3, 80}, {50, 80}, {50, -80}}, color = {95, 95, 95}, thickness = 0.5));
  connect(actuator1_4.flange_a, speedSensor[4].flange)
    annotation (Line(origin = {110, -170}, points = {{13, 35}, {60, 35}, {60, -35}}, color = {95, 95, 95}, thickness = 0.5));

  annotation(
    Diagram(coordinateSystem(extent = {{-380, -300}, {500, 240}}, grid = {5, 5}),
      graphics = {
        Rectangle(origin = {-300, 95}, extent = {{-70, 125}, {70, -270}}, lineColor = {0, 0, 127}, pattern = LinePattern.Dash),
        Text(origin = {-300, 220}, extent = {{-70, 15}, {70, -15}}, textString = "mission, perception and state data", textColor = {0, 0, 127}),
        Rectangle(origin = {-80, 20}, extent = {{-55, 105}, {55, -105}}, lineColor = {0, 127, 0}, pattern = LinePattern.Dash),
        Text(origin = {-80, 130}, extent = {{-60, 15}, {60, -15}}, textString = "graphical AWFF controller", textColor = {0, 127, 0}),
        Rectangle(origin = {15, 5}, extent = {{-125, 185}, {125, -165}}, lineColor = {127, 0, 127}, pattern = LinePattern.Dash),
        Text(origin = {15, 200}, extent = {{-90, 15}, {90, -15}}, textString = "motor command scaling and actuators", textColor = {127, 0, 127}),
        Rectangle(origin = {235, -40}, extent = {{-55, 100}, {55, -120}}, lineColor = {160, 80, 0}, pattern = LinePattern.Dash),
        Text(origin = {235, 75}, extent = {{-50, 15}, {50, -15}}, textString = "Sunray150 plant and sensors", textColor = {160, 80, 0})}),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemGraphical_Sysblock;

end QuadrotorExperiments;
