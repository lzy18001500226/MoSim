within MoSimQuadrotorModel.Control.InnerLoop;
model AttitudeTrackingCore
  "Inner-loop attitude tracking controller extracted from OfficialPid - tracks desired roll/pitch/yaw and converts to rotor amplitude commands"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;

  annotation(
    __MWORKS(
      SECInstance = true,
      version = "26.3.0",
      PortArrangement(
        Left(desired_roll_rad, desired_pitch_rad, desired_yaw_rad, roll_mea, pitch_mea, yaw_mea, thrust_baseline),
        Right(amplitude_1, amplitude_2, amplitude_3, amplitude_4)
      ),
      modelType = Control,
      BlockSystem(
        blockKind = BlockKind.userModel,
        SampleTime(auto=true, group = "")=0.01,
        OutputInterval=0.01
      ),
      SysblockVersion = "1.0"
    ),
    Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
      Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 100, 150}, fillColor = {255, 240, 245}, fillPattern = FillPattern.Solid),
      Text(origin = {0, 30}, extent = {{-90, 18}, {90, -18}}, textString = "Attitude", textColor = {0, 100, 150}),
      Text(origin = {0, 0}, extent = {{-90, 18}, {90, -18}}, textString = "Tracking", textColor = {0, 100, 150}),
      Text(origin = {0, -30}, extent = {{-90, 14}, {90, -14}}, textString = "INNER LOOP", textColor = {0, 100, 150})}),
    experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01, StartTime = 0, StopTime = 0.02)
  );

  // Input ports
  SysplorerEmbeddedCoder.Port.Inport desired_roll_rad
    annotation(Placement(transformation(origin = {-560, 280}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport desired_pitch_rad
    annotation(Placement(transformation(origin = {-560, 220}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport desired_yaw_rad
    annotation(Placement(transformation(origin = {-560, 160}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea
    annotation(Placement(transformation(origin = {-560, 80}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea
    annotation(Placement(transformation(origin = {-560, 20}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea
    annotation(Placement(transformation(origin = {-560, -40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport thrust_baseline
    annotation(Placement(transformation(origin = {-560, -120}, extent = {{-17, -13}, {17, 13}})));

  // Output ports
  SysplorerEmbeddedCoder.Port.Outport amplitude_1
    annotation(Placement(transformation(origin = {430, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_2
    annotation(Placement(transformation(origin = {430, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_3
    annotation(Placement(transformation(origin = {430, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport amplitude_4
    annotation(Placement(transformation(origin = {430, -180}, extent = {{-17, -13}, {17, 13}})));

  // Pitch channel
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(inputs = "+-")
    annotation(Placement(transformation(origin = {-480, 220}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_p(k = 14.142)
    annotation(Placement(transformation(origin = {-400, 255}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_input(k = 1.0)
    annotation(Placement(transformation(origin = {-480, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference pitch_derivative_difference
    annotation(Placement(transformation(origin = {-420, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_slope(k = 100.0)
    annotation(Placement(transformation(origin = {-360, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_filtered_increment(k = 0.631839272714496)
    annotation(Placement(transformation(origin = {-300, 155}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_derivative_previous_state(initCond = 0.0)
    annotation(Placement(transformation(origin = {-300, 215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_state_decay(k = 0.368160727285504)
    annotation(Placement(transformation(origin = {-240, 215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_derivative_state_sum(inputs = "++")
    annotation(Placement(transformation(origin = {-180, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative(k = 1.0)
    annotation(Placement(transformation(origin = {-120, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_d(k = 1.414)
    annotation(Placement(transformation(origin = {-320, 185}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_pd(inputs = "++")
    annotation(Placement(transformation(origin = {-240, 220}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(upLimit = 7.0, lowLimit = -7.0)
    annotation(Placement(transformation(origin = {-160, 220}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix(k = 0.707)
    annotation(Placement(transformation(origin = {-80, 220}, extent = {{-17, -13}, {17, 13}})));

  // Roll channel
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mea_sign(k = -1)
    annotation(Placement(transformation(origin = {-500, 80}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(inputs = "+-")
    annotation(Placement(transformation(origin = {-480, 80}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_p(k = 14.142)
    annotation(Placement(transformation(origin = {-400, 115}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_input(k = 1.0)
    annotation(Placement(transformation(origin = {-480, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference roll_derivative_difference
    annotation(Placement(transformation(origin = {-420, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_slope(k = 100.0)
    annotation(Placement(transformation(origin = {-360, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_filtered_increment(k = 0.631839272714496)
    annotation(Placement(transformation(origin = {-300, 15}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_derivative_previous_state(initCond = 0.0)
    annotation(Placement(transformation(origin = {-300, 75}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_state_decay(k = 0.368160727285504)
    annotation(Placement(transformation(origin = {-240, 75}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_derivative_state_sum(inputs = "++")
    annotation(Placement(transformation(origin = {-180, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative(k = 1.0)
    annotation(Placement(transformation(origin = {-120, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_d(k = 1.414)
    annotation(Placement(transformation(origin = {-320, 45}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_pd(inputs = "++")
    annotation(Placement(transformation(origin = {-240, 80}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(upLimit = 7.0, lowLimit = -7.0)
    annotation(Placement(transformation(origin = {-160, 80}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix(k = 0.707)
    annotation(Placement(transformation(origin = {-80, 80}, extent = {{-17, -13}, {17, 13}})));

  // Yaw channel (P-only)
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(inputs = "+-")
    annotation(Placement(transformation(origin = {-480, -40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_p(k = 5.0)
    annotation(Placement(transformation(origin = {-400, -40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_limit(upLimit = 7.0, lowLimit = -7.0)
    annotation(Placement(transformation(origin = {-160, -40}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix(k = 0.707)
    annotation(Placement(transformation(origin = {-80, -40}, extent = {{-17, -13}, {17, 13}})));

  // Mixing matrix - Rotor 1
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_yaw_gain(k = -1)
    annotation(Placement(transformation(origin = {55, 215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_pitch_gain(k = -1)
    annotation(Placement(transformation(origin = {55, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_roll_gain(k = 1)
    annotation(Placement(transformation(origin = {55, 145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1_first(inputs = "++")
    annotation(Placement(transformation(origin = {160, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1(inputs = "++")
    annotation(Placement(transformation(origin = {260, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_1_sum(inputs = "++")
    annotation(Placement(transformation(origin = {340, 180}, extent = {{-17, -13}, {17, 13}})));

  // Mixing matrix - Rotor 2
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_yaw_gain(k = 1)
    annotation(Placement(transformation(origin = {55, 95}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_pitch_gain(k = -1)
    annotation(Placement(transformation(origin = {55, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_roll_gain(k = -1)
    annotation(Placement(transformation(origin = {55, 25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2_first(inputs = "++")
    annotation(Placement(transformation(origin = {160, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2(inputs = "++")
    annotation(Placement(transformation(origin = {260, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_2_sum(inputs = "++")
    annotation(Placement(transformation(origin = {340, 60}, extent = {{-17, -13}, {17, 13}})));

  // Mixing matrix - Rotor 3
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_yaw_gain(k = -1)
    annotation(Placement(transformation(origin = {55, -25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_pitch_gain(k = 1)
    annotation(Placement(transformation(origin = {55, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_roll_gain(k = -1)
    annotation(Placement(transformation(origin = {55, -95}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3_first(inputs = "++")
    annotation(Placement(transformation(origin = {160, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3(inputs = "++")
    annotation(Placement(transformation(origin = {260, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_3_sum(inputs = "++")
    annotation(Placement(transformation(origin = {340, -60}, extent = {{-17, -13}, {17, 13}})));

  // Mixing matrix - Rotor 4
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_yaw_gain(k = 1)
    annotation(Placement(transformation(origin = {55, -145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_pitch_gain(k = 1)
    annotation(Placement(transformation(origin = {55, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_roll_gain(k = 1)
    annotation(Placement(transformation(origin = {55, -215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4_first(inputs = "++")
    annotation(Placement(transformation(origin = {160, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4(inputs = "++")
    annotation(Placement(transformation(origin = {260, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_4_sum(inputs = "++")
    annotation(Placement(transformation(origin = {340, -180}, extent = {{-17, -13}, {17, 13}})));

  model ModelWorkspace
    annotation(__MWORKS(hide = true, BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  // Pitch channel connections
  connect(desired_pitch_rad, pitch_error.u1);
  connect(pitch_mea, pitch_error.u2);
  connect(pitch_error.y, pitch_p.u);
  connect(pitch_error.y, pitch_derivative_input.u);
  connect(pitch_derivative_input.y, pitch_derivative_difference.u);
  connect(pitch_derivative_difference.y, pitch_derivative_slope.u);
  connect(pitch_derivative_slope.y, pitch_derivative_filtered_increment.u);
  connect(pitch_derivative_filtered_increment.y, pitch_derivative_state_sum.u2);
  connect(pitch_derivative_previous_state.y, pitch_derivative_state_decay.u);
  connect(pitch_derivative_state_decay.y, pitch_derivative_state_sum.u1);
  connect(pitch_derivative_state_sum.y, pitch_derivative_previous_state.u1);
  connect(pitch_derivative_state_sum.y, pitch_derivative.u);
  connect(pitch_derivative.y, pitch_d.u);
  connect(pitch_p.y, pitch_pd.u1);
  connect(pitch_d.y, pitch_pd.u2);
  connect(pitch_pd.y, pitch_limit.u);
  connect(pitch_limit.y, pitch_mix.u);

  // Roll channel connections
  connect(roll_mea, roll_mea_sign.u);
  connect(desired_roll_rad, roll_error.u1);
  connect(roll_mea_sign.y, roll_error.u2);
  connect(roll_error.y, roll_p.u);
  connect(roll_error.y, roll_derivative_input.u);
  connect(roll_derivative_input.y, roll_derivative_difference.u);
  connect(roll_derivative_difference.y, roll_derivative_slope.u);
  connect(roll_derivative_slope.y, roll_derivative_filtered_increment.u);
  connect(roll_derivative_filtered_increment.y, roll_derivative_state_sum.u2);
  connect(roll_derivative_previous_state.y, roll_derivative_state_decay.u);
  connect(roll_derivative_state_decay.y, roll_derivative_state_sum.u1);
  connect(roll_derivative_state_sum.y, roll_derivative_previous_state.u1);
  connect(roll_derivative_state_sum.y, roll_derivative.u);
  connect(roll_derivative.y, roll_d.u);
  connect(roll_p.y, roll_pd.u1);
  connect(roll_d.y, roll_pd.u2);
  connect(roll_pd.y, roll_limit.u);
  connect(roll_limit.y, roll_mix.u);

  // Yaw channel connections
  connect(desired_yaw_rad, yaw_error.u1);
  connect(yaw_mea, yaw_error.u2);
  connect(yaw_error.y, yaw_p.u);
  connect(yaw_p.y, yaw_limit.u);
  connect(yaw_limit.y, yaw_mix.u);

  // Rotor 1 mixing
  connect(yaw_mix.y, mixer_1_yaw_gain.u);
  connect(pitch_mix.y, mixer_1_pitch_gain.u);
  connect(roll_mix.y, mixer_1_roll_gain.u);
  connect(mixer_1_yaw_gain.y, mixer_1_first.u1);
  connect(mixer_1_pitch_gain.y, mixer_1_first.u2);
  connect(mixer_1_first.y, mixer_1.u1);
  connect(mixer_1_roll_gain.y, mixer_1.u2);
  connect(mixer_1.y, rotor_1_sum.u1);
  connect(thrust_baseline, rotor_1_sum.u2);
  connect(rotor_1_sum.y, amplitude_1);

  // Rotor 2 mixing
  connect(yaw_mix.y, mixer_2_yaw_gain.u);
  connect(pitch_mix.y, mixer_2_pitch_gain.u);
  connect(roll_mix.y, mixer_2_roll_gain.u);
  connect(mixer_2_yaw_gain.y, mixer_2_first.u1);
  connect(mixer_2_pitch_gain.y, mixer_2_first.u2);
  connect(mixer_2_first.y, mixer_2.u1);
  connect(mixer_2_roll_gain.y, mixer_2.u2);
  connect(mixer_2.y, rotor_2_sum.u1);
  connect(thrust_baseline, rotor_2_sum.u2);
  connect(rotor_2_sum.y, amplitude_2);

  // Rotor 3 mixing
  connect(yaw_mix.y, mixer_3_yaw_gain.u);
  connect(pitch_mix.y, mixer_3_pitch_gain.u);
  connect(roll_mix.y, mixer_3_roll_gain.u);
  connect(mixer_3_yaw_gain.y, mixer_3_first.u1);
  connect(mixer_3_pitch_gain.y, mixer_3_first.u2);
  connect(mixer_3_first.y, mixer_3.u1);
  connect(mixer_3_roll_gain.y, mixer_3.u2);
  connect(mixer_3.y, rotor_3_sum.u1);
  connect(thrust_baseline, rotor_3_sum.u2);
  connect(rotor_3_sum.y, amplitude_3);

  // Rotor 4 mixing
  connect(yaw_mix.y, mixer_4_yaw_gain.u);
  connect(pitch_mix.y, mixer_4_pitch_gain.u);
  connect(roll_mix.y, mixer_4_roll_gain.u);
  connect(mixer_4_yaw_gain.y, mixer_4_first.u1);
  connect(mixer_4_pitch_gain.y, mixer_4_first.u2);
  connect(mixer_4_first.y, mixer_4.u1);
  connect(mixer_4_roll_gain.y, mixer_4.u2);
  connect(mixer_4.y, rotor_4_sum.u1);
  connect(thrust_baseline, rotor_4_sum.u2);
  connect(rotor_4_sum.y, amplitude_4);

  annotation(
    Diagram(coordinateSystem(extent = {{-600, -300}, {500, 350}})));
end AttitudeTrackingCore;
