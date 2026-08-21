within MoSimQuadrotorModel.Control.ClassicRobust.Ndi;
model NdiCore "NDI direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(drag_inverse_x_out, position_error_x_out, velocity_error_x_out, virtual_acceleration_x_out, desired_acceleration_x_out, drag_inverse_y_out, position_error_y_out, velocity_error_y_out, virtual_acceleration_y_out, desired_acceleration_y_out, drag_inverse_z_out, position_error_z_out, velocity_error_z_out, virtual_acceleration_z_out, desired_acceleration_z_out, desired_roll_rad_out, desired_pitch_rad_out, collective_thrust_n_out, normalized_thrust_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
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
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, 277}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, 193}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_position_feedback_x(k=8.0) 
    annotation (Placement(transformation(origin = {-370, 277}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_velocity_feedback_x(k=5.0) 
    annotation (Placement(transformation(origin = {-370, 193}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_x_stage_2(inputs="++") 
    annotation (Placement(transformation(origin = {-258, 235}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_x(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 235}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_drag_inverse_x(k=0.1791044776119403) 
    annotation (Placement(transformation(origin = {-50, 157}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_desired_acceleration_pre_gravity_x(inputs="++") 
    annotation (Placement(transformation(origin = {65, 235}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0) 
    annotation (Placement(transformation(origin = {140, 235}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, 62}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, -22}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_position_feedback_y(k=8.0) 
    annotation (Placement(transformation(origin = {-370, 62}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_velocity_feedback_y(k=5.0) 
    annotation (Placement(transformation(origin = {-370, -22}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_y_stage_2(inputs="++") 
    annotation (Placement(transformation(origin = {-258, 20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_y(inputs="++") 
    annotation (Placement(transformation(origin = {-190, 20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_drag_inverse_y(k=0.1791044776119403) 
    annotation (Placement(transformation(origin = {-50, -58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_desired_acceleration_pre_gravity_y(inputs="++") 
    annotation (Placement(transformation(origin = {65, 20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0) 
    annotation (Placement(transformation(origin = {140, 20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, -153}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-500, -237}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_position_feedback_z(k=5.0) 
    annotation (Placement(transformation(origin = {-370, -153}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_velocity_feedback_z(k=4.0) 
    annotation (Placement(transformation(origin = {-370, -237}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_z_stage_2(inputs="++") 
    annotation (Placement(transformation(origin = {-258, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_virtual_acceleration_z(inputs="++") 
    annotation (Placement(transformation(origin = {-190, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ndi_drag_inverse_z(k=0.26865671641791045) 
    annotation (Placement(transformation(origin = {-50, -273}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ndi_desired_acceleration_pre_gravity_z(inputs="++") 
    annotation (Placement(transformation(origin = {65, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665) 
    annotation (Placement(transformation(origin = {55, -123}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z(inputs="++") 
    annotation (Placement(transformation(origin = {140, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_drag_inverse_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport drag_inverse_x_out 
    annotation (Placement(transformation(origin = {695, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 322}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out 
    annotation (Placement(transformation(origin = {695, 322}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 284}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out 
    annotation (Placement(transformation(origin = {695, 284}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_virtual_acceleration_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 246}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport virtual_acceleration_x_out 
    annotation (Placement(transformation(origin = {695, 246}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out 
    annotation (Placement(transformation(origin = {695, 208}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_drag_inverse_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport drag_inverse_y_out 
    annotation (Placement(transformation(origin = {695, 170}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 132}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out 
    annotation (Placement(transformation(origin = {695, 132}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out 
    annotation (Placement(transformation(origin = {695, 94}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_virtual_acceleration_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport virtual_acceleration_y_out 
    annotation (Placement(transformation(origin = {695, 56}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, 18}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out 
    annotation (Placement(transformation(origin = {695, 18}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_drag_inverse_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport drag_inverse_z_out 
    annotation (Placement(transformation(origin = {695, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out 
    annotation (Placement(transformation(origin = {695, -58}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -96}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out 
    annotation (Placement(transformation(origin = {695, -96}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_virtual_acceleration_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {535, -134}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport virtual_acceleration_z_out 
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
  connect(reference_position_x, ndi_position_error_x.u1) 
    annotation(Line(points = {{-666, 126}, {-590, 126}, {-590, 277}, {-514, 277}}, color = {0, 0, 127}));
  connect(position_x, ndi_position_error_x.u2) 
    annotation(Line(points = {{-666, 350}, {-590, 350}, {-590, 277}, {-514, 277}}, color = {0, 0, 127}));
  connect(reference_velocity_x, ndi_velocity_error_x.u1) 
    annotation(Line(points = {{-666, 14}, {-590, 14}, {-590, 193}, {-514, 193}}, color = {0, 0, 127}));
  connect(velocity_x, ndi_velocity_error_x.u2) 
    annotation(Line(points = {{-666, 238}, {-590, 238}, {-590, 193}, {-514, 193}}, color = {0, 0, 127}));
  connect(ndi_position_error_x.y, ndi_position_feedback_x.u) 
    annotation(Line(points = {{-486, 277}, {-384, 277}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_x.y, ndi_velocity_feedback_x.u) 
    annotation(Line(points = {{-486, 193}, {-384, 193}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, ndi_virtual_acceleration_x_stage_2.u1) 
    annotation(Line(points = {{-666, -98}, {-469, -98}, {-469, 235}, {-272, 235}}, color = {0, 0, 127}));
  connect(ndi_position_feedback_x.y, ndi_virtual_acceleration_x_stage_2.u2) 
    annotation(Line(points = {{-356, 277}, {-314, 277}, {-314, 235}, {-272, 235}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_x_stage_2.y, ndi_virtual_acceleration_x.u1) 
    annotation(Line(points = {{-244, 235}, {-204, 235}}, color = {0, 0, 127}));
  connect(ndi_velocity_feedback_x.y, ndi_virtual_acceleration_x.u2) 
    annotation(Line(points = {{-356, 193}, {-280, 193}, {-280, 235}, {-204, 235}}, color = {0, 0, 127}));
  connect(velocity_x, ndi_drag_inverse_x.u) 
    annotation(Line(points = {{-666, 238}, {-365, 238}, {-365, 157}, {-64, 157}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_x.y, ndi_desired_acceleration_pre_gravity_x.u1) 
    annotation(Line(points = {{-176, 235}, {51, 235}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_x.y, ndi_desired_acceleration_pre_gravity_x.u2) 
    annotation(Line(points = {{-36, 157}, {7.5, 157}, {7.5, 235}, {51, 235}}, color = {0, 0, 127}));
  connect(ndi_desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u) 
    annotation(Line(points = {{79, 235}, {126, 235}}, color = {0, 0, 127}));
  connect(reference_position_y, ndi_position_error_y.u1) 
    annotation(Line(points = {{-666, 100}, {-590, 100}, {-590, 62}, {-514, 62}}, color = {0, 0, 127}));
  connect(position_y, ndi_position_error_y.u2) 
    annotation(Line(points = {{-680, 313}, {-680, 193}, {-500, 193}, {-500, 73}}, color = {0, 0, 127}));
  connect(reference_velocity_y, ndi_velocity_error_y.u1) 
    annotation(Line(points = {{-666, -12}, {-590, -12}, {-590, -22}, {-514, -22}}, color = {0, 0, 127}));
  connect(velocity_y, ndi_velocity_error_y.u2) 
    annotation(Line(points = {{-680, 201}, {-680, 95}, {-500, 95}, {-500, -11}}, color = {0, 0, 127}));
  connect(ndi_position_error_y.y, ndi_position_feedback_y.u) 
    annotation(Line(points = {{-486, 62}, {-384, 62}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_y.y, ndi_velocity_feedback_y.u) 
    annotation(Line(points = {{-486, -22}, {-384, -22}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, ndi_virtual_acceleration_y_stage_2.u1) 
    annotation(Line(points = {{-666, -124}, {-469, -124}, {-469, 20}, {-272, 20}}, color = {0, 0, 127}));
  connect(ndi_position_feedback_y.y, ndi_virtual_acceleration_y_stage_2.u2) 
    annotation(Line(points = {{-356, 62}, {-314, 62}, {-314, 20}, {-272, 20}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_y_stage_2.y, ndi_virtual_acceleration_y.u1) 
    annotation(Line(points = {{-244, 20}, {-204, 20}}, color = {0, 0, 127}));
  connect(ndi_velocity_feedback_y.y, ndi_virtual_acceleration_y.u2) 
    annotation(Line(points = {{-356, -22}, {-280, -22}, {-280, 20}, {-204, 20}}, color = {0, 0, 127}));
  connect(velocity_y, ndi_drag_inverse_y.u) 
    annotation(Line(points = {{-666, 212}, {-365, 212}, {-365, -58}, {-64, -58}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_y.y, ndi_desired_acceleration_pre_gravity_y.u1) 
    annotation(Line(points = {{-176, 20}, {51, 20}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_y.y, ndi_desired_acceleration_pre_gravity_y.u2) 
    annotation(Line(points = {{-36, -58}, {7.5, -58}, {7.5, 20}, {51, 20}}, color = {0, 0, 127}));
  connect(ndi_desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u) 
    annotation(Line(points = {{79, 20}, {126, 20}}, color = {0, 0, 127}));
  connect(reference_position_z, ndi_position_error_z.u1) 
    annotation(Line(points = {{-680, 63}, {-680, -39.5}, {-500, -39.5}, {-500, -142}}, color = {0, 0, 127}));
  connect(position_z, ndi_position_error_z.u2) 
    annotation(Line(points = {{-680, 287}, {-680, 72.5}, {-500, 72.5}, {-500, -142}}, color = {0, 0, 127}));
  connect(reference_velocity_z, ndi_velocity_error_z.u1) 
    annotation(Line(points = {{-680, -49}, {-680, -137.5}, {-500, -137.5}, {-500, -226}}, color = {0, 0, 127}));
  connect(velocity_z, ndi_velocity_error_z.u2) 
    annotation(Line(points = {{-680, 175}, {-680, -25.5}, {-500, -25.5}, {-500, -226}}, color = {0, 0, 127}));
  connect(ndi_position_error_z.y, ndi_position_feedback_z.u) 
    annotation(Line(points = {{-486, -153}, {-384, -153}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_z.y, ndi_velocity_feedback_z.u) 
    annotation(Line(points = {{-486, -237}, {-384, -237}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, ndi_virtual_acceleration_z_stage_2.u1) 
    annotation(Line(points = {{-666, -150}, {-469, -150}, {-469, -195}, {-272, -195}}, color = {0, 0, 127}));
  connect(ndi_position_feedback_z.y, ndi_virtual_acceleration_z_stage_2.u2) 
    annotation(Line(points = {{-356, -153}, {-314, -153}, {-314, -195}, {-272, -195}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_z_stage_2.y, ndi_virtual_acceleration_z.u1) 
    annotation(Line(points = {{-244, -195}, {-204, -195}}, color = {0, 0, 127}));
  connect(ndi_velocity_feedback_z.y, ndi_virtual_acceleration_z.u2) 
    annotation(Line(points = {{-356, -237}, {-280, -237}, {-280, -195}, {-204, -195}}, color = {0, 0, 127}));
  connect(velocity_z, ndi_drag_inverse_z.u) 
    annotation(Line(points = {{-666, 186}, {-365, 186}, {-365, -273}, {-64, -273}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_z.y, ndi_desired_acceleration_pre_gravity_z.u1) 
    annotation(Line(points = {{-176, -195}, {51, -195}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_z.y, ndi_desired_acceleration_pre_gravity_z.u2) 
    annotation(Line(points = {{-36, -273}, {7.5, -273}, {7.5, -195}, {51, -195}}, color = {0, 0, 127}));
  connect(ndi_desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1) 
    annotation(Line(points = {{79, -195}, {126, -195}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z.u2) 
    annotation(Line(points = {{69, -123}, {97.5, -123}, {97.5, -195}, {126, -195}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u) 
    annotation(Line(points = {{154, 20}, {185, 20}, {185, 75}, {216, 75}}, color = {0, 0, 127}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u) 
    annotation(Line(points = {{244, 75}, {306, 75}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u) 
    annotation(Line(points = {{140, 224}, {140, 182.5}, {230, 182.5}, {230, 141}}, color = {0, 0, 127}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u) 
    annotation(Line(points = {{244, 130}, {306, 130}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, vertical_force_allocation.u) 
    annotation(Line(points = {{140, -184}, {140, -120}, {230, -120}, {230, -56}}, color = {0, 0, 127}));
  connect(vertical_force_allocation.y, collective_thrust_limit.u) 
    annotation(Line(points = {{244, -45}, {306, -45}}, color = {0, 0, 127}));
  connect(collective_thrust_limit.y, normalized_thrust_from_collective.u) 
    annotation(Line(points = {{334, -45}, {396, -45}}, color = {0, 0, 127}));
  connect(normalized_thrust_from_collective.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{424, -45}, {486, -45}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_x.y, enable_drag_inverse_x.u1) 
    annotation(Line(points = {{-36, 157}, {242.5, 157}, {242.5, 360}, {521, 360}}, color = {0, 0, 127}));
  connect(enable, enable_drag_inverse_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 360}, {521, 360}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_drag_inverse_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 25}, {535, 25}, {535, 349}}, color = {0, 0, 127}));
  connect(enable_drag_inverse_x.y, drag_inverse_x_out) 
    annotation(Line(points = {{549, 360}, {681, 360}}, color = {0, 0, 127}));
  connect(ndi_position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(points = {{-486, 277}, {17.5, 277}, {17.5, 322}, {521, 322}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 322}, {521, 322}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(points = {{500, -299}, {500, 6}, {535, 6}, {535, 311}}, color = {0, 0, 127}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(points = {{549, 322}, {681, 322}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_x.y, enable_velocity_error_x.u1) 
    annotation(Line(points = {{-486, 193}, {17.5, 193}, {17.5, 284}, {521, 284}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 284}, {521, 284}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -13}, {535, -13}, {535, 273}}, color = {0, 0, 127}));
  connect(enable_velocity_error_x.y, velocity_error_x_out) 
    annotation(Line(points = {{549, 284}, {681, 284}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_x.y, enable_virtual_acceleration_x.u1) 
    annotation(Line(points = {{-176, 235}, {172.5, 235}, {172.5, 246}, {521, 246}}, color = {0, 0, 127}));
  connect(enable, enable_virtual_acceleration_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 246}, {521, 246}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_virtual_acceleration_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -32}, {535, -32}, {535, 235}}, color = {0, 0, 127}));
  connect(enable_virtual_acceleration_x.y, virtual_acceleration_x_out) 
    annotation(Line(points = {{549, 246}, {681, 246}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{154, 235}, {337.5, 235}, {337.5, 208}, {521, 208}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 208}, {521, 208}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{500, -299}, {500, -51}, {535, -51}, {535, 197}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{549, 208}, {681, 208}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_y.y, enable_drag_inverse_y.u1) 
    annotation(Line(points = {{-36, -58}, {242.5, -58}, {242.5, 170}, {521, 170}}, color = {0, 0, 127}));
  connect(enable, enable_drag_inverse_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 170}, {521, 170}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_drag_inverse_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -70}, {535, -70}, {535, 159}}, color = {0, 0, 127}));
  connect(enable_drag_inverse_y.y, drag_inverse_y_out) 
    annotation(Line(points = {{549, 170}, {681, 170}}, color = {0, 0, 127}));
  connect(ndi_position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(points = {{-486, 62}, {17.5, 62}, {17.5, 132}, {521, 132}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 132}, {521, 132}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -89}, {535, -89}, {535, 121}}, color = {0, 0, 127}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(points = {{549, 132}, {681, 132}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_y.y, enable_velocity_error_y.u1) 
    annotation(Line(points = {{-486, -22}, {17.5, -22}, {17.5, 94}, {521, 94}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 94}, {521, 94}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -108}, {535, -108}, {535, 83}}, color = {0, 0, 127}));
  connect(enable_velocity_error_y.y, velocity_error_y_out) 
    annotation(Line(points = {{549, 94}, {681, 94}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_y.y, enable_virtual_acceleration_y.u1) 
    annotation(Line(points = {{-176, 20}, {172.5, 20}, {172.5, 56}, {521, 56}}, color = {0, 0, 127}));
  connect(enable, enable_virtual_acceleration_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 56}, {521, 56}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_virtual_acceleration_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -127}, {535, -127}, {535, 45}}, color = {0, 0, 127}));
  connect(enable_virtual_acceleration_y.y, virtual_acceleration_y_out) 
    annotation(Line(points = {{549, 56}, {681, 56}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{154, 20}, {337.5, 20}, {337.5, 18}, {521, 18}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, 18}, {521, 18}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{500, -299}, {500, -146}, {535, -146}, {535, 7}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{549, 18}, {681, 18}}, color = {0, 0, 127}));
  connect(ndi_drag_inverse_z.y, enable_drag_inverse_z.u1) 
    annotation(Line(points = {{-36, -273}, {242.5, -273}, {242.5, -20}, {521, -20}}, color = {0, 0, 127}));
  connect(enable, enable_drag_inverse_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -20}, {521, -20}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_drag_inverse_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -165}, {535, -165}, {535, -31}}, color = {0, 0, 127}));
  connect(enable_drag_inverse_z.y, drag_inverse_z_out) 
    annotation(Line(points = {{549, -20}, {681, -20}}, color = {0, 0, 127}));
  connect(ndi_position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(points = {{-486, -153}, {17.5, -153}, {17.5, -58}, {521, -58}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -58}, {521, -58}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -184}, {535, -184}, {535, -69}}, color = {0, 0, 127}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(points = {{549, -58}, {681, -58}}, color = {0, 0, 127}));
  connect(ndi_velocity_error_z.y, enable_velocity_error_z.u1) 
    annotation(Line(points = {{-486, -237}, {17.5, -237}, {17.5, -96}, {521, -96}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -96}, {521, -96}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -203}, {535, -203}, {535, -107}}, color = {0, 0, 127}));
  connect(enable_velocity_error_z.y, velocity_error_z_out) 
    annotation(Line(points = {{549, -96}, {681, -96}}, color = {0, 0, 127}));
  connect(ndi_virtual_acceleration_z.y, enable_virtual_acceleration_z.u1) 
    annotation(Line(points = {{-176, -195}, {172.5, -195}, {172.5, -134}, {521, -134}}, color = {0, 0, 127}));
  connect(enable, enable_virtual_acceleration_z.u2) 
    annotation(Line(points = {{-666, -285}, {-72.5, -285}, {-72.5, -134}, {521, -134}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_virtual_acceleration_z.u3) 
    annotation(Line(points = {{500, -299}, {500, -222}, {535, -222}, {535, -145}}, color = {0, 0, 127}));
  connect(enable_virtual_acceleration_z.y, virtual_acceleration_z_out) 
    annotation(Line(points = {{549, -134}, {681, -134}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{154, -195}, {337.5, -195}, {337.5, -172}, {521, -172}}, color = {0, 0, 127}));
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

end NdiCore;