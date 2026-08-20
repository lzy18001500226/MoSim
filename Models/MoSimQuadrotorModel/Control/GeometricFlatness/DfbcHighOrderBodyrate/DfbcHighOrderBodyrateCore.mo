within MoSimQuadrotorModel.Control.GeometricFlatness.DfbcHighOrderBodyrate;
model DfbcHighOrderBodyrateCore "Direct graphical high-order DFBC with body-rate/thrust adapter"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, body_rate_x, body_rate_y, body_rate_z, dt, enable), Right(position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, sliding_surface_x_out, sliding_surface_y_out, sliding_surface_z_out, surface_rate_x_out, surface_rate_y_out, surface_rate_z_out, disturbance_estimate_x_out, disturbance_estimate_y_out, disturbance_estimate_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, desired_body_rate_x_out, desired_body_rate_y_out, desired_body_rate_z_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
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
  SysplorerEmbeddedCoder.MathOperation.Gain body_rate_from_acceleration_x(k=0.72) 
    annotation (Placement(transformation(origin = {745, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation body_rate_limit_x(lowLimit=-6.0,upLimit=6.0) 
    annotation (Placement(transformation(origin = {855, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain body_rate_from_acceleration_y(k=0.72) 
    annotation (Placement(transformation(origin = {745, 83}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation body_rate_limit_y(lowLimit=-6.0,upLimit=6.0) 
    annotation (Placement(transformation(origin = {855, 83}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain body_rate_from_acceleration_z(k=0.55) 
    annotation (Placement(transformation(origin = {745, 11}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation body_rate_limit_z(lowLimit=-3.0,upLimit=3.0) 
    annotation (Placement(transformation(origin = {855, 11}, extent = {{-14, -11}, {14, 11}})));
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
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_body_rate_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {1185, -257}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_x_out 
    annotation (Placement(transformation(origin = {1345, -257}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_body_rate_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {1185, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_y_out 
    annotation (Placement(transformation(origin = {1345, -296}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_body_rate_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {1185, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_body_rate_z_out 
    annotation (Placement(transformation(origin = {1345, -335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5) 
    annotation (Placement(transformation(origin = {1185, -374}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin = {1345, -374}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(reference_position_x, position_error_x.u1) 
    annotation(Line(points = {{-766, 256}, {-715, 256}, {-715, 312}, {-664, 312}}, color = {0, 0, 127}));
  connect(position_x, position_error_x.u2) 
    annotation(Line(points = {{-780, 489}, {-780, 406}, {-650, 406}, {-650, 323}}, color = {0, 0, 127}));
  connect(reference_velocity_x, velocity_error_x.u1) 
    annotation(Line(points = {{-766, 134}, {-715, 134}, {-715, 208}, {-664, 208}}, color = {0, 0, 127}));
  connect(velocity_x, velocity_error_x.u2) 
    annotation(Line(points = {{-780, 367}, {-780, 293}, {-650, 293}, {-650, 219}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_feedback_x.u) 
    annotation(Line(points = {{-636, 312}, {-524, 312}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, velocity_feedback_x.u) 
    annotation(Line(points = {{-636, 208}, {-524, 208}}, color = {0, 0, 127}));
  connect(position_feedback_x.y, sliding_surface_x.u1) 
    annotation(Line(points = {{-496, 312}, {-437.5, 312}, {-437.5, 260}, {-379, 260}}, color = {0, 0, 127}));
  connect(velocity_feedback_x.y, sliding_surface_x.u2) 
    annotation(Line(points = {{-496, 208}, {-437.5, 208}, {-437.5, 260}, {-379, 260}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, previous_surface_x.u1) 
    annotation(Line(points = {{-365, 249}, {-365, 186}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, surface_delta_x.u1) 
    annotation(Line(points = {{-351, 260}, {-292.5, 260}, {-292.5, 235}, {-234, 235}}, color = {0, 0, 127}));
  connect(previous_surface_x.y, surface_delta_x.u2) 
    annotation(Line(points = {{-351, 175}, {-292.5, 175}, {-292.5, 235}, {-234, 235}}, color = {0, 0, 127}));
  connect(surface_delta_x.y, surface_rate_x.u) 
    annotation(Line(points = {{-206, 235}, {-109, 235}}, color = {0, 0, 127}));
  connect(surface_rate_x.y, high_order_rate_feedback_x.u) 
    annotation(Line(points = {{-81, 235}, {11, 235}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, high_order_feedback_x.u1) 
    annotation(Line(points = {{-351, 260}, {121, 260}}, color = {0, 0, 127}));
  connect(high_order_rate_feedback_x.y, high_order_feedback_x.u2) 
    annotation(Line(points = {{39, 235}, {80, 235}, {80, 260}, {121, 260}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, high_order_desired_acceleration_x.u1) 
    annotation(Line(points = {{-766, 12}, {-250, 12}, {-250, 260}, {266, 260}}, color = {0, 0, 127}));
  connect(high_order_feedback_x.y, high_order_desired_acceleration_x.u2) 
    annotation(Line(points = {{149, 260}, {266, 260}}, color = {0, 0, 127}));
  connect(high_order_desired_acceleration_x.y, high_order_acceleration_limit_x.u) 
    annotation(Line(points = {{294, 260}, {396, 260}}, color = {0, 0, 127}));
  connect(reference_position_y, position_error_y.u1) 
    annotation(Line(points = {{-780, 217}, {-780, 127.5}, {-650, 127.5}, {-650, 38}}, color = {0, 0, 127}));
  connect(position_y, position_error_y.u2) 
    annotation(Line(points = {{-780, 461}, {-780, 249.5}, {-650, 249.5}, {-650, 38}}, color = {0, 0, 127}));
  connect(reference_velocity_y, velocity_error_y.u1) 
    annotation(Line(points = {{-780, 95}, {-780, 14.5}, {-650, 14.5}, {-650, -66}}, color = {0, 0, 127}));
  connect(velocity_y, velocity_error_y.u2) 
    annotation(Line(points = {{-780, 339}, {-780, 136.5}, {-650, 136.5}, {-650, -66}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_feedback_y.u) 
    annotation(Line(points = {{-636, 27}, {-524, 27}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, velocity_feedback_y.u) 
    annotation(Line(points = {{-636, -77}, {-524, -77}}, color = {0, 0, 127}));
  connect(position_feedback_y.y, sliding_surface_y.u1) 
    annotation(Line(points = {{-496, 27}, {-437.5, 27}, {-437.5, -25}, {-379, -25}}, color = {0, 0, 127}));
  connect(velocity_feedback_y.y, sliding_surface_y.u2) 
    annotation(Line(points = {{-496, -77}, {-437.5, -77}, {-437.5, -25}, {-379, -25}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, previous_surface_y.u1) 
    annotation(Line(points = {{-365, -36}, {-365, -99}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, surface_delta_y.u1) 
    annotation(Line(points = {{-351, -25}, {-292.5, -25}, {-292.5, -50}, {-234, -50}}, color = {0, 0, 127}));
  connect(previous_surface_y.y, surface_delta_y.u2) 
    annotation(Line(points = {{-351, -110}, {-292.5, -110}, {-292.5, -50}, {-234, -50}}, color = {0, 0, 127}));
  connect(surface_delta_y.y, surface_rate_y.u) 
    annotation(Line(points = {{-206, -50}, {-109, -50}}, color = {0, 0, 127}));
  connect(surface_rate_y.y, high_order_rate_feedback_y.u) 
    annotation(Line(points = {{-81, -50}, {11, -50}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, high_order_feedback_y.u1) 
    annotation(Line(points = {{-351, -25}, {121, -25}}, color = {0, 0, 127}));
  connect(high_order_rate_feedback_y.y, high_order_feedback_y.u2) 
    annotation(Line(points = {{39, -50}, {80, -50}, {80, -25}, {121, -25}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, high_order_desired_acceleration_y.u1) 
    annotation(Line(points = {{-766, -16}, {-250, -16}, {-250, -25}, {266, -25}}, color = {0, 0, 127}));
  connect(high_order_feedback_y.y, high_order_desired_acceleration_y.u2) 
    annotation(Line(points = {{149, -25}, {266, -25}}, color = {0, 0, 127}));
  connect(high_order_desired_acceleration_y.y, high_order_acceleration_limit_y.u) 
    annotation(Line(points = {{294, -25}, {396, -25}}, color = {0, 0, 127}));
  connect(reference_position_z, position_error_z.u1) 
    annotation(Line(points = {{-780, 189}, {-780, -29}, {-650, -29}, {-650, -247}}, color = {0, 0, 127}));
  connect(position_z, position_error_z.u2) 
    annotation(Line(points = {{-780, 433}, {-780, 93}, {-650, 93}, {-650, -247}}, color = {0, 0, 127}));
  connect(reference_velocity_z, velocity_error_z.u1) 
    annotation(Line(points = {{-780, 67}, {-780, -142}, {-650, -142}, {-650, -351}}, color = {0, 0, 127}));
  connect(velocity_z, velocity_error_z.u2) 
    annotation(Line(points = {{-780, 311}, {-780, -20}, {-650, -20}, {-650, -351}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_feedback_z.u) 
    annotation(Line(points = {{-636, -258}, {-524, -258}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, velocity_feedback_z.u) 
    annotation(Line(points = {{-636, -362}, {-524, -362}}, color = {0, 0, 127}));
  connect(position_feedback_z.y, sliding_surface_z.u1) 
    annotation(Line(points = {{-496, -258}, {-437.5, -258}, {-437.5, -310}, {-379, -310}}, color = {0, 0, 127}));
  connect(velocity_feedback_z.y, sliding_surface_z.u2) 
    annotation(Line(points = {{-496, -362}, {-437.5, -362}, {-437.5, -310}, {-379, -310}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, previous_surface_z.u1) 
    annotation(Line(points = {{-365, -321}, {-365, -384}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, surface_delta_z.u1) 
    annotation(Line(points = {{-351, -310}, {-292.5, -310}, {-292.5, -335}, {-234, -335}}, color = {0, 0, 127}));
  connect(previous_surface_z.y, surface_delta_z.u2) 
    annotation(Line(points = {{-351, -395}, {-292.5, -395}, {-292.5, -335}, {-234, -335}}, color = {0, 0, 127}));
  connect(surface_delta_z.y, surface_rate_z.u) 
    annotation(Line(points = {{-206, -335}, {-109, -335}}, color = {0, 0, 127}));
  connect(surface_rate_z.y, high_order_rate_feedback_z.u) 
    annotation(Line(points = {{-81, -335}, {11, -335}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, high_order_feedback_z.u1) 
    annotation(Line(points = {{-351, -310}, {121, -310}}, color = {0, 0, 127}));
  connect(high_order_rate_feedback_z.y, high_order_feedback_z.u2) 
    annotation(Line(points = {{39, -335}, {80, -335}, {80, -310}, {121, -310}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, high_order_desired_acceleration_z.u1) 
    annotation(Line(points = {{-766, -44}, {-250, -44}, {-250, -310}, {266, -310}}, color = {0, 0, 127}));
  connect(high_order_feedback_z.y, high_order_desired_acceleration_z.u2) 
    annotation(Line(points = {{149, -310}, {266, -310}}, color = {0, 0, 127}));
  connect(high_order_desired_acceleration_z.y, high_order_acceleration_limit_z.u) 
    annotation(Line(points = {{294, -310}, {396, -310}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_x.y, body_rate_from_acceleration_x.u) 
    annotation(Line(points = {{424, 260}, {577.5, 260}, {577.5, 155}, {731, 155}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_x.y, body_rate_limit_x.u) 
    annotation(Line(points = {{759, 155}, {841, 155}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_y.y, body_rate_from_acceleration_y.u) 
    annotation(Line(points = {{424, -25}, {577.5, -25}, {577.5, 83}, {731, 83}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_y.y, body_rate_limit_y.u) 
    annotation(Line(points = {{759, 83}, {841, 83}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_z.y, body_rate_from_acceleration_z.u) 
    annotation(Line(points = {{424, -310}, {577.5, -310}, {577.5, 11}, {731, 11}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_z.y, body_rate_limit_z.u) 
    annotation(Line(points = {{759, 11}, {841, 11}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_z.y, collective_thrust_pre_normalization.u1) 
    annotation(Line(points = {{424, -310}, {632.5, -310}, {632.5, -155}, {841, -155}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, collective_thrust_pre_normalization.u2) 
    annotation(Line(points = {{759, -155}, {841, -155}}, color = {0, 0, 127}));
  connect(collective_thrust_pre_normalization.y, normalized_thrust_scaling.u) 
    annotation(Line(points = {{869, -155}, {951, -155}}, color = {0, 0, 127}));
  connect(normalized_thrust_scaling.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{979, -155}, {1061, -155}}, color = {0, 0, 127}));
  connect(position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(points = {{-636, 312}, {267.5, 312}, {267.5, 445}, {1171, 445}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 445}, {1171, 445}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(points = {{660, -374}, {660, 30}, {1185, 30}, {1185, 434}}, color = {0, 0, 127}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(points = {{1199, 445}, {1331, 445}}, color = {0, 0, 127}));
  connect(position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(points = {{-636, 27}, {267.5, 27}, {267.5, 406}, {1171, 406}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 406}, {1171, 406}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(points = {{660, -374}, {660, 10.5}, {1185, 10.5}, {1185, 395}}, color = {0, 0, 127}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(points = {{1199, 406}, {1331, 406}}, color = {0, 0, 127}));
  connect(position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(points = {{-636, -258}, {267.5, -258}, {267.5, 367}, {1171, 367}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 367}, {1171, 367}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(points = {{660, -374}, {660, -9}, {1185, -9}, {1185, 356}}, color = {0, 0, 127}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(points = {{1199, 367}, {1331, 367}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, enable_velocity_error_x.u1) 
    annotation(Line(points = {{-636, 208}, {267.5, 208}, {267.5, 328}, {1171, 328}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 328}, {1171, 328}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_x.u3) 
    annotation(Line(points = {{660, -374}, {660, -28.5}, {1185, -28.5}, {1185, 317}}, color = {0, 0, 127}));
  connect(enable_velocity_error_x.y, velocity_error_x_out) 
    annotation(Line(points = {{1199, 328}, {1331, 328}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, enable_velocity_error_y.u1) 
    annotation(Line(points = {{-636, -77}, {267.5, -77}, {267.5, 289}, {1171, 289}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 289}, {1171, 289}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_y.u3) 
    annotation(Line(points = {{660, -374}, {660, -48}, {1185, -48}, {1185, 278}}, color = {0, 0, 127}));
  connect(enable_velocity_error_y.y, velocity_error_y_out) 
    annotation(Line(points = {{1199, 289}, {1331, 289}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, enable_velocity_error_z.u1) 
    annotation(Line(points = {{-636, -362}, {267.5, -362}, {267.5, 250}, {1171, 250}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 250}, {1171, 250}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_z.u3) 
    annotation(Line(points = {{660, -374}, {660, -67.5}, {1185, -67.5}, {1185, 239}}, color = {0, 0, 127}));
  connect(enable_velocity_error_z.y, velocity_error_z_out) 
    annotation(Line(points = {{1199, 250}, {1331, 250}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, enable_sliding_surface_x.u1) 
    annotation(Line(points = {{-351, 260}, {410, 260}, {410, 211}, {1171, 211}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 211}, {1171, 211}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_x.u3) 
    annotation(Line(points = {{660, -374}, {660, -87}, {1185, -87}, {1185, 200}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_x.y, sliding_surface_x_out) 
    annotation(Line(points = {{1199, 211}, {1331, 211}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, enable_sliding_surface_y.u1) 
    annotation(Line(points = {{-351, -25}, {410, -25}, {410, 172}, {1171, 172}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 172}, {1171, 172}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_y.u3) 
    annotation(Line(points = {{660, -374}, {660, -106.5}, {1185, -106.5}, {1185, 161}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_y.y, sliding_surface_y_out) 
    annotation(Line(points = {{1199, 172}, {1331, 172}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, enable_sliding_surface_z.u1) 
    annotation(Line(points = {{-351, -310}, {410, -310}, {410, 133}, {1171, 133}}, color = {0, 0, 127}));
  connect(enable, enable_sliding_surface_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 133}, {1171, 133}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_sliding_surface_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, 133}, {1171, 133}}, color = {0, 0, 127}));
  connect(enable_sliding_surface_z.y, sliding_surface_z_out) 
    annotation(Line(points = {{1199, 133}, {1331, 133}}, color = {0, 0, 127}));
  connect(surface_rate_x.y, enable_surface_rate_x.u1) 
    annotation(Line(points = {{-81, 235}, {545, 235}, {545, 94}, {1171, 94}}, color = {0, 0, 127}));
  connect(enable, enable_surface_rate_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 94}, {1171, 94}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_surface_rate_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, 94}, {1171, 94}}, color = {0, 0, 127}));
  connect(enable_surface_rate_x.y, surface_rate_x_out) 
    annotation(Line(points = {{1199, 94}, {1331, 94}}, color = {0, 0, 127}));
  connect(surface_rate_y.y, enable_surface_rate_y.u1) 
    annotation(Line(points = {{-81, -50}, {545, -50}, {545, 55}, {1171, 55}}, color = {0, 0, 127}));
  connect(enable, enable_surface_rate_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 55}, {1171, 55}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_surface_rate_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, 55}, {1171, 55}}, color = {0, 0, 127}));
  connect(enable_surface_rate_y.y, surface_rate_y_out) 
    annotation(Line(points = {{1199, 55}, {1331, 55}}, color = {0, 0, 127}));
  connect(surface_rate_z.y, enable_surface_rate_z.u1) 
    annotation(Line(points = {{-81, -335}, {545, -335}, {545, 16}, {1171, 16}}, color = {0, 0, 127}));
  connect(enable, enable_surface_rate_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, 16}, {1171, 16}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_surface_rate_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, 16}, {1171, 16}}, color = {0, 0, 127}));
  connect(enable_surface_rate_z.y, surface_rate_z_out) 
    annotation(Line(points = {{1199, 16}, {1331, 16}}, color = {0, 0, 127}));
  connect(high_order_disturbance_path_x.y, enable_disturbance_estimate_x.u1) 
    annotation(Line(points = {{149, 150}, {660, 150}, {660, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_x.y, disturbance_estimate_x_out) 
    annotation(Line(points = {{1199, -23}, {1331, -23}}, color = {0, 0, 127}));
  connect(high_order_disturbance_path_y.y, enable_disturbance_estimate_y.u1) 
    annotation(Line(points = {{149, -135}, {660, -135}, {660, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_y.y, disturbance_estimate_y_out) 
    annotation(Line(points = {{1199, -62}, {1331, -62}}, color = {0, 0, 127}));
  connect(high_order_disturbance_path_z.y, enable_disturbance_estimate_z.u1) 
    annotation(Line(points = {{149, -420}, {660, -420}, {660, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_z.y, disturbance_estimate_z_out) 
    annotation(Line(points = {{1199, -101}, {1331, -101}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{424, 260}, {797.5, 260}, {797.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{1199, -140}, {1331, -140}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{424, -25}, {797.5, -25}, {797.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{1199, -179}, {1331, -179}}, color = {0, 0, 127}));
  connect(high_order_acceleration_limit_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{424, -310}, {797.5, -310}, {797.5, -218}, {1171, -218}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -218}, {1171, -218}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -218}, {1171, -218}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out) 
    annotation(Line(points = {{1199, -218}, {1331, -218}}, color = {0, 0, 127}));
  connect(body_rate_limit_x.y, enable_desired_body_rate_x.u1) 
    annotation(Line(points = {{855, 144}, {855, -51}, {1185, -51}, {1185, -246}}, color = {0, 0, 127}));
  connect(enable, enable_desired_body_rate_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -257}, {1171, -257}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_body_rate_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -257}, {1171, -257}}, color = {0, 0, 127}));
  connect(enable_desired_body_rate_x.y, desired_body_rate_x_out) 
    annotation(Line(points = {{1199, -257}, {1331, -257}}, color = {0, 0, 127}));
  connect(body_rate_limit_y.y, enable_desired_body_rate_y.u1) 
    annotation(Line(points = {{855, 72}, {855, -106.5}, {1185, -106.5}, {1185, -285}}, color = {0, 0, 127}));
  connect(enable, enable_desired_body_rate_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -296}, {1171, -296}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_body_rate_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -296}, {1171, -296}}, color = {0, 0, 127}));
  connect(enable_desired_body_rate_y.y, desired_body_rate_y_out) 
    annotation(Line(points = {{1199, -296}, {1331, -296}}, color = {0, 0, 127}));
  connect(body_rate_limit_z.y, enable_desired_body_rate_z.u1) 
    annotation(Line(points = {{855, 0}, {855, -162}, {1185, -162}, {1185, -324}}, color = {0, 0, 127}));
  connect(enable, enable_desired_body_rate_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -335}, {1171, -335}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_body_rate_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -335}, {1171, -335}}, color = {0, 0, 127}));
  connect(enable_desired_body_rate_z.y, desired_body_rate_z_out) 
    annotation(Line(points = {{1199, -335}, {1331, -335}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{1075, -166}, {1075, -264.5}, {1185, -264.5}, {1185, -363}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -374}, {1171, -374}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -374}, {1171, -374}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{1199, -374}, {1331, -374}}, color = {0, 0, 127}));

end DfbcHighOrderBodyrateCore;
