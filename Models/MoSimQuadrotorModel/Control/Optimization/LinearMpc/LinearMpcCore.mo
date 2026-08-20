within MoSimQuadrotorModel.Control.Optimization.LinearMpc;
model LinearMpcCore "P4 native graphical fixed-budget MPC controller core: linear_mpc"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, unconstrained_acceleration_x, unconstrained_acceleration_y, unconstrained_acceleration_z, auxiliary_x, auxiliary_y, auxiliary_z, solver_cost, solver_iterations)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_x(k=0.2) 
    annotation (Placement(transformation(origin = {-950, 520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_y(k=-0.1) 
    annotation (Placement(transformation(origin = {-895, 520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_z(k=0.7) 
    annotation (Placement(transformation(origin = {-840, 520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_x(k=-0.3) 
    annotation (Placement(transformation(origin = {-950, 465}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_y(k=0.2) 
    annotation (Placement(transformation(origin = {-895, 465}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_z(k=-0.1) 
    annotation (Placement(transformation(origin = {-840, 465}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_x(k=1.0) 
    annotation (Placement(transformation(origin = {-950, 410}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_y(k=0.5) 
    annotation (Placement(transformation(origin = {-895, 410}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_z(k=1.2) 
    annotation (Placement(transformation(origin = {-840, 410}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_x(k=0.1) 
    annotation (Placement(transformation(origin = {-950, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_y(k=-0.2) 
    annotation (Placement(transformation(origin = {-895, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_z(k=0.0) 
    annotation (Placement(transformation(origin = {-840, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_x(k=0.05) 
    annotation (Placement(transformation(origin = {-950, 300}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_y(k=-0.04) 
    annotation (Placement(transformation(origin = {-895, 300}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_z(k=0.02) 
    annotation (Placement(transformation(origin = {-840, 300}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_acceleration_x(initCond=0.0)
    "P4 distinguishing native graphical path for linear_mpc" annotation (Placement(transformation(origin = {-860, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, 373}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, 263}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_position_term_x(k=3.9177277179236047) 
    annotation (Placement(transformation(origin = {-690, 395}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_velocity_term_x(k=2.507345739471107) 
    annotation (Placement(transformation(origin = {-690, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_previous_term_x(k=0.2507345739471107) 
    annotation (Placement(transformation(origin = {-690, 285}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_x_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-566, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_x(inputs="++") 
    annotation (Placement(transformation(origin = {-532, 296}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant auxiliary_zero_x(k=0.0) 
    annotation (Placement(transformation(origin = {110, 510}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum unconstrained_command_x(inputs="++") 
    annotation (Placement(transformation(origin = {1019, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation absolute_acceleration_limit_x(lowLimit=-4.0,upLimit=4.0) 
    annotation (Placement(transformation(origin = {1070, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain previous_lower_bound_x(k=1.0) 
    annotation (Placement(transformation(origin = {1070, 425}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant increment_limit_x(k=1.2) 
    annotation (Placement(transformation(origin = {1070, 470}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_lower_x(inputs="+-") 
    annotation (Placement(transformation(origin = {1189, 423}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_upper_x(inputs="++") 
    annotation (Placement(transformation(origin = {1189, 383}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_lower_clip_x(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max) 
    annotation (Placement(transformation(origin = {1240, 375}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_upper_clip_x(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min) 
    annotation (Placement(transformation(origin = {1325, 340}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, 240}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, 195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_x_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, 208}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_x_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, 186}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, 140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_x_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, 118}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_x_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 230}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_x_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 175}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_x_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_position_cost(k=1.0) 
    annotation (Placement(transformation(origin = {1240, 230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_velocity_cost(k=0.08) 
    annotation (Placement(transformation(origin = {1240, 175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_x_control_cost(k=0.002) 
    annotation (Placement(transformation(origin = {1240, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_x_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, 153}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_x_stage_cost(inputs="++") 
    annotation (Placement(transformation(origin = {1393, 131}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_acceleration_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {-860, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, -57}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, -167}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_position_term_y(k=3.9177277179236047) 
    annotation (Placement(transformation(origin = {-690, -35}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_velocity_term_y(k=2.507345739471107) 
    annotation (Placement(transformation(origin = {-690, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_previous_term_y(k=0.2507345739471107) 
    annotation (Placement(transformation(origin = {-690, -145}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_y_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-566, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_y(inputs="++") 
    annotation (Placement(transformation(origin = {-532, -134}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant auxiliary_zero_y(k=0.0) 
    annotation (Placement(transformation(origin = {110, 80}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum unconstrained_command_y(inputs="++") 
    annotation (Placement(transformation(origin = {1019, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation absolute_acceleration_limit_y(lowLimit=-4.0,upLimit=4.0) 
    annotation (Placement(transformation(origin = {1070, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain previous_lower_bound_y(k=1.0) 
    annotation (Placement(transformation(origin = {1070, -5}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant increment_limit_y(k=1.2) 
    annotation (Placement(transformation(origin = {1070, 40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_lower_y(inputs="+-") 
    annotation (Placement(transformation(origin = {1189, -7}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_upper_y(inputs="++") 
    annotation (Placement(transformation(origin = {1189, -47}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_lower_clip_y(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max) 
    annotation (Placement(transformation(origin = {1240, -55}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_upper_clip_y(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min) 
    annotation (Placement(transformation(origin = {1325, -90}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, -235}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_y_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, -222}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_y_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, -244}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, -290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_y_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, -312}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_y_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -200}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_y_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -255}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_y_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_position_cost(k=1.0) 
    annotation (Placement(transformation(origin = {1240, -200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_velocity_cost(k=0.08) 
    annotation (Placement(transformation(origin = {1240, -255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_y_control_cost(k=0.002) 
    annotation (Placement(transformation(origin = {1240, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_y_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, -277}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_y_stage_cost(inputs="++") 
    annotation (Placement(transformation(origin = {1393, -299}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay previous_acceleration_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {-860, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, -487}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-746, -597}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_position_term_z(k=3.5982008995502244) 
    annotation (Placement(transformation(origin = {-690, -465}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_velocity_term_z(k=2.39880059970015) 
    annotation (Placement(transformation(origin = {-690, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_previous_term_z(k=0.28785607196401797) 
    annotation (Placement(transformation(origin = {-690, -575}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_z_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-566, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_solution_z(inputs="++") 
    annotation (Placement(transformation(origin = {-532, -564}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant auxiliary_zero_z(k=0.0) 
    annotation (Placement(transformation(origin = {110, -350}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum unconstrained_command_z(inputs="++") 
    annotation (Placement(transformation(origin = {1019, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation absolute_acceleration_limit_z(lowLimit=-2.5,upLimit=2.5) 
    annotation (Placement(transformation(origin = {1070, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain previous_lower_bound_z(k=1.0) 
    annotation (Placement(transformation(origin = {1070, -435}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant increment_limit_z(k=0.8) 
    annotation (Placement(transformation(origin = {1070, -390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_lower_z(inputs="+-") 
    annotation (Placement(transformation(origin = {1189, -437}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum increment_upper_z(inputs="++") 
    annotation (Placement(transformation(origin = {1189, -477}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_lower_clip_z(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max) 
    annotation (Placement(transformation(origin = {1240, -485}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin increment_upper_clip_z(portNumber=2,maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min) 
    annotation (Placement(transformation(origin = {1325, -520}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity(k=9.80665) 
    annotation (Placement(transformation(origin = {1325, -425}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum gravity_compensation(inputs="++") 
    annotation (Placement(transformation(origin = {1444, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, -620}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, -665}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_z_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, -652}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_z_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, -674}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, -720}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_z_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, -742}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_z_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -630}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_z_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -685}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_linear_mpc_z_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -740}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_position_cost(k=1.2) 
    annotation (Placement(transformation(origin = {1240, -630}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_velocity_cost(k=0.1) 
    annotation (Placement(transformation(origin = {1240, -685}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_linear_mpc_z_control_cost(k=0.003) 
    annotation (Placement(transformation(origin = {1240, -740}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_z_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, -707}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_linear_mpc_z_stage_cost(inputs="++") 
    annotation (Placement(transformation(origin = {1393, -729}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1544, -952}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum(inputs="++") 
    annotation (Placement(transformation(origin = {1578, -974}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant fixed_solver_budget(k=0.0) 
    annotation (Placement(transformation(origin = {1510, -1000}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x 
    annotation (Placement(transformation(origin = {1610, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y 
    annotation (Placement(transformation(origin = {1610, 255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z 
    annotation (Placement(transformation(origin = {1610, 150}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_x 
    annotation (Placement(transformation(origin = {1610, 45}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_y 
    annotation (Placement(transformation(origin = {1610, -60}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport unconstrained_acceleration_z 
    annotation (Placement(transformation(origin = {1610, -165}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_x 
    annotation (Placement(transformation(origin = {1610, -270}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_y 
    annotation (Placement(transformation(origin = {1610, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_z 
    annotation (Placement(transformation(origin = {1610, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport solver_cost 
    annotation (Placement(transformation(origin = {1610, -585}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport solver_iterations 
    annotation (Placement(transformation(origin = {1610, -690}, extent = {{-13, -10}, {13, 10}})));
  equation
  connect(reference_position_x.y, position_error_x.u1) 
    annotation(Line(points = {{-937, 410}, {-848, 410}, {-848, 373}, {-759, 373}}, color = {0, 0, 127}));
  connect(position_x.y, position_error_x.u2) 
    annotation(Line(points = {{-937, 520}, {-848, 520}, {-848, 373}, {-759, 373}}, color = {0, 0, 127}));
  connect(reference_velocity_x.y, velocity_error_x.u1) 
    annotation(Line(points = {{-937, 355}, {-848, 355}, {-848, 263}, {-759, 263}}, color = {0, 0, 127}));
  connect(velocity_x.y, velocity_error_x.u2) 
    annotation(Line(points = {{-937, 465}, {-848, 465}, {-848, 263}, {-759, 263}}, color = {0, 0, 127}));
  connect(position_error_x.y, linear_position_term_x.u) 
    annotation(Line(points = {{-733, 373}, {-718, 373}, {-718, 395}, {-703, 395}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, linear_velocity_term_x.u) 
    annotation(Line(points = {{-746, 273}, {-746, 301.5}, {-690, 301.5}, {-690, 330}}, color = {0, 0, 127}));
  connect(previous_acceleration_x.y, linear_previous_term_x.u) 
    annotation(Line(points = {{-847, 340}, {-775, 340}, {-775, 285}, {-703, 285}}, color = {0, 0, 127}));
  connect(linear_position_term_x.y, linear_solution_x_stage1.u1) 
    annotation(Line(points = {{-677, 395}, {-628, 395}, {-628, 318}, {-579, 318}}, color = {0, 0, 127}));
  connect(linear_velocity_term_x.y, linear_solution_x_stage1.u2) 
    annotation(Line(points = {{-677, 340}, {-628, 340}, {-628, 318}, {-579, 318}}, color = {0, 0, 127}));
  connect(linear_solution_x_stage1.y, linear_solution_x.u1) 
    annotation(Line(points = {{-553, 318}, {-549, 318}, {-549, 296}, {-545, 296}}, color = {0, 0, 127}));
  connect(linear_previous_term_x.y, linear_solution_x.u2) 
    annotation(Line(points = {{-677, 285}, {-611, 285}, {-611, 296}, {-545, 296}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, unconstrained_command_x.u1) 
    annotation(Line(points = {{-519, 296}, {243.5, 296}, {243.5, 318}, {1006, 318}}, color = {0, 0, 127}));
  connect(reference_acceleration_x.y, unconstrained_command_x.u2) 
    annotation(Line(points = {{-937, 300}, {34.5, 300}, {34.5, 318}, {1006, 318}}, color = {0, 0, 127}));
  connect(unconstrained_command_x.y, absolute_acceleration_limit_x.u) 
    annotation(Line(points = {{1032, 318}, {1044.5, 318}, {1044.5, 340}, {1057, 340}}, color = {0, 0, 127}));
  connect(previous_acceleration_x.y, previous_lower_bound_x.u) 
    annotation(Line(points = {{-847, 340}, {105, 340}, {105, 425}, {1057, 425}}, color = {0, 0, 127}));
  connect(previous_lower_bound_x.y, increment_lower_x.u1) 
    annotation(Line(points = {{1083, 425}, {1129.5, 425}, {1129.5, 423}, {1176, 423}}, color = {0, 0, 127}));
  connect(increment_limit_x.y, increment_lower_x.u2) 
    annotation(Line(points = {{1083, 470}, {1129.5, 470}, {1129.5, 423}, {1176, 423}}, color = {0, 0, 127}));
  connect(previous_lower_bound_x.y, increment_upper_x.u1) 
    annotation(Line(points = {{1083, 425}, {1129.5, 425}, {1129.5, 383}, {1176, 383}}, color = {0, 0, 127}));
  connect(increment_limit_x.y, increment_upper_x.u2) 
    annotation(Line(points = {{1083, 470}, {1129.5, 470}, {1129.5, 383}, {1176, 383}}, color = {0, 0, 127}));
  connect(absolute_acceleration_limit_x.y, increment_lower_clip_x.u1) 
    annotation(Line(points = {{1083, 340}, {1155, 340}, {1155, 375}, {1227, 375}}, color = {0, 0, 127}));
  connect(increment_lower_x.y, increment_lower_clip_x.u2) 
    annotation(Line(points = {{1202, 423}, {1214.5, 423}, {1214.5, 375}, {1227, 375}}, color = {0, 0, 127}));
  connect(increment_lower_clip_x.y, increment_upper_clip_x.u1) 
    annotation(Line(points = {{1253, 375}, {1282.5, 375}, {1282.5, 340}, {1312, 340}}, color = {0, 0, 127}));
  connect(increment_upper_x.y, increment_upper_clip_x.u2) 
    annotation(Line(points = {{1202, 383}, {1257, 383}, {1257, 340}, {1312, 340}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, previous_acceleration_x.u1) 
    annotation(Line(points = {{1312, 340}, {-847, 340}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, final_linear_mpc_x_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {119.5, 263}, {119.5, 240}, {972, 240}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_linear_mpc_x_half_h2_acc.u) 
    annotation(Line(points = {{1312, 340}, {1155, 340}, {1155, 195}, {998, 195}}, color = {0, 0, 127}));
  connect(position_error_x.y, final_linear_mpc_x_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {179, 373}, {179, 208}, {1091, 208}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_h_ev.y, final_linear_mpc_x_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, 240}, {1044.5, 240}, {1044.5, 208}, {1091, 208}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_predicted_position_error_stage1.y, final_linear_mpc_x_predicted_position_error.u1) 
    annotation(Line(points = {{1117, 208}, {1121, 208}, {1121, 186}, {1125, 186}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_half_h2_acc.y, final_linear_mpc_x_predicted_position_error.u2) 
    annotation(Line(points = {{998, 195}, {1061.5, 195}, {1061.5, 186}, {1125, 186}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_linear_mpc_x_h_acc.u) 
    annotation(Line(points = {{1312, 340}, {1155, 340}, {1155, 140}, {998, 140}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, final_linear_mpc_x_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {179, 263}, {179, 118}, {1091, 118}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_h_acc.y, final_linear_mpc_x_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, 140}, {1044.5, 140}, {1044.5, 118}, {1091, 118}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_predicted_position_error.y, final_linear_mpc_x_position_error_squared.u1) 
    annotation(Line(points = {{1138, 196}, {1138, 208}, {1155, 208}, {1155, 220}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_predicted_position_error.y, final_linear_mpc_x_position_error_squared.u2) 
    annotation(Line(points = {{1138, 196}, {1138, 208}, {1155, 208}, {1155, 220}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_predicted_velocity_error.y, final_linear_mpc_x_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, 128}, {1104, 146.5}, {1155, 146.5}, {1155, 165}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_predicted_velocity_error.y, final_linear_mpc_x_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, 128}, {1104, 146.5}, {1155, 146.5}, {1155, 165}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_linear_mpc_x_acceleration_squared.u1) 
    annotation(Line(points = {{1325, 330}, {1325, 230}, {1155, 230}, {1155, 130}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_linear_mpc_x_acceleration_squared.u2) 
    annotation(Line(points = {{1325, 330}, {1325, 230}, {1155, 230}, {1155, 130}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_position_error_squared.y, final_linear_mpc_x_position_cost.u) 
    annotation(Line(points = {{1168, 230}, {1227, 230}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_velocity_error_squared.y, final_linear_mpc_x_velocity_cost.u) 
    annotation(Line(points = {{1168, 175}, {1227, 175}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_acceleration_squared.y, final_linear_mpc_x_control_cost.u) 
    annotation(Line(points = {{1168, 120}, {1227, 120}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_position_cost.y, final_linear_mpc_x_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, 230}, {1299.5, 230}, {1299.5, 153}, {1346, 153}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_velocity_cost.y, final_linear_mpc_x_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, 175}, {1299.5, 175}, {1299.5, 153}, {1346, 153}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_stage_cost_stage1.y, final_linear_mpc_x_stage_cost.u1) 
    annotation(Line(points = {{1372, 153}, {1376, 153}, {1376, 131}, {1380, 131}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_control_cost.y, final_linear_mpc_x_stage_cost.u2) 
    annotation(Line(points = {{1253, 120}, {1316.5, 120}, {1316.5, 131}, {1380, 131}}, color = {0, 0, 127}));
  connect(reference_position_y.y, position_error_y.u1) 
    annotation(Line(points = {{-895, 400}, {-895, 176.5}, {-746, 176.5}, {-746, -47}}, color = {0, 0, 127}));
  connect(position_y.y, position_error_y.u2) 
    annotation(Line(points = {{-895, 510}, {-895, 231.5}, {-746, 231.5}, {-746, -47}}, color = {0, 0, 127}));
  connect(reference_velocity_y.y, velocity_error_y.u1) 
    annotation(Line(points = {{-895, 345}, {-895, 94}, {-746, 94}, {-746, -157}}, color = {0, 0, 127}));
  connect(velocity_y.y, velocity_error_y.u2) 
    annotation(Line(points = {{-895, 455}, {-895, 149}, {-746, 149}, {-746, -157}}, color = {0, 0, 127}));
  connect(position_error_y.y, linear_position_term_y.u) 
    annotation(Line(points = {{-733, -57}, {-718, -57}, {-718, -35}, {-703, -35}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, linear_velocity_term_y.u) 
    annotation(Line(points = {{-746, -157}, {-746, -128.5}, {-690, -128.5}, {-690, -100}}, color = {0, 0, 127}));
  connect(previous_acceleration_y.y, linear_previous_term_y.u) 
    annotation(Line(points = {{-847, -90}, {-775, -90}, {-775, -145}, {-703, -145}}, color = {0, 0, 127}));
  connect(linear_position_term_y.y, linear_solution_y_stage1.u1) 
    annotation(Line(points = {{-677, -35}, {-628, -35}, {-628, -112}, {-579, -112}}, color = {0, 0, 127}));
  connect(linear_velocity_term_y.y, linear_solution_y_stage1.u2) 
    annotation(Line(points = {{-677, -90}, {-628, -90}, {-628, -112}, {-579, -112}}, color = {0, 0, 127}));
  connect(linear_solution_y_stage1.y, linear_solution_y.u1) 
    annotation(Line(points = {{-553, -112}, {-549, -112}, {-549, -134}, {-545, -134}}, color = {0, 0, 127}));
  connect(linear_previous_term_y.y, linear_solution_y.u2) 
    annotation(Line(points = {{-677, -145}, {-611, -145}, {-611, -134}, {-545, -134}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, unconstrained_command_y.u1) 
    annotation(Line(points = {{-519, -134}, {243.5, -134}, {243.5, -112}, {1006, -112}}, color = {0, 0, 127}));
  connect(reference_acceleration_y.y, unconstrained_command_y.u2) 
    annotation(Line(points = {{-882, 300}, {62, 300}, {62, -112}, {1006, -112}}, color = {0, 0, 127}));
  connect(unconstrained_command_y.y, absolute_acceleration_limit_y.u) 
    annotation(Line(points = {{1032, -112}, {1044.5, -112}, {1044.5, -90}, {1057, -90}}, color = {0, 0, 127}));
  connect(previous_acceleration_y.y, previous_lower_bound_y.u) 
    annotation(Line(points = {{-847, -90}, {105, -90}, {105, -5}, {1057, -5}}, color = {0, 0, 127}));
  connect(previous_lower_bound_y.y, increment_lower_y.u1) 
    annotation(Line(points = {{1083, -5}, {1129.5, -5}, {1129.5, -7}, {1176, -7}}, color = {0, 0, 127}));
  connect(increment_limit_y.y, increment_lower_y.u2) 
    annotation(Line(points = {{1083, 40}, {1129.5, 40}, {1129.5, -7}, {1176, -7}}, color = {0, 0, 127}));
  connect(previous_lower_bound_y.y, increment_upper_y.u1) 
    annotation(Line(points = {{1083, -5}, {1129.5, -5}, {1129.5, -47}, {1176, -47}}, color = {0, 0, 127}));
  connect(increment_limit_y.y, increment_upper_y.u2) 
    annotation(Line(points = {{1083, 40}, {1129.5, 40}, {1129.5, -47}, {1176, -47}}, color = {0, 0, 127}));
  connect(absolute_acceleration_limit_y.y, increment_lower_clip_y.u1) 
    annotation(Line(points = {{1083, -90}, {1155, -90}, {1155, -55}, {1227, -55}}, color = {0, 0, 127}));
  connect(increment_lower_y.y, increment_lower_clip_y.u2) 
    annotation(Line(points = {{1202, -7}, {1214.5, -7}, {1214.5, -55}, {1227, -55}}, color = {0, 0, 127}));
  connect(increment_lower_clip_y.y, increment_upper_clip_y.u1) 
    annotation(Line(points = {{1253, -55}, {1282.5, -55}, {1282.5, -90}, {1312, -90}}, color = {0, 0, 127}));
  connect(increment_upper_y.y, increment_upper_clip_y.u2) 
    annotation(Line(points = {{1202, -47}, {1257, -47}, {1257, -90}, {1312, -90}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, previous_acceleration_y.u1) 
    annotation(Line(points = {{1312, -90}, {-847, -90}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, final_linear_mpc_y_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {119.5, -167}, {119.5, -190}, {972, -190}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_linear_mpc_y_half_h2_acc.u) 
    annotation(Line(points = {{1312, -90}, {1155, -90}, {1155, -235}, {998, -235}}, color = {0, 0, 127}));
  connect(position_error_y.y, final_linear_mpc_y_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {179, -57}, {179, -222}, {1091, -222}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_h_ev.y, final_linear_mpc_y_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, -190}, {1044.5, -190}, {1044.5, -222}, {1091, -222}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_predicted_position_error_stage1.y, final_linear_mpc_y_predicted_position_error.u1) 
    annotation(Line(points = {{1117, -222}, {1121, -222}, {1121, -244}, {1125, -244}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_half_h2_acc.y, final_linear_mpc_y_predicted_position_error.u2) 
    annotation(Line(points = {{998, -235}, {1061.5, -235}, {1061.5, -244}, {1125, -244}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_linear_mpc_y_h_acc.u) 
    annotation(Line(points = {{1312, -90}, {1155, -90}, {1155, -290}, {998, -290}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, final_linear_mpc_y_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {179, -167}, {179, -312}, {1091, -312}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_h_acc.y, final_linear_mpc_y_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, -290}, {1044.5, -290}, {1044.5, -312}, {1091, -312}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_predicted_position_error.y, final_linear_mpc_y_position_error_squared.u1) 
    annotation(Line(points = {{1138, -234}, {1138, -222}, {1155, -222}, {1155, -210}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_predicted_position_error.y, final_linear_mpc_y_position_error_squared.u2) 
    annotation(Line(points = {{1138, -234}, {1138, -222}, {1155, -222}, {1155, -210}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_predicted_velocity_error.y, final_linear_mpc_y_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, -302}, {1104, -283.5}, {1155, -283.5}, {1155, -265}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_predicted_velocity_error.y, final_linear_mpc_y_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, -302}, {1104, -283.5}, {1155, -283.5}, {1155, -265}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_linear_mpc_y_acceleration_squared.u1) 
    annotation(Line(points = {{1325, -100}, {1325, -200}, {1155, -200}, {1155, -300}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_linear_mpc_y_acceleration_squared.u2) 
    annotation(Line(points = {{1325, -100}, {1325, -200}, {1155, -200}, {1155, -300}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_position_error_squared.y, final_linear_mpc_y_position_cost.u) 
    annotation(Line(points = {{1168, -200}, {1227, -200}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_velocity_error_squared.y, final_linear_mpc_y_velocity_cost.u) 
    annotation(Line(points = {{1168, -255}, {1227, -255}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_acceleration_squared.y, final_linear_mpc_y_control_cost.u) 
    annotation(Line(points = {{1168, -310}, {1227, -310}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_position_cost.y, final_linear_mpc_y_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, -200}, {1299.5, -200}, {1299.5, -277}, {1346, -277}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_velocity_cost.y, final_linear_mpc_y_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, -255}, {1299.5, -255}, {1299.5, -277}, {1346, -277}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_stage_cost_stage1.y, final_linear_mpc_y_stage_cost.u1) 
    annotation(Line(points = {{1372, -277}, {1376, -277}, {1376, -299}, {1380, -299}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_control_cost.y, final_linear_mpc_y_stage_cost.u2) 
    annotation(Line(points = {{1253, -310}, {1316.5, -310}, {1316.5, -299}, {1380, -299}}, color = {0, 0, 127}));
  connect(reference_position_z.y, position_error_z.u1) 
    annotation(Line(points = {{-840, 400}, {-840, -38.5}, {-746, -38.5}, {-746, -477}}, color = {0, 0, 127}));
  connect(position_z.y, position_error_z.u2) 
    annotation(Line(points = {{-840, 510}, {-840, 16.5}, {-746, 16.5}, {-746, -477}}, color = {0, 0, 127}));
  connect(reference_velocity_z.y, velocity_error_z.u1) 
    annotation(Line(points = {{-840, 345}, {-840, -121}, {-746, -121}, {-746, -587}}, color = {0, 0, 127}));
  connect(velocity_z.y, velocity_error_z.u2) 
    annotation(Line(points = {{-840, 455}, {-840, -66}, {-746, -66}, {-746, -587}}, color = {0, 0, 127}));
  connect(position_error_z.y, linear_position_term_z.u) 
    annotation(Line(points = {{-733, -487}, {-718, -487}, {-718, -465}, {-703, -465}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, linear_velocity_term_z.u) 
    annotation(Line(points = {{-746, -587}, {-746, -558.5}, {-690, -558.5}, {-690, -530}}, color = {0, 0, 127}));
  connect(previous_acceleration_z.y, linear_previous_term_z.u) 
    annotation(Line(points = {{-847, -520}, {-775, -520}, {-775, -575}, {-703, -575}}, color = {0, 0, 127}));
  connect(linear_position_term_z.y, linear_solution_z_stage1.u1) 
    annotation(Line(points = {{-677, -465}, {-628, -465}, {-628, -542}, {-579, -542}}, color = {0, 0, 127}));
  connect(linear_velocity_term_z.y, linear_solution_z_stage1.u2) 
    annotation(Line(points = {{-677, -520}, {-628, -520}, {-628, -542}, {-579, -542}}, color = {0, 0, 127}));
  connect(linear_solution_z_stage1.y, linear_solution_z.u1) 
    annotation(Line(points = {{-553, -542}, {-549, -542}, {-549, -564}, {-545, -564}}, color = {0, 0, 127}));
  connect(linear_previous_term_z.y, linear_solution_z.u2) 
    annotation(Line(points = {{-677, -575}, {-611, -575}, {-611, -564}, {-545, -564}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, unconstrained_command_z.u1) 
    annotation(Line(points = {{-519, -564}, {243.5, -564}, {243.5, -542}, {1006, -542}}, color = {0, 0, 127}));
  connect(reference_acceleration_z.y, unconstrained_command_z.u2) 
    annotation(Line(points = {{-827, 300}, {89.5, 300}, {89.5, -542}, {1006, -542}}, color = {0, 0, 127}));
  connect(unconstrained_command_z.y, absolute_acceleration_limit_z.u) 
    annotation(Line(points = {{1032, -542}, {1044.5, -542}, {1044.5, -520}, {1057, -520}}, color = {0, 0, 127}));
  connect(previous_acceleration_z.y, previous_lower_bound_z.u) 
    annotation(Line(points = {{-847, -520}, {105, -520}, {105, -435}, {1057, -435}}, color = {0, 0, 127}));
  connect(previous_lower_bound_z.y, increment_lower_z.u1) 
    annotation(Line(points = {{1083, -435}, {1129.5, -435}, {1129.5, -437}, {1176, -437}}, color = {0, 0, 127}));
  connect(increment_limit_z.y, increment_lower_z.u2) 
    annotation(Line(points = {{1083, -390}, {1129.5, -390}, {1129.5, -437}, {1176, -437}}, color = {0, 0, 127}));
  connect(previous_lower_bound_z.y, increment_upper_z.u1) 
    annotation(Line(points = {{1083, -435}, {1129.5, -435}, {1129.5, -477}, {1176, -477}}, color = {0, 0, 127}));
  connect(increment_limit_z.y, increment_upper_z.u2) 
    annotation(Line(points = {{1083, -390}, {1129.5, -390}, {1129.5, -477}, {1176, -477}}, color = {0, 0, 127}));
  connect(absolute_acceleration_limit_z.y, increment_lower_clip_z.u1) 
    annotation(Line(points = {{1083, -520}, {1155, -520}, {1155, -485}, {1227, -485}}, color = {0, 0, 127}));
  connect(increment_lower_z.y, increment_lower_clip_z.u2) 
    annotation(Line(points = {{1202, -437}, {1214.5, -437}, {1214.5, -485}, {1227, -485}}, color = {0, 0, 127}));
  connect(increment_lower_clip_z.y, increment_upper_clip_z.u1) 
    annotation(Line(points = {{1253, -485}, {1282.5, -485}, {1282.5, -520}, {1312, -520}}, color = {0, 0, 127}));
  connect(increment_upper_z.y, increment_upper_clip_z.u2) 
    annotation(Line(points = {{1202, -477}, {1257, -477}, {1257, -520}, {1312, -520}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, previous_acceleration_z.u1) 
    annotation(Line(points = {{1312, -520}, {-847, -520}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, gravity_compensation.u1) 
    annotation(Line(points = {{1338, -520}, {1384.5, -520}, {1384.5, -542}, {1431, -542}}, color = {0, 0, 127}));
  connect(gravity.y, gravity_compensation.u2) 
    annotation(Line(points = {{1338, -425}, {1384.5, -425}, {1384.5, -542}, {1431, -542}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, final_linear_mpc_z_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {119.5, -597}, {119.5, -620}, {972, -620}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_linear_mpc_z_half_h2_acc.u) 
    annotation(Line(points = {{1312, -520}, {1155, -520}, {1155, -665}, {998, -665}}, color = {0, 0, 127}));
  connect(position_error_z.y, final_linear_mpc_z_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {179, -487}, {179, -652}, {1091, -652}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_h_ev.y, final_linear_mpc_z_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, -620}, {1044.5, -620}, {1044.5, -652}, {1091, -652}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_predicted_position_error_stage1.y, final_linear_mpc_z_predicted_position_error.u1) 
    annotation(Line(points = {{1117, -652}, {1121, -652}, {1121, -674}, {1125, -674}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_half_h2_acc.y, final_linear_mpc_z_predicted_position_error.u2) 
    annotation(Line(points = {{998, -665}, {1061.5, -665}, {1061.5, -674}, {1125, -674}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_linear_mpc_z_h_acc.u) 
    annotation(Line(points = {{1312, -520}, {1155, -520}, {1155, -720}, {998, -720}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, final_linear_mpc_z_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {179, -597}, {179, -742}, {1091, -742}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_h_acc.y, final_linear_mpc_z_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, -720}, {1044.5, -720}, {1044.5, -742}, {1091, -742}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_predicted_position_error.y, final_linear_mpc_z_position_error_squared.u1) 
    annotation(Line(points = {{1138, -664}, {1138, -652}, {1155, -652}, {1155, -640}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_predicted_position_error.y, final_linear_mpc_z_position_error_squared.u2) 
    annotation(Line(points = {{1138, -664}, {1138, -652}, {1155, -652}, {1155, -640}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_predicted_velocity_error.y, final_linear_mpc_z_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, -732}, {1104, -713.5}, {1155, -713.5}, {1155, -695}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_predicted_velocity_error.y, final_linear_mpc_z_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, -732}, {1104, -713.5}, {1155, -713.5}, {1155, -695}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_linear_mpc_z_acceleration_squared.u1) 
    annotation(Line(points = {{1325, -530}, {1325, -630}, {1155, -630}, {1155, -730}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_linear_mpc_z_acceleration_squared.u2) 
    annotation(Line(points = {{1325, -530}, {1325, -630}, {1155, -630}, {1155, -730}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_position_error_squared.y, final_linear_mpc_z_position_cost.u) 
    annotation(Line(points = {{1168, -630}, {1227, -630}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_velocity_error_squared.y, final_linear_mpc_z_velocity_cost.u) 
    annotation(Line(points = {{1168, -685}, {1227, -685}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_acceleration_squared.y, final_linear_mpc_z_control_cost.u) 
    annotation(Line(points = {{1168, -740}, {1227, -740}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_position_cost.y, final_linear_mpc_z_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, -630}, {1299.5, -630}, {1299.5, -707}, {1346, -707}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_velocity_cost.y, final_linear_mpc_z_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, -685}, {1299.5, -685}, {1299.5, -707}, {1346, -707}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_stage_cost_stage1.y, final_linear_mpc_z_stage_cost.u1) 
    annotation(Line(points = {{1372, -707}, {1376, -707}, {1376, -729}, {1380, -729}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_control_cost.y, final_linear_mpc_z_stage_cost.u2) 
    annotation(Line(points = {{1253, -740}, {1316.5, -740}, {1316.5, -729}, {1380, -729}}, color = {0, 0, 127}));
  connect(final_linear_mpc_x_stage_cost.y, solver_cost_sum_stage1.u1) 
    annotation(Line(points = {{1393, 121}, {1393, -410.5}, {1544, -410.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(final_linear_mpc_y_stage_cost.y, solver_cost_sum_stage1.u2) 
    annotation(Line(points = {{1393, -309}, {1393, -625.5}, {1544, -625.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1) 
    annotation(Line(points = {{1557, -952}, {1561, -952}, {1561, -974}, {1565, -974}}, color = {0, 0, 127}));
  connect(final_linear_mpc_z_stage_cost.y, solver_cost_sum.u2) 
    annotation(Line(points = {{1393, -739}, {1393, -851.5}, {1578, -851.5}, {1578, -964}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, desired_acceleration_x) 
    annotation(Line(points = {{1338, 340}, {1467.5, 340}, {1467.5, 360}, {1597, 360}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, desired_acceleration_y) 
    annotation(Line(points = {{1325, -80}, {1325, 82.5}, {1610, 82.5}, {1610, 245}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z) 
    annotation(Line(points = {{1444, -532}, {1444, -196}, {1610, -196}, {1610, 140}}, color = {0, 0, 127}));
  connect(unconstrained_command_x.y, unconstrained_acceleration_x) 
    annotation(Line(points = {{1032, 318}, {1314.5, 318}, {1314.5, 45}, {1597, 45}}, color = {0, 0, 127}));
  connect(unconstrained_command_y.y, unconstrained_acceleration_y) 
    annotation(Line(points = {{1032, -112}, {1314.5, -112}, {1314.5, -60}, {1597, -60}}, color = {0, 0, 127}));
  connect(unconstrained_command_z.y, unconstrained_acceleration_z) 
    annotation(Line(points = {{1032, -542}, {1314.5, -542}, {1314.5, -165}, {1597, -165}}, color = {0, 0, 127}));
  connect(auxiliary_zero_x.y, auxiliary_x) 
    annotation(Line(points = {{123, 510}, {860, 510}, {860, -270}, {1597, -270}}, color = {0, 0, 127}));
  connect(auxiliary_zero_y.y, auxiliary_y) 
    annotation(Line(points = {{123, 80}, {860, 80}, {860, -375}, {1597, -375}}, color = {0, 0, 127}));
  connect(auxiliary_zero_z.y, auxiliary_z) 
    annotation(Line(points = {{123, -350}, {860, -350}, {860, -480}, {1597, -480}}, color = {0, 0, 127}));
  connect(solver_cost_sum.y, solver_cost) 
    annotation(Line(points = {{1578, -964}, {1578, -779.5}, {1610, -779.5}, {1610, -595}}, color = {0, 0, 127}));
  connect(fixed_solver_budget.y, solver_iterations) 
    annotation(Line(points = {{1510, -990}, {1510, -845}, {1610, -845}, {1610, -700}}, color = {0, 0, 127}));
  end LinearMpcCore;