within;
package QuadrotorExperiments
  "Project-local experiment models for official quadrotor comparisons"

  extends Modelica.Icons.Package;
  annotation(uses(
    Modelica(version = "4.0.0.TY.1"),
    QuadrotorModel));

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
end QuadrotorExperiments;
