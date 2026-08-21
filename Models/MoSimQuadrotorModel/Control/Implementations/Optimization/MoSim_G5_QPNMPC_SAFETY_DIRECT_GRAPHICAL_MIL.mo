within MoSimQuadrotorModel.Control.Implementations.Optimization;

model MoSim_G5_QPNMPC_SAFETY_DIRECT_GRAPHICAL_MIL "Direct graphical QP/NMPC safety projection core"
  import BaseWorkspace.*;
  import SysplorerEmbeddedCoder.Types.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(x_error, y_error, z_error, z_ref_rate, roll_mea, pitch_mea, yaw_mea, yaw_ref, safety_override), Right(nmpc_scale_out, safety_active_out, motor1_command_out, motor2_command_out, motor3_command_out, motor4_command_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true)),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  SysplorerEmbeddedCoder.Port.Inport x_error
    annotation (Placement(transformation(origin = {-700, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport y_error
    annotation (Placement(transformation(origin = {-700, 262}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport z_error
    annotation (Placement(transformation(origin = {-700, 194}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate
    annotation (Placement(transformation(origin = {-700, 126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea
    annotation (Placement(transformation(origin = {-700, 58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea
    annotation (Placement(transformation(origin = {-700, -10}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea
    annotation (Placement(transformation(origin = {-700, -78}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref
    annotation (Placement(transformation(origin = {-700, -146}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport safety_override
    annotation (Placement(transformation(origin = {-700, -214}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant zero(k=0.0)
    annotation (Placement(transformation(origin = {810, -320}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant one(k=1.0)
    annotation (Placement(transformation(origin = {-525, -250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_roll_square(inputs="**")
    annotation (Placement(transformation(origin = {-525, -75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_pitch_square(inputs="**")
    annotation (Placement(transformation(origin = {-525, -125}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_tilt_norm_square
    annotation (Placement(transformation(origin = {-380, -100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_tilt_softening(k=0.02)
    annotation (Placement(transformation(origin = {-240, -100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_softening_denominator
    annotation (Placement(transformation(origin = {-95, -100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_scale(inputs="*/")
    annotation (Placement(transformation(origin = {45, -100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain altitude_cbf_gain(k=0.25)
    annotation (Placement(transformation(origin = {-240, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation altitude_cbf_correction(lowLimit=0.0,upLimit=2.0)
    annotation (Placement(transformation(origin = {-95, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Abs safety_abs_x_error
    annotation (Placement(transformation(origin = {-525, -235}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Abs safety_abs_y_error
    annotation (Placement(transformation(origin = {-425, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Abs safety_abs_z_error
    annotation (Placement(transformation(origin = {-325, -305}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum safety_error_norm_l1_stage_2
    annotation (Placement(transformation(origin = {-243, -270}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum safety_error_norm_l1
    annotation (Placement(transformation(origin = {-185, -270}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain safety_threshold_normalization(k=1.3333333333333333)
    annotation (Placement(transformation(origin = {-45, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation safety_active_indicator(lowLimit=0.0,upLimit=1.0)
    annotation (Placement(transformation(origin = {95, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum safety_signal_combine
    annotation (Placement(transformation(origin = {245, -270}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation safety_event_selector(lowLimit=0.0,upLimit=1.0)
    annotation (Placement(transformation(origin = {390, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor1_z_tracking(k=2.0)
    annotation (Placement(transformation(origin = {-385, 230}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor1_roll_coupling(k=0.7)
    annotation (Placement(transformation(origin = {-385, 202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor1_pitch_coupling(k=-0.7)
    annotation (Placement(transformation(origin = {-385, 174}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor1_yaw_coupling(k=0.1)
    annotation (Placement(transformation(origin = {-385, 146}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor1_nominal_raw_stage_2
    annotation (Placement(transformation(origin = {-246, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor1_nominal_raw_stage_3
    annotation (Placement(transformation(origin = {-188, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor1_nominal_raw
    annotation (Placement(transformation(origin = {-130, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_motor1_tilt_softened_nominal(inputs="**")
    annotation (Placement(transformation(origin = {55, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor1_altitude_cbf_sign(k=1.0)
    annotation (Placement(transformation(origin = {170, 204}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor1_nominal_with_cbf
    annotation (Placement(transformation(origin = {285, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain qp_motor1_regularization(k=0.5)
    annotation (Placement(transformation(origin = {400, 174}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum qp_motor1_candidate(inputs="+-")
    annotation (Placement(transformation(origin = {510, 204}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor1_projection_stage1(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {625, 204}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor1_projection_stage2(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {735, 204}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant safety_motor1_fallback(k=-0.25)
    annotation (Placement(transformation(origin = {735, 138}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch safety_motor1_event_branch(threshold=0.5)
    annotation (Placement(transformation(origin = {850, 204}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor2_z_tracking(k=2.0)
    annotation (Placement(transformation(origin = {-385, 112}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor2_roll_coupling(k=-0.7)
    annotation (Placement(transformation(origin = {-385, 84}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor2_pitch_coupling(k=-0.7)
    annotation (Placement(transformation(origin = {-385, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor2_yaw_coupling(k=-0.1)
    annotation (Placement(transformation(origin = {-385, 28}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor2_nominal_raw_stage_2
    annotation (Placement(transformation(origin = {-246, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor2_nominal_raw_stage_3
    annotation (Placement(transformation(origin = {-188, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor2_nominal_raw
    annotation (Placement(transformation(origin = {-130, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_motor2_tilt_softened_nominal(inputs="**")
    annotation (Placement(transformation(origin = {55, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor2_altitude_cbf_sign(k=-1.0)
    annotation (Placement(transformation(origin = {170, 86}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor2_nominal_with_cbf
    annotation (Placement(transformation(origin = {285, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain qp_motor2_regularization(k=0.5)
    annotation (Placement(transformation(origin = {400, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum qp_motor2_candidate(inputs="+-")
    annotation (Placement(transformation(origin = {510, 86}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor2_projection_stage1(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {625, 86}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor2_projection_stage2(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {735, 86}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant safety_motor2_fallback(k=-0.25)
    annotation (Placement(transformation(origin = {735, 20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch safety_motor2_event_branch(threshold=0.5)
    annotation (Placement(transformation(origin = {850, 86}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor3_z_tracking(k=2.0)
    annotation (Placement(transformation(origin = {-385, -6}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor3_roll_coupling(k=-0.7)
    annotation (Placement(transformation(origin = {-385, -34}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor3_pitch_coupling(k=0.7)
    annotation (Placement(transformation(origin = {-385, -62}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor3_yaw_coupling(k=0.1)
    annotation (Placement(transformation(origin = {-385, -90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor3_nominal_raw_stage_2
    annotation (Placement(transformation(origin = {-246, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor3_nominal_raw_stage_3
    annotation (Placement(transformation(origin = {-188, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor3_nominal_raw
    annotation (Placement(transformation(origin = {-130, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_motor3_tilt_softened_nominal(inputs="**")
    annotation (Placement(transformation(origin = {55, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor3_altitude_cbf_sign(k=1.0)
    annotation (Placement(transformation(origin = {170, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor3_nominal_with_cbf
    annotation (Placement(transformation(origin = {285, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain qp_motor3_regularization(k=0.5)
    annotation (Placement(transformation(origin = {400, -62}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum qp_motor3_candidate(inputs="+-")
    annotation (Placement(transformation(origin = {510, -32}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor3_projection_stage1(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {625, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor3_projection_stage2(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {735, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant safety_motor3_fallback(k=-0.25)
    annotation (Placement(transformation(origin = {735, -98}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch safety_motor3_event_branch(threshold=0.5)
    annotation (Placement(transformation(origin = {850, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor4_z_tracking(k=2.0)
    annotation (Placement(transformation(origin = {-385, -124}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor4_roll_coupling(k=0.7)
    annotation (Placement(transformation(origin = {-385, -152}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor4_pitch_coupling(k=0.7)
    annotation (Placement(transformation(origin = {-385, -180}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor4_yaw_coupling(k=-0.1)
    annotation (Placement(transformation(origin = {-385, -208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor4_nominal_raw_stage_2
    annotation (Placement(transformation(origin = {-246, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor4_nominal_raw_stage_3
    annotation (Placement(transformation(origin = {-188, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor4_nominal_raw
    annotation (Placement(transformation(origin = {-130, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product nmpc_motor4_tilt_softened_nominal(inputs="**")
    annotation (Placement(transformation(origin = {55, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain nmpc_motor4_altitude_cbf_sign(k=-1.0)
    annotation (Placement(transformation(origin = {170, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum nmpc_motor4_nominal_with_cbf
    annotation (Placement(transformation(origin = {285, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain qp_motor4_regularization(k=0.5)
    annotation (Placement(transformation(origin = {400, -180}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum qp_motor4_candidate(inputs="+-")
    annotation (Placement(transformation(origin = {510, -150}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor4_projection_stage1(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {625, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation qp_motor4_projection_stage2(lowLimit=-20.0,upLimit=20.0)
    annotation (Placement(transformation(origin = {735, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant safety_motor4_fallback(k=-0.25)
    annotation (Placement(transformation(origin = {735, -216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch safety_motor4_event_branch(threshold=0.5)
    annotation (Placement(transformation(origin = {850, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport nmpc_scale_out
    annotation (Placement(transformation(origin = {1015, 280}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport safety_active_out
    annotation (Placement(transformation(origin = {1015, 195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport motor1_command_out
    annotation (Placement(transformation(origin = {1015, 110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport motor2_command_out
    annotation (Placement(transformation(origin = {1015, 25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport motor3_command_out
    annotation (Placement(transformation(origin = {1015, -60}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport motor4_command_out
    annotation (Placement(transformation(origin = {1015, -145}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(roll_mea, nmpc_roll_square.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, nmpc_roll_square.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_pitch_square.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_pitch_square.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_roll_square.y, nmpc_tilt_norm_square.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_pitch_square.y, nmpc_tilt_norm_square.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_tilt_norm_square.y, nmpc_tilt_softening.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(one.y, nmpc_softening_denominator.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_tilt_softening.y, nmpc_softening_denominator.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(one.y, nmpc_scale.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_softening_denominator.y, nmpc_scale.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, altitude_cbf_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(altitude_cbf_gain.y, altitude_cbf_correction.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(x_error, safety_abs_x_error.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(y_error, safety_abs_y_error.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, safety_abs_z_error.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_abs_x_error.y, safety_error_norm_l1_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_abs_y_error.y, safety_error_norm_l1_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_error_norm_l1_stage_2.y, safety_error_norm_l1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_abs_z_error.y, safety_error_norm_l1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_error_norm_l1.y, safety_threshold_normalization.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_threshold_normalization.y, safety_active_indicator.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_active_indicator.y, safety_signal_combine.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_override, safety_signal_combine.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_signal_combine.y, safety_event_selector.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, nmpc_motor1_z_tracking.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, nmpc_motor1_roll_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_motor1_pitch_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_mea, nmpc_motor1_yaw_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_z_tracking.y, nmpc_motor1_nominal_raw_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_roll_coupling.y, nmpc_motor1_nominal_raw_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_nominal_raw_stage_2.y, nmpc_motor1_nominal_raw_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_pitch_coupling.y, nmpc_motor1_nominal_raw_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_nominal_raw_stage_3.y, nmpc_motor1_nominal_raw.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_yaw_coupling.y, nmpc_motor1_nominal_raw.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_scale.y, nmpc_motor1_tilt_softened_nominal.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_nominal_raw.y, nmpc_motor1_tilt_softened_nominal.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(altitude_cbf_correction.y, nmpc_motor1_altitude_cbf_sign.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_tilt_softened_nominal.y, nmpc_motor1_nominal_with_cbf.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_altitude_cbf_sign.y, nmpc_motor1_nominal_with_cbf.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_nominal_with_cbf.y, qp_motor1_regularization.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor1_nominal_with_cbf.y, qp_motor1_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor1_regularization.y, qp_motor1_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor1_candidate.y, qp_motor1_projection_stage1.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor1_projection_stage1.y, qp_motor1_projection_stage2.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor1_projection_stage2.y, safety_motor1_event_branch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_event_selector.y, safety_motor1_event_branch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor1_fallback.y, safety_motor1_event_branch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, nmpc_motor2_z_tracking.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, nmpc_motor2_roll_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_motor2_pitch_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_mea, nmpc_motor2_yaw_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_z_tracking.y, nmpc_motor2_nominal_raw_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_roll_coupling.y, nmpc_motor2_nominal_raw_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_nominal_raw_stage_2.y, nmpc_motor2_nominal_raw_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_pitch_coupling.y, nmpc_motor2_nominal_raw_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_nominal_raw_stage_3.y, nmpc_motor2_nominal_raw.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_yaw_coupling.y, nmpc_motor2_nominal_raw.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_scale.y, nmpc_motor2_tilt_softened_nominal.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_nominal_raw.y, nmpc_motor2_tilt_softened_nominal.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(altitude_cbf_correction.y, nmpc_motor2_altitude_cbf_sign.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_tilt_softened_nominal.y, nmpc_motor2_nominal_with_cbf.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_altitude_cbf_sign.y, nmpc_motor2_nominal_with_cbf.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_nominal_with_cbf.y, qp_motor2_regularization.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor2_nominal_with_cbf.y, qp_motor2_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor2_regularization.y, qp_motor2_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor2_candidate.y, qp_motor2_projection_stage1.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor2_projection_stage1.y, qp_motor2_projection_stage2.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor2_projection_stage2.y, safety_motor2_event_branch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_event_selector.y, safety_motor2_event_branch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor2_fallback.y, safety_motor2_event_branch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, nmpc_motor3_z_tracking.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, nmpc_motor3_roll_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_motor3_pitch_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_mea, nmpc_motor3_yaw_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_z_tracking.y, nmpc_motor3_nominal_raw_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_roll_coupling.y, nmpc_motor3_nominal_raw_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_nominal_raw_stage_2.y, nmpc_motor3_nominal_raw_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_pitch_coupling.y, nmpc_motor3_nominal_raw_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_nominal_raw_stage_3.y, nmpc_motor3_nominal_raw.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_yaw_coupling.y, nmpc_motor3_nominal_raw.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_scale.y, nmpc_motor3_tilt_softened_nominal.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_nominal_raw.y, nmpc_motor3_tilt_softened_nominal.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(altitude_cbf_correction.y, nmpc_motor3_altitude_cbf_sign.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_tilt_softened_nominal.y, nmpc_motor3_nominal_with_cbf.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_altitude_cbf_sign.y, nmpc_motor3_nominal_with_cbf.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_nominal_with_cbf.y, qp_motor3_regularization.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor3_nominal_with_cbf.y, qp_motor3_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor3_regularization.y, qp_motor3_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor3_candidate.y, qp_motor3_projection_stage1.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor3_projection_stage1.y, qp_motor3_projection_stage2.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor3_projection_stage2.y, safety_motor3_event_branch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_event_selector.y, safety_motor3_event_branch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor3_fallback.y, safety_motor3_event_branch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(z_error, nmpc_motor4_z_tracking.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(roll_mea, nmpc_motor4_roll_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pitch_mea, nmpc_motor4_pitch_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(yaw_mea, nmpc_motor4_yaw_coupling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_z_tracking.y, nmpc_motor4_nominal_raw_stage_2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_roll_coupling.y, nmpc_motor4_nominal_raw_stage_2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_nominal_raw_stage_2.y, nmpc_motor4_nominal_raw_stage_3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_pitch_coupling.y, nmpc_motor4_nominal_raw_stage_3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_nominal_raw_stage_3.y, nmpc_motor4_nominal_raw.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_yaw_coupling.y, nmpc_motor4_nominal_raw.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_scale.y, nmpc_motor4_tilt_softened_nominal.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_nominal_raw.y, nmpc_motor4_tilt_softened_nominal.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(altitude_cbf_correction.y, nmpc_motor4_altitude_cbf_sign.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_tilt_softened_nominal.y, nmpc_motor4_nominal_with_cbf.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_altitude_cbf_sign.y, nmpc_motor4_nominal_with_cbf.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_nominal_with_cbf.y, qp_motor4_regularization.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_motor4_nominal_with_cbf.y, qp_motor4_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor4_regularization.y, qp_motor4_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor4_candidate.y, qp_motor4_projection_stage1.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor4_projection_stage1.y, qp_motor4_projection_stage2.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(qp_motor4_projection_stage2.y, safety_motor4_event_branch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_event_selector.y, safety_motor4_event_branch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor4_fallback.y, safety_motor4_event_branch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(nmpc_scale.y, nmpc_scale_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_event_selector.y, safety_active_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor1_event_branch.y, motor1_command_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor2_event_branch.y, motor2_command_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor3_event_branch.y, motor3_command_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(safety_motor4_event_branch.y, motor4_command_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_G5_QPNMPC_SAFETY_DIRECT_GRAPHICAL_MIL;
