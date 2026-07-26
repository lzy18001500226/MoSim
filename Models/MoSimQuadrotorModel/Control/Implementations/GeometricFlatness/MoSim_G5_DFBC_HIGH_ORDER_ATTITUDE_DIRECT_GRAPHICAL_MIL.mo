within MoSimQuadrotorModel.Control.Implementations.GeometricFlatness;
model MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL "Direct graphical high-order DFBC with attitude/thrust adapter"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, body_rate_x, body_rate_y, body_rate_z, dt, enable), Right(position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, sliding_surface_x_out, sliding_surface_y_out, sliding_surface_z_out, surface_rate_x_out, surface_rate_y_out, surface_rate_z_out, disturbance_estimate_x_out, disturbance_estimate_y_out, disturbance_estimate_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Port.Inport position_x
    annotation (Placement(transformation(origin = {-780, 500}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_y
    annotation (Placement(transformation(origin = {-780, 472}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_z
    annotation (Placement(transformation(origin = {-780, 444}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_x
    annotation (Placement(transformation(origin = {-780, 378}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_y
    annotation (Placement(transformation(origin = {-780, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_z
    annotation (Placement(transformation(origin = {-780, 322}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x
    annotation (Placement(transformation(origin = {-780, 256}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y
    annotation (Placement(transformation(origin = {-780, 228}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z
    annotation (Placement(transformation(origin = {-780, 200}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x
    annotation (Placement(transformation(origin = {-780, 134}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y
    annotation (Placement(transformation(origin = {-780, 106}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z
    annotation (Placement(transformation(origin = {-780, 78}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x
    annotation (Placement(transformation(origin = {-780, 12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y
    annotation (Placement(transformation(origin = {-780, -16}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z
    annotation (Placement(transformation(origin = {-780, -44}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport body_rate_x
    annotation (Placement(transformation(origin = {-780, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport body_rate_y
    annotation (Placement(transformation(origin = {-780, -138}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport body_rate_z
    annotation (Placement(transformation(origin = {-780, -166}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport dt
    annotation (Placement(transformation(origin = {-780, -310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable
    annotation (Placement(transformation(origin = {-780, -350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0)
    annotation (Placement(transformation(origin = {660, -385}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-650, 312}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-")
    annotation (Placement(transformation(origin = {-650, 208}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_x(k=1.7)
    annotation (Placement(transformation(origin = {-510, 312}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_x(k=1.2)
    annotation (Placement(transformation(origin = {-510, 208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_x
    annotation (Placement(transformation(origin = {-365, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_surface_x(initCond=0.0)
    annotation (Placement(transformation(origin = {-365, 175}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum surface_delta_x(inputs="+-")
    annotation (Placement(transformation(origin = {-220, 235}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain surface_rate_x(k=100.0)
    annotation (Placement(transformation(origin = {-95, 235}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain high_order_rate_feedback_x(k=0.045)
    annotation (Placement(transformation(origin = {25, 235}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_feedback_x
    annotation (Placement(transformation(origin = {135, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_desired_acceleration_x
    annotation (Placement(transformation(origin = {280, 260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant high_order_disturbance_path_x(k=0.0)
    annotation (Placement(transformation(origin = {135, 150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation high_order_acceleration_limit_x(lowLimit=-4.0,upLimit=4.0)
    annotation (Placement(transformation(origin = {410, 260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-650, 27}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-")
    annotation (Placement(transformation(origin = {-650, -77}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_y(k=1.7)
    annotation (Placement(transformation(origin = {-510, 27}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_y(k=1.2)
    annotation (Placement(transformation(origin = {-510, -77}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_y
    annotation (Placement(transformation(origin = {-365, -25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_surface_y(initCond=0.0)
    annotation (Placement(transformation(origin = {-365, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum surface_delta_y(inputs="+-")
    annotation (Placement(transformation(origin = {-220, -50}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain surface_rate_y(k=100.0)
    annotation (Placement(transformation(origin = {-95, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain high_order_rate_feedback_y(k=0.045)
    annotation (Placement(transformation(origin = {25, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_feedback_y
    annotation (Placement(transformation(origin = {135, -25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_desired_acceleration_y
    annotation (Placement(transformation(origin = {280, -25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant high_order_disturbance_path_y(k=0.0)
    annotation (Placement(transformation(origin = {135, -135}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation high_order_acceleration_limit_y(lowLimit=-4.0,upLimit=4.0)
    annotation (Placement(transformation(origin = {410, -25}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-650, -258}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-")
    annotation (Placement(transformation(origin = {-650, -362}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_z(k=2.1)
    annotation (Placement(transformation(origin = {-510, -258}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_z(k=1.55)
    annotation (Placement(transformation(origin = {-510, -362}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_z
    annotation (Placement(transformation(origin = {-365, -310}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_surface_z(initCond=0.0)
    annotation (Placement(transformation(origin = {-365, -395}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum surface_delta_z(inputs="+-")
    annotation (Placement(transformation(origin = {-220, -335}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain surface_rate_z(k=100.0)
    annotation (Placement(transformation(origin = {-95, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain high_order_rate_feedback_z(k=0.06)
    annotation (Placement(transformation(origin = {25, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_feedback_z
    annotation (Placement(transformation(origin = {135, -310}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum high_order_desired_acceleration_z
    annotation (Placement(transformation(origin = {280, -310}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant high_order_disturbance_path_z(k=0.0)
    annotation (Placement(transformation(origin = {135, -420}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation high_order_acceleration_limit_z(lowLimit=-3.0,upLimit=3.0)
    annotation (Placement(transformation(origin = {410, -310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain attitude_roll_from_lateral_acceleration(k=-0.10197162129779283)
    annotation (Placement(transformation(origin = {745, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain attitude_pitch_from_lateral_acceleration(k=0.10197162129779283)
    annotation (Placement(transformation(origin = {745, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation attitude_roll_tilt_limit(lowLimit=-0.52,upLimit=0.52)
    annotation (Placement(transformation(origin = {855, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation attitude_pitch_tilt_limit(lowLimit=-0.52,upLimit=0.52)
    annotation (Placement(transformation(origin = {855, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665)
    annotation (Placement(transformation(origin = {745, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum collective_thrust_pre_normalization
    annotation (Placement(transformation(origin = {855, -155}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain normalized_thrust_scaling(k=0.03772949988018335)
    annotation (Placement(transformation(origin = {965, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation normalized_thrust_limit(lowLimit=0.0,upLimit=1.0)
    annotation (Placement(transformation(origin = {1075, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 445}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out
    annotation (Placement(transformation(origin = {1345, 445}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 406}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out
    annotation (Placement(transformation(origin = {1345, 406}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 367}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out
    annotation (Placement(transformation(origin = {1345, 367}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 328}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out
    annotation (Placement(transformation(origin = {1345, 328}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 289}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out
    annotation (Placement(transformation(origin = {1345, 289}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out
    annotation (Placement(transformation(origin = {1345, 250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 211}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_x_out
    annotation (Placement(transformation(origin = {1345, 211}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 172}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_y_out
    annotation (Placement(transformation(origin = {1345, 172}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_sliding_surface_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 133}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_z_out
    annotation (Placement(transformation(origin = {1345, 133}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_surface_rate_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport surface_rate_x_out
    annotation (Placement(transformation(origin = {1345, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_surface_rate_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport surface_rate_y_out
    annotation (Placement(transformation(origin = {1345, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_surface_rate_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, 16}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport surface_rate_z_out
    annotation (Placement(transformation(origin = {1345, 16}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_disturbance_estimate_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -23}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_x_out
    annotation (Placement(transformation(origin = {1345, -23}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_disturbance_estimate_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -62}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_y_out
    annotation (Placement(transformation(origin = {1345, -62}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_disturbance_estimate_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -101}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport disturbance_estimate_z_out
    annotation (Placement(transformation(origin = {1345, -101}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out
    annotation (Placement(transformation(origin = {1345, -140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -179}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out
    annotation (Placement(transformation(origin = {1345, -179}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -218}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out
    annotation (Placement(transformation(origin = {1345, -218}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -257}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out
    annotation (Placement(transformation(origin = {1345, -257}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out
    annotation (Placement(transformation(origin = {1345, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5)
    annotation (Placement(transformation(origin = {1185, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out
    annotation (Placement(transformation(origin = {1345, -335}, extent = {{-14, -11}, {14, 11}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(reference_position_x, position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x, position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_x, velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_x, velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, position_feedback_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, velocity_feedback_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_feedback_x.y, sliding_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_feedback_x.y, sliding_surface_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_x.y, previous_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_x.y, surface_delta_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_surface_x.y, surface_delta_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_delta_x.y, surface_rate_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_x.y, high_order_rate_feedback_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_x.y, high_order_feedback_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_rate_feedback_x.y, high_order_feedback_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x, high_order_desired_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_feedback_x.y, high_order_desired_acceleration_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_desired_acceleration_x.y, high_order_acceleration_limit_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y, position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y, position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_y, velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_y, velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, position_feedback_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, velocity_feedback_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_feedback_y.y, sliding_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_feedback_y.y, sliding_surface_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_y.y, previous_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_y.y, surface_delta_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_surface_y.y, surface_delta_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_delta_y.y, surface_rate_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_y.y, high_order_rate_feedback_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_y.y, high_order_feedback_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_rate_feedback_y.y, high_order_feedback_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y, high_order_desired_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_feedback_y.y, high_order_desired_acceleration_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_desired_acceleration_y.y, high_order_acceleration_limit_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z, position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z, position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_z, velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_z, velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, position_feedback_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, velocity_feedback_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_feedback_z.y, sliding_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_feedback_z.y, sliding_surface_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_z.y, previous_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_z.y, surface_delta_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_surface_z.y, surface_delta_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_delta_z.y, surface_rate_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_z.y, high_order_rate_feedback_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_z.y, high_order_feedback_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_rate_feedback_z.y, high_order_feedback_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z, high_order_desired_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_feedback_z.y, high_order_desired_acceleration_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_desired_acceleration_z.y, high_order_acceleration_limit_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_y.y, attitude_roll_from_lateral_acceleration.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_x.y, attitude_pitch_from_lateral_acceleration.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(attitude_roll_from_lateral_acceleration.y, attitude_roll_tilt_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(attitude_pitch_from_lateral_acceleration.y, attitude_pitch_tilt_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_z.y, collective_thrust_pre_normalization.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gravity_compensation.y, collective_thrust_pre_normalization.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(collective_thrust_pre_normalization.y, normalized_thrust_scaling.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_scaling.y, normalized_thrust_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, enable_position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_x.y, position_error_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, enable_position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_y.y, position_error_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, enable_position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_position_error_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_position_error_z.y, position_error_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, enable_velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_x.y, velocity_error_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, enable_velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_y.y, velocity_error_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, enable_velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_velocity_error_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_velocity_error_z.y, velocity_error_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_x.y, enable_sliding_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_x.y, sliding_surface_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_y.y, enable_sliding_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_y.y, sliding_surface_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(sliding_surface_z.y, enable_sliding_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_sliding_surface_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_sliding_surface_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_sliding_surface_z.y, sliding_surface_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_x.y, enable_surface_rate_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_surface_rate_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_surface_rate_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_surface_rate_x.y, surface_rate_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_y.y, enable_surface_rate_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_surface_rate_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_surface_rate_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_surface_rate_y.y, surface_rate_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(surface_rate_z.y, enable_surface_rate_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_surface_rate_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_surface_rate_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_surface_rate_z.y, surface_rate_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_disturbance_path_x.y, enable_disturbance_estimate_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_disturbance_estimate_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_disturbance_estimate_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_disturbance_estimate_x.y, disturbance_estimate_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_disturbance_path_y.y, enable_disturbance_estimate_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_disturbance_estimate_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_disturbance_estimate_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_disturbance_estimate_y.y, disturbance_estimate_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_disturbance_path_z.y, enable_disturbance_estimate_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_disturbance_estimate_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_disturbance_estimate_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_disturbance_estimate_z.y, disturbance_estimate_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_x.y, enable_desired_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_y.y, enable_desired_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(high_order_acceleration_limit_z.y, enable_desired_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_acceleration_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(attitude_roll_tilt_limit.y, enable_desired_roll_rad.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_roll_rad.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_roll_rad.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(attitude_pitch_tilt_limit.y, enable_desired_pitch_rad.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_desired_pitch_rad.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_normalized_thrust.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(disabled_command.y, enable_normalized_thrust.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_normalized_thrust.y, normalized_thrust_out)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL;