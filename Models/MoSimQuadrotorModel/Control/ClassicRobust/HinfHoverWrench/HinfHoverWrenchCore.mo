within MoSimQuadrotorModel.Control.ClassicRobust.HinfHoverWrench;
model HinfHoverWrenchCore "H-infinity hover-wrench direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(state_roll, reference_roll, state_pitch, reference_pitch, state_yaw, reference_yaw, state_p, reference_p, state_q, reference_q, state_r, reference_r, state_u, reference_u, state_v, reference_v, state_w, reference_w, state_x, reference_x, state_y, reference_y, state_z, reference_z, enable), Right(state_error_roll_out, state_error_pitch_out, state_error_yaw_out, wrench_force_n_out, wrench_tau_x_nm_out, wrench_tau_y_nm_out, wrench_tau_z_nm_out, collective_thrust_n_out, normalized_thrust_out, adapted_roll_rad_out, adapted_pitch_rad_out, adapted_yaw_rad_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport state_roll 
    annotation (Placement(transformation(origin = {-660, 365}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_roll 
    annotation (Placement(transformation(origin = {-570, 365}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_pitch 
    annotation (Placement(transformation(origin = {-660, 309}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_pitch 
    annotation (Placement(transformation(origin = {-570, 309}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_yaw 
    annotation (Placement(transformation(origin = {-660, 253}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_yaw 
    annotation (Placement(transformation(origin = {-570, 253}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_p 
    annotation (Placement(transformation(origin = {-660, 197}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_p 
    annotation (Placement(transformation(origin = {-570, 197}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_q 
    annotation (Placement(transformation(origin = {-660, 141}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_q 
    annotation (Placement(transformation(origin = {-570, 141}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_r 
    annotation (Placement(transformation(origin = {-660, 85}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_r 
    annotation (Placement(transformation(origin = {-570, 85}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_u 
    annotation (Placement(transformation(origin = {-660, 29}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_u 
    annotation (Placement(transformation(origin = {-570, 29}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_v 
    annotation (Placement(transformation(origin = {-660, -27}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_v 
    annotation (Placement(transformation(origin = {-570, -27}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_w 
    annotation (Placement(transformation(origin = {-660, -83}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_w 
    annotation (Placement(transformation(origin = {-570, -83}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_x 
    annotation (Placement(transformation(origin = {-660, -139}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_x 
    annotation (Placement(transformation(origin = {-570, -139}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_y 
    annotation (Placement(transformation(origin = {-660, -195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_y 
    annotation (Placement(transformation(origin = {-570, -195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport state_z 
    annotation (Placement(transformation(origin = {-660, -251}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_z 
    annotation (Placement(transformation(origin = {-570, -251}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable 
    annotation (Placement(transformation(origin = {-660, -355}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0) 
    annotation (Placement(transformation(origin = {430, -310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_roll(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 365}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_pitch(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 309}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_yaw(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 253}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_p(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 197}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_q(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 141}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_r(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 85}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_u(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, 29}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_v(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, -27}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_w(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, -83}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, -139}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum state_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-440, -251}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant hover_force_bias(k=9.80665) 
    annotation (Placement(transformation(origin = {-235, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_force_gain_w(k=102.07465646871916) 
    annotation (Placement(transformation(origin = {-250, -83}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_force_gain_z(k=160.7556564350713) 
    annotation (Placement(transformation(origin = {-250, -251}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_force_raw_stage_2 
    annotation (Placement(transformation(origin = {-33, 160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_force_raw 
    annotation (Placement(transformation(origin = {35, 160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_force_limit(lowLimit=0.0,upLimit=25.0) 
    annotation (Placement(transformation(origin = {145, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_x_gain_roll(k=-521.4516779287975) 
    annotation (Placement(transformation(origin = {-250, 365}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_x_gain_p(k=-10.806018318480602) 
    annotation (Placement(transformation(origin = {-250, 197}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_x_gain_v(k=-437.5189132603606) 
    annotation (Placement(transformation(origin = {-250, -27}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_x_gain_y(k=-1050.0326682458417) 
    annotation (Placement(transformation(origin = {-250, -195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_x_raw_stage_2 
    annotation (Placement(transformation(origin = {-101, 55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_x_raw_stage_3 
    annotation (Placement(transformation(origin = {-33, 55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_x_raw 
    annotation (Placement(transformation(origin = {35, 55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_tau_x_limit(lowLimit=-8.0,upLimit=8.0) 
    annotation (Placement(transformation(origin = {145, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_y_gain_pitch(k=-521.451677928797) 
    annotation (Placement(transformation(origin = {-250, 309}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_y_gain_q(k=-10.806018318480536) 
    annotation (Placement(transformation(origin = {-250, 141}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_y_gain_u(k=437.51891326036105) 
    annotation (Placement(transformation(origin = {-250, 29}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_y_gain_x(k=1050.0326682458376) 
    annotation (Placement(transformation(origin = {-250, -139}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_y_raw_stage_2 
    annotation (Placement(transformation(origin = {-101, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_y_raw_stage_3 
    annotation (Placement(transformation(origin = {-33, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_y_raw 
    annotation (Placement(transformation(origin = {35, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_tau_y_limit(lowLimit=-8.0,upLimit=8.0) 
    annotation (Placement(transformation(origin = {145, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_z_gain_yaw(k=-125.5903565899079) 
    annotation (Placement(transformation(origin = {-250, 253}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_tau_z_gain_r(k=-25.26141057148942) 
    annotation (Placement(transformation(origin = {-250, 85}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_tau_z_raw 
    annotation (Placement(transformation(origin = {35, -155}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_tau_z_limit(lowLimit=-8.0,upLimit=8.0) 
    annotation (Placement(transformation(origin = {145, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_normalized_thrust_from_force(k=0.029999999999999995) 
    annotation (Placement(transformation(origin = {255, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_normalized_thrust_limit(lowLimit=0.0,upLimit=0.62) 
    annotation (Placement(transformation(origin = {355, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_roll_wrench_to_angle(k=0.03333333333333333) 
    annotation (Placement(transformation(origin = {255, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_roll_reference_plus_correction 
    annotation (Placement(transformation(origin = {355, 55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_roll_tilt_limit(lowLimit=-0.35,upLimit=0.35) 
    annotation (Placement(transformation(origin = {455, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_pitch_wrench_to_angle(k=0.03333333333333333) 
    annotation (Placement(transformation(origin = {255, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_pitch_reference_plus_correction 
    annotation (Placement(transformation(origin = {355, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_pitch_tilt_limit(lowLimit=-0.35,upLimit=0.35) 
    annotation (Placement(transformation(origin = {455, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain hinf_yaw_wrench_to_angle(k=0.025) 
    annotation (Placement(transformation(origin = {255, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation hinf_yaw_correction_limit(lowLimit=-0.2,upLimit=0.2) 
    annotation (Placement(transformation(origin = {355, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum hinf_yaw_reference_plus_correction 
    annotation (Placement(transformation(origin = {455, -155}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_state_error_roll(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport state_error_roll_out 
    annotation (Placement(transformation(origin = {720, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_state_error_pitch(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport state_error_pitch_out 
    annotation (Placement(transformation(origin = {720, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_state_error_yaw(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport state_error_yaw_out 
    annotation (Placement(transformation(origin = {720, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_wrench_force_n(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport wrench_force_n_out 
    annotation (Placement(transformation(origin = {720, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_wrench_tau_x_nm(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_x_nm_out 
    annotation (Placement(transformation(origin = {720, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_wrench_tau_y_nm(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_y_nm_out 
    annotation (Placement(transformation(origin = {720, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_wrench_tau_z_nm(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport wrench_tau_z_nm_out 
    annotation (Placement(transformation(origin = {720, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out 
    annotation (Placement(transformation(origin = {720, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin = {720, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adapted_roll_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adapted_roll_rad_out 
    annotation (Placement(transformation(origin = {720, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adapted_pitch_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adapted_pitch_rad_out 
    annotation (Placement(transformation(origin = {720, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_adapted_yaw_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {560, -88}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adapted_yaw_rad_out 
    annotation (Placement(transformation(origin = {720, -88}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(state_roll, state_error_roll.u1) 
    annotation(Line(points = {{-646, 365}, {-454, 365}}, color = {0, 0, 127}));
  connect(reference_roll, state_error_roll.u2) 
    annotation(Line(points = {{-556, 365}, {-454, 365}}, color = {0, 0, 127}));
  connect(state_pitch, state_error_pitch.u1) 
    annotation(Line(points = {{-646, 309}, {-454, 309}}, color = {0, 0, 127}));
  connect(reference_pitch, state_error_pitch.u2) 
    annotation(Line(points = {{-556, 309}, {-454, 309}}, color = {0, 0, 127}));
  connect(state_yaw, state_error_yaw.u1) 
    annotation(Line(points = {{-646, 253}, {-454, 253}}, color = {0, 0, 127}));
  connect(reference_yaw, state_error_yaw.u2) 
    annotation(Line(points = {{-556, 253}, {-454, 253}}, color = {0, 0, 127}));
  connect(state_p, state_error_p.u1) 
    annotation(Line(points = {{-646, 197}, {-454, 197}}, color = {0, 0, 127}));
  connect(reference_p, state_error_p.u2) 
    annotation(Line(points = {{-556, 197}, {-454, 197}}, color = {0, 0, 127}));
  connect(state_q, state_error_q.u1) 
    annotation(Line(points = {{-646, 141}, {-454, 141}}, color = {0, 0, 127}));
  connect(reference_q, state_error_q.u2) 
    annotation(Line(points = {{-556, 141}, {-454, 141}}, color = {0, 0, 127}));
  connect(state_r, state_error_r.u1) 
    annotation(Line(points = {{-646, 85}, {-454, 85}}, color = {0, 0, 127}));
  connect(reference_r, state_error_r.u2) 
    annotation(Line(points = {{-556, 85}, {-454, 85}}, color = {0, 0, 127}));
  connect(state_u, state_error_u.u1) 
    annotation(Line(points = {{-646, 29}, {-454, 29}}, color = {0, 0, 127}));
  connect(reference_u, state_error_u.u2) 
    annotation(Line(points = {{-556, 29}, {-454, 29}}, color = {0, 0, 127}));
  connect(state_v, state_error_v.u1) 
    annotation(Line(points = {{-646, -27}, {-454, -27}}, color = {0, 0, 127}));
  connect(reference_v, state_error_v.u2) 
    annotation(Line(points = {{-556, -27}, {-454, -27}}, color = {0, 0, 127}));
  connect(state_w, state_error_w.u1) 
    annotation(Line(points = {{-646, -83}, {-454, -83}}, color = {0, 0, 127}));
  connect(reference_w, state_error_w.u2) 
    annotation(Line(points = {{-556, -83}, {-454, -83}}, color = {0, 0, 127}));
  connect(state_x, state_error_x.u1) 
    annotation(Line(points = {{-646, -139}, {-454, -139}}, color = {0, 0, 127}));
  connect(reference_x, state_error_x.u2) 
    annotation(Line(points = {{-556, -139}, {-454, -139}}, color = {0, 0, 127}));
  connect(state_y, state_error_y.u1) 
    annotation(Line(points = {{-646, -195}, {-454, -195}}, color = {0, 0, 127}));
  connect(reference_y, state_error_y.u2) 
    annotation(Line(points = {{-556, -195}, {-454, -195}}, color = {0, 0, 127}));
  connect(state_z, state_error_z.u1) 
    annotation(Line(points = {{-646, -251}, {-454, -251}}, color = {0, 0, 127}));
  connect(reference_z, state_error_z.u2) 
    annotation(Line(points = {{-556, -251}, {-454, -251}}, color = {0, 0, 127}));
  connect(state_error_w.y, hinf_force_gain_w.u) 
    annotation(Line(points = {{-426, -83}, {-264, -83}}, color = {0, 0, 127}));
  connect(state_error_z.y, hinf_force_gain_z.u) 
    annotation(Line(points = {{-426, -251}, {-264, -251}}, color = {0, 0, 127}));
  connect(hover_force_bias.y, hinf_force_raw_stage_2.u1) 
    annotation(Line(points = {{-221, 160}, {-47, 160}}, color = {0, 0, 127}));
  connect(hinf_force_gain_w.y, hinf_force_raw_stage_2.u2) 
    annotation(Line(points = {{-250, -72}, {-250, 38.5}, {-33, 38.5}, {-33, 149}}, color = {0, 0, 127}));
  connect(hinf_force_raw_stage_2.y, hinf_force_raw.u1) 
    annotation(Line(points = {{-19, 160}, {21, 160}}, color = {0, 0, 127}));
  connect(hinf_force_gain_z.y, hinf_force_raw.u2) 
    annotation(Line(points = {{-250, -240}, {-250, -45.5}, {35, -45.5}, {35, 149}}, color = {0, 0, 127}));
  connect(hinf_force_raw.y, hinf_force_limit.u) 
    annotation(Line(points = {{49, 160}, {131, 160}}, color = {0, 0, 127}));
  connect(state_error_roll.y, hinf_tau_x_gain_roll.u) 
    annotation(Line(points = {{-426, 365}, {-264, 365}}, color = {0, 0, 127}));
  connect(state_error_p.y, hinf_tau_x_gain_p.u) 
    annotation(Line(points = {{-426, 197}, {-264, 197}}, color = {0, 0, 127}));
  connect(state_error_v.y, hinf_tau_x_gain_v.u) 
    annotation(Line(points = {{-426, -27}, {-264, -27}}, color = {0, 0, 127}));
  connect(state_error_y.y, hinf_tau_x_gain_y.u) 
    annotation(Line(points = {{-426, -195}, {-264, -195}}, color = {0, 0, 127}));
  connect(hinf_tau_x_gain_roll.y, hinf_tau_x_raw_stage_2.u1) 
    annotation(Line(points = {{-250, 354}, {-250, 210}, {-101, 210}, {-101, 66}}, color = {0, 0, 127}));
  connect(hinf_tau_x_gain_p.y, hinf_tau_x_raw_stage_2.u2) 
    annotation(Line(points = {{-236, 197}, {-175.5, 197}, {-175.5, 55}, {-115, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_x_raw_stage_2.y, hinf_tau_x_raw_stage_3.u1) 
    annotation(Line(points = {{-87, 55}, {-47, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_x_gain_v.y, hinf_tau_x_raw_stage_3.u2) 
    annotation(Line(points = {{-236, -27}, {-141.5, -27}, {-141.5, 55}, {-47, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_x_raw_stage_3.y, hinf_tau_x_raw.u1) 
    annotation(Line(points = {{-19, 55}, {21, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_x_gain_y.y, hinf_tau_x_raw.u2) 
    annotation(Line(points = {{-236, -195}, {-107.5, -195}, {-107.5, 55}, {21, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_x_raw.y, hinf_tau_x_limit.u) 
    annotation(Line(points = {{49, 55}, {131, 55}}, color = {0, 0, 127}));
  connect(state_error_pitch.y, hinf_tau_y_gain_pitch.u) 
    annotation(Line(points = {{-426, 309}, {-264, 309}}, color = {0, 0, 127}));
  connect(state_error_q.y, hinf_tau_y_gain_q.u) 
    annotation(Line(points = {{-426, 141}, {-264, 141}}, color = {0, 0, 127}));
  connect(state_error_u.y, hinf_tau_y_gain_u.u) 
    annotation(Line(points = {{-426, 29}, {-264, 29}}, color = {0, 0, 127}));
  connect(state_error_x.y, hinf_tau_y_gain_x.u) 
    annotation(Line(points = {{-426, -139}, {-264, -139}}, color = {0, 0, 127}));
  connect(hinf_tau_y_gain_pitch.y, hinf_tau_y_raw_stage_2.u1) 
    annotation(Line(points = {{-250, 298}, {-250, 129.5}, {-101, 129.5}, {-101, -39}}, color = {0, 0, 127}));
  connect(hinf_tau_y_gain_q.y, hinf_tau_y_raw_stage_2.u2) 
    annotation(Line(points = {{-250, 130}, {-250, 45.5}, {-101, 45.5}, {-101, -39}}, color = {0, 0, 127}));
  connect(hinf_tau_y_raw_stage_2.y, hinf_tau_y_raw_stage_3.u1) 
    annotation(Line(points = {{-87, -50}, {-47, -50}}, color = {0, 0, 127}));
  connect(hinf_tau_y_gain_u.y, hinf_tau_y_raw_stage_3.u2) 
    annotation(Line(points = {{-236, 29}, {-141.5, 29}, {-141.5, -50}, {-47, -50}}, color = {0, 0, 127}));
  connect(hinf_tau_y_raw_stage_3.y, hinf_tau_y_raw.u1) 
    annotation(Line(points = {{-19, -50}, {21, -50}}, color = {0, 0, 127}));
  connect(hinf_tau_y_gain_x.y, hinf_tau_y_raw.u2) 
    annotation(Line(points = {{-236, -139}, {-107.5, -139}, {-107.5, -50}, {21, -50}}, color = {0, 0, 127}));
  connect(hinf_tau_y_raw.y, hinf_tau_y_limit.u) 
    annotation(Line(points = {{49, -50}, {131, -50}}, color = {0, 0, 127}));
  connect(state_error_yaw.y, hinf_tau_z_gain_yaw.u) 
    annotation(Line(points = {{-426, 253}, {-264, 253}}, color = {0, 0, 127}));
  connect(state_error_r.y, hinf_tau_z_gain_r.u) 
    annotation(Line(points = {{-426, 85}, {-264, 85}}, color = {0, 0, 127}));
  connect(hinf_tau_z_gain_yaw.y, hinf_tau_z_raw.u1) 
    annotation(Line(points = {{-250, 242}, {-250, 49}, {35, 49}, {35, -144}}, color = {0, 0, 127}));
  connect(hinf_tau_z_gain_r.y, hinf_tau_z_raw.u2) 
    annotation(Line(points = {{-236, 85}, {-107.5, 85}, {-107.5, -155}, {21, -155}}, color = {0, 0, 127}));
  connect(hinf_tau_z_raw.y, hinf_tau_z_limit.u) 
    annotation(Line(points = {{49, -155}, {131, -155}}, color = {0, 0, 127}));
  connect(hinf_force_limit.y, hinf_normalized_thrust_from_force.u) 
    annotation(Line(points = {{159, 160}, {241, 160}}, color = {0, 0, 127}));
  connect(hinf_normalized_thrust_from_force.y, hinf_normalized_thrust_limit.u) 
    annotation(Line(points = {{269, 160}, {341, 160}}, color = {0, 0, 127}));
  connect(hinf_tau_x_limit.y, hinf_roll_wrench_to_angle.u) 
    annotation(Line(points = {{159, 55}, {241, 55}}, color = {0, 0, 127}));
  connect(reference_roll, hinf_roll_reference_plus_correction.u1) 
    annotation(Line(points = {{-556, 365}, {-107.5, 365}, {-107.5, 55}, {341, 55}}, color = {0, 0, 127}));
  connect(hinf_roll_wrench_to_angle.y, hinf_roll_reference_plus_correction.u2) 
    annotation(Line(points = {{269, 55}, {341, 55}}, color = {0, 0, 127}));
  connect(hinf_roll_reference_plus_correction.y, hinf_roll_tilt_limit.u) 
    annotation(Line(points = {{369, 55}, {441, 55}}, color = {0, 0, 127}));
  connect(hinf_tau_y_limit.y, hinf_pitch_wrench_to_angle.u) 
    annotation(Line(points = {{159, -50}, {241, -50}}, color = {0, 0, 127}));
  connect(reference_pitch, hinf_pitch_reference_plus_correction.u1) 
    annotation(Line(points = {{-556, 309}, {-107.5, 309}, {-107.5, -50}, {341, -50}}, color = {0, 0, 127}));
  connect(hinf_pitch_wrench_to_angle.y, hinf_pitch_reference_plus_correction.u2) 
    annotation(Line(points = {{269, -50}, {341, -50}}, color = {0, 0, 127}));
  connect(hinf_pitch_reference_plus_correction.y, hinf_pitch_tilt_limit.u) 
    annotation(Line(points = {{369, -50}, {441, -50}}, color = {0, 0, 127}));
  connect(hinf_tau_z_limit.y, hinf_yaw_wrench_to_angle.u) 
    annotation(Line(points = {{159, -155}, {241, -155}}, color = {0, 0, 127}));
  connect(hinf_yaw_wrench_to_angle.y, hinf_yaw_correction_limit.u) 
    annotation(Line(points = {{269, -155}, {341, -155}}, color = {0, 0, 127}));
  connect(reference_yaw, hinf_yaw_reference_plus_correction.u1) 
    annotation(Line(points = {{-556, 253}, {-57.5, 253}, {-57.5, -155}, {441, -155}}, color = {0, 0, 127}));
  connect(hinf_yaw_correction_limit.y, hinf_yaw_reference_plus_correction.u2) 
    annotation(Line(points = {{369, -155}, {441, -155}}, color = {0, 0, 127}));
  connect(state_error_roll.y, enable_state_error_roll.u1) 
    annotation(Line(points = {{-426, 365}, {60, 365}, {60, 330}, {546, 330}}, color = {0, 0, 127}));
  connect(enable, enable_state_error_roll.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 330}, {546, 330}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_state_error_roll.u3) 
    annotation(Line(points = {{430, -299}, {430, 10}, {560, 10}, {560, 319}}, color = {0, 0, 127}));
  connect(enable_state_error_roll.y, state_error_roll_out) 
    annotation(Line(points = {{574, 330}, {706, 330}}, color = {0, 0, 127}));
  connect(state_error_pitch.y, enable_state_error_pitch.u1) 
    annotation(Line(points = {{-426, 309}, {60, 309}, {60, 292}, {546, 292}}, color = {0, 0, 127}));
  connect(enable, enable_state_error_pitch.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 292}, {546, 292}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_state_error_pitch.u3) 
    annotation(Line(points = {{430, -299}, {430, -9}, {560, -9}, {560, 281}}, color = {0, 0, 127}));
  connect(enable_state_error_pitch.y, state_error_pitch_out) 
    annotation(Line(points = {{574, 292}, {706, 292}}, color = {0, 0, 127}));
  connect(state_error_yaw.y, enable_state_error_yaw.u1) 
    annotation(Line(points = {{-426, 253}, {60, 253}, {60, 254}, {546, 254}}, color = {0, 0, 127}));
  connect(enable, enable_state_error_yaw.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 254}, {546, 254}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_state_error_yaw.u3) 
    annotation(Line(points = {{430, -299}, {430, -28}, {560, -28}, {560, 243}}, color = {0, 0, 127}));
  connect(enable_state_error_yaw.y, state_error_yaw_out) 
    annotation(Line(points = {{574, 254}, {706, 254}}, color = {0, 0, 127}));
  connect(hinf_force_limit.y, enable_wrench_force_n.u1) 
    annotation(Line(points = {{159, 160}, {352.5, 160}, {352.5, 216}, {546, 216}}, color = {0, 0, 127}));
  connect(enable, enable_wrench_force_n.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 216}, {546, 216}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_wrench_force_n.u3) 
    annotation(Line(points = {{430, -299}, {430, -47}, {560, -47}, {560, 205}}, color = {0, 0, 127}));
  connect(enable_wrench_force_n.y, wrench_force_n_out) 
    annotation(Line(points = {{574, 216}, {706, 216}}, color = {0, 0, 127}));
  connect(hinf_tau_x_limit.y, enable_wrench_tau_x_nm.u1) 
    annotation(Line(points = {{159, 55}, {352.5, 55}, {352.5, 178}, {546, 178}}, color = {0, 0, 127}));
  connect(enable, enable_wrench_tau_x_nm.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 178}, {546, 178}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_wrench_tau_x_nm.u3) 
    annotation(Line(points = {{430, -299}, {430, -66}, {560, -66}, {560, 167}}, color = {0, 0, 127}));
  connect(enable_wrench_tau_x_nm.y, wrench_tau_x_nm_out) 
    annotation(Line(points = {{574, 178}, {706, 178}}, color = {0, 0, 127}));
  connect(hinf_tau_y_limit.y, enable_wrench_tau_y_nm.u1) 
    annotation(Line(points = {{159, -50}, {352.5, -50}, {352.5, 140}, {546, 140}}, color = {0, 0, 127}));
  connect(enable, enable_wrench_tau_y_nm.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 140}, {546, 140}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_wrench_tau_y_nm.u3) 
    annotation(Line(points = {{430, -299}, {430, -85}, {560, -85}, {560, 129}}, color = {0, 0, 127}));
  connect(enable_wrench_tau_y_nm.y, wrench_tau_y_nm_out) 
    annotation(Line(points = {{574, 140}, {706, 140}}, color = {0, 0, 127}));
  connect(hinf_tau_z_limit.y, enable_wrench_tau_z_nm.u1) 
    annotation(Line(points = {{159, -155}, {352.5, -155}, {352.5, 102}, {546, 102}}, color = {0, 0, 127}));
  connect(enable, enable_wrench_tau_z_nm.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 102}, {546, 102}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_wrench_tau_z_nm.u3) 
    annotation(Line(points = {{430, -299}, {430, -104}, {560, -104}, {560, 91}}, color = {0, 0, 127}));
  connect(enable_wrench_tau_z_nm.y, wrench_tau_z_nm_out) 
    annotation(Line(points = {{574, 102}, {706, 102}}, color = {0, 0, 127}));
  connect(hinf_force_limit.y, enable_collective_thrust_n.u1) 
    annotation(Line(points = {{159, 160}, {352.5, 160}, {352.5, 64}, {546, 64}}, color = {0, 0, 127}));
  connect(enable, enable_collective_thrust_n.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 64}, {546, 64}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_collective_thrust_n.u3) 
    annotation(Line(points = {{430, -299}, {430, -123}, {560, -123}, {560, 53}}, color = {0, 0, 127}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out) 
    annotation(Line(points = {{574, 64}, {706, 64}}, color = {0, 0, 127}));
  connect(hinf_normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{369, 160}, {457.5, 160}, {457.5, 26}, {546, 26}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, 26}, {546, 26}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{430, -299}, {430, -142}, {560, -142}, {560, 15}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{574, 26}, {706, 26}}, color = {0, 0, 127}));
  connect(hinf_roll_tilt_limit.y, enable_adapted_roll_rad.u1) 
    annotation(Line(points = {{469, 55}, {507.5, 55}, {507.5, -12}, {546, -12}}, color = {0, 0, 127}));
  connect(enable, enable_adapted_roll_rad.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, -12}, {546, -12}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adapted_roll_rad.u3) 
    annotation(Line(points = {{430, -299}, {430, -161}, {560, -161}, {560, -23}}, color = {0, 0, 127}));
  connect(enable_adapted_roll_rad.y, adapted_roll_rad_out) 
    annotation(Line(points = {{574, -12}, {706, -12}}, color = {0, 0, 127}));
  connect(hinf_pitch_tilt_limit.y, enable_adapted_pitch_rad.u1) 
    annotation(Line(points = {{469, -50}, {546, -50}}, color = {0, 0, 127}));
  connect(enable, enable_adapted_pitch_rad.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, -50}, {546, -50}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adapted_pitch_rad.u3) 
    annotation(Line(points = {{430, -299}, {430, -180}, {560, -180}, {560, -61}}, color = {0, 0, 127}));
  connect(enable_adapted_pitch_rad.y, adapted_pitch_rad_out) 
    annotation(Line(points = {{574, -50}, {706, -50}}, color = {0, 0, 127}));
  connect(hinf_yaw_reference_plus_correction.y, enable_adapted_yaw_rad.u1) 
    annotation(Line(points = {{469, -155}, {507.5, -155}, {507.5, -88}, {546, -88}}, color = {0, 0, 127}));
  connect(enable, enable_adapted_yaw_rad.u2) 
    annotation(Line(points = {{-646, -355}, {-50, -355}, {-50, -88}, {546, -88}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_adapted_yaw_rad.u3) 
    annotation(Line(points = {{430, -299}, {430, -199}, {560, -199}, {560, -99}}, color = {0, 0, 127}));
  connect(enable_adapted_yaw_rad.y, adapted_yaw_rad_out) 
    annotation(Line(points = {{574, -88}, {706, -88}}, color = {0, 0, 127}));

end HinfHoverWrenchCore;