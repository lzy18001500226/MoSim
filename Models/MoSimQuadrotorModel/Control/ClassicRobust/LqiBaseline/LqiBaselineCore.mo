within MoSimQuadrotorModel.Control.ClassicRobust.LqiBaseline;
model LqiBaselineCore "LQI outer-loop direct graphical core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(position_x, position_y, position_z, velocity_x, velocity_y, velocity_z, reference_position_x, reference_position_y, reference_position_z, reference_velocity_x, reference_velocity_y, reference_velocity_z, reference_acceleration_x, reference_acceleration_y, reference_acceleration_z, dt, enable), Right(position_error_x_out, position_error_y_out, position_error_z_out, velocity_error_x_out, velocity_error_y_out, velocity_error_z_out, desired_acceleration_x_out, desired_acceleration_y_out, desired_acceleration_z_out, integral_position_error_x_out, integral_position_error_y_out, integral_position_error_z_out, desired_roll_rad_out, desired_pitch_rad_out, normalized_thrust_out, collective_thrust_n_out)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.004),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1,IntegratorStep=0,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport position_x 
    annotation (Placement(transformation(origin = {-650, 350}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_y 
    annotation (Placement(transformation(origin = {-650, 324}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport position_z 
    annotation (Placement(transformation(origin = {-650, 298}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_x 
    annotation (Placement(transformation(origin = {-650, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_y 
    annotation (Placement(transformation(origin = {-650, 214}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport velocity_z 
    annotation (Placement(transformation(origin = {-650, 188}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_x 
    annotation (Placement(transformation(origin = {-650, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_y 
    annotation (Placement(transformation(origin = {-650, 104}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_position_z 
    annotation (Placement(transformation(origin = {-650, 78}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_x 
    annotation (Placement(transformation(origin = {-650, 20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_y 
    annotation (Placement(transformation(origin = {-650, -6}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_velocity_z 
    annotation (Placement(transformation(origin = {-650, -32}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_x 
    annotation (Placement(transformation(origin = {-650, -90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_y 
    annotation (Placement(transformation(origin = {-650, -116}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport reference_acceleration_z 
    annotation (Placement(transformation(origin = {-650, -142}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport dt 
    annotation (Placement(transformation(origin = {-650, -245}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Inport enable 
    annotation (Placement(transformation(origin = {-650, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant disabled_command(k=0.0) 
    annotation (Placement(transformation(origin = {510, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, 297}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, 213}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_x(k=1.6) 
    annotation (Placement(transformation(origin = {-400, 297}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_x(k=1.8) 
    annotation (Placement(transformation(origin = {-400, 213}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_x(inputs="++") 
    annotation (Placement(transformation(origin = {-300, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay integral_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, 135}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product integral_drive_x(inputs="**") 
    annotation (Placement(transformation(origin = {-315, 135}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum integral_pre_x(inputs="++") 
    annotation (Placement(transformation(origin = {-230, 135}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation integral_limit_x(lowLimit=-0.5,upLimit=0.5) 
    annotation (Placement(transformation(origin = {-145, 135}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain integral_gain_x(k=0.2) 
    annotation (Placement(transformation(origin = {-65, 135}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqi_feedback_x(inputs="++") 
    annotation (Placement(transformation(origin = {-65, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_x(inputs="++") 
    annotation (Placement(transformation(origin = {35, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_x(k=1.0) 
    annotation (Placement(transformation(origin = {125, 255}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, 87}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, 3}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_y(k=1.6) 
    annotation (Placement(transformation(origin = {-400, 87}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_y(k=1.8) 
    annotation (Placement(transformation(origin = {-400, 3}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_y(inputs="++") 
    annotation (Placement(transformation(origin = {-300, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay integral_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product integral_drive_y(inputs="**") 
    annotation (Placement(transformation(origin = {-315, -75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum integral_pre_y(inputs="++") 
    annotation (Placement(transformation(origin = {-230, -75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation integral_limit_y(lowLimit=-0.5,upLimit=0.5) 
    annotation (Placement(transformation(origin = {-145, -75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain integral_gain_y(k=0.2) 
    annotation (Placement(transformation(origin = {-65, -75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqi_feedback_y(inputs="++") 
    annotation (Placement(transformation(origin = {-65, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_y(inputs="++") 
    annotation (Placement(transformation(origin = {35, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain desired_acceleration_y(k=1.0) 
    annotation (Placement(transformation(origin = {125, 45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, -123}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-510, -207}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_gain_z(k=2.2) 
    annotation (Placement(transformation(origin = {-400, -123}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_gain_z(k=2.0) 
    annotation (Placement(transformation(origin = {-400, -207}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pv_feedback_z(inputs="++") 
    annotation (Placement(transformation(origin = {-300, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay integral_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-410, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product integral_drive_z(inputs="**") 
    annotation (Placement(transformation(origin = {-315, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum integral_pre_z(inputs="++") 
    annotation (Placement(transformation(origin = {-230, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation integral_limit_z(lowLimit=-0.35,upLimit=0.35) 
    annotation (Placement(transformation(origin = {-145, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain integral_gain_z(k=0.3) 
    annotation (Placement(transformation(origin = {-65, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum lqi_feedback_z(inputs="++") 
    annotation (Placement(transformation(origin = {-65, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_pre_gravity_z(inputs="++") 
    annotation (Placement(transformation(origin = {35, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity_compensation(k=9.80665) 
    annotation (Placement(transformation(origin = {35, -95}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acceleration_z(inputs="++") 
    annotation (Placement(transformation(origin = {125, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_from_lateral_acceleration(k=-0.10197162129779283) 
    annotation (Placement(transformation(origin = {240, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    "Attitude adapter roll limit from lateral acceleration" annotation (Placement(transformation(origin = {325, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_from_lateral_acceleration(k=0.10197162129779283) 
    annotation (Placement(transformation(origin = {240, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_tilt_limit(lowLimit=-0.5235987755982988,upLimit=0.5235987755982988)
    "Attitude adapter pitch limit from lateral acceleration" annotation (Placement(transformation(origin = {325, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain normalized_thrust_pre_limit(k=0.03772949988018335) 
    annotation (Placement(transformation(origin = {240, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation normalized_thrust_limit(lowLimit=0.0,upLimit=1.0)
    "Normalized thrust saturation [0, 1]" annotation (Placement(transformation(origin = {325, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain collective_thrust_from_normalized(k=17.745945945945948)
    "Collective thrust allocation from normalized thrust" annotation (Placement(transformation(origin = {410, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_x_out 
    annotation (Placement(transformation(origin = {675, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_y_out 
    annotation (Placement(transformation(origin = {675, 292}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_position_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport position_error_z_out 
    annotation (Placement(transformation(origin = {675, 254}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_x_out 
    annotation (Placement(transformation(origin = {675, 216}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_y_out 
    annotation (Placement(transformation(origin = {675, 178}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_velocity_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport velocity_error_z_out 
    annotation (Placement(transformation(origin = {675, 140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x_out 
    annotation (Placement(transformation(origin = {675, 102}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y_out 
    annotation (Placement(transformation(origin = {675, 64}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_acceleration_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z_out 
    annotation (Placement(transformation(origin = {675, 26}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_integral_position_error_x(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport integral_position_error_x_out 
    annotation (Placement(transformation(origin = {675, -12}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_integral_position_error_y(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport integral_position_error_y_out 
    annotation (Placement(transformation(origin = {675, -50}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_integral_position_error_z(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -88}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport integral_position_error_z_out 
    annotation (Placement(transformation(origin = {675, -88}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_roll_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_roll_rad_out 
    annotation (Placement(transformation(origin = {675, -126}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_desired_pitch_rad(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -164}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_pitch_rad_out 
    annotation (Placement(transformation(origin = {675, -164}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_normalized_thrust(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust_out 
    annotation (Placement(transformation(origin = {675, -202}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_collective_thrust_n(threshold=0.5) 
    annotation (Placement(transformation(origin = {525, -240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n_out 
    annotation (Placement(transformation(origin = {675, -240}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(reference_position_x, position_error_x.u1) 
    annotation(Line(points = {{-650, 141}, {-650, 213.5}, {-510, 213.5}, {-510, 286}}, color = {0, 0, 127}));
  connect(position_x, position_error_x.u2) 
    annotation(Line(points = {{-636, 350}, {-580, 350}, {-580, 297}, {-524, 297}}, color = {0, 0, 127}));
  connect(reference_velocity_x, velocity_error_x.u1) 
    annotation(Line(points = {{-650, 31}, {-650, 116.5}, {-510, 116.5}, {-510, 202}}, color = {0, 0, 127}));
  connect(velocity_x, velocity_error_x.u2) 
    annotation(Line(points = {{-636, 240}, {-580, 240}, {-580, 213}, {-524, 213}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_gain_x.u) 
    annotation(Line(points = {{-496, 297}, {-414, 297}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, velocity_gain_x.u) 
    annotation(Line(points = {{-496, 213}, {-414, 213}}, color = {0, 0, 127}));
  connect(position_gain_x.y, pv_feedback_x.u1) 
    annotation(Line(points = {{-386, 297}, {-350, 297}, {-350, 255}, {-314, 255}}, color = {0, 0, 127}));
  connect(velocity_gain_x.y, pv_feedback_x.u2) 
    annotation(Line(points = {{-386, 213}, {-350, 213}, {-350, 255}, {-314, 255}}, color = {0, 0, 127}));
  connect(position_error_x.y, integral_drive_x.u1) 
    annotation(Line(points = {{-496, 297}, {-412.5, 297}, {-412.5, 135}, {-329, 135}}, color = {0, 0, 127}));
  connect(dt, integral_drive_x.u2) 
    annotation(Line(points = {{-650, -234}, {-650, -55}, {-315, -55}, {-315, 124}}, color = {0, 0, 127}));
  connect(integral_state_x.y, integral_pre_x.u1) 
    annotation(Line(points = {{-396, 135}, {-244, 135}}, color = {0, 0, 127}));
  connect(integral_drive_x.y, integral_pre_x.u2) 
    annotation(Line(points = {{-301, 135}, {-244, 135}}, color = {0, 0, 127}));
  connect(integral_pre_x.y, integral_limit_x.u) 
    annotation(Line(points = {{-216, 135}, {-159, 135}}, color = {0, 0, 127}));
  connect(integral_limit_x.y, integral_state_x.u1) 
    annotation(Line(points = {{-159, 135}, {-396, 135}}, color = {0, 0, 127}));
  connect(integral_limit_x.y, integral_gain_x.u) 
    annotation(Line(points = {{-131, 135}, {-79, 135}}, color = {0, 0, 127}));
  connect(pv_feedback_x.y, lqi_feedback_x.u1) 
    annotation(Line(points = {{-286, 255}, {-79, 255}}, color = {0, 0, 127}));
  connect(integral_gain_x.y, lqi_feedback_x.u2) 
    annotation(Line(points = {{-65, 146}, {-65, 244}}, color = {0, 0, 127}));
  connect(reference_acceleration_x, desired_acceleration_pre_gravity_x.u1) 
    annotation(Line(points = {{-636, -90}, {-307.5, -90}, {-307.5, 255}, {21, 255}}, color = {0, 0, 127}));
  connect(lqi_feedback_x.y, desired_acceleration_pre_gravity_x.u2) 
    annotation(Line(points = {{-51, 255}, {21, 255}}, color = {0, 0, 127}));
  connect(desired_acceleration_pre_gravity_x.y, desired_acceleration_x.u) 
    annotation(Line(points = {{49, 255}, {111, 255}}, color = {0, 0, 127}));
  connect(reference_position_y, position_error_y.u1) 
    annotation(Line(points = {{-636, 104}, {-580, 104}, {-580, 87}, {-524, 87}}, color = {0, 0, 127}));
  connect(position_y, position_error_y.u2) 
    annotation(Line(points = {{-650, 313}, {-650, 205.5}, {-510, 205.5}, {-510, 98}}, color = {0, 0, 127}));
  connect(reference_velocity_y, velocity_error_y.u1) 
    annotation(Line(points = {{-636, -6}, {-580, -6}, {-580, 3}, {-524, 3}}, color = {0, 0, 127}));
  connect(velocity_y, velocity_error_y.u2) 
    annotation(Line(points = {{-650, 203}, {-650, 108.5}, {-510, 108.5}, {-510, 14}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_gain_y.u) 
    annotation(Line(points = {{-496, 87}, {-414, 87}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, velocity_gain_y.u) 
    annotation(Line(points = {{-496, 3}, {-414, 3}}, color = {0, 0, 127}));
  connect(position_gain_y.y, pv_feedback_y.u1) 
    annotation(Line(points = {{-386, 87}, {-350, 87}, {-350, 45}, {-314, 45}}, color = {0, 0, 127}));
  connect(velocity_gain_y.y, pv_feedback_y.u2) 
    annotation(Line(points = {{-386, 3}, {-350, 3}, {-350, 45}, {-314, 45}}, color = {0, 0, 127}));
  connect(position_error_y.y, integral_drive_y.u1) 
    annotation(Line(points = {{-496, 87}, {-412.5, 87}, {-412.5, -75}, {-329, -75}}, color = {0, 0, 127}));
  connect(dt, integral_drive_y.u2) 
    annotation(Line(points = {{-636, -245}, {-482.5, -245}, {-482.5, -75}, {-329, -75}}, color = {0, 0, 127}));
  connect(integral_state_y.y, integral_pre_y.u1) 
    annotation(Line(points = {{-396, -75}, {-244, -75}}, color = {0, 0, 127}));
  connect(integral_drive_y.y, integral_pre_y.u2) 
    annotation(Line(points = {{-301, -75}, {-244, -75}}, color = {0, 0, 127}));
  connect(integral_pre_y.y, integral_limit_y.u) 
    annotation(Line(points = {{-216, -75}, {-159, -75}}, color = {0, 0, 127}));
  connect(integral_limit_y.y, integral_state_y.u1) 
    annotation(Line(points = {{-159, -75}, {-396, -75}}, color = {0, 0, 127}));
  connect(integral_limit_y.y, integral_gain_y.u) 
    annotation(Line(points = {{-131, -75}, {-79, -75}}, color = {0, 0, 127}));
  connect(pv_feedback_y.y, lqi_feedback_y.u1) 
    annotation(Line(points = {{-286, 45}, {-79, 45}}, color = {0, 0, 127}));
  connect(integral_gain_y.y, lqi_feedback_y.u2) 
    annotation(Line(points = {{-65, -64}, {-65, 34}}, color = {0, 0, 127}));
  connect(reference_acceleration_y, desired_acceleration_pre_gravity_y.u1) 
    annotation(Line(points = {{-636, -116}, {-307.5, -116}, {-307.5, 45}, {21, 45}}, color = {0, 0, 127}));
  connect(lqi_feedback_y.y, desired_acceleration_pre_gravity_y.u2) 
    annotation(Line(points = {{-51, 45}, {21, 45}}, color = {0, 0, 127}));
  connect(desired_acceleration_pre_gravity_y.y, desired_acceleration_y.u) 
    annotation(Line(points = {{49, 45}, {111, 45}}, color = {0, 0, 127}));
  connect(reference_position_z, position_error_z.u1) 
    annotation(Line(points = {{-650, 67}, {-650, -22.5}, {-510, -22.5}, {-510, -112}}, color = {0, 0, 127}));
  connect(position_z, position_error_z.u2) 
    annotation(Line(points = {{-650, 287}, {-650, 87.5}, {-510, 87.5}, {-510, -112}}, color = {0, 0, 127}));
  connect(reference_velocity_z, velocity_error_z.u1) 
    annotation(Line(points = {{-650, -43}, {-650, -119.5}, {-510, -119.5}, {-510, -196}}, color = {0, 0, 127}));
  connect(velocity_z, velocity_error_z.u2) 
    annotation(Line(points = {{-650, 177}, {-650, -9.5}, {-510, -9.5}, {-510, -196}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_gain_z.u) 
    annotation(Line(points = {{-496, -123}, {-414, -123}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, velocity_gain_z.u) 
    annotation(Line(points = {{-496, -207}, {-414, -207}}, color = {0, 0, 127}));
  connect(position_gain_z.y, pv_feedback_z.u1) 
    annotation(Line(points = {{-386, -123}, {-350, -123}, {-350, -165}, {-314, -165}}, color = {0, 0, 127}));
  connect(velocity_gain_z.y, pv_feedback_z.u2) 
    annotation(Line(points = {{-386, -207}, {-350, -207}, {-350, -165}, {-314, -165}}, color = {0, 0, 127}));
  connect(position_error_z.y, integral_drive_z.u1) 
    annotation(Line(points = {{-496, -123}, {-412.5, -123}, {-412.5, -285}, {-329, -285}}, color = {0, 0, 127}));
  connect(dt, integral_drive_z.u2) 
    annotation(Line(points = {{-636, -245}, {-482.5, -245}, {-482.5, -285}, {-329, -285}}, color = {0, 0, 127}));
  connect(integral_state_z.y, integral_pre_z.u1) 
    annotation(Line(points = {{-396, -285}, {-244, -285}}, color = {0, 0, 127}));
  connect(integral_drive_z.y, integral_pre_z.u2) 
    annotation(Line(points = {{-301, -285}, {-244, -285}}, color = {0, 0, 127}));
  connect(integral_pre_z.y, integral_limit_z.u) 
    annotation(Line(points = {{-216, -285}, {-159, -285}}, color = {0, 0, 127}));
  connect(integral_limit_z.y, integral_state_z.u1) 
    annotation(Line(points = {{-159, -285}, {-396, -285}}, color = {0, 0, 127}));
  connect(integral_limit_z.y, integral_gain_z.u) 
    annotation(Line(points = {{-131, -285}, {-79, -285}}, color = {0, 0, 127}));
  connect(pv_feedback_z.y, lqi_feedback_z.u1) 
    annotation(Line(points = {{-286, -165}, {-79, -165}}, color = {0, 0, 127}));
  connect(integral_gain_z.y, lqi_feedback_z.u2) 
    annotation(Line(points = {{-65, -274}, {-65, -176}}, color = {0, 0, 127}));
  connect(reference_acceleration_z, desired_acceleration_pre_gravity_z.u1) 
    annotation(Line(points = {{-636, -142}, {-307.5, -142}, {-307.5, -165}, {21, -165}}, color = {0, 0, 127}));
  connect(lqi_feedback_z.y, desired_acceleration_pre_gravity_z.u2) 
    annotation(Line(points = {{-51, -165}, {21, -165}}, color = {0, 0, 127}));
  connect(desired_acceleration_pre_gravity_z.y, desired_acceleration_z.u1) 
    annotation(Line(points = {{49, -165}, {111, -165}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z.u2) 
    annotation(Line(points = {{49, -95}, {80, -95}, {80, -165}, {111, -165}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, roll_from_lateral_acceleration.u) 
    annotation(Line(points = {{139, 45}, {182.5, 45}, {182.5, 55}, {226, 55}}, color = {0, 0, 127}));
  connect(roll_from_lateral_acceleration.y, roll_tilt_limit.u) 
    annotation(Line(points = {{254, 55}, {311, 55}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, pitch_from_lateral_acceleration.u) 
    annotation(Line(points = {{125, 244}, {125, 187.5}, {240, 187.5}, {240, 131}}, color = {0, 0, 127}));
  connect(pitch_from_lateral_acceleration.y, pitch_tilt_limit.u) 
    annotation(Line(points = {{254, 120}, {311, 120}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, normalized_thrust_pre_limit.u) 
    annotation(Line(points = {{139, -165}, {182.5, -165}, {182.5, -55}, {226, -55}}, color = {0, 0, 127}));
  connect(normalized_thrust_pre_limit.y, normalized_thrust_limit.u) 
    annotation(Line(points = {{254, -55}, {311, -55}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, collective_thrust_from_normalized.u) 
    annotation(Line(points = {{339, -55}, {396, -55}}, color = {0, 0, 127}));
  connect(position_error_x.y, enable_position_error_x.u1) 
    annotation(Line(points = {{-496, 297}, {7.5, 297}, {7.5, 330}, {511, 330}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_x.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 330}, {511, 330}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_x.u3) 
    annotation(Line(points = {{510, -259}, {510, 30}, {525, 30}, {525, 319}}, color = {0, 0, 127}));
  connect(enable_position_error_x.y, position_error_x_out) 
    annotation(Line(points = {{539, 330}, {661, 330}}, color = {0, 0, 127}));
  connect(position_error_y.y, enable_position_error_y.u1) 
    annotation(Line(points = {{-496, 87}, {7.5, 87}, {7.5, 292}, {511, 292}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_y.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 292}, {511, 292}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_y.u3) 
    annotation(Line(points = {{510, -259}, {510, 11}, {525, 11}, {525, 281}}, color = {0, 0, 127}));
  connect(enable_position_error_y.y, position_error_y_out) 
    annotation(Line(points = {{539, 292}, {661, 292}}, color = {0, 0, 127}));
  connect(position_error_z.y, enable_position_error_z.u1) 
    annotation(Line(points = {{-496, -123}, {7.5, -123}, {7.5, 254}, {511, 254}}, color = {0, 0, 127}));
  connect(enable, enable_position_error_z.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 254}, {511, 254}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_position_error_z.u3) 
    annotation(Line(points = {{510, -259}, {510, -8}, {525, -8}, {525, 243}}, color = {0, 0, 127}));
  connect(enable_position_error_z.y, position_error_z_out) 
    annotation(Line(points = {{539, 254}, {661, 254}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, enable_velocity_error_x.u1) 
    annotation(Line(points = {{-496, 213}, {7.5, 213}, {7.5, 216}, {511, 216}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_x.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 216}, {511, 216}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_x.u3) 
    annotation(Line(points = {{510, -259}, {510, -27}, {525, -27}, {525, 205}}, color = {0, 0, 127}));
  connect(enable_velocity_error_x.y, velocity_error_x_out) 
    annotation(Line(points = {{539, 216}, {661, 216}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, enable_velocity_error_y.u1) 
    annotation(Line(points = {{-496, 3}, {7.5, 3}, {7.5, 178}, {511, 178}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_y.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 178}, {511, 178}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_y.u3) 
    annotation(Line(points = {{510, -259}, {510, -46}, {525, -46}, {525, 167}}, color = {0, 0, 127}));
  connect(enable_velocity_error_y.y, velocity_error_y_out) 
    annotation(Line(points = {{539, 178}, {661, 178}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, enable_velocity_error_z.u1) 
    annotation(Line(points = {{-496, -207}, {7.5, -207}, {7.5, 140}, {511, 140}}, color = {0, 0, 127}));
  connect(enable, enable_velocity_error_z.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 140}, {511, 140}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_velocity_error_z.u3) 
    annotation(Line(points = {{510, -259}, {510, -65}, {525, -65}, {525, 129}}, color = {0, 0, 127}));
  connect(enable_velocity_error_z.y, velocity_error_z_out) 
    annotation(Line(points = {{539, 140}, {661, 140}}, color = {0, 0, 127}));
  connect(desired_acceleration_x.y, enable_desired_acceleration_x.u1) 
    annotation(Line(points = {{139, 255}, {325, 255}, {325, 102}, {511, 102}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_x.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 102}, {511, 102}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_x.u3) 
    annotation(Line(points = {{510, -259}, {510, -84}, {525, -84}, {525, 91}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_x.y, desired_acceleration_x_out) 
    annotation(Line(points = {{539, 102}, {661, 102}}, color = {0, 0, 127}));
  connect(desired_acceleration_y.y, enable_desired_acceleration_y.u1) 
    annotation(Line(points = {{139, 45}, {325, 45}, {325, 64}, {511, 64}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_y.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 64}, {511, 64}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_y.u3) 
    annotation(Line(points = {{510, -259}, {510, -103}, {525, -103}, {525, 53}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_y.y, desired_acceleration_y_out) 
    annotation(Line(points = {{539, 64}, {661, 64}}, color = {0, 0, 127}));
  connect(desired_acceleration_z.y, enable_desired_acceleration_z.u1) 
    annotation(Line(points = {{139, -165}, {325, -165}, {325, 26}, {511, 26}}, color = {0, 0, 127}));
  connect(enable, enable_desired_acceleration_z.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, 26}, {511, 26}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_acceleration_z.u3) 
    annotation(Line(points = {{510, -259}, {510, -122}, {525, -122}, {525, 15}}, color = {0, 0, 127}));
  connect(enable_desired_acceleration_z.y, desired_acceleration_z_out) 
    annotation(Line(points = {{539, 26}, {661, 26}}, color = {0, 0, 127}));
  connect(integral_limit_x.y, enable_integral_position_error_x.u1) 
    annotation(Line(points = {{-131, 135}, {190, 135}, {190, -12}, {511, -12}}, color = {0, 0, 127}));
  connect(enable, enable_integral_position_error_x.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -12}, {511, -12}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_integral_position_error_x.u3) 
    annotation(Line(points = {{510, -259}, {510, -141}, {525, -141}, {525, -23}}, color = {0, 0, 127}));
  connect(enable_integral_position_error_x.y, integral_position_error_x_out) 
    annotation(Line(points = {{539, -12}, {661, -12}}, color = {0, 0, 127}));
  connect(integral_limit_y.y, enable_integral_position_error_y.u1) 
    annotation(Line(points = {{-131, -75}, {190, -75}, {190, -50}, {511, -50}}, color = {0, 0, 127}));
  connect(enable, enable_integral_position_error_y.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -50}, {511, -50}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_integral_position_error_y.u3) 
    annotation(Line(points = {{510, -259}, {510, -160}, {525, -160}, {525, -61}}, color = {0, 0, 127}));
  connect(enable_integral_position_error_y.y, integral_position_error_y_out) 
    annotation(Line(points = {{539, -50}, {661, -50}}, color = {0, 0, 127}));
  connect(integral_limit_z.y, enable_integral_position_error_z.u1) 
    annotation(Line(points = {{-131, -285}, {190, -285}, {190, -88}, {511, -88}}, color = {0, 0, 127}));
  connect(enable, enable_integral_position_error_z.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -88}, {511, -88}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_integral_position_error_z.u3) 
    annotation(Line(points = {{510, -259}, {510, -179}, {525, -179}, {525, -99}}, color = {0, 0, 127}));
  connect(enable_integral_position_error_z.y, integral_position_error_z_out) 
    annotation(Line(points = {{539, -88}, {661, -88}}, color = {0, 0, 127}));
  connect(roll_tilt_limit.y, enable_desired_roll_rad.u1) 
    annotation(Line(points = {{339, 55}, {425, 55}, {425, -126}, {511, -126}}, color = {0, 0, 127}));
  connect(enable, enable_desired_roll_rad.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -126}, {511, -126}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_roll_rad.u3) 
    annotation(Line(points = {{510, -259}, {510, -198}, {525, -198}, {525, -137}}, color = {0, 0, 127}));
  connect(enable_desired_roll_rad.y, desired_roll_rad_out) 
    annotation(Line(points = {{539, -126}, {661, -126}}, color = {0, 0, 127}));
  connect(pitch_tilt_limit.y, enable_desired_pitch_rad.u1) 
    annotation(Line(points = {{325, 109}, {325, -22}, {525, -22}, {525, -153}}, color = {0, 0, 127}));
  connect(enable, enable_desired_pitch_rad.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -164}, {511, -164}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_desired_pitch_rad.u3) 
    annotation(Line(points = {{510, -259}, {510, -217}, {525, -217}, {525, -175}}, color = {0, 0, 127}));
  connect(enable_desired_pitch_rad.y, desired_pitch_rad_out) 
    annotation(Line(points = {{539, -164}, {661, -164}}, color = {0, 0, 127}));
  connect(normalized_thrust_limit.y, enable_normalized_thrust.u1) 
    annotation(Line(points = {{339, -55}, {425, -55}, {425, -202}, {511, -202}}, color = {0, 0, 127}));
  connect(enable, enable_normalized_thrust.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -202}, {511, -202}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_normalized_thrust.u3) 
    annotation(Line(points = {{510, -259}, {510, -236}, {525, -236}, {525, -213}}, color = {0, 0, 127}));
  connect(enable_normalized_thrust.y, normalized_thrust_out) 
    annotation(Line(points = {{539, -202}, {661, -202}}, color = {0, 0, 127}));
  connect(collective_thrust_from_normalized.y, enable_collective_thrust_n.u1) 
    annotation(Line(points = {{410, -66}, {410, -147.5}, {525, -147.5}, {525, -229}}, color = {0, 0, 127}));
  connect(enable, enable_collective_thrust_n.u2) 
    annotation(Line(points = {{-636, -285}, {-62.5, -285}, {-62.5, -240}, {511, -240}}, color = {0, 0, 127}));
  connect(disabled_command.y, enable_collective_thrust_n.u3) 
    annotation(Line(points = {{510, -259}, {510, -255}, {525, -255}, {525, -251}}, color = {0, 0, 127}));
  connect(enable_collective_thrust_n.y, collective_thrust_n_out) 
    annotation(Line(points = {{539, -240}, {661, -240}}, color = {0, 0, 127}));

end LqiBaselineCore;
