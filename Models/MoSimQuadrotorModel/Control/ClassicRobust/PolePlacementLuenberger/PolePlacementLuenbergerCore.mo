within MoSimQuadrotorModel.Control.ClassicRobust.PolePlacementLuenberger;
model PolePlacementLuenbergerCore "Pole-placement Luenberger direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(observer_position_x_out, observer_velocity_x_out, position_error_x_out, velocity_error_x_out, desired_acceleration_x_out, observer_position_y_out, observer_velocity_y_out, position_error_y_out, velocity_error_y_out, desired_acceleration_y_out, observer_position_z_out, observer_velocity_z_out, position_error_z_out, velocity_error_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport position_x 
    annotation (Placement(transformation(origin = {-680, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_y 
    annotation (Placement(transformation(origin = {-680, 324}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_z 
    annotation (Placement(transformation(origin = {-680, 298}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_x 
    annotation (Placement(transformation(origin = {-680, 238}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_y 
    annotation (Placement(transformation(origin = {-680, 212}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_z 
    annotation (Placement(transformation(origin = {-680, 186}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x 
    annotation (Placement(transformation(origin = {-680, 126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y 
    annotation (Placement(transformation(origin = {-680, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z 
    annotation (Placement(transformation(origin = {-680, 74}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x 
    annotation (Placement(transformation(origin = {-680, 14}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y 
    annotation (Placement(transformation(origin = {-680, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z 
    annotation (Placement(transformation(origin = {-680, -38}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x 
    annotation (Placement(transformation(origin = {-680, -98}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y 
    annotation (Placement(transformation(origin = {-680, -124}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z 
    annotation (Placement(transformation(origin = {-680, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport dt 
    annotation (Placement(transformation(origin = {-680, -245}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable 
    annotation (Placement(transformation(origin = {-680, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0) 
    annotation (Placement(transformation(origin = {500, -310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_position_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_velocity_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 290}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_virtual_acceleration_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_residual_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-535, 330}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_position_correction_x(k=8.0) 
    annotation (Placement(transformation(origin = {-300, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_dot_x(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 330}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_position_increment_x(inputs="**") 
    annotation (Placement(transformation(origin = {-90, 330}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_next_x(inputs="++") 
    annotation (Placement(transformation(origin = {10, 330}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_velocity_correction_x(k=16.0) 
    annotation (Placement(transformation(origin = {-300, 280}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_dot_x(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 290}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_velocity_increment_x(inputs="**") 
    annotation (Placement(transformation(origin = {-90, 290}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_next_x(inputs="++") 
    annotation (Placement(transformation(origin = {10, 290}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, 190}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_position_feedback_x(k=9.0) 
    annotation (Placement(transformation(origin = {-180, 230}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_velocity_feedback_x(k=6.0) 
    annotation (Placement(transformation(origin = {-180, 190}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_state_feedback_x(inputs="++") 
    annotation (Placement(transformation(origin = {-55, 210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_virtual_acceleration_x(inputs="++") 
    annotation (Placement(transformation(origin = {55, 210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0) 
    annotation (Placement(transformation(origin = {140, 210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_position_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 105}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_velocity_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 65}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_virtual_acceleration_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -125}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_residual_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-535, 105}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_position_correction_y(k=8.0) 
    annotation (Placement(transformation(origin = {-300, 125}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_dot_y(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 105}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_position_increment_y(inputs="**") 
    annotation (Placement(transformation(origin = {-90, 105}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_next_y(inputs="++") 
    annotation (Placement(transformation(origin = {10, 105}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_velocity_correction_y(k=16.0) 
    annotation (Placement(transformation(origin = {-300, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_dot_y(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 65}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_velocity_increment_y(inputs="**") 
    annotation (Placement(transformation(origin = {-90, 65}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_next_y(inputs="++") 
    annotation (Placement(transformation(origin = {10, 65}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, 5}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, -35}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_position_feedback_y(k=9.0) 
    annotation (Placement(transformation(origin = {-180, 5}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_velocity_feedback_y(k=6.0) 
    annotation (Placement(transformation(origin = {-180, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_state_feedback_y(inputs="++") 
    annotation (Placement(transformation(origin = {-55, -15}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_virtual_acceleration_y(inputs="++") 
    annotation (Placement(transformation(origin = {55, -15}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0) 
    annotation (Placement(transformation(origin = {140, -15}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_position_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay observer_velocity_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_virtual_acceleration_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_residual_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-535, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_position_correction_z(k=9.0) 
    annotation (Placement(transformation(origin = {-300, -100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_dot_z(inputs="++") 
    annotation (Placement(transformation(origin = {-190, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_position_increment_z(inputs="**") 
    annotation (Placement(transformation(origin = {-90, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_position_next_z(inputs="++") 
    annotation (Placement(transformation(origin = {10, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain observer_velocity_correction_z(k=20.25) 
    annotation (Placement(transformation(origin = {-300, -170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_dot_z(inputs="++") 
    annotation (Placement(transformation(origin = {-190, -160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product observer_velocity_increment_z(inputs="**") 
    annotation (Placement(transformation(origin = {-90, -160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum observer_velocity_next_z(inputs="++") 
    annotation (Placement(transformation(origin = {10, -160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, -220}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-300, -260}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_position_feedback_z(k=6.25) 
    annotation (Placement(transformation(origin = {-180, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pole_velocity_feedback_z(k=5.0) 
    annotation (Placement(transformation(origin = {-180, -260}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_state_feedback_z(inputs="++") 
    annotation (Placement(transformation(origin = {-55, -240}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pole_virtual_acceleration_z(inputs="++") 
    annotation (Placement(transformation(origin = {55, -240}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665) 
    annotation (Placement(transformation(origin = {55, -168}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z(inputs="++") 
    annotation (Placement(transformation(origin = {140, -240}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_from_lateral_acceleration(k=-0.10197162129779283) 
    annotation (Placement(transformation(origin = {230, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988) 
    annotation (Placement(transformation(origin = {320, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_from_lateral_acceleration(k=0.10197162129779283) 
    annotation (Placement(transformation(origin = {230, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988) 
    annotation (Placement(transformation(origin = {320, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain vertical_force_allocation(k=1.0) 
    annotation (Placement(transformation(origin = {230, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation collective_thrust_limit(lowLimit=0.0,upLimit=16.0) 
    annotation (Placement(transformation(origin = {320, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain normalized_thrust_from_collective(k=0.04428916686217568) 
    annotation (Placement(transformation(origin = {410, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation normalized_thrust_limit(lowLimit=0.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {500, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_position_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_position_x_out 
    annotation (Placement(transformation(origin = {695, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_velocity_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 322}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_velocity_x_out 
    annotation (Placement(transformation(origin = {695, 322}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 284}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out 
    annotation (Placement(transformation(origin = {695, 284}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 246}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out 
    annotation (Placement(transformation(origin = {695, 246}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out 
    annotation (Placement(transformation(origin = {695, 208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_position_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_position_y_out 
    annotation (Placement(transformation(origin = {695, 170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_velocity_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 132}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_velocity_y_out 
    annotation (Placement(transformation(origin = {695, 132}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out 
    annotation (Placement(transformation(origin = {695, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out 
    annotation (Placement(transformation(origin = {695, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 18}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out 
    annotation (Placement(transformation(origin = {695, 18}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_position_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_position_z_out 
    annotation (Placement(transformation(origin = {695, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_observer_velocity_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport observer_velocity_z_out 
    annotation (Placement(transformation(origin = {695, -58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -96}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out 
    annotation (Placement(transformation(origin = {695, -96}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -134}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out 
    annotation (Placement(transformation(origin = {695, -134}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -172}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out 
    annotation (Placement(transformation(origin = {695, -172}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out 
    annotation (Placement(transformation(origin = {695, -210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -248}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out 
    annotation (Placement(transformation(origin = {695, -248}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -286}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out 
    annotation (Placement(transformation(origin = {695, -286}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -324}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin = {695, -324}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(position_x, observer_residual_x.u1) 
    annotation(Line(points = {{-666, 350}, {-607.5, 350}, {-607.5, 330}, {-549, 330}}, color = {0, 0, 127}));
  connect(observer_position_state_x.y, observer_residual_x.u2) 
    annotation(Line(points = {{-424, 330}, {-521, 330}}, color = {0, 0, 127}));
  connect(observer_residual_x.y, observer_position_correction_x.u) 
    annotation(Line(points = {{-521, 330}, {-417.5, 330}, {-417.5, 350}, {-314, 350}}, color = {0, 0, 127}));
  connect(observer_velocity_state_x.y, observer_position_dot_x.u1) 
    annotation(Line(points = {{-396, 290}, {-300, 290}, {-300, 330}, {-204, 330}}, color = {0, 0, 127}));
  connect(observer_position_correction_x.y, observer_position_dot_x.u2) 
    annotation(Line(points = {{-286, 350}, {-245, 350}, {-245, 330}, {-204, 330}}, color = {0, 0, 127}));
  connect(observer_position_dot_x.y, observer_position_increment_x.u1) 
    annotation(Line(points = {{-176, 330}, {-104, 330}}, color = {0, 0, 127}));
  connect(dt, observer_position_increment_x.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, 330}, {-104, 330}}, color = {0, 0, 127}));
  connect(observer_position_state_x.y, observer_position_next_x.u1) 
    annotation(Line(points = {{-396, 330}, {-4, 330}}, color = {0, 0, 127}));
  connect(observer_position_increment_x.y, observer_position_next_x.u2) 
    annotation(Line(points = {{-76, 330}, {-4, 330}}, color = {0, 0, 127}));
  connect(observer_position_next_x.y, observer_position_state_x.u1) 
    annotation(Line(points = {{-4, 330}, {-396, 330}}, color = {0, 0, 127}));
  connect(observer_residual_x.y, observer_velocity_correction_x.u) 
    annotation(Line(points = {{-521, 330}, {-417.5, 330}, {-417.5, 280}, {-314, 280}}, color = {0, 0, 127}));
  connect(previous_virtual_acceleration_state_x.y, observer_velocity_dot_x.u1) 
    annotation(Line(points = {{-396, 100}, {-300, 100}, {-300, 290}, {-204, 290}}, color = {0, 0, 127}));
  connect(observer_velocity_correction_x.y, observer_velocity_dot_x.u2) 
    annotation(Line(points = {{-286, 280}, {-245, 280}, {-245, 290}, {-204, 290}}, color = {0, 0, 127}));
  connect(observer_velocity_dot_x.y, observer_velocity_increment_x.u1) 
    annotation(Line(points = {{-176, 290}, {-104, 290}}, color = {0, 0, 127}));
  connect(dt, observer_velocity_increment_x.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, 290}, {-104, 290}}, color = {0, 0, 127}));
  connect(observer_velocity_state_x.y, observer_velocity_next_x.u1) 
    annotation(Line(points = {{-396, 290}, {-4, 290}}, color = {0, 0, 127}));
  connect(observer_velocity_increment_x.y, observer_velocity_next_x.u2) 
    annotation(Line(points = {{-76, 290}, {-4, 290}}, color = {0, 0, 127}));
  connect(observer_velocity_next_x.y, observer_velocity_state_x.u1) 
    annotation(Line(points = {{-4, 290}, {-396, 290}}, color = {0, 0, 127}));
  connect(reference_position_x, pole_position_error_x.u1) 
    annotation(Line(points = {{-666, 126}, {-490, 126}, {-490, 230}, {-314, 230}}, color = {0, 0, 127}));
  connect(observer_position_state_x.y, pole_position_error_x.u2) 
    annotation(Line(points = {{-396, 330}, {-355, 330}, {-355, 230}, {-314, 230}}, color = {0, 0, 127}));
  connect(reference_velocity_x, pole_velocity_error_x.u1) 
    annotation(Line(points = {{-666, 14}, {-490, 14}, {-490, 190}, {-314, 190}}, color = {0, 0, 127}));
  connect(observer_velocity_state_x.y, pole_velocity_error_x.u2) 
    annotation(Line(points = {{-396, 290}, {-355, 290}, {-355, 190}, {-314, 190}}, color = {0, 0, 127}));
  connect(pole_position_error_x.y, pole_position_feedback_x.u) 
    annotation(Line(points = {{-286, 230}, {-194, 230}}, color = {0, 0, 127}));
  connect(pole_velocity_error_x.y, pole_velocity_feedback_x.u) 
    annotation(Line(points = {{-286, 190}, {-194, 190}}, color = {0, 0, 127}));
  connect(pole_position_feedback_x.y, pole_state_feedback_x.u1) 
    annotation(Line(points = {{-166, 230}, {-117.5, 230}, {-117.5, 210}, {-69, 210}}, color = {0, 0, 127}));
  connect(pole_velocity_feedback_x.y, pole_state_feedback_x.u2) 
    annotation(Line(points = {{-166, 190}, {-117.5, 190}, {-117.5, 210}, {-69, 210}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, pole_virtual_acceleration_x.u1) 
    annotation(Line(points = {{-666, -98}, {-312.5, -98}, {-312.5, 210}, {41, 210}}, color = {0, 0, 127}));
  connect(pole_state_feedback_x.y, pole_virtual_acceleration_x.u2) 
    annotation(Line(points = {{-41, 210}, {41, 210}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_x.y, previous_virtual_acceleration_state_x.u1) 
    annotation(Line(points = {{41, 210}, {-177.5, 210}, {-177.5, 100}, {-396, 100}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_x.y, desired_acceleration_x.u) 
    annotation(Line(points = {{69, 210}, {126, 210}}, color = {0, 0, 127}));
  connect(position_y, observer_residual_y.u1) 
    annotation(Line(points = {{-680, 313}, {-680, 214.5}, {-535, 214.5}, {-535, 116}}, color = {0, 0, 127}));
  connect(observer_position_state_y.y, observer_residual_y.u2) 
    annotation(Line(points = {{-424, 105}, {-521, 105}}, color = {0, 0, 127}));
  connect(observer_residual_y.y, observer_position_correction_y.u) 
    annotation(Line(points = {{-521, 105}, {-417.5, 105}, {-417.5, 125}, {-314, 125}}, color = {0, 0, 127}));
  connect(observer_velocity_state_y.y, observer_position_dot_y.u1) 
    annotation(Line(points = {{-396, 65}, {-300, 65}, {-300, 105}, {-204, 105}}, color = {0, 0, 127}));
  connect(observer_position_correction_y.y, observer_position_dot_y.u2) 
    annotation(Line(points = {{-286, 125}, {-245, 125}, {-245, 105}, {-204, 105}}, color = {0, 0, 127}));
  connect(observer_position_dot_y.y, observer_position_increment_y.u1) 
    annotation(Line(points = {{-176, 105}, {-104, 105}}, color = {0, 0, 127}));
  connect(dt, observer_position_increment_y.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, 105}, {-104, 105}}, color = {0, 0, 127}));
  connect(observer_position_state_y.y, observer_position_next_y.u1) 
    annotation(Line(points = {{-396, 105}, {-4, 105}}, color = {0, 0, 127}));
  connect(observer_position_increment_y.y, observer_position_next_y.u2) 
    annotation(Line(points = {{-76, 105}, {-4, 105}}, color = {0, 0, 127}));
  connect(observer_position_next_y.y, observer_position_state_y.u1) 
    annotation(Line(points = {{-4, 105}, {-396, 105}}, color = {0, 0, 127}));
  connect(observer_residual_y.y, observer_velocity_correction_y.u) 
    annotation(Line(points = {{-521, 105}, {-417.5, 105}, {-417.5, 55}, {-314, 55}}, color = {0, 0, 127}));
  connect(previous_virtual_acceleration_state_y.y, observer_velocity_dot_y.u1) 
    annotation(Line(points = {{-396, -125}, {-300, -125}, {-300, 65}, {-204, 65}}, color = {0, 0, 127}));
  connect(observer_velocity_correction_y.y, observer_velocity_dot_y.u2) 
    annotation(Line(points = {{-286, 55}, {-245, 55}, {-245, 65}, {-204, 65}}, color = {0, 0, 127}));
  connect(observer_velocity_dot_y.y, observer_velocity_increment_y.u1) 
    annotation(Line(points = {{-176, 65}, {-104, 65}}, color = {0, 0, 127}));
  connect(dt, observer_velocity_increment_y.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, 65}, {-104, 65}}, color = {0, 0, 127}));
  connect(observer_velocity_state_y.y, observer_velocity_next_y.u1) 
    annotation(Line(points = {{-396, 65}, {-4, 65}}, color = {0, 0, 127}));
  connect(observer_velocity_increment_y.y, observer_velocity_next_y.u2) 
    annotation(Line(points = {{-76, 65}, {-4, 65}}, color = {0, 0, 127}));
  connect(observer_velocity_next_y.y, observer_velocity_state_y.u1) 
    annotation(Line(points = {{-4, 65}, {-396, 65}}, color = {0, 0, 127}));
  connect(reference_position_y, pole_position_error_y.u1) 
    annotation(Line(points = {{-666, 100}, {-490, 100}, {-490, 5}, {-314, 5}}, color = {0, 0, 127}));
  connect(observer_position_state_y.y, pole_position_error_y.u2) 
    annotation(Line(points = {{-396, 105}, {-355, 105}, {-355, 5}, {-314, 5}}, color = {0, 0, 127}));
  connect(reference_velocity_y, pole_velocity_error_y.u1) 
    annotation(Line(points = {{-666, -12}, {-490, -12}, {-490, -35}, {-314, -35}}, color = {0, 0, 127}));
  connect(observer_velocity_state_y.y, pole_velocity_error_y.u2) 
    annotation(Line(points = {{-396, 65}, {-355, 65}, {-355, -35}, {-314, -35}}, color = {0, 0, 127}));
  connect(pole_position_error_y.y, pole_position_feedback_y.u) 
    annotation(Line(points = {{-286, 5}, {-194, 5}}, color = {0, 0, 127}));
  connect(pole_velocity_error_y.y, pole_velocity_feedback_y.u) 
    annotation(Line(points = {{-286, -35}, {-194, -35}}, color = {0, 0, 127}));
  connect(pole_position_feedback_y.y, pole_state_feedback_y.u1) 
    annotation(Line(points = {{-166, 5}, {-117.5, 5}, {-117.5, -15}, {-69, -15}}, color = {0, 0, 127}));
  connect(pole_velocity_feedback_y.y, pole_state_feedback_y.u2) 
    annotation(Line(points = {{-166, -35}, {-117.5, -35}, {-117.5, -15}, {-69, -15}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, pole_virtual_acceleration_y.u1) 
    annotation(Line(points = {{-666, -124}, {-312.5, -124}, {-312.5, -15}, {41, -15}}, color = {0, 0, 127}));
  connect(pole_state_feedback_y.y, pole_virtual_acceleration_y.u2) 
    annotation(Line(points = {{-41, -15}, {41, -15}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_y.y, previous_virtual_acceleration_state_y.u1) 
    annotation(Line(points = {{41, -15}, {-177.5, -15}, {-177.5, -125}, {-396, -125}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_y.y, desired_acceleration_y.u) 
    annotation(Line(points = {{69, -15}, {126, -15}}, color = {0, 0, 127}));
  connect(position_z, observer_residual_z.u1) 
    annotation(Line(points = {{-680, 287}, {-680, 89}, {-535, 89}, {-535, -109}}, color = {0, 0, 127}));
  connect(observer_position_state_z.y, observer_residual_z.u2) 
    annotation(Line(points = {{-424, -120}, {-521, -120}}, color = {0, 0, 127}));
  connect(observer_residual_z.y, observer_position_correction_z.u) 
    annotation(Line(points = {{-521, -120}, {-417.5, -120}, {-417.5, -100}, {-314, -100}}, color = {0, 0, 127}));
  connect(observer_velocity_state_z.y, observer_position_dot_z.u1) 
    annotation(Line(points = {{-396, -160}, {-300, -160}, {-300, -120}, {-204, -120}}, color = {0, 0, 127}));
  connect(observer_position_correction_z.y, observer_position_dot_z.u2) 
    annotation(Line(points = {{-286, -100}, {-245, -100}, {-245, -120}, {-204, -120}}, color = {0, 0, 127}));
  connect(observer_position_dot_z.y, observer_position_increment_z.u1) 
    annotation(Line(points = {{-176, -120}, {-104, -120}}, color = {0, 0, 127}));
  connect(dt, observer_position_increment_z.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, -120}, {-104, -120}}, color = {0, 0, 127}));
  connect(observer_position_state_z.y, observer_position_next_z.u1) 
    annotation(Line(points = {{-396, -120}, {-4, -120}}, color = {0, 0, 127}));
  connect(observer_position_increment_z.y, observer_position_next_z.u2) 
    annotation(Line(points = {{-76, -120}, {-4, -120}}, color = {0, 0, 127}));
  connect(observer_position_next_z.y, observer_position_state_z.u1) 
    annotation(Line(points = {{-4, -120}, {-396, -120}}, color = {0, 0, 127}));
  connect(observer_residual_z.y, observer_velocity_correction_z.u) 
    annotation(Line(points = {{-521, -120}, {-417.5, -120}, {-417.5, -170}, {-314, -170}}, color = {0, 0, 127}));
  connect(previous_virtual_acceleration_state_z.y, observer_velocity_dot_z.u1) 
    annotation(Line(points = {{-396, -350}, {-300, -350}, {-300, -160}, {-204, -160}}, color = {0, 0, 127}));
  connect(observer_velocity_correction_z.y, observer_velocity_dot_z.u2) 
    annotation(Line(points = {{-286, -170}, {-245, -170}, {-245, -160}, {-204, -160}}, color = {0, 0, 127}));
  connect(observer_velocity_dot_z.y, observer_velocity_increment_z.u1) 
    annotation(Line(points = {{-176, -160}, {-104, -160}}, color = {0, 0, 127}));
  connect(dt, observer_velocity_increment_z.u2) 
    annotation(Line(points = {{-666, -245}, {-385, -245}, {-385, -160}, {-104, -160}}, color = {0, 0, 127}));
  connect(observer_velocity_state_z.y, observer_velocity_next_z.u1) 
    annotation(Line(points = {{-396, -160}, {-4, -160}}, color = {0, 0, 127}));
  connect(observer_velocity_increment_z.y, observer_velocity_next_z.u2) 
    annotation(Line(points = {{-76, -160}, {-4, -160}}, color = {0, 0, 127}));
  connect(observer_velocity_next_z.y, observer_velocity_state_z.u1) 
    annotation(Line(points = {{-4, -160}, {-396, -160}}, color = {0, 0, 127}));
  connect(reference_position_z, pole_position_error_z.u1) 
    annotation(Line(points = {{-666, 74}, {-490, 74}, {-490, -220}, {-314, -220}}, color = {0, 0, 127}));
  connect(observer_position_state_z.y, pole_position_error_z.u2) 
    annotation(Line(points = {{-396, -120}, {-355, -120}, {-355, -220}, {-314, -220}}, color = {0, 0, 127}));
  connect(reference_velocity_z, pole_velocity_error_z.u1) 
    annotation(Line(points = {{-666, -38}, {-490, -38}, {-490, -260}, {-314, -260}}, color = {0, 0, 127}));
  connect(observer_velocity_state_z.y, pole_velocity_error_z.u2) 
    annotation(Line(points = {{-396, -160}, {-355, -160}, {-355, -260}, {-314, -260}}, color = {0, 0, 127}));
  connect(pole_position_error_z.y, pole_position_feedback_z.u) 
    annotation(Line(points = {{-286, -220}, {-194, -220}}, color = {0, 0, 127}));
  connect(pole_velocity_error_z.y, pole_velocity_feedback_z.u) 
    annotation(Line(points = {{-286, -260}, {-194, -260}}, color = {0, 0, 127}));
  connect(pole_position_feedback_z.y, pole_state_feedback_z.u1) 
    annotation(Line(points = {{-166, -220}, {-117.5, -220}, {-117.5, -240}, {-69, -240}}, color = {0, 0, 127}));
  connect(pole_velocity_feedback_z.y, pole_state_feedback_z.u2) 
    annotation(Line(points = {{-166, -260}, {-117.5, -260}, {-117.5, -240}, {-69, -240}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, pole_virtual_acceleration_z.u1) 
    annotation(Line(points = {{-666, -150}, {-312.5, -150}, {-312.5, -240}, {41, -240}}, color = {0, 0, 127}));
  connect(pole_state_feedback_z.y, pole_virtual_acceleration_z.u2) 
    annotation(Line(points = {{-41, -240}, {41, -240}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_z.y, previous_virtual_acceleration_state_z.u1) 
    annotation(Line(points = {{41, -240}, {-177.5, -240}, {-177.5, -350}, {-396, -350}}, color = {0, 0, 127}));
  connect(pole_virtual_acceleration_z.y, desired_acceleration_z.u1) 
    annotation(Line(points = {{69, -240}, {126, -240}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z.u2) 
    annotation(Line(points = {{69, -168}, {97.5, -168}, {97.5, -240}, {126, -240}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u) 
    annotation(Line(points = {{154, -15}, {185, -15}, {185, 75}, {216, 75}}, color = {0, 0, 127}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u) 
    annotation(Line(points = {{244, 75}, {306, 75}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u) 
    annotation(Line(points = {{154, 210}, {185, 210}, {185, 130}, {216, 130}}, color = {0, 0, 127}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u) 
    annotation(Line(points = {{244, 130}, {306, 130}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, vertical_force_allocation.u) 
    annotation(Line(points = {{140, -229}, {140, -142.5}, {230, -142.5}, {230, -56}}, color = {0, 0, 127}));
  connect(vertical_force_allocation.y, collective_thrust_limit.u) 
    annotation(Line(points = {{244, -45}, {306, -45}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, normalized_thrust_from_collective.u) 
    annotation(Line(points = {{334, -45}, {396, -45}}, color = {0, 0, 127}));
  connect(normalized_thrust_from_collective.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{424, -45}, {486, -45}}, color = {0, 0, 127}));
  connect(observer_position_state_x.y, enable_observer_position_x.u1) 
    annotation(Line(points = {{-396, 330}, {62.5, 330}, {62.5, 360}, {521, 360}}, color = {0, 0, 127}));
  connect(enable, enable_observer_position_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 360}, {521, 360}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_position_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 25}, {535, 25}, {535, 349}}, color = {0, 0, 127}));
  connect(enable_observer_position_x.y, observer_position_x_out) 
    annotation(Line(points = {{549, 360}, {681, 360}}, color = {0, 0, 127}));
  connect(observer_velocity_state_x.y, enable_observer_velocity_x.u1) 
    annotation(Line(points = {{-396, 290}, {62.5, 290}, {62.5, 322}, {521, 322}}, color = {0, 0, 127}));
  connect(enable, enable_observer_velocity_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 322}, {521, 322}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_velocity_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 6}, {535, 6}, {535, 311}}, color = {0, 0, 127}));
  connect(enable_observer_velocity_x.y, observer_velocity_x_out) 
    annotation(Line(points = {{549, 322}, {681, 322}}, color = {0, 0, 127}));
  connect(pole_position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(points = {{-286, 230}, {117.5, 230}, {117.5, 284}, {521, 284}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 284}, {521, 284}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -13}, {535, -13}, {535, 273}}, color = {0, 0, 127}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(points = {{549, 284}, {681, 284}}, color = {0, 0, 127}));
  connect(pole_velocity_error_x.y, enable_velocity_error_x.u1) 
    annotation(Line(points = {{-286, 190}, {117.5, 190}, {117.5, 246}, {521, 246}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 246}, {521, 246}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -32}, {535, -32}, {535, 235}}, color = {0, 0, 127}));
  connect(enable_velocity_error_x.y, velocity_error_x_out) 
    annotation(Line(points = {{549, 246}, {681, 246}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{154, 210}, {337.5, 210}, {337.5, 208}, {521, 208}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 208}, {521, 208}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -51}, {535, -51}, {535, 197}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{549, 208}, {681, 208}}, color = {0, 0, 127}));
  connect(observer_position_state_y.y, enable_observer_position_y.u1) 
    annotation(Line(points = {{-396, 105}, {62.5, 105}, {62.5, 170}, {521, 170}}, color = {0, 0, 127}));
  connect(enable, enable_observer_position_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 170}, {521, 170}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_position_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -70}, {535, -70}, {535, 159}}, color = {0, 0, 127}));
  connect(enable_observer_position_y.y, observer_position_y_out) 
    annotation(Line(points = {{549, 170}, {681, 170}}, color = {0, 0, 127}));
  connect(observer_velocity_state_y.y, enable_observer_velocity_y.u1) 
    annotation(Line(points = {{-396, 65}, {62.5, 65}, {62.5, 132}, {521, 132}}, color = {0, 0, 127}));
  connect(enable, enable_observer_velocity_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 132}, {521, 132}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_velocity_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -89}, {535, -89}, {535, 121}}, color = {0, 0, 127}));
  connect(enable_observer_velocity_y.y, observer_velocity_y_out) 
    annotation(Line(points = {{549, 132}, {681, 132}}, color = {0, 0, 127}));
  connect(pole_position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(points = {{-286, 5}, {117.5, 5}, {117.5, 94}, {521, 94}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 94}, {521, 94}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -108}, {535, -108}, {535, 83}}, color = {0, 0, 127}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(points = {{549, 94}, {681, 94}}, color = {0, 0, 127}));
  connect(pole_velocity_error_y.y, enable_velocity_error_y.u1) 
    annotation(Line(points = {{-286, -35}, {117.5, -35}, {117.5, 56}, {521, 56}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 56}, {521, 56}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -127}, {535, -127}, {535, 45}}, color = {0, 0, 127}));
  connect(enable_velocity_error_y.y, velocity_error_y_out) 
    annotation(Line(points = {{549, 56}, {681, 56}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{154, -15}, {337.5, -15}, {337.5, 18}, {521, 18}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 18}, {521, 18}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -146}, {535, -146}, {535, 7}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{549, 18}, {681, 18}}, color = {0, 0, 127}));
  connect(observer_position_state_z.y, enable_observer_position_z.u1) 
    annotation(Line(points = {{-396, -120}, {62.5, -120}, {62.5, -20}, {521, -20}}, color = {0, 0, 127}));
  connect(enable, enable_observer_position_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -20}, {521, -20}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_position_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -165}, {535, -165}, {535, -31}}, color = {0, 0, 127}));
  connect(enable_observer_position_z.y, observer_position_z_out) 
    annotation(Line(points = {{549, -20}, {681, -20}}, color = {0, 0, 127}));
  connect(observer_velocity_state_z.y, enable_observer_velocity_z.u1) 
    annotation(Line(points = {{-396, -160}, {62.5, -160}, {62.5, -58}, {521, -58}}, color = {0, 0, 127}));
  connect(enable, enable_observer_velocity_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -58}, {521, -58}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_observer_velocity_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -184}, {535, -184}, {535, -69}}, color = {0, 0, 127}));
  connect(enable_observer_velocity_z.y, observer_velocity_z_out) 
    annotation(Line(points = {{549, -58}, {681, -58}}, color = {0, 0, 127}));
  connect(pole_position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(points = {{-286, -220}, {117.5, -220}, {117.5, -96}, {521, -96}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -96}, {521, -96}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -203}, {535, -203}, {535, -107}}, color = {0, 0, 127}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(points = {{549, -96}, {681, -96}}, color = {0, 0, 127}));
  connect(pole_velocity_error_z.y, enable_velocity_error_z.u1) 
    annotation(Line(points = {{-286, -260}, {117.5, -260}, {117.5, -134}, {521, -134}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -134}, {521, -134}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -222}, {535, -222}, {535, -145}}, color = {0, 0, 127}));
  connect(enable_velocity_error_z.y, velocity_error_z_out) 
    annotation(Line(points = {{549, -134}, {681, -134}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{154, -240}, {337.5, -240}, {337.5, -172}, {521, -172}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -172}, {521, -172}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -241}, {535, -241}, {535, -183}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out) 
    annotation(Line(points = {{549, -172}, {681, -172}}, color = {0, 0, 127}));
  connect(roll_tilt_limit.y, enable_desired_roll_rad.u1) 
    annotation(Line(points = {{320, 64}, {320, -67.5}, {535, -67.5}, {535, -199}}, color = {0, 0, 127}));
  connect(enable, enable_desired_roll_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -210}, {521, -210}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_roll_rad.u3) 
    annotation(Line(points = {{500, -299}, {500, -260}, {535, -260}, {535, -221}}, color = {0, 0, 127}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out) 
    annotation(Line(points = {{549, -210}, {681, -210}}, color = {0, 0, 127}));
  connect(pitch_tilt_limit.y, enable_desired_pitch_rad.u1) 
    annotation(Line(points = {{320, 119}, {320, -59}, {535, -59}, {535, -237}}, color = {0, 0, 127}));
  connect(enable, enable_desired_pitch_rad.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -248}, {521, -248}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3) 
    annotation(Line(points = {{500, -299}, {500, -279}, {535, -279}, {535, -259}}, color = {0, 0, 127}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out) 
    annotation(Line(points = {{549, -248}, {681, -248}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, enable_collective_thrust_n.u1) 
    annotation(Line(points = {{320, -56}, {320, -165.5}, {535, -165.5}, {535, -275}}, color = {0, 0, 127}));
  connect(enable, enable_collective_thrust_n.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -286}, {521, -286}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_collective_thrust_n.u3) 
    annotation(Line(points = {{514, -310}, {517.5, -310}, {517.5, -286}, {521, -286}}, color = {0, 0, 127}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out) 
    annotation(Line(points = {{549, -286}, {681, -286}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{500, -56}, {500, -184.5}, {535, -184.5}, {535, -313}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -324}, {521, -324}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{514, -310}, {517.5, -310}, {517.5, -324}, {521, -324}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{549, -324}, {681, -324}}, color = {0, 0, 127}));

end PolePlacementLuenbergerCore;
