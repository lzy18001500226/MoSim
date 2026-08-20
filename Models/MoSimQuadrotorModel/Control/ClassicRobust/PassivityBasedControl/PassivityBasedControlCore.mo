within MoSimQuadrotorModel.Control.ClassicRobust.PassivityBasedControl;
model PassivityBasedControlCore "P2 fixed-input graphical controller core for passivity_based_control"
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
    "Reference minus measured position" annotation (Placement(transformation(origin = {-390, 265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, 195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_x(k=1.6) 
    annotation (Placement(transformation(origin = {-305, 265}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_x(k=1.8) 
    annotation (Placement(transformation(origin = {-305, 195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {-220, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {-135, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product velocity_error_square_x(inputs="**") 
    annotation (Placement(transformation(origin = {15, 175}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product position_error_square_x(inputs="**") 
    annotation (Placement(transformation(origin = {15, 285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain kinetic_storage_x(k=0.335) 
    annotation (Placement(transformation(origin = {95, 175}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain potential_storage_x(k=0.8) 
    annotation (Placement(transformation(origin = {95, 285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum storage_axis_x(inputs="++") 
    annotation (Placement(transformation(origin = {175, 230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, 35}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -35}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_y(k=1.6) 
    annotation (Placement(transformation(origin = {-305, 35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_y(k=1.8) 
    annotation (Placement(transformation(origin = {-305, -35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {-220, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {-135, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product velocity_error_square_y(inputs="**") 
    annotation (Placement(transformation(origin = {15, -55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product position_error_square_y(inputs="**") 
    annotation (Placement(transformation(origin = {15, 55}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain kinetic_storage_y(k=0.335) 
    annotation (Placement(transformation(origin = {95, -55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain potential_storage_y(k=0.8) 
    annotation (Placement(transformation(origin = {95, 55}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum storage_axis_y(inputs="++") 
    annotation (Placement(transformation(origin = {175, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -195}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-390, -265}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain position_feedback_z(k=2.2) 
    annotation (Placement(transformation(origin = {-305, -195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain velocity_feedback_z(k=2.0) 
    annotation (Placement(transformation(origin = {-305, -265}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {-220, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {-135, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity(k=9.80665) 
    annotation (Placement(transformation(origin = {-220, -145}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum gravity_compensation(inputs="++") 
    annotation (Placement(transformation(origin = {-50, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product velocity_error_square_z(inputs="**") 
    annotation (Placement(transformation(origin = {15, -285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product position_error_square_z(inputs="**") 
    annotation (Placement(transformation(origin = {15, -175}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain kinetic_storage_z(k=0.335) 
    annotation (Placement(transformation(origin = {95, -285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain potential_storage_z(k=1.1) 
    annotation (Placement(transformation(origin = {95, -175}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum storage_axis_z(inputs="++") 
    annotation (Placement(transformation(origin = {175, -230}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum storage_xy(inputs="++") 
    annotation (Placement(transformation(origin = {270, 120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum storage_total(inputs="++")
    "Passivity storage function" annotation (Placement(transformation(origin = {350, 75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
equation
  connect(reference_position_x.y, position_error_x.u1) 
    annotation(Line(points = {{-596, 206}, {-500, 206}, {-500, 265}, {-404, 265}}, color = {0, 0, 127}));
  connect(position_x.y, position_error_x.u2) 
    annotation(Line(points = {{-596, 330}, {-500, 330}, {-500, 265}, {-404, 265}}, color = {0, 0, 127}));
  connect(reference_velocity_x.y, velocity_error_x.u1) 
    annotation(Line(points = {{-596, 144}, {-500, 144}, {-500, 195}, {-404, 195}}, color = {0, 0, 127}));
  connect(velocity_x.y, velocity_error_x.u2) 
    annotation(Line(points = {{-596, 268}, {-500, 268}, {-500, 195}, {-404, 195}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_feedback_x.u) 
    annotation(Line(points = {{-376, 265}, {-319, 265}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, velocity_feedback_x.u) 
    annotation(Line(points = {{-376, 195}, {-319, 195}}, color = {0, 0, 127}));
  connect(position_feedback_x.y, feedback_sum_x.u1) 
    annotation(Line(points = {{-291, 265}, {-262.5, 265}, {-262.5, 230}, {-234, 230}}, color = {0, 0, 127}));
  connect(velocity_feedback_x.y, feedback_sum_x.u2) 
    annotation(Line(points = {{-291, 195}, {-262.5, 195}, {-262.5, 230}, {-234, 230}}, color = {0, 0, 127}));
  connect(reference_acceleration_x.y, acceleration_sum_x.u1) 
    annotation(Line(points = {{-596, 82}, {-372.5, 82}, {-372.5, 230}, {-149, 230}}, color = {0, 0, 127}));
  connect(feedback_sum_x.y, acceleration_sum_x.u2) 
    annotation(Line(points = {{-206, 230}, {-149, 230}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, velocity_error_square_x.u1) 
    annotation(Line(points = {{-376, 195}, {-187.5, 195}, {-187.5, 175}, {1, 175}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, velocity_error_square_x.u2) 
    annotation(Line(points = {{-376, 195}, {-187.5, 195}, {-187.5, 175}, {1, 175}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_error_square_x.u1) 
    annotation(Line(points = {{-376, 265}, {-187.5, 265}, {-187.5, 285}, {1, 285}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_error_square_x.u2) 
    annotation(Line(points = {{-376, 265}, {-187.5, 265}, {-187.5, 285}, {1, 285}}, color = {0, 0, 127}));
  connect(velocity_error_square_x.y, kinetic_storage_x.u) 
    annotation(Line(points = {{29, 175}, {81, 175}}, color = {0, 0, 127}));
  connect(position_error_square_x.y, potential_storage_x.u) 
    annotation(Line(points = {{29, 285}, {81, 285}}, color = {0, 0, 127}));
  connect(kinetic_storage_x.y, storage_axis_x.u1) 
    annotation(Line(points = {{109, 175}, {135, 175}, {135, 230}, {161, 230}}, color = {0, 0, 127}));
  connect(potential_storage_x.y, storage_axis_x.u2) 
    annotation(Line(points = {{109, 285}, {135, 285}, {135, 230}, {161, 230}}, color = {0, 0, 127}));
  connect(reference_position_y.y, position_error_y.u1) 
    annotation(Line(points = {{-555, 195}, {-555, 120.5}, {-390, 120.5}, {-390, 46}}, color = {0, 0, 127}));
  connect(position_y.y, position_error_y.u2) 
    annotation(Line(points = {{-555, 319}, {-555, 182.5}, {-390, 182.5}, {-390, 46}}, color = {0, 0, 127}));
  connect(reference_velocity_y.y, velocity_error_y.u1) 
    annotation(Line(points = {{-555, 133}, {-555, 54.5}, {-390, 54.5}, {-390, -24}}, color = {0, 0, 127}));
  connect(velocity_y.y, velocity_error_y.u2) 
    annotation(Line(points = {{-555, 257}, {-555, 116.5}, {-390, 116.5}, {-390, -24}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_feedback_y.u) 
    annotation(Line(points = {{-376, 35}, {-319, 35}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, velocity_feedback_y.u) 
    annotation(Line(points = {{-376, -35}, {-319, -35}}, color = {0, 0, 127}));
  connect(position_feedback_y.y, feedback_sum_y.u1) 
    annotation(Line(points = {{-291, 35}, {-262.5, 35}, {-262.5, 0}, {-234, 0}}, color = {0, 0, 127}));
  connect(velocity_feedback_y.y, feedback_sum_y.u2) 
    annotation(Line(points = {{-291, -35}, {-262.5, -35}, {-262.5, 0}, {-234, 0}}, color = {0, 0, 127}));
  connect(reference_acceleration_y.y, acceleration_sum_y.u1) 
    annotation(Line(points = {{-541, 82}, {-345, 82}, {-345, 0}, {-149, 0}}, color = {0, 0, 127}));
  connect(feedback_sum_y.y, acceleration_sum_y.u2) 
    annotation(Line(points = {{-206, 0}, {-149, 0}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, velocity_error_square_y.u1) 
    annotation(Line(points = {{-376, -35}, {-187.5, -35}, {-187.5, -55}, {1, -55}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, velocity_error_square_y.u2) 
    annotation(Line(points = {{-376, -35}, {-187.5, -35}, {-187.5, -55}, {1, -55}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_error_square_y.u1) 
    annotation(Line(points = {{-376, 35}, {-187.5, 35}, {-187.5, 55}, {1, 55}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_error_square_y.u2) 
    annotation(Line(points = {{-376, 35}, {-187.5, 35}, {-187.5, 55}, {1, 55}}, color = {0, 0, 127}));
  connect(velocity_error_square_y.y, kinetic_storage_y.u) 
    annotation(Line(points = {{29, -55}, {81, -55}}, color = {0, 0, 127}));
  connect(position_error_square_y.y, potential_storage_y.u) 
    annotation(Line(points = {{29, 55}, {81, 55}}, color = {0, 0, 127}));
  connect(kinetic_storage_y.y, storage_axis_y.u1) 
    annotation(Line(points = {{109, -55}, {135, -55}, {135, 0}, {161, 0}}, color = {0, 0, 127}));
  connect(potential_storage_y.y, storage_axis_y.u2) 
    annotation(Line(points = {{109, 55}, {135, 55}, {135, 0}, {161, 0}}, color = {0, 0, 127}));
  connect(reference_position_z.y, position_error_z.u1) 
    annotation(Line(points = {{-500, 195}, {-500, 5.5}, {-390, 5.5}, {-390, -184}}, color = {0, 0, 127}));
  connect(position_z.y, position_error_z.u2) 
    annotation(Line(points = {{-500, 319}, {-500, 67.5}, {-390, 67.5}, {-390, -184}}, color = {0, 0, 127}));
  connect(reference_velocity_z.y, velocity_error_z.u1) 
    annotation(Line(points = {{-500, 133}, {-500, -60.5}, {-390, -60.5}, {-390, -254}}, color = {0, 0, 127}));
  connect(velocity_z.y, velocity_error_z.u2) 
    annotation(Line(points = {{-500, 257}, {-500, 1.5}, {-390, 1.5}, {-390, -254}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_feedback_z.u) 
    annotation(Line(points = {{-376, -195}, {-319, -195}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, velocity_feedback_z.u) 
    annotation(Line(points = {{-376, -265}, {-319, -265}}, color = {0, 0, 127}));
  connect(position_feedback_z.y, feedback_sum_z.u1) 
    annotation(Line(points = {{-291, -195}, {-262.5, -195}, {-262.5, -230}, {-234, -230}}, color = {0, 0, 127}));
  connect(velocity_feedback_z.y, feedback_sum_z.u2) 
    annotation(Line(points = {{-291, -265}, {-262.5, -265}, {-262.5, -230}, {-234, -230}}, color = {0, 0, 127}));
  connect(reference_acceleration_z.y, acceleration_sum_z.u1) 
    annotation(Line(points = {{-486, 82}, {-317.5, 82}, {-317.5, -230}, {-149, -230}}, color = {0, 0, 127}));
  connect(feedback_sum_z.y, acceleration_sum_z.u2) 
    annotation(Line(points = {{-206, -230}, {-149, -230}}, color = {0, 0, 127}));
  connect(acceleration_sum_z.y, gravity_compensation.u1) 
    annotation(Line(points = {{-121, -230}, {-64, -230}}, color = {0, 0, 127}));
  connect(gravity.y, gravity_compensation.u2) 
    annotation(Line(points = {{-206, -145}, {-135, -145}, {-135, -230}, {-64, -230}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, velocity_error_square_z.u1) 
    annotation(Line(points = {{-376, -265}, {-187.5, -265}, {-187.5, -285}, {1, -285}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, velocity_error_square_z.u2) 
    annotation(Line(points = {{-376, -265}, {-187.5, -265}, {-187.5, -285}, {1, -285}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_error_square_z.u1) 
    annotation(Line(points = {{-376, -195}, {-187.5, -195}, {-187.5, -175}, {1, -175}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_error_square_z.u2) 
    annotation(Line(points = {{-376, -195}, {-187.5, -195}, {-187.5, -175}, {1, -175}}, color = {0, 0, 127}));
  connect(velocity_error_square_z.y, kinetic_storage_z.u) 
    annotation(Line(points = {{29, -285}, {81, -285}}, color = {0, 0, 127}));
  connect(position_error_square_z.y, potential_storage_z.u) 
    annotation(Line(points = {{29, -175}, {81, -175}}, color = {0, 0, 127}));
  connect(kinetic_storage_z.y, storage_axis_z.u1) 
    annotation(Line(points = {{109, -285}, {135, -285}, {135, -230}, {161, -230}}, color = {0, 0, 127}));
  connect(potential_storage_z.y, storage_axis_z.u2) 
    annotation(Line(points = {{109, -175}, {135, -175}, {135, -230}, {161, -230}}, color = {0, 0, 127}));
  connect(storage_axis_x.y, storage_xy.u1) 
    annotation(Line(points = {{175, 219}, {175, 175}, {270, 175}, {270, 131}}, color = {0, 0, 127}));
  connect(storage_axis_y.y, storage_xy.u2) 
    annotation(Line(points = {{175, 11}, {175, 60}, {270, 60}, {270, 109}}, color = {0, 0, 127}));
  connect(storage_xy.y, storage_total.u1) 
    annotation(Line(points = {{284, 120}, {310, 120}, {310, 75}, {336, 75}}, color = {0, 0, 127}));
  connect(storage_axis_z.y, storage_total.u2) 
    annotation(Line(points = {{175, -219}, {175, -77.5}, {350, -77.5}, {350, 64}}, color = {0, 0, 127}));
  connect(acceleration_sum_x.y, desired_acceleration_x) 
    annotation(Line(points = {{-121, 230}, {192.5, 230}, {192.5, 325}, {506, 325}}, color = {0, 0, 127}));
  connect(acceleration_sum_y.y, desired_acceleration_y) 
    annotation(Line(points = {{-121, 0}, {192.5, 0}, {192.5, 277}, {506, 277}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z) 
    annotation(Line(points = {{-36, -230}, {235, -230}, {235, 229}, {506, 229}}, color = {0, 0, 127}));
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
  connect(zero.y, adaptive_disturbance_x) 
    annotation(Line(points = {{430, 329}, {430, 116.5}, {520, 116.5}, {520, -96}}, color = {0, 0, 127}));
  connect(zero.y, adaptive_disturbance_y) 
    annotation(Line(points = {{430, 329}, {430, 92.5}, {520, 92.5}, {520, -144}}, color = {0, 0, 127}));
  connect(zero.y, adaptive_disturbance_z) 
    annotation(Line(points = {{430, 329}, {430, 68.5}, {520, 68.5}, {520, -192}}, color = {0, 0, 127}));
  connect(storage_total.y, storage_function) 
    annotation(Line(points = {{350, 64}, {350, -88}, {520, -88}, {520, -240}}, color = {0, 0, 127}));
  end PassivityBasedControlCore;