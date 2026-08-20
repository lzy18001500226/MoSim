within MoSimQuadrotorModel.Control.GeometricFlatness.DfbcSmoothRobustBodyrate;
model DfbcSmoothRobustBodyrateCore "Direct graphical smooth-robust DFBC with body-rate/thrust adapter"
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
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_boundary_normalization_x(k=2.2222222222222223) 
    annotation (Placement(transformation(origin = {25, 295}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction smooth_tanh_feedback_x(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {135, 295}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_robust_gain_x(k=-0.75) 
    annotation (Placement(transformation(origin = {250, 295}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay disturbance_observer_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {25, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_innovation_x(inputs="+-") 
    annotation (Placement(transformation(origin = {135, 155}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain disturbance_observer_gain_x(k=0.18) 
    annotation (Placement(transformation(origin = {250, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_next_x 
    annotation (Placement(transformation(origin = {370, 155}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation disturbance_compensation_limit_x(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {485, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_x_stage_2 
    annotation (Placement(transformation(origin = {369, 265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_x_stage_3 
    annotation (Placement(transformation(origin = {427, 265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_x(inputs="+-") 
    annotation (Placement(transformation(origin = {485, 265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation smooth_robust_acceleration_limit_x(lowLimit=-4.0,upLimit=4.0) 
    annotation (Placement(transformation(origin = {620, 265}, extent = {{-14, -11}, {14, 11}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_boundary_normalization_y(k=2.2222222222222223) 
    annotation (Placement(transformation(origin = {25, 10}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction smooth_tanh_feedback_y(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {135, 10}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_robust_gain_y(k=-0.75) 
    annotation (Placement(transformation(origin = {250, 10}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay disturbance_observer_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {25, -130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_innovation_y(inputs="+-") 
    annotation (Placement(transformation(origin = {135, -130}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain disturbance_observer_gain_y(k=0.18) 
    annotation (Placement(transformation(origin = {250, -130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_next_y 
    annotation (Placement(transformation(origin = {370, -130}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation disturbance_compensation_limit_y(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {485, -130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_y_stage_2 
    annotation (Placement(transformation(origin = {369, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_y_stage_3 
    annotation (Placement(transformation(origin = {427, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_y(inputs="+-") 
    annotation (Placement(transformation(origin = {485, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation smooth_robust_acceleration_limit_y(lowLimit=-4.0,upLimit=4.0) 
    annotation (Placement(transformation(origin = {620, -20}, extent = {{-14, -11}, {14, 11}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_boundary_normalization_z(k=2.857142857142857) 
    annotation (Placement(transformation(origin = {25, -275}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction smooth_tanh_feedback_z(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {135, -275}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain smooth_robust_gain_z(k=-0.95) 
    annotation (Placement(transformation(origin = {250, -275}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay disturbance_observer_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {25, -415}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_innovation_z(inputs="+-") 
    annotation (Placement(transformation(origin = {135, -415}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain disturbance_observer_gain_z(k=0.14) 
    annotation (Placement(transformation(origin = {250, -415}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum disturbance_observer_next_z 
    annotation (Placement(transformation(origin = {370, -415}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation disturbance_compensation_limit_z(lowLimit=-0.8,upLimit=0.8) 
    annotation (Placement(transformation(origin = {485, -415}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_z_stage_2 
    annotation (Placement(transformation(origin = {369, -305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_z_stage_3 
    annotation (Placement(transformation(origin = {427, -305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum smooth_robust_desired_acceleration_z(inputs="+-") 
    annotation (Placement(transformation(origin = {485, -305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation smooth_robust_acceleration_limit_z(lowLimit=-3.0,upLimit=3.0) 
    annotation (Placement(transformation(origin = {620, -305}, extent = {{-14, -11}, {14, 11}})));
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
  connect(sliding_surface_x.y, smooth_boundary_normalization_x.u) 
    annotation(Line(points = {{-351, 260}, {-170, 260}, {-170, 295}, {11, 295}}, color = {0, 0, 127}));
  connect(smooth_boundary_normalization_x.y, smooth_tanh_feedback_x.u1) 
    annotation(Line(points = {{39, 295}, {121, 295}}, color = {0, 0, 127}));
  connect(smooth_tanh_feedback_x.y1, smooth_robust_gain_x.u) 
    annotation(Line(points = {{149, 295}, {236, 295}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, disturbance_observer_innovation_x.u1) 
    annotation(Line(points = {{-351, 260}, {-115, 260}, {-115, 155}, {121, 155}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_x.y, disturbance_observer_innovation_x.u2) 
    annotation(Line(points = {{39, 155}, {121, 155}}, color = {0, 0, 127}));
  connect(disturbance_observer_innovation_x.y, disturbance_observer_gain_x.u) 
    annotation(Line(points = {{149, 155}, {236, 155}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_x.y, disturbance_observer_next_x.u1) 
    annotation(Line(points = {{39, 155}, {356, 155}}, color = {0, 0, 127}));
  connect(disturbance_observer_gain_x.y, disturbance_observer_next_x.u2) 
    annotation(Line(points = {{264, 155}, {356, 155}}, color = {0, 0, 127}));
  connect(disturbance_observer_next_x.y, disturbance_compensation_limit_x.u) 
    annotation(Line(points = {{384, 155}, {471, 155}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_x.y, disturbance_observer_state_x.u1) 
    annotation(Line(points = {{471, 155}, {39, 155}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, smooth_robust_desired_acceleration_x_stage_2.u1) 
    annotation(Line(points = {{-766, 12}, {-205.5, 12}, {-205.5, 265}, {355, 265}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, smooth_robust_desired_acceleration_x_stage_2.u2) 
    annotation(Line(points = {{-351, 260}, {2, 260}, {2, 265}, {355, 265}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_x_stage_2.y, smooth_robust_desired_acceleration_x_stage_3.u1) 
    annotation(Line(points = {{383, 265}, {413, 265}}, color = {0, 0, 127}));
  connect(smooth_robust_gain_x.y, smooth_robust_desired_acceleration_x_stage_3.u2) 
    annotation(Line(points = {{264, 295}, {338.5, 295}, {338.5, 265}, {413, 265}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_x_stage_3.y, smooth_robust_desired_acceleration_x.u1) 
    annotation(Line(points = {{441, 265}, {471, 265}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_x.y, smooth_robust_desired_acceleration_x.u2) 
    annotation(Line(points = {{485, 166}, {485, 254}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_x.y, smooth_robust_acceleration_limit_x.u) 
    annotation(Line(points = {{499, 265}, {606, 265}}, color = {0, 0, 127}));
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
  connect(sliding_surface_y.y, smooth_boundary_normalization_y.u) 
    annotation(Line(points = {{-351, -25}, {-170, -25}, {-170, 10}, {11, 10}}, color = {0, 0, 127}));
  connect(smooth_boundary_normalization_y.y, smooth_tanh_feedback_y.u1) 
    annotation(Line(points = {{39, 10}, {121, 10}}, color = {0, 0, 127}));
  connect(smooth_tanh_feedback_y.y1, smooth_robust_gain_y.u) 
    annotation(Line(points = {{149, 10}, {236, 10}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, disturbance_observer_innovation_y.u1) 
    annotation(Line(points = {{-351, -25}, {-115, -25}, {-115, -130}, {121, -130}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_y.y, disturbance_observer_innovation_y.u2) 
    annotation(Line(points = {{39, -130}, {121, -130}}, color = {0, 0, 127}));
  connect(disturbance_observer_innovation_y.y, disturbance_observer_gain_y.u) 
    annotation(Line(points = {{149, -130}, {236, -130}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_y.y, disturbance_observer_next_y.u1) 
    annotation(Line(points = {{39, -130}, {356, -130}}, color = {0, 0, 127}));
  connect(disturbance_observer_gain_y.y, disturbance_observer_next_y.u2) 
    annotation(Line(points = {{264, -130}, {356, -130}}, color = {0, 0, 127}));
  connect(disturbance_observer_next_y.y, disturbance_compensation_limit_y.u) 
    annotation(Line(points = {{384, -130}, {471, -130}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_y.y, disturbance_observer_state_y.u1) 
    annotation(Line(points = {{471, -130}, {39, -130}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, smooth_robust_desired_acceleration_y_stage_2.u1) 
    annotation(Line(points = {{-766, -16}, {-205.5, -16}, {-205.5, -20}, {355, -20}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, smooth_robust_desired_acceleration_y_stage_2.u2) 
    annotation(Line(points = {{-351, -25}, {2, -25}, {2, -20}, {355, -20}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_y_stage_2.y, smooth_robust_desired_acceleration_y_stage_3.u1) 
    annotation(Line(points = {{383, -20}, {413, -20}}, color = {0, 0, 127}));
  connect(smooth_robust_gain_y.y, smooth_robust_desired_acceleration_y_stage_3.u2) 
    annotation(Line(points = {{264, 10}, {338.5, 10}, {338.5, -20}, {413, -20}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_y_stage_3.y, smooth_robust_desired_acceleration_y.u1) 
    annotation(Line(points = {{441, -20}, {471, -20}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_y.y, smooth_robust_desired_acceleration_y.u2) 
    annotation(Line(points = {{485, -119}, {485, -31}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_y.y, smooth_robust_acceleration_limit_y.u) 
    annotation(Line(points = {{499, -20}, {606, -20}}, color = {0, 0, 127}));
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
  connect(sliding_surface_z.y, smooth_boundary_normalization_z.u) 
    annotation(Line(points = {{-351, -310}, {-170, -310}, {-170, -275}, {11, -275}}, color = {0, 0, 127}));
  connect(smooth_boundary_normalization_z.y, smooth_tanh_feedback_z.u1) 
    annotation(Line(points = {{39, -275}, {121, -275}}, color = {0, 0, 127}));
  connect(smooth_tanh_feedback_z.y1, smooth_robust_gain_z.u) 
    annotation(Line(points = {{149, -275}, {236, -275}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, disturbance_observer_innovation_z.u1) 
    annotation(Line(points = {{-351, -310}, {-115, -310}, {-115, -415}, {121, -415}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_z.y, disturbance_observer_innovation_z.u2) 
    annotation(Line(points = {{39, -415}, {121, -415}}, color = {0, 0, 127}));
  connect(disturbance_observer_innovation_z.y, disturbance_observer_gain_z.u) 
    annotation(Line(points = {{149, -415}, {236, -415}}, color = {0, 0, 127}));
  connect(disturbance_observer_state_z.y, disturbance_observer_next_z.u1) 
    annotation(Line(points = {{39, -415}, {356, -415}}, color = {0, 0, 127}));
  connect(disturbance_observer_gain_z.y, disturbance_observer_next_z.u2) 
    annotation(Line(points = {{264, -415}, {356, -415}}, color = {0, 0, 127}));
  connect(disturbance_observer_next_z.y, disturbance_compensation_limit_z.u) 
    annotation(Line(points = {{384, -415}, {471, -415}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_z.y, disturbance_observer_state_z.u1) 
    annotation(Line(points = {{471, -415}, {39, -415}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, smooth_robust_desired_acceleration_z_stage_2.u1) 
    annotation(Line(points = {{-766, -44}, {-205.5, -44}, {-205.5, -305}, {355, -305}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, smooth_robust_desired_acceleration_z_stage_2.u2) 
    annotation(Line(points = {{-351, -310}, {2, -310}, {2, -305}, {355, -305}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_z_stage_2.y, smooth_robust_desired_acceleration_z_stage_3.u1) 
    annotation(Line(points = {{383, -305}, {413, -305}}, color = {0, 0, 127}));
  connect(smooth_robust_gain_z.y, smooth_robust_desired_acceleration_z_stage_3.u2) 
    annotation(Line(points = {{264, -275}, {338.5, -275}, {338.5, -305}, {413, -305}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_z_stage_3.y, smooth_robust_desired_acceleration_z.u1) 
    annotation(Line(points = {{441, -305}, {471, -305}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_z.y, smooth_robust_desired_acceleration_z.u2) 
    annotation(Line(points = {{485, -404}, {485, -316}}, color = {0, 0, 127}));
  connect(smooth_robust_desired_acceleration_z.y, smooth_robust_acceleration_limit_z.u) 
    annotation(Line(points = {{499, -305}, {606, -305}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_x.y, body_rate_from_acceleration_x.u) 
    annotation(Line(points = {{634, 265}, {682.5, 265}, {682.5, 155}, {731, 155}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_x.y, body_rate_limit_x.u) 
    annotation(Line(points = {{759, 155}, {841, 155}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_y.y, body_rate_from_acceleration_y.u) 
    annotation(Line(points = {{634, -20}, {682.5, -20}, {682.5, 83}, {731, 83}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_y.y, body_rate_limit_y.u) 
    annotation(Line(points = {{759, 83}, {841, 83}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_z.y, body_rate_from_acceleration_z.u) 
    annotation(Line(points = {{620, -294}, {620, -147}, {745, -147}, {745, 0}}, color = {0, 0, 127}));
  connect(body_rate_from_acceleration_z.y, body_rate_limit_z.u) 
    annotation(Line(points = {{759, 11}, {841, 11}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_z.y, collective_thrust_pre_normalization.u1) 
    annotation(Line(points = {{634, -305}, {737.5, -305}, {737.5, -155}, {841, -155}}, color = {0, 0, 127}));
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
  connect(disturbance_compensation_limit_x.y, enable_disturbance_estimate_x.u1) 
    annotation(Line(points = {{499, 155}, {835, 155}, {835, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -23}, {1171, -23}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_x.y, disturbance_estimate_x_out) 
    annotation(Line(points = {{1199, -23}, {1331, -23}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_y.y, enable_disturbance_estimate_y.u1) 
    annotation(Line(points = {{499, -130}, {835, -130}, {835, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -62}, {1171, -62}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_y.y, disturbance_estimate_y_out) 
    annotation(Line(points = {{1199, -62}, {1331, -62}}, color = {0, 0, 127}));
  connect(disturbance_compensation_limit_z.y, enable_disturbance_estimate_z.u1) 
    annotation(Line(points = {{499, -415}, {835, -415}, {835, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(enable, enable_disturbance_estimate_z.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_disturbance_estimate_z.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -101}, {1171, -101}}, color = {0, 0, 127}));
  connect(enable_disturbance_estimate_z.y, disturbance_estimate_z_out) 
    annotation(Line(points = {{1199, -101}, {1331, -101}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{634, 265}, {902.5, 265}, {902.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -140}, {1171, -140}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{1199, -140}, {1331, -140}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{634, -20}, {902.5, -20}, {902.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-766, -350}, {202.5, -350}, {202.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{674, -385}, {922.5, -385}, {922.5, -179}, {1171, -179}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{1199, -179}, {1331, -179}}, color = {0, 0, 127}));
  connect(smooth_robust_acceleration_limit_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{634, -305}, {902.5, -305}, {902.5, -218}, {1171, -218}}, color = {0, 0, 127}));
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

end DfbcSmoothRobustBodyrateCore;
