within MoSimQuadrotorModel.Control.InnerLoop;
model AttitudeTrackingCore
  "Inner-loop attitude tracking controller extracted from OfficialPid - tracks desired roll/pitch/yaw and converts to rotor amplitude commands"

  annotation(
    Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 100, 150}, fillColor = {255, 240, 245}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 30}, extent = {{-90, 18}, {90, -18}}, textString = "Attitude", textColor = {0, 100, 150}),
      Text(origin = {0, 0}, extent = {{-90, 18}, {90, -18}}, textString = "Tracking", textColor = {0, 100, 150}),
      Text(origin = {0, -30}, extent = {{-90, 14}, {90, -14}}, textString = "INNER LOOP", textColor = {0, 100, 150})}),
    experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01, StartTime = 0, StopTime = 0.02)
  );

  // Input ports
  Modelica.Blocks.Interfaces.RealInput desired_roll_rad
    annotation(Placement(transformation(origin = {-110, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput desired_pitch_rad
    annotation(Placement(transformation(origin = {-110, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput desired_yaw_rad
    annotation(Placement(transformation(origin = {-110, 30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput roll_mea
    annotation(Placement(transformation(origin = {-110, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput pitch_mea
    annotation(Placement(transformation(origin = {-110, -10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_mea
    annotation(Placement(transformation(origin = {-110, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput thrust_baseline
    annotation(Placement(transformation(origin = {-110, -50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput roll_rate_mea
    annotation(Placement(transformation(origin = {-110, -70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput pitch_rate_mea
    annotation(Placement(transformation(origin = {-110, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_rate_mea
    annotation(Placement(transformation(origin = {-110, -110}, extent = {{-10, -10}, {10, 10}})));

  // Output ports
  Modelica.Blocks.Interfaces.RealOutput amplitude_1
    annotation(Placement(transformation(origin = {110, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_2
    annotation(Placement(transformation(origin = {110, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_3
    annotation(Placement(transformation(origin = {110, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_4
    annotation(Placement(transformation(origin = {110, -60}, extent = {{-10, -10}, {10, 10}})));

  // Pitch channel
  Modelica.Blocks.Math.Add pitch_error(k1 = 1, k2 = -1)
    annotation(Placement(transformation(origin = {-80, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain pitch_p(k = 14.142)
    annotation(Placement(transformation(origin = {-50, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain pitch_d(k = -1.414)
    annotation(Placement(transformation(origin = {-50, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add pitch_pd(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {-20, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Nonlinear.Limiter pitch_limit(uMax = 7.0, uMin = -7.0)
    annotation(Placement(transformation(origin = {10, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain pitch_mix(k = 0.707)
    annotation(Placement(transformation(origin = {40, 50}, extent = {{-10, -10}, {10, 10}})));

  // Roll channel
  Modelica.Blocks.Math.Gain roll_mea_sign(k = -1)
    annotation(Placement(transformation(origin = {-90, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add roll_error(k1 = 1, k2 = -1)
    annotation(Placement(transformation(origin = {-80, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain roll_p(k = 14.142)
    annotation(Placement(transformation(origin = {-50, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain roll_d(k = -1.414)
    annotation(Placement(transformation(origin = {-50, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add roll_pd(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {-20, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Nonlinear.Limiter roll_limit(uMax = 7.0, uMin = -7.0)
    annotation(Placement(transformation(origin = {10, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain roll_mix(k = 0.707)
    annotation(Placement(transformation(origin = {40, 10}, extent = {{-10, -10}, {10, 10}})));

  // Yaw channel
  Modelica.Blocks.Math.Add yaw_error(k1 = 1, k2 = -1)
    annotation(Placement(transformation(origin = {-80, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain yaw_p(k = 5.0)
    annotation(Placement(transformation(origin = {-50, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Nonlinear.Limiter yaw_limit(uMax = 7.0, uMin = -7.0)
    annotation(Placement(transformation(origin = {-20, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain yaw_mix(k = 0.707)
    annotation(Placement(transformation(origin = {10, -30}, extent = {{-10, -10}, {10, 10}})));

  // Mixing matrix
  Modelica.Blocks.Math.Gain mixer_1_yaw(k = -1)
    annotation(Placement(transformation(origin = {50, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_1_pitch(k = -1)
    annotation(Placement(transformation(origin = {50, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_1_roll(k = 1)
    annotation(Placement(transformation(origin = {50, 40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add3 mixer_1_sum
    annotation(Placement(transformation(origin = {70, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add rotor_1_sum(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {90, 60}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Gain mixer_2_yaw(k = 1)
    annotation(Placement(transformation(origin = {50, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_2_pitch(k = -1)
    annotation(Placement(transformation(origin = {50, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_2_roll(k = -1)
    annotation(Placement(transformation(origin = {50, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add3 mixer_2_sum
    annotation(Placement(transformation(origin = {70, 10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add rotor_2_sum(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {90, 20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Gain mixer_3_yaw(k = -1)
    annotation(Placement(transformation(origin = {50, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_3_pitch(k = 1)
    annotation(Placement(transformation(origin = {50, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_3_roll(k = -1)
    annotation(Placement(transformation(origin = {50, -40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add3 mixer_3_sum
    annotation(Placement(transformation(origin = {70, -30}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add rotor_3_sum(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {90, -20}, extent = {{-10, -10}, {10, 10}})));

  Modelica.Blocks.Math.Gain mixer_4_yaw(k = 1)
    annotation(Placement(transformation(origin = {50, -60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_4_pitch(k = 1)
    annotation(Placement(transformation(origin = {50, -70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain mixer_4_roll(k = 1)
    annotation(Placement(transformation(origin = {50, -80}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add3 mixer_4_sum
    annotation(Placement(transformation(origin = {70, -70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add rotor_4_sum(k1 = 1, k2 = 1)
    annotation(Placement(transformation(origin = {90, -60}, extent = {{-10, -10}, {10, 10}})));

equation
  // Pitch channel
  connect(desired_pitch_rad, pitch_error.u1);
  connect(pitch_mea, pitch_error.u2);
  connect(pitch_error.y, pitch_p.u);
  connect(pitch_rate_mea, pitch_d.u);
  connect(pitch_p.y, pitch_pd.u1);
  connect(pitch_d.y, pitch_pd.u2);
  connect(pitch_pd.y, pitch_limit.u);
  connect(pitch_limit.y, pitch_mix.u);

  // Roll channel
  connect(roll_mea, roll_mea_sign.u);
  connect(desired_roll_rad, roll_error.u1);
  connect(roll_mea_sign.y, roll_error.u2);
  connect(roll_error.y, roll_p.u);
  connect(roll_rate_mea, roll_d.u);
  connect(roll_p.y, roll_pd.u1);
  connect(roll_d.y, roll_pd.u2);
  connect(roll_pd.y, roll_limit.u);
  connect(roll_limit.y, roll_mix.u);

  // Yaw channel
  connect(desired_yaw_rad, yaw_error.u1);
  connect(yaw_mea, yaw_error.u2);
  connect(yaw_error.y, yaw_p.u);
  connect(yaw_p.y, yaw_limit.u);
  connect(yaw_limit.y, yaw_mix.u);

  // Rotor 1
  connect(yaw_mix.y, mixer_1_yaw.u);
  connect(pitch_mix.y, mixer_1_pitch.u);
  connect(roll_mix.y, mixer_1_roll.u);
  connect(mixer_1_yaw.y, mixer_1_sum.u1);
  connect(mixer_1_pitch.y, mixer_1_sum.u2);
  connect(mixer_1_roll.y, mixer_1_sum.u3);
  connect(mixer_1_sum.y, rotor_1_sum.u1);
  connect(thrust_baseline, rotor_1_sum.u2);
  connect(rotor_1_sum.y, amplitude_1);

  // Rotor 2
  connect(yaw_mix.y, mixer_2_yaw.u);
  connect(pitch_mix.y, mixer_2_pitch.u);
  connect(roll_mix.y, mixer_2_roll.u);
  connect(mixer_2_yaw.y, mixer_2_sum.u1);
  connect(mixer_2_pitch.y, mixer_2_sum.u2);
  connect(mixer_2_roll.y, mixer_2_sum.u3);
  connect(mixer_2_sum.y, rotor_2_sum.u1);
  connect(thrust_baseline, rotor_2_sum.u2);
  connect(rotor_2_sum.y, amplitude_2);

  // Rotor 3
  connect(yaw_mix.y, mixer_3_yaw.u);
  connect(pitch_mix.y, mixer_3_pitch.u);
  connect(roll_mix.y, mixer_3_roll.u);
  connect(mixer_3_yaw.y, mixer_3_sum.u1);
  connect(mixer_3_pitch.y, mixer_3_sum.u2);
  connect(mixer_3_roll.y, mixer_3_sum.u3);
  connect(mixer_3_sum.y, rotor_3_sum.u1);
  connect(thrust_baseline, rotor_3_sum.u2);
  connect(rotor_3_sum.y, amplitude_3);

  // Rotor 4
  connect(yaw_mix.y, mixer_4_yaw.u);
  connect(pitch_mix.y, mixer_4_pitch.u);
  connect(roll_mix.y, mixer_4_roll.u);
  connect(mixer_4_yaw.y, mixer_4_sum.u1);
  connect(mixer_4_pitch.y, mixer_4_sum.u2);
  connect(mixer_4_roll.y, mixer_4_sum.u3);
  connect(mixer_4_sum.y, rotor_4_sum.u1);
  connect(thrust_baseline, rotor_4_sum.u2);
  connect(rotor_4_sum.y, amplitude_4);

  annotation(
    Diagram(coordinateSystem(extent = {{-120, -100}, {120, 80}})));
end AttitudeTrackingCore;
