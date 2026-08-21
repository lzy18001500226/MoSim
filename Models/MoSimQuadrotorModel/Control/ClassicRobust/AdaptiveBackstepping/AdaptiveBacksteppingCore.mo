within MoSimQuadrotorModel.Control.ClassicRobust.AdaptiveBackstepping;
model AdaptiveBacksteppingCore "P2 fixed-input graphical controller core for adaptive_backstepping"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, estimated_position_x, estimated_position_y, estimated_position_z, estimated_velocity_x, estimated_velocity_y, estimated_velocity_z, adaptive_disturbance_x, adaptive_disturbance_y, adaptive_disturbance_z, storage_function)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_x(k=0.2) 
    annotation (Placement(transformation(origin = {-610, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant position_y(k=-0.1) 
    annotation (Placement(transformation(origin = {-555, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant position_z(k=0.7) 
    annotation (Placement(transformation(origin = {-500, 330}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_x(k=-0.3) 
    annotation (Placement(transformation(origin = {-610, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_y(k=0.2) 
    annotation (Placement(transformation(origin = {-555, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_z(k=-0.1) 
    annotation (Placement(transformation(origin = {-500, 268}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_x(k=1.0) 
    annotation (Placement(transformation(origin = {-610, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_y(k=0.5) 
    annotation (Placement(transformation(origin = {-555, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_z(k=1.2) 
    annotation (Placement(transformation(origin = {-500, 206}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_x(k=0.1) 
    annotation (Placement(transformation(origin = {-610, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_y(k=-0.2) 
    annotation (Placement(transformation(origin = {-555, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_z(k=0.0) 
    annotation (Placement(transformation(origin = {-500, 144}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_x(k=0.05) 
    annotation (Placement(transformation(origin = {-610, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_y(k=-0.04) 
    annotation (Placement(transformation(origin = {-555, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_z(k=0.02) 
    annotation (Placement(transformation(origin = {-500, 82}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant zero(k=0.0) 
    annotation (Placement(transformation(origin = {430, 340}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-")
    "Reference minus measured position" annotation (Placement(transformation(origin = {-390, 275}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, 185}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain k1_position_x(k=1.1) 
    annotation (Placement(transformation(origin = {-305, 275}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_x(inputs="++")
    "Adaptive backstepping sliding coordinate" annotation (Placement(transformation(origin = {-220, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain adaptive_increment_x(k=0.0034999999999999996) 
    annotation (Placement(transformation(origin = {-135, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_state_x(initCond=0.0) 
    annotation (Placement(transformation(origin = {-135, 345}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum adaptive_pre_x(inputs="++") 
    annotation (Placement(transformation(origin = {-50, 320}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation adaptive_limit_x(upLimit=1.0,lowLimit=-1.0) 
    annotation (Placement(transformation(origin = {35, 320}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_velocity_x(k=1.1) 
    annotation (Placement(transformation(origin = {-50, 195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_sliding_x(k=1.8) 
    annotation (Placement(transformation(origin = {35, 195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_nominal_feedback_x(inputs="++") 
    annotation (Placement(transformation(origin = {120, 195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_feedback_x(inputs="+-") 
    annotation (Placement(transformation(origin = {120, 245}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {205, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain k1_position_y(k=1.1) 
    annotation (Placement(transformation(origin = {-305, 45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_y(inputs="++") 
    annotation (Placement(transformation(origin = {-220, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain adaptive_increment_y(k=0.0034999999999999996) 
    annotation (Placement(transformation(origin = {-135, 70}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_state_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-135, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum adaptive_pre_y(inputs="++") 
    annotation (Placement(transformation(origin = {-50, 90}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation adaptive_limit_y(upLimit=1.0,lowLimit=-1.0) 
    annotation (Placement(transformation(origin = {35, 90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_velocity_y(k=1.1) 
    annotation (Placement(transformation(origin = {-50, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_sliding_y(k=1.8) 
    annotation (Placement(transformation(origin = {35, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_nominal_feedback_y(inputs="++") 
    annotation (Placement(transformation(origin = {120, -35}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_feedback_y(inputs="+-") 
    annotation (Placement(transformation(origin = {120, 15}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {205, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -185}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -275}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain k1_position_z(k=1.3) 
    annotation (Placement(transformation(origin = {-305, -185}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum sliding_surface_z(inputs="++") 
    annotation (Placement(transformation(origin = {-220, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain adaptive_increment_z(k=0.0045000000000000005) 
    annotation (Placement(transformation(origin = {-135, -160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay adaptive_state_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-135, -115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum adaptive_pre_z(inputs="++") 
    annotation (Placement(transformation(origin = {-50, -140}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation adaptive_limit_z(upLimit=1.2,lowLimit=-1.2) 
    annotation (Placement(transformation(origin = {35, -140}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_velocity_z(k=1.3) 
    annotation (Placement(transformation(origin = {-50, -265}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain backstepping_sliding_z(k=2.0) 
    annotation (Placement(transformation(origin = {35, -265}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_nominal_feedback_z(inputs="++") 
    annotation (Placement(transformation(origin = {120, -265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum backstepping_feedback_z(inputs="+-") 
    annotation (Placement(transformation(origin = {120, -215}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {205, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity(k=9.80665) 
    annotation (Placement(transformation(origin = {120, -70}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum gravity_compensation(inputs="++") 
    annotation (Placement(transformation(origin = {290, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x 
    annotation (Placement(transformation(origin = {520, 325}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y 
    annotation (Placement(transformation(origin = {520, 277}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z 
    annotation (Placement(transformation(origin = {520, 229}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_x 
    annotation (Placement(transformation(origin = {520, 181}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_y 
    annotation (Placement(transformation(origin = {520, 133}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_position_z 
    annotation (Placement(transformation(origin = {520, 85}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_x 
    annotation (Placement(transformation(origin = {520, 37}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_y 
    annotation (Placement(transformation(origin = {520, -11}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport estimated_velocity_z 
    annotation (Placement(transformation(origin = {520, -59}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_x 
    annotation (Placement(transformation(origin = {520, -107}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_y 
    annotation (Placement(transformation(origin = {520, -155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport adaptive_disturbance_z 
    annotation (Placement(transformation(origin = {520, -203}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport storage_function 
    annotation (Placement(transformation(origin = {520, -251}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport command 
    annotation (Placement(transformation(origin = {520, 400}, extent = {{-14, -11}, {14, 11}})));
  equation
  connect(reference_position_x.y, position_error_x.u1) 
    annotation(Line(points = {{-596, 206}, {-500, 206}, {-500, 275}, {-404, 275}}, color = {0, 0, 127}));
  connect(position_x.y, position_error_x.u2) 
    annotation(Line(points = {{-596, 330}, {-500, 330}, {-500, 275}, {-404, 275}}, color = {0, 0, 127}));
  connect(reference_velocity_x.y, velocity_error_x.u1) 
    annotation(Line(points = {{-596, 144}, {-500, 144}, {-500, 185}, {-404, 185}}, color = {0, 0, 127}));
  connect(velocity_x.y, velocity_error_x.u2) 
    annotation(Line(points = {{-596, 268}, {-500, 268}, {-500, 185}, {-404, 185}}, color = {0, 0, 127}));
  connect(position_error_x.y, k1_position_x.u) 
    annotation(Line(points = {{-376, 275}, {-319, 275}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, sliding_surface_x.u1) 
    annotation(Line(points = {{-376, 185}, {-305, 185}, {-305, 230}, {-234, 230}}, color = {0, 0, 127}));
  connect(k1_position_x.y, sliding_surface_x.u2) 
    annotation(Line(points = {{-291, 275}, {-262.5, 275}, {-262.5, 230}, {-234, 230}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, adaptive_increment_x.u) 
    annotation(Line(points = {{-206, 230}, {-177.5, 230}, {-177.5, 300}, {-149, 300}}, color = {0, 0, 127}));
  connect(adaptive_state_x.y, adaptive_pre_x.u1) 
    annotation(Line(points = {{-121, 345}, {-92.5, 345}, {-92.5, 320}, {-64, 320}}, color = {0, 0, 127}));
  connect(adaptive_increment_x.y, adaptive_pre_x.u2) 
    annotation(Line(points = {{-121, 300}, {-92.5, 300}, {-92.5, 320}, {-64, 320}}, color = {0, 0, 127}));
  connect(adaptive_pre_x.y, adaptive_limit_x.u) 
    annotation(Line(points = {{-36, 320}, {21, 320}}, color = {0, 0, 127}));
  connect(adaptive_limit_x.y, adaptive_state_x.u1) 
    annotation(Line(points = {{21, 320}, {-50, 320}, {-50, 345}, {-121, 345}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, backstepping_velocity_x.u) 
    annotation(Line(points = {{-376, 185}, {-220, 185}, {-220, 195}, {-64, 195}}, color = {0, 0, 127}));
  connect(sliding_surface_x.y, backstepping_sliding_x.u) 
    annotation(Line(points = {{-206, 230}, {-92.5, 230}, {-92.5, 195}, {21, 195}}, color = {0, 0, 127}));
  connect(backstepping_velocity_x.y, backstepping_nominal_feedback_x.u1) 
    annotation(Line(points = {{-36, 195}, {106, 195}}, color = {0, 0, 127}));
  connect(backstepping_sliding_x.y, backstepping_nominal_feedback_x.u2) 
    annotation(Line(points = {{49, 195}, {106, 195}}, color = {0, 0, 127}));
  connect(backstepping_nominal_feedback_x.y, backstepping_feedback_x.u1) 
    annotation(Line(points = {{120, 206}, {120, 234}}, color = {0, 0, 127}));
  connect(adaptive_limit_x.y, backstepping_feedback_x.u2) 
    annotation(Line(points = {{49, 320}, {77.5, 320}, {77.5, 245}, {106, 245}}, color = {0, 0, 127}));
  connect(reference_acceleration_x.y, acceleration_sum_x.u1) 
    annotation(Line(points = {{-596, 82}, {-202.5, 82}, {-202.5, 230}, {191, 230}}, color = {0, 0, 127}));
  connect(backstepping_feedback_x.y, acceleration_sum_x.u2) 
    annotation(Line(points = {{134, 245}, {162.5, 245}, {162.5, 230}, {191, 230}}, color = {0, 0, 127}));
  connect(reference_position_y.y, position_error_y.u1) 
    annotation(Line(points = {{-541, 206}, {-472.5, 206}, {-472.5, 45}, {-404, 45}}, color = {0, 0, 127}));
  connect(position_y.y, position_error_y.u2) 
    annotation(Line(points = {{-555, 319}, {-555, 187.5}, {-390, 187.5}, {-390, 56}}, color = {0, 0, 127}));
  connect(reference_velocity_y.y, velocity_error_y.u1) 
    annotation(Line(points = {{-555, 133}, {-555, 49.5}, {-390, 49.5}, {-390, -34}}, color = {0, 0, 127}));
  connect(velocity_y.y, velocity_error_y.u2) 
    annotation(Line(points = {{-555, 257}, {-555, 111.5}, {-390, 111.5}, {-390, -34}}, color = {0, 0, 127}));
  connect(position_error_y.y, k1_position_y.u) 
    annotation(Line(points = {{-376, 45}, {-319, 45}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, sliding_surface_y.u1) 
    annotation(Line(points = {{-376, -45}, {-305, -45}, {-305, 0}, {-234, 0}}, color = {0, 0, 127}));
  connect(k1_position_y.y, sliding_surface_y.u2) 
    annotation(Line(points = {{-291, 45}, {-262.5, 45}, {-262.5, 0}, {-234, 0}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, adaptive_increment_y.u) 
    annotation(Line(points = {{-206, 0}, {-177.5, 0}, {-177.5, 70}, {-149, 70}}, color = {0, 0, 127}));
  connect(adaptive_state_y.y, adaptive_pre_y.u1) 
    annotation(Line(points = {{-121, 115}, {-92.5, 115}, {-92.5, 90}, {-64, 90}}, color = {0, 0, 127}));
  connect(adaptive_increment_y.y, adaptive_pre_y.u2) 
    annotation(Line(points = {{-121, 70}, {-92.5, 70}, {-92.5, 90}, {-64, 90}}, color = {0, 0, 127}));
  connect(adaptive_pre_y.y, adaptive_limit_y.u) 
    annotation(Line(points = {{-36, 90}, {21, 90}}, color = {0, 0, 127}));
  connect(adaptive_limit_y.y, adaptive_state_y.u1) 
    annotation(Line(points = {{21, 90}, {-50, 90}, {-50, 115}, {-121, 115}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, backstepping_velocity_y.u) 
    annotation(Line(points = {{-376, -45}, {-220, -45}, {-220, -35}, {-64, -35}}, color = {0, 0, 127}));
  connect(sliding_surface_y.y, backstepping_sliding_y.u) 
    annotation(Line(points = {{-206, 0}, {-92.5, 0}, {-92.5, -35}, {21, -35}}, color = {0, 0, 127}));
  connect(backstepping_velocity_y.y, backstepping_nominal_feedback_y.u1) 
    annotation(Line(points = {{-36, -35}, {106, -35}}, color = {0, 0, 127}));
  connect(backstepping_sliding_y.y, backstepping_nominal_feedback_y.u2) 
    annotation(Line(points = {{49, -35}, {106, -35}}, color = {0, 0, 127}));
  connect(backstepping_nominal_feedback_y.y, backstepping_feedback_y.u1) 
    annotation(Line(points = {{120, -24}, {120, 4}}, color = {0, 0, 127}));
  connect(adaptive_limit_y.y, backstepping_feedback_y.u2) 
    annotation(Line(points = {{49, 90}, {77.5, 90}, {77.5, 15}, {106, 15}}, color = {0, 0, 127}));
  connect(reference_acceleration_y.y, acceleration_sum_y.u1) 
    annotation(Line(points = {{-541, 82}, {-175, 82}, {-175, 0}, {191, 0}}, color = {0, 0, 127}));
  connect(backstepping_feedback_y.y, acceleration_sum_y.u2) 
    annotation(Line(points = {{134, 15}, {162.5, 15}, {162.5, 0}, {191, 0}}, color = {0, 0, 127}));
  connect(reference_position_z.y, position_error_z.u1) 
    annotation(Line(points = {{-500, 195}, {-500, 10.5}, {-390, 10.5}, {-390, -174}}, color = {0, 0, 127}));
  connect(position_z.y, position_error_z.u2) 
    annotation(Line(points = {{-500, 319}, {-500, 72.5}, {-390, 72.5}, {-390, -174}}, color = {0, 0, 127}));
  connect(reference_velocity_z.y, velocity_error_z.u1) 
    annotation(Line(points = {{-500, 133}, {-500, -65.5}, {-390, -65.5}, {-390, -264}}, color = {0, 0, 127}));
  connect(velocity_z.y, velocity_error_z.u2) 
    annotation(Line(points = {{-500, 257}, {-500, -3.5}, {-390, -3.5}, {-390, -264}}, color = {0, 0, 127}));
  connect(position_error_z.y, k1_position_z.u) 
    annotation(Line(points = {{-376, -185}, {-319, -185}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, sliding_surface_z.u1) 
    annotation(Line(points = {{-376, -275}, {-305, -275}, {-305, -230}, {-234, -230}}, color = {0, 0, 127}));
  connect(k1_position_z.y, sliding_surface_z.u2) 
    annotation(Line(points = {{-291, -185}, {-262.5, -185}, {-262.5, -230}, {-234, -230}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, adaptive_increment_z.u) 
    annotation(Line(points = {{-206, -230}, {-177.5, -230}, {-177.5, -160}, {-149, -160}}, color = {0, 0, 127}));
  connect(adaptive_state_z.y, adaptive_pre_z.u1) 
    annotation(Line(points = {{-121, -115}, {-92.5, -115}, {-92.5, -140}, {-64, -140}}, color = {0, 0, 127}));
  connect(adaptive_increment_z.y, adaptive_pre_z.u2) 
    annotation(Line(points = {{-121, -160}, {-92.5, -160}, {-92.5, -140}, {-64, -140}}, color = {0, 0, 127}));
  connect(adaptive_pre_z.y, adaptive_limit_z.u) 
    annotation(Line(points = {{-36, -140}, {21, -140}}, color = {0, 0, 127}));
  connect(adaptive_limit_z.y, adaptive_state_z.u1) 
    annotation(Line(points = {{21, -140}, {-50, -140}, {-50, -115}, {-121, -115}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, backstepping_velocity_z.u) 
    annotation(Line(points = {{-376, -275}, {-220, -275}, {-220, -265}, {-64, -265}}, color = {0, 0, 127}));
  connect(sliding_surface_z.y, backstepping_sliding_z.u) 
    annotation(Line(points = {{-206, -230}, {-92.5, -230}, {-92.5, -265}, {21, -265}}, color = {0, 0, 127}));
  connect(backstepping_velocity_z.y, backstepping_nominal_feedback_z.u1) 
    annotation(Line(points = {{-36, -265}, {106, -265}}, color = {0, 0, 127}));
  connect(backstepping_sliding_z.y, backstepping_nominal_feedback_z.u2) 
    annotation(Line(points = {{49, -265}, {106, -265}}, color = {0, 0, 127}));
  connect(backstepping_nominal_feedback_z.y, backstepping_feedback_z.u1) 
    annotation(Line(points = {{120, -254}, {120, -226}}, color = {0, 0, 127}));
  connect(adaptive_limit_z.y, backstepping_feedback_z.u2) 
    annotation(Line(points = {{49, -140}, {77.5, -140}, {77.5, -215}, {106, -215}}, color = {0, 0, 127}));
  connect(reference_acceleration_z.y, acceleration_sum_z.u1) 
    annotation(Line(points = {{-486, 82}, {-147.5, 82}, {-147.5, -230}, {191, -230}}, color = {0, 0, 127}));
  connect(backstepping_feedback_z.y, acceleration_sum_z.u2) 
    annotation(Line(points = {{134, -215}, {162.5, -215}, {162.5, -230}, {191, -230}}, color = {0, 0, 127}));
  connect(acceleration_sum_z.y, gravity_compensation.u1) 
    annotation(Line(points = {{219, -230}, {276, -230}}, color = {0, 0, 127}));
  connect(gravity.y, gravity_compensation.u2) 
    annotation(Line(points = {{134, -70}, {205, -70}, {205, -230}, {276, -230}}, color = {0, 0, 127}));
  connect(acceleration_sum_x.y, desired_acceleration_x) 
    annotation(Line(points = {{219, 230}, {362.5, 230}, {362.5, 325}, {506, 325}}, color = {0, 0, 127}));
  connect(acceleration_sum_y.y, desired_acceleration_y) 
    annotation(Line(points = {{219, 0}, {362.5, 0}, {362.5, 277}, {506, 277}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z) 
    annotation(Line(points = {{290, -219}, {290, -0.5}, {520, -0.5}, {520, 218}}, color = {0, 0, 127}));
  connect(zero.y, estimated_position_x) 
    annotation(Line(points = {{430, 329}, {430, 260.5}, {520, 260.5}, {520, 192}}, color = {0, 0, 127}));
  connect(zero.y, estimated_position_y) 
    annotation(Line(points = {{430, 329}, {430, 236.5}, {520, 236.5}, {520, 144}}, color = {0, 0, 127}));
  connect(zero.y, estimated_position_z) 
    annotation(Line(points = {{430, 329}, {430, 212.5}, {520, 212.5}, {520, 96}}, color = {0, 0, 127}));
  connect(zero.y, estimated_velocity_x) 
    annotation(Line(points = {{430, 329}, {430, 188.5}, {520, 188.5}, {520, 48}}, color = {0, 0, 127}));
  connect(zero.y, estimated_velocity_y) 
    annotation(Line(points = {{430, 329}, {430, 164.5}, {520, 164.5}, {520, 0}}, color = {0, 0, 127}));
  connect(zero.y, estimated_velocity_z) 
    annotation(Line(points = {{430, 329}, {430, 140.5}, {520, 140.5}, {520, -48}}, color = {0, 0, 127}));
  connect(adaptive_limit_x.y, adaptive_disturbance_x) 
    annotation(Line(points = {{49, 320}, {277.5, 320}, {277.5, -107}, {506, -107}}, color = {0, 0, 127}));
  connect(adaptive_limit_y.y, adaptive_disturbance_y) 
    annotation(Line(points = {{49, 90}, {277.5, 90}, {277.5, -155}, {506, -155}}, color = {0, 0, 127}));
  connect(adaptive_limit_z.y, adaptive_disturbance_z) 
    annotation(Line(points = {{49, -140}, {277.5, -140}, {277.5, -203}, {506, -203}}, color = {0, 0, 127}));
  connect(zero.y, storage_function) 
    annotation(Line(points = {{430, 329}, {430, 44.5}, {520, 44.5}, {520, -240}}, color = {0, 0, 127}));
  connect(acceleration_sum_x.y, command) 
    annotation(Line(points = {{219, 230}, {362.5, 230}, {362.5, 400}, {506, 400}}, color = {0, 0, 127}));
  end AdaptiveBacksteppingCore;