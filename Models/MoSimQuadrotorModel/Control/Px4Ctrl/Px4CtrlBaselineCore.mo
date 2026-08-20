within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlBaselineCore "Native graphical px4ctrl baseline core with the OfficialPidRunner 9-in/4-out slot boundary"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version = "26.3.0",PortArrangement(Left(x_ref, y_ref, z_ref, vx_ref, vy_ref, vz_ref, ax_ref, ay_ref, az_ref, x_mea, y_mea, z_mea, vx_mea, vy_mea, vz_mea, roll_mea, pitch_mea, yaw_mea), Right(y, y1, y2, y3)),modelType = Control,BlockSystem(blockKind = BlockKind.userModel,SampleTime(auto=true,group = "")=0.01,OutputInterval=0.01),SysblockVersion = "1.0"), Icon(coordinateSystem(preserveAspectRatio = false)), experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01, StartTime = 0, StopTime = 0.02, StoreEventValue = 0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport x_ref 
    annotation(Placement(transformation(origin = {-502, -78},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 94.4444},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport y_ref 
    annotation(Placement(transformation(origin = {-502, -182},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 83.3333},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref 
    annotation(Placement(transformation(origin = {-502, -286},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 72.2222},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vx_ref 
    annotation(Placement(transformation(origin = {-502, 234},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 61.1111},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vy_ref 
    annotation(Placement(transformation(origin = {-502, 130},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 50},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vz_ref 
    annotation(Placement(transformation(origin = {-502, 26},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 38.8889},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport ax_ref 
    annotation(Placement(transformation(origin = {-502, 442},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 27.7778},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport ay_ref 
    annotation(Placement(transformation(origin = {-502, 390},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 16.6667},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport az_ref 
    annotation(Placement(transformation(origin = {-502, 338},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, 5.55556},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport x_mea 
    annotation(Placement(transformation(origin = {-502, -26},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -5.55556},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport y_mea 
    annotation(Placement(transformation(origin = {-502, -130},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -16.6667},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport z_mea 
    annotation(Placement(transformation(origin = {-502, -234},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -27.7778},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vx_mea 
    annotation(Placement(transformation(origin = {-502, 286},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -38.8889},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vy_mea 
    annotation(Placement(transformation(origin = {-502, 182},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -50},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport vz_mea 
    annotation(Placement(transformation(origin = {-502, 78},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -61.1111},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea 
    annotation(Placement(transformation(origin = {-502, -338},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -72.2222},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea 
    annotation(Placement(transformation(origin = {-502, 494},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -83.3333},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation(Placement(transformation(origin = {-502, -390},
    extent = {{-14, -10}, {14, 10}}),
    iconTransformation(origin = {-101.8, -94.4444},
    extent = {{-1.8, -1.8}, {1.8, 1.8}})));
  SysplorerEmbeddedCoder.Port.Outport y 
    annotation(Placement(transformation(extent = {{444, 68}, {472, 88}})));
  SysplorerEmbeddedCoder.Port.Outport y1 
    annotation(Placement(transformation(extent = {{444, 16}, {472, 36}})));
  SysplorerEmbeddedCoder.Port.Outport y2 
    annotation(Placement(transformation(extent = {{444, -36}, {472, -16}})));
  SysplorerEmbeddedCoder.Port.Outport y3 
    annotation(Placement(transformation(extent = {{444, -88}, {472, -68}})));
  Px4CtrlOuterLoopGraphicalSysblock outer_loop 
    annotation(Placement(transformation(origin = {-356, 0},
    extent = {{-95, -140}, {95, 140}})), __MWORKS(SECInstance = true, PortLabels(labelType = "PortName")));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_reference_scale(k = 0.10197162129779283) 
    annotation(Placement(transformation(extent = {{-231, -65}, {-197, -39}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_limit(upLimit = 0.2617801047120419, lowLimit = -0.2617801047120419)
    "Clamp pitch reference to ±15 deg — mirrors OfficialPidGraphicalCore pitch_ref_limit" 
    annotation(Placement(transformation(extent = {{-183, -91}, {-149, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_reference_scale(k = 0.10197162129779283) 
    annotation(Placement(transformation(extent = {{-231, 91}, {-197, 117}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_limit(upLimit = 0.2617801047120419, lowLimit = -0.2617801047120419)
    "Clamp roll reference to ±15 deg — mirrors OfficialPidGraphicalCore roll_ref_limit" 
    annotation(Placement(transformation(extent = {{-183, 65}, {-149, 91}})));
  SysplorerEmbeddedCoder.Sources.Constant z_gravity_offset(k = -9.80665) 
    annotation(Placement(transformation(origin = {-356, -327},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_collective_delta 
    annotation(Placement(transformation(extent = {{-231, -169}, {-197, -143}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error 
    annotation(Placement(transformation(extent = {{-135, 39}, {-101, 65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_measurement_sign(k = 1.0) 
    annotation(Placement(transformation(origin = {-356, -223},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_attitude_gain(k = 14.142) 
    annotation(Placement(transformation(extent = {{-87, 65}, {-53, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_pd 
    annotation(Placement(transformation(extent = {{-39, 13}, {-5, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(extent = {{9, -13}, {43, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix(k = 0.707) 
    annotation(Placement(transformation(extent = {{57, -65}, {91, -39}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_diff_delay(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-356, 171},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_diff_sum(inputs = "+-", isSaturate = false) 
    annotation(Placement(transformation(origin = {-420, 171},
    extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(extent = {{-231, 39}, {-197, 65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(extent = {{-183, 13}, {-149, 39}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(extent = {{-87, -91}, {-53, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(extent = {{-39, -143}, {-5, -117}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_derivative_state 
    annotation(Placement(transformation(extent = {{-135, -13}, {-101, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_gain(k = 1.414) 
    annotation(Placement(transformation(extent = {{-87, 13}, {-53, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error 
    annotation(Placement(transformation(extent = {{-135, -117}, {-101, -91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_measurement_sign(k = -1.0) 
    annotation(Placement(transformation(origin = {-356, 223},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_attitude_gain(k = 14.142) 
    annotation(Placement(transformation(extent = {{-87, -143}, {-53, -117}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_pd 
    annotation(Placement(transformation(extent = {{9, 91}, {43, 117}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(extent = {{57, 39}, {91, 65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix(k = 0.707) 
    annotation(Placement(transformation(extent = {{105, 117}, {139, 143}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_diff_delay(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-214, 163},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_diff_sum(inputs = "+-", isSaturate = false) 
    annotation(Placement(transformation(origin = {-278, 163},
    extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(extent = {{-183, 117}, {-149, 143}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(extent = {{-135, 91}, {-101, 117}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(extent = {{-39, -39}, {-5, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(extent = {{9, -65}, {43, -39}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_derivative_state 
    annotation(Placement(transformation(extent = {{-87, 117}, {-53, 143}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_gain(k = 1.414) 
    annotation(Placement(transformation(extent = {{-39, 117}, {-5, 143}})));
  SysplorerEmbeddedCoder.Sources.Constant yaw_reference(k = 0.0) 
    annotation(Placement(transformation(origin = {-356, -275},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error 
    annotation(Placement(transformation(extent = {{-231, -117}, {-197, -91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_measurement_sign(k = -1.0) 
    annotation(Placement(transformation(origin = {-356, -171},
    extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_attitude_gain(k = 5.0) 
    annotation(Placement(transformation(extent = {{-183, -143}, {-149, -117}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(extent = {{57, -13}, {91, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix(k = 0.707) 
    annotation(Placement(transformation(extent = {{105, 65}, {139, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_pd 
    annotation(Placement(transformation(extent = {{9, 39}, {43, 65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay yaw_diff_delay(initCond = 0.0) 
    annotation(Placement(transformation(extent = {{-231, -13}, {-197, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_diff_sum(inputs = "+-", isSaturate = false) 
    annotation(Placement(transformation(origin = {-295, 0},
    extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(extent = {{-183, -39}, {-149, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_derivative_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(extent = {{-135, -65}, {-101, -39}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay yaw_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(extent = {{-39, -91}, {-5, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_derivative_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(extent = {{9, -117}, {43, -91}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_derivative_state 
    annotation(Placement(transformation(extent = {{-87, -39}, {-53, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_derivative_gain(k = 0.5) 
    annotation(Placement(transformation(extent = {{-39, 65}, {-5, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_roll_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{105, 13}, {139, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_pitch_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{153, 169}, {187, 195}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_yaw_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{153, -39}, {187, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1_first 
    annotation(Placement(transformation(extent = {{201, 65}, {235, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1_second 
    annotation(Placement(transformation(extent = {{249, 65}, {283, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1 
    annotation(Placement(transformation(extent = {{297, 65}, {331, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation amplitude_limit_1(upLimit = 200.0, lowLimit = -200.0) 
    annotation(Placement(transformation(extent = {{345, 65}, {379, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_1_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{393, 65}, {427, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_roll_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{105, -39}, {139, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_pitch_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{153, 117}, {187, 143}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_yaw_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{153, -91}, {187, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2_first 
    annotation(Placement(transformation(extent = {{201, 13}, {235, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2_second 
    annotation(Placement(transformation(extent = {{249, 13}, {283, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2 
    annotation(Placement(transformation(extent = {{297, 13}, {331, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation amplitude_limit_2(upLimit = 200.0, lowLimit = -200.0) 
    annotation(Placement(transformation(extent = {{345, 13}, {379, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_2_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{393, 13}, {427, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_roll_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{105, -91}, {139, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_pitch_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{153, 65}, {187, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_yaw_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{153, -143}, {187, -117}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3_first 
    annotation(Placement(transformation(extent = {{201, -39}, {235, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3_second 
    annotation(Placement(transformation(extent = {{249, -39}, {283, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3 
    annotation(Placement(transformation(extent = {{297, -39}, {331, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation amplitude_limit_3(upLimit = 200.0, lowLimit = -200.0) 
    annotation(Placement(transformation(extent = {{345, -39}, {379, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_3_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{393, -39}, {427, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_roll_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{105, -143}, {139, -117}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_pitch_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{153, 13}, {187, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_yaw_sign(k = 1.0) 
    annotation(Placement(transformation(extent = {{153, -195}, {187, -169}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4_first 
    annotation(Placement(transformation(extent = {{201, -91}, {235, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4_second 
    annotation(Placement(transformation(extent = {{249, -91}, {283, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4 
    annotation(Placement(transformation(extent = {{297, -91}, {331, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation amplitude_limit_4(upLimit = 200.0, lowLimit = -200.0) 
    annotation(Placement(transformation(extent = {{345, -91}, {379, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_4_sign(k = -1.0) 
    annotation(Placement(transformation(extent = {{393, -91}, {427, -65}})));
equation
  connect(x_ref, outer_loop.ref_p_x) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -78}, {-422, -78}, {-422, 130.667}, {-408.8, 130.667}},
    color = {0, 0, 127}));
  connect(x_mea, outer_loop.mea_p_x) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -26}, {-422, -26}, {-422, 112}, {-408.8, 112}},
    color = {0, 0, 127}));
  connect(vx_ref, outer_loop.ref_v_x) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 234}, {-422, 234}, {-422, 93.3333}, {-408.8, 93.3333}},
    color = {0, 0, 127}));
  connect(vx_mea, outer_loop.mea_v_x) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 286}, {-422, 286}, {-422, 74.6667}, {-408.8, 74.6667}},
    color = {0, 0, 127}));
  connect(ax_ref, outer_loop.ref_a_x) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 442}, {-422, 442}, {-422, 56}, {-408.8, 56}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(y_ref, outer_loop.ref_p_y) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -182}, {-422, -182}, {-422, 37.3333}, {-408.8, 37.3333}},
    color = {0, 0, 127}));
  connect(y_mea, outer_loop.mea_p_y) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -130}, {-422, -130}, {-422, 18.6667}, {-408.8, 18.6667}},
    color = {0, 0, 127}));
  connect(vy_ref, outer_loop.ref_v_y) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 130}, {-422, 130}, {-422, -2.84217e-14}, {-408.8, -2.84217e-14}},
    color = {0, 0, 127}));
  connect(vy_mea, outer_loop.mea_v_y) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 182}, {-422, 182}, {-422, -18.6667}, {-408.8, -18.6667}},
    color = {0, 0, 127}));
  connect(ay_ref, outer_loop.ref_a_y) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 390}, {-422, 390}, {-422, -37.3333}, {-408.8, -37.3333}},
    color = {0, 0, 127}));
  connect(z_ref, outer_loop.ref_p_z) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -286}, {-422, -286}, {-422, -56}, {-408.8, -56}},
    color = {0, 0, 127}));
  connect(z_mea, outer_loop.mea_p_z) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -234}, {-422, -234}, {-422, -74.6667}, {-408.8, -74.6667}},
    color = {0, 0, 127}));
  connect(vz_ref, outer_loop.ref_v_z) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 26.0000048}, {-422, 26.0000048}, {-422, -93.3333}, {-408.8, -93.3333}},
    color = {0, 0, 127}));
  connect(vz_mea, outer_loop.mea_v_z) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 78.0000048}, {-422, 78.0000048}, {-422, -112}, {-408.8, -112}},
    color = {0, 0, 127}));
  connect(az_ref, outer_loop.ref_a_z) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, 338}, {-422, 338}, {-422, -130.667}, {-408.8, -130.667}},
    color = {0, 0, 127}));
  connect(outer_loop.desired_acc_x, pitch_reference_scale.u) 
    annotation(Line(origin = {0, 0},
    points = {{-259.2, 93.3333}, {-248, 93.3333}, {-248, -52}, {-232.8, -52}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(outer_loop.desired_acc_y, roll_reference_scale.u) 
    annotation(Line(origin = {0, 0},
    points = {{-259.2, 0}, {-248, 0}, {-248, 104}, {-232.8, 104}},
    color = {0, 0, 127}));
  connect(outer_loop.desired_acc_z, z_collective_delta.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-259.2, -93.3333}, {-248, -93.3333}, {-248, -149.5}, {-232.8, -149.5}},
    color = {0, 0, 127}));
  connect(z_gravity_offset.y, z_collective_delta.u2) 
    annotation(Line(origin = {-44, -8},
    points = {{-293.2, -319}, {-204, -319}, {-204, -154.5}, {-188.8, -154.5}},
    color = {0, 0, 127}));
  connect(roll_diff_sum.y, roll_derivative_slope.u) 
    annotation(Line(points = {{-401.2, 171}, {-390, 171}, {-390, 52}, {-232.8, 52}},
    color = {0, 0, 127}));
  connect(roll_derivative_slope.y, roll_derivative_increment.u) 
    annotation(Line(points = {{-197, 52}, {-190, 52}, {-190, 26}, {-183, 26}}, color = {0, 0, 127}));
  connect(roll_derivative_increment.y, roll_derivative_state.u2) 
    annotation(Line(points = {{-149, 26}, {-142, 26}, {-142, 0}, {-135, 0}}, color = {0, 0, 127}));
  connect(roll_derivative_previous_state.y, roll_derivative_decay.u) 
    annotation(Line(points = {{-53, -78}, {-46, -78}, {-46, -130}, {-39, -130}}, color = {0, 0, 127}));
  connect(roll_derivative_decay.y, roll_derivative_state.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-3.2, -130}, {50, -130}, {50, -156}, {-142, -156}, {-142, 6.5}, {-136.8, 6.5}},
    color = {0, 0, 127}));
  connect(roll_derivative_state.y, roll_derivative_previous_state.u1) 
    annotation(Line(points = {{-101, 0}, {-94, 0}, {-94, -78}, {-87, -78}}, color = {0, 0, 127}));
  connect(roll_derivative_state.y, roll_derivative_gain.u) 
    annotation(Line(points = {{-101, 0}, {-94, 0}, {-94, 26}, {-87, 26}}, color = {0, 0, 127}));
  connect(roll_reference_scale.y, roll_ref_limit.u) 
    annotation(Line(points = {{-197, 104}, {-190, 104}, {-190, 78}, {-183, 78}}, color = {0, 0, 127}));
  connect(roll_ref_limit.y, roll_error.u1) 
    annotation(Line(points = {{-149, 78}, {-142, 78}, {-142, 52}, {-135, 52}}, color = {0, 0, 127}));
  connect(roll_mea, roll_measurement_sign.u) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -338}, {-422, -338}, {-422, -223}, {-330.8, -223}},
    color = {0, 0, 127}));
  connect(roll_measurement_sign.y, roll_error.u2) 
    annotation(Line(origin = {-20, -8},
    points = {{-317.2, -215}, {-122, -215}, {-122, 53.5}, {-116.8, 53.5}},
    color = {0, 0, 127}));
  connect(roll_error.y, roll_attitude_gain.u) 
    annotation(Line(points = {{-101, 52}, {-94, 52}, {-94, 78}, {-87, 78}}, color = {0, 0, 127}));
  connect(roll_mea, roll_diff_delay.u1) 
    annotation(Line(points = {{-502, -338}, {-490, -338}, {-490, 171}, {-373, 171}},
    color = {0, 0, 127}));
  connect(roll_mea, roll_diff_sum.u1) 
    annotation(Line(points = {{-502, -338}, {-490, -338}, {-490, 171}, {-437, 171}},
    color = {0, 0, 127}));
  connect(roll_diff_delay.y, roll_diff_sum.u2) 
    annotation(Line(points = {{-339, 171}, {-330, 171}, {-330, 164.5}, {-437, 164.5}},
    color = {0, 0, 127}));
  connect(roll_attitude_gain.y, roll_pd.u1) 
    annotation(Line(points = {{-53, 78}, {-46, 78}, {-46, 26}, {-39, 26}}, color = {0, 0, 127}));
  connect(roll_derivative_gain.y, roll_pd.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-51.2, 26}, {-46, 26}, {-46, 19.5}, {-40.8, 19.5}},
    color = {0, 0, 127}));
  connect(roll_pd.y, roll_limit.u) 
    annotation(Line(points = {{-5, 26}, {2, 26}, {2, 0}, {9, 0}}, color = {0, 0, 127}));
  connect(roll_limit.y, roll_mix.u) 
    annotation(Line(points = {{43, 0}, {50, 0}, {50, -52}, {57, -52}}, color = {0, 0, 127}));
  connect(pitch_diff_sum.y, pitch_derivative_slope.u) 
    annotation(Line(points = {{-259.2, 163}, {-248, 163}, {-248, 130}, {-184.8, 130}},
    color = {0, 0, 127}));
  connect(pitch_derivative_slope.y, pitch_derivative_increment.u) 
    annotation(Line(points = {{-149, 130}, {-142, 130}, {-142, 104}, {-135, 104}}, color = {0, 0, 127}));
  connect(pitch_derivative_increment.y, pitch_derivative_state.u2) 
    annotation(Line(points = {{-101, 104}, {-94, 104}, {-94, 130}, {-87, 130}}, color = {0, 0, 127}));
  connect(pitch_derivative_previous_state.y, pitch_derivative_decay.u) 
    annotation(Line(points = {{-5, -26}, {2, -26}, {2, -52}, {9, -52}}, color = {0, 0, 127}));
  connect(pitch_derivative_decay.y, pitch_derivative_state.u1) 
    annotation(Line(origin = {0, 0},
    points = {{44.8, -52}, {50, -52}, {50, -156}, {-94, -156}, {-94, 136.5}, {-88.8, 136.5}},
    color = {0, 0, 127}));
  connect(pitch_derivative_state.y, pitch_derivative_previous_state.u1) 
    annotation(Line(points = {{-53, 130}, {-46, 130}, {-46, -26}, {-39, -26}}, color = {0, 0, 127}));
  connect(pitch_derivative_state.y, pitch_derivative_gain.u) 
    annotation(Line(points = {{-53, 130}, {-39, 130}}, color = {0, 0, 127}));
  connect(pitch_reference_scale.y, pitch_ref_limit.u) 
    annotation(Line(points = {{-197, -52}, {-190, -52}, {-190, -78}, {-183, -78}}, color = {0, 0, 127}));
  connect(pitch_ref_limit.y, pitch_error.u1) 
    annotation(Line(points = {{-149, -78}, {-142, -78}, {-142, -104}, {-135, -104}}, color = {0, 0, 127}));
  connect(pitch_mea, pitch_measurement_sign.u) 
    annotation(Line(origin = {-44, 8},
    points = {{-441.974, 486}, {-422, 486}, {-422, 215}, {-330.8, 215}},
    color = {0, 0, 127}));
  connect(pitch_measurement_sign.y, pitch_error.u2) 
    annotation(Line(origin = {-20, 8},
    points = {{-317.2, 215}, {-122, 215}, {-122, -118.5}, {-116.8, -118.5}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_measurement_sign.y, pitch_diff_delay.u1) 
    annotation(Line(points = {{-337.2, 223}, {-214, 223}, {-214, 176}},
    color = {0, 0, 127}));
  connect(pitch_measurement_sign.y, pitch_diff_sum.u1) 
    annotation(Line(points = {{-337.2, 223}, {-278, 223}, {-278, 176}},
    color = {0, 0, 127}));
  connect(pitch_diff_delay.y, pitch_diff_sum.u2) 
    annotation(Line(points = {{-197, 163}, {-190, 163}, {-190, 156.5}, {-295, 156.5}},
    color = {0, 0, 127}));
  connect(pitch_error.y, pitch_attitude_gain.u) 
    annotation(Line(points = {{-101, -104}, {-94, -104}, {-94, -130}, {-87, -130}}, color = {0, 0, 127}));
  connect(pitch_attitude_gain.y, pitch_pd.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-51.2, -130}, {-46, -130}, {-46, 98}, {2, 98}, {2, 110.5}, {7.2, 110.5}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(pitch_derivative_gain.y, pitch_pd.u2) 
    annotation(Line(points = {{-5, 130}, {2, 130}, {2, 104}, {9, 104}}, color = {0, 0, 127}));
  connect(pitch_pd.y, pitch_limit.u) 
    annotation(Line(points = {{43, 104}, {50, 104}, {50, 52}, {57, 52}}, color = {0, 0, 127}));
  connect(pitch_limit.y, pitch_mix.u) 
    annotation(Line(points = {{91, 52}, {98, 52}, {98, 130}, {105, 130}}, color = {0, 0, 127}));
  connect(yaw_reference.y, yaw_error.u1) 
    annotation(Line(origin = {-44, -8},
    points = {{-293.2, -267}, {-204, -267}, {-204, -89.5}, {-188.8, -89.5}},
    color = {0, 0, 127}));
  connect(yaw_mea, yaw_measurement_sign.u) 
    annotation(Line(origin = {-44, 0},
    points = {{-441.974, -390}, {-422, -390}, {-422, -171}, {-330.8, -171}},
    color = {0, 0, 127}));
  connect(yaw_measurement_sign.y, yaw_error.u2) 
    annotation(Line(origin = {-20, -8},
    points = {{-317.2, -163}, {-228, -163}, {-228, -102.5}, {-212.8, -102.5}},
    color = {0, 0, 127}));
  connect(yaw_error.y, yaw_attitude_gain.u) 
    annotation(Line(points = {{-197, -104}, {-190, -104}, {-190, -130}, {-183, -130}}, color = {0, 0, 127}));
  connect(yaw_attitude_gain.y, yaw_pd.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-147.2, -130}, {-94, -130}, {-94, 46}, {2, 46}, {2, 58.5}, {7.2, 58.5}},
    color = {0, 0, 127}));
  connect(yaw_derivative_gain.y, yaw_pd.u2) 
    annotation(Line(points = {{-5, 78}, {2, 78}, {2, 52}, {9, 52}}, color = {0, 0, 127}));
  connect(yaw_pd.y, yaw_limit.u) 
    annotation(Line(points = {{43, 52}, {50, 52}, {50, 0}, {57, 0}}, color = {0, 0, 127}));
  connect(yaw_measurement_sign.y, yaw_diff_delay.u1) 
    annotation(Line(points = {{-337.2, -171}, {-248, -171}, {-248, 0}, {-231, 0}},
    color = {0, 0, 127}));
  connect(yaw_measurement_sign.y, yaw_diff_sum.u1) 
    annotation(Line(points = {{-337.2, -171}, {-295, -171}, {-295, -13}},
    color = {0, 0, 127}));
  connect(yaw_diff_delay.y, yaw_diff_sum.u2) 
    annotation(Line(points = {{-197, 0}, {-178, 0}, {-178, -13}, {-278, -13}, {-278, -6.5}},
    color = {0, 0, 127}));
  connect(yaw_diff_sum.y, yaw_derivative_slope.u) 
    annotation(Line(points = {{-276.8, 0}, {-270, 0}, {-270, -26}, {-184.8, -26}},
    color = {0, 0, 127}));
  connect(yaw_derivative_slope.y, yaw_derivative_increment.u) 
    annotation(Line(points = {{-149, -26}, {-142, -26}, {-142, -52}, {-135, -52}}, color = {0, 0, 127}));
  connect(yaw_derivative_increment.y, yaw_derivative_state.u2) 
    annotation(Line(points = {{-101, -52}, {-94, -52}, {-94, -26}, {-87, -26}}, color = {0, 0, 127}));
  connect(yaw_derivative_previous_state.y, yaw_derivative_decay.u) 
    annotation(Line(points = {{-5, -78}, {2, -78}, {2, -104}, {9, -104}}, color = {0, 0, 127}));
  connect(yaw_derivative_decay.y, yaw_derivative_state.u1) 
    annotation(Line(origin = {0, 0},
    points = {{44.8, -104}, {50, -104}, {50, -156}, {-94, -156}, {-94, -19.5}, {-88.8, -19.5}},
    color = {0, 0, 127}));
  connect(yaw_derivative_state.y, yaw_derivative_previous_state.u1) 
    annotation(Line(points = {{-53, -26}, {-46, -26}, {-46, -78}, {-39, -78}}, color = {0, 0, 127}));
  connect(yaw_derivative_state.y, yaw_derivative_gain.u) 
    annotation(Line(points = {{-53, -26}, {-46, -26}, {-46, 78}, {-39, 78}}, color = {0, 0, 127}));
  connect(yaw_limit.y, yaw_mix.u) 
    annotation(Line(points = {{91, 0}, {98, 0}, {98, 78}, {105, 78}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_1_roll_sign.u) 
    annotation(Line(points = {{91, -52}, {98, -52}, {98, 26}, {105, 26}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_1_pitch_sign.u) 
    annotation(Line(points = {{139, 130}, {146, 130}, {146, 182}, {153, 182}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_1_yaw_sign.u) 
    annotation(Line(points = {{139, 78}, {146, 78}, {146, -26}, {153, -26}}, color = {0, 0, 127}));
  connect(mixer_1_roll_sign.y, mixer_1_first.u1) 
    annotation(Line(origin = {0, 0},
    points = {{140.8, 26}, {146, 26}, {146, 104}, {194, 104}, {194, 84.5}, {199.2, 84.5}},
    color = {0, 0, 127}));
  connect(mixer_1_pitch_sign.y, mixer_1_first.u2) 
    annotation(Line(points = {{187, 182}, {194, 182}, {194, 78}, {201, 78}}, color = {0, 0, 127}));
  connect(mixer_1_first.y, mixer_1_second.u1) 
    annotation(Line(origin = {0, 0},
    points = {{236.8, 78}, {242, 78}, {242, 84.5}, {247.2, 84.5}},
    color = {0, 0, 127}));
  connect(mixer_1_yaw_sign.y, mixer_1_second.u2) 
    annotation(Line(origin = {0, 0},
    points = {{188.8, -26}, {194, -26}, {194, 54}, {242, 54}, {242, 71.5}, {247.2, 71.5}},
    color = {0, 0, 127}));
  connect(mixer_1_second.y, mixer_1.u1) 
    annotation(Line(origin = {0, 0},
    points = {{284.8, 78}, {290, 78}, {290, 84.5}, {295.2, 84.5}},
    color = {0, 0, 127}));
  connect(z_collective_delta.y, mixer_1.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-195.2, -156}, {50, -156}, {50, 104}, {290, 104}, {290, 71.5}, {295.2, 71.5}},
    color = {0, 0, 127}));
  connect(mixer_1.y, amplitude_limit_1.u) 
    annotation(Line(points = {{331, 78}, {345, 78}}, color = {0, 0, 127}));
  connect(amplitude_limit_1.y, rotor_1_sign.u) 
    annotation(Line(points = {{379, 78}, {393, 78}}, color = {0, 0, 127}));
  connect(rotor_1_sign.y, y) 
    annotation(Line(points = {{427, 78}, {472, 78}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_2_roll_sign.u) 
    annotation(Line(points = {{91, -52}, {98, -52}, {98, -26}, {105, -26}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_2_pitch_sign.u) 
    annotation(Line(points = {{139, 130}, {153, 130}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_2_yaw_sign.u) 
    annotation(Line(points = {{139, 78}, {146, 78}, {146, -78}, {153, -78}}, color = {0, 0, 127}));
  connect(mixer_2_roll_sign.y, mixer_2_first.u1) 
    annotation(Line(origin = {0, 0},
    points = {{140.8, -26}, {194, -26}, {194, 32.5}, {199.2, 32.5}},
    color = {0, 0, 127}));
  connect(mixer_2_pitch_sign.y, mixer_2_first.u2) 
    annotation(Line(points = {{187, 130}, {194, 130}, {194, 26}, {201, 26}}, color = {0, 0, 127}));
  connect(mixer_2_first.y, mixer_2_second.u1) 
    annotation(Line(origin = {0, 0},
    points = {{236.8, 26}, {242, 26}, {242, 32.5}, {247.2, 32.5}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(mixer_2_yaw_sign.y, mixer_2_second.u2) 
    annotation(Line(origin = {0, 0},
    points = {{188.8, -78}, {194, -78}, {194, -2}, {242, -2}, {242, 19.5}, {247.2, 19.5}},
    color = {0, 0, 127}));
  connect(mixer_2_second.y, mixer_2.u1) 
    annotation(Line(origin = {0, 0},
    points = {{284.8, 26}, {290, 26}, {290, 32.5}, {295.2, 32.5}},
    color = {0, 0, 127}));
  connect(z_collective_delta.y, mixer_2.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-195.2, -156}, {50, -156}, {50, 104}, {290, 104}, {290, 19.5}, {295.2, 19.5}},
    color = {0, 0, 127}));
  connect(mixer_2.y, amplitude_limit_2.u) 
    annotation(Line(points = {{331, 26}, {345, 26}}, color = {0, 0, 127}));
  connect(amplitude_limit_2.y, rotor_2_sign.u) 
    annotation(Line(points = {{379, 26}, {393, 26}}, color = {0, 0, 127}));
  connect(rotor_2_sign.y, y1) 
    annotation(Line(points = {{427, 26}, {472, 26}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_3_roll_sign.u) 
    annotation(Line(points = {{91, -52}, {98, -52}, {98, -78}, {105, -78}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_3_pitch_sign.u) 
    annotation(Line(points = {{139, 130}, {146, 130}, {146, 78}, {153, 78}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_3_yaw_sign.u) 
    annotation(Line(points = {{139, 78}, {146, 78}, {146, -130}, {153, -130}}, color = {0, 0, 127}));
  connect(mixer_3_roll_sign.y, mixer_3_first.u1) 
    annotation(Line(origin = {0, 0},
    points = {{140.8, -78}, {146, -78}, {146, -108}, {194, -108}, {194, -19.5}, {199.2, -19.5}},
    color = {0, 0, 127}));
  connect(mixer_3_pitch_sign.y, mixer_3_first.u2) 
    annotation(Line(points = {{187, 78}, {194, 78}, {194, -26}, {201, -26}}, color = {0, 0, 127}));
  connect(mixer_3_first.y, mixer_3_second.u1) 
    annotation(Line(origin = {0, 0},
    points = {{236.8, -26}, {242, -26}, {242, -19.5}, {247.2, -19.5}},
    color = {0, 0, 127}));
  connect(mixer_3_yaw_sign.y, mixer_3_second.u2) 
    annotation(Line(origin = {0, 0},
    points = {{188.8, -130}, {194, -130}, {194, -54}, {242, -54}, {242, -32.5}, {247.2, -32.5}},
    color = {0, 0, 127}));
  connect(mixer_3_second.y, mixer_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{284.8, -26}, {290, -26}, {290, -19.5}, {295.2, -19.5}},
    color = {0, 0, 127}));
  connect(z_collective_delta.y, mixer_3.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-195.2, -156}, {50, -156}, {50, 104}, {290, 104}, {290, -32.5}, {295.2, -32.5}},
    color = {0, 0, 127}));
  connect(mixer_3.y, amplitude_limit_3.u) 
    annotation(Line(points = {{331, -26}, {345, -26}}, color = {0, 0, 127}));
  connect(amplitude_limit_3.y, rotor_3_sign.u) 
    annotation(Line(points = {{379, -26}, {393, -26}}, color = {0, 0, 127}));
  connect(rotor_3_sign.y, y2) 
    annotation(Line(points = {{427, -26}, {472, -26}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_4_roll_sign.u) 
    annotation(Line(points = {{91, -52}, {98, -52}, {98, -130}, {105, -130}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_4_pitch_sign.u) 
    annotation(Line(points = {{139, 130}, {146, 130}, {146, 26}, {153, 26}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_4_yaw_sign.u) 
    annotation(Line(points = {{139, 78}, {146, 78}, {146, -182}, {153, -182}}, color = {0, 0, 127}));
  connect(mixer_4_roll_sign.y, mixer_4_first.u1) 
    annotation(Line(origin = {0, 0},
    points = {{140.8, -130}, {146, -130}, {146, -108}, {194, -108}, {194, -71.5}, {199.2, -71.5}},
    color = {0, 0, 127}));
  connect(mixer_4_pitch_sign.y, mixer_4_first.u2) 
    annotation(Line(origin = {0, 0},
    points = {{188.8, 26}, {194, 26}, {194, -84.5}, {199.2, -84.5}},
    color = {0, 0, 127}));
  connect(mixer_4_first.y, mixer_4_second.u1) 
    annotation(Line(origin = {0, 0},
    points = {{236.8, -78}, {242, -78}, {242, -71.5}, {247.2, -71.5}},
    color = {0, 0, 127}));
  connect(mixer_4_yaw_sign.y, mixer_4_second.u2) 
    annotation(Line(origin = {0, 0},
    points = {{188.8, -182}, {242, -182}, {242, -84.5}, {247.2, -84.5}},
    color = {0, 0, 127}));
  connect(mixer_4_second.y, mixer_4.u1) 
    annotation(Line(origin = {0, 0},
    points = {{284.8, -78}, {290, -78}, {290, -71.5}, {295.2, -71.5}},
    color = {0, 0, 127}));
  connect(z_collective_delta.y, mixer_4.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-195.2, -156}, {50, -156}, {50, 104}, {290, 104}, {290, -84.5}, {295.2, -84.5}},
    color = {0, 0, 127}));
  connect(mixer_4.y, amplitude_limit_4.u) 
    annotation(Line(points = {{331, -78}, {345, -78}}, color = {0, 0, 127}));
  connect(amplitude_limit_4.y, rotor_4_sign.u) 
    annotation(Line(points = {{379, -78}, {393, -78}}, color = {0, 0, 127}));
  connect(rotor_4_sign.y, y3) 
    annotation(Line(points = {{427, -78}, {444, -78}}, color = {0, 0, 127}));
end Px4CtrlBaselineCore;
