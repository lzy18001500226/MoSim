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
    QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1;
    QuadrotorModel.Electricals.Actuator actuator1_2;
    QuadrotorModel.Electricals.Actuator actuator1_3;
    QuadrotorModel.Electricals.Actuator actuator1_4;
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(actuator1_1.u, controller3_2.y);
    connect(actuator1_2.u, controller3_2.y1);
    connect(actuator1_3.u, controller3_2.y2);
    connect(actuator1_4.u, controller3_2.y3);
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
    QuadrotorModel.PathPlanning.CirclePath climbePath(ramp(height = 20), sine(f = 0.05), cosine(f = 0.05, startTime = 10, phase = 0));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1;
    QuadrotorModel.Electricals.Actuator actuator1_2;
    QuadrotorModel.Electricals.Actuator actuator1_3;
    QuadrotorModel.Electricals.Actuator actuator1_4;
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(actuator1_1.u, controller3_2.y);
    connect(actuator1_2.u, controller3_2.y1);
    connect(actuator1_3.u, controller3_2.y2);
    connect(actuator1_4.u, controller3_2.y3);
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
    QuadrotorModel.PathPlanning.EightPath climbePath;
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1;
    QuadrotorModel.Electricals.Actuator actuator1_2;
    QuadrotorModel.Electricals.Actuator actuator1_3;
    QuadrotorModel.Electricals.Actuator actuator1_4;
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(actuator1_1.u, controller3_2.y);
    connect(actuator1_2.u, controller3_2.y1);
    connect(actuator1_3.u, controller3_2.y2);
    connect(actuator1_4.u, controller3_2.y3);
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

  model Example3AntiWindupFeedforwardPID
    "Example3 with project-owned anti-windup and reference-feedforward controller"
    extends Example3ProjectControllerBase;
  end Example3AntiWindupFeedforwardPID;

  model Example1Mass20AntiWindupFeedforwardPID
    "Example1 AWFF PID with +20% central body mass perturbation"
    extends Example1ProjectControllerBase(
      quadChassisTest17_1.body(m = 0.191405));
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
      quadChassisTest17_1.gain2(k = 0.0017));
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
      quadChassisTest17_1.body(m = 0.191405));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20PID;

  model Example1Mass20ImprovedPID
    "Example1 improved PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 0.191405),
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
      quadChassisTest17_1.body(m = 0.191405),
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
      quadChassisTest17_1.gain2(k = 0.0017));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15PID;

  model Example1Rotor1Loss15ImprovedPID
    "Example1 improved PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0017),
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
      quadChassisTest17_1.gain2(k = 0.0017),
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
end QuadrotorExperiments;
