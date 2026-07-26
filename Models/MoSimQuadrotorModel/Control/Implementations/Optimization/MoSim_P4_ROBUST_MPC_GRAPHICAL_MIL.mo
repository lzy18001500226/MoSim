within MoSimQuadrotorModel.Control.Implementations.Optimization;
model MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL "P4 native graphical fixed-budget MPC controller core: robust_mpc"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, unconstrained_acceleration_x, unconstrained_acceleration_y, unconstrained_acceleration_z, auxiliary_x, auxiliary_y, auxiliary_z, solver_cost, solver_iterations)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
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
    annotation (Placement(transformation(origin = {-860, 340}, extent = {{-13, -10}, {13, 10}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain robust_horizon_velocity_x(k=0.25)
    annotation (Placement(transformation(origin = {-505, 470}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_surface_x(inputs="++")
    annotation (Placement(transformation(origin = {-386, 448}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_surface_scale_x(k=4.0)
    annotation (Placement(transformation(origin = {-335, 470}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction robust_tanh_x(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh)
    "P4 distinguishing native graphical path for robust_mpc" annotation (Placement(transformation(origin = {-250, 470}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_bound_term_x(k=0.25)
    annotation (Placement(transformation(origin = {-165, 470}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_solution_x(inputs="++")
    annotation (Placement(transformation(origin = {-46, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant robust_bound_debug_x(k=0.25)
    annotation (Placement(transformation(origin = {-80, 510}, extent = {{-13, -10}, {13, 10}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {985, 240}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {985, 195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_x_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1104, 208}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_x_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {1138, 186}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {985, 140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_x_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {1104, 118}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_x_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, 230}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_x_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, 175}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_x_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {1240, 230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {1240, 175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_x_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {1240, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_x_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1359, 153}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_x_stage_cost(inputs="++")
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
  SysplorerEmbeddedCoder.MathOperation.Gain robust_horizon_velocity_y(k=0.25)
    annotation (Placement(transformation(origin = {-505, 40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_surface_y(inputs="++")
    annotation (Placement(transformation(origin = {-386, 18}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_surface_scale_y(k=4.0)
    annotation (Placement(transformation(origin = {-335, 40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction robust_tanh_y(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh)
    annotation (Placement(transformation(origin = {-250, 40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_bound_term_y(k=0.25)
    annotation (Placement(transformation(origin = {-165, 40}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_solution_y(inputs="++")
    annotation (Placement(transformation(origin = {-46, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant robust_bound_debug_y(k=0.25)
    annotation (Placement(transformation(origin = {-80, 80}, extent = {{-13, -10}, {13, 10}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {985, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {985, -235}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_y_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1104, -222}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_y_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {1138, -244}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {985, -290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_y_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {1104, -312}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_y_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -200}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_y_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -255}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_y_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {1240, -200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {1240, -255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_y_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {1240, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_y_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1359, -277}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_y_stage_cost(inputs="++")
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
  SysplorerEmbeddedCoder.MathOperation.Gain robust_horizon_velocity_z(k=0.25)
    annotation (Placement(transformation(origin = {-505, -390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_surface_z(inputs="++")
    annotation (Placement(transformation(origin = {-386, -412}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_surface_scale_z(k=4.0)
    annotation (Placement(transformation(origin = {-335, -390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction robust_tanh_z(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh)
    annotation (Placement(transformation(origin = {-250, -390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain robust_bound_term_z(k=0.2)
    annotation (Placement(transformation(origin = {-165, -390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum robust_solution_z(inputs="++")
    annotation (Placement(transformation(origin = {-46, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant robust_bound_debug_z(k=0.2)
    annotation (Placement(transformation(origin = {-80, -350}, extent = {{-13, -10}, {13, 10}})));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {985, -620}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {985, -665}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_z_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1104, -652}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_z_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {1138, -674}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {985, -720}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_z_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {1104, -742}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_z_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -630}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_z_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -685}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_robust_mpc_z_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {1155, -740}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {1240, -630}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {1240, -685}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_robust_mpc_z_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {1240, -740}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_z_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1359, -707}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_robust_mpc_z_stage_cost(inputs="++")
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
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  equation
  connect(reference_position_x.y, position_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_x.y, position_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_x.y, velocity_error_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_x.y, velocity_error_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, linear_position_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, linear_velocity_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_x.y, linear_previous_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_position_term_x.y, linear_solution_x_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_velocity_term_x.y, linear_solution_x_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x_stage1.y, linear_solution_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_previous_term_x.y, linear_solution_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, robust_horizon_velocity_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, robust_surface_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_horizon_velocity_x.y, robust_surface_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_x.y, robust_surface_scale_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_scale_x.y, robust_tanh_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_tanh_x.y1, robust_bound_term_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, robust_solution_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_term_x.y, robust_solution_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_solution_x.y, unconstrained_command_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_x.y, unconstrained_command_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_x.y, absolute_acceleration_limit_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_x.y, previous_lower_bound_x.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_x.y, increment_lower_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_x.y, increment_lower_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_x.y, increment_upper_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_x.y, increment_upper_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(absolute_acceleration_limit_x.y, increment_lower_clip_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_x.y, increment_lower_clip_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_clip_x.y, increment_upper_clip_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_x.y, increment_upper_clip_x.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, previous_acceleration_x.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, final_robust_mpc_x_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_robust_mpc_x_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, final_robust_mpc_x_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_h_ev.y, final_robust_mpc_x_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_predicted_position_error_stage1.y, final_robust_mpc_x_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_half_h2_acc.y, final_robust_mpc_x_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_robust_mpc_x_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, final_robust_mpc_x_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_h_acc.y, final_robust_mpc_x_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_predicted_position_error.y, final_robust_mpc_x_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_predicted_position_error.y, final_robust_mpc_x_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_predicted_velocity_error.y, final_robust_mpc_x_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_predicted_velocity_error.y, final_robust_mpc_x_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_robust_mpc_x_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_robust_mpc_x_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_position_error_squared.y, final_robust_mpc_x_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_velocity_error_squared.y, final_robust_mpc_x_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_acceleration_squared.y, final_robust_mpc_x_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_position_cost.y, final_robust_mpc_x_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_velocity_cost.y, final_robust_mpc_x_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_stage_cost_stage1.y, final_robust_mpc_x_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_control_cost.y, final_robust_mpc_x_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_y.y, position_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_y.y, position_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_y.y, velocity_error_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_y.y, velocity_error_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, linear_position_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, linear_velocity_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_y.y, linear_previous_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_position_term_y.y, linear_solution_y_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_velocity_term_y.y, linear_solution_y_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y_stage1.y, linear_solution_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_previous_term_y.y, linear_solution_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, robust_horizon_velocity_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, robust_surface_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_horizon_velocity_y.y, robust_surface_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_y.y, robust_surface_scale_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_scale_y.y, robust_tanh_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_tanh_y.y1, robust_bound_term_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, robust_solution_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_term_y.y, robust_solution_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_solution_y.y, unconstrained_command_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_y.y, unconstrained_command_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_y.y, absolute_acceleration_limit_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_y.y, previous_lower_bound_y.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_y.y, increment_lower_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_y.y, increment_lower_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_y.y, increment_upper_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_y.y, increment_upper_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(absolute_acceleration_limit_y.y, increment_lower_clip_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_y.y, increment_lower_clip_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_clip_y.y, increment_upper_clip_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_y.y, increment_upper_clip_y.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, previous_acceleration_y.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, final_robust_mpc_y_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_robust_mpc_y_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, final_robust_mpc_y_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_h_ev.y, final_robust_mpc_y_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_predicted_position_error_stage1.y, final_robust_mpc_y_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_half_h2_acc.y, final_robust_mpc_y_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_robust_mpc_y_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, final_robust_mpc_y_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_h_acc.y, final_robust_mpc_y_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_predicted_position_error.y, final_robust_mpc_y_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_predicted_position_error.y, final_robust_mpc_y_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_predicted_velocity_error.y, final_robust_mpc_y_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_predicted_velocity_error.y, final_robust_mpc_y_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_robust_mpc_y_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_robust_mpc_y_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_position_error_squared.y, final_robust_mpc_y_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_velocity_error_squared.y, final_robust_mpc_y_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_acceleration_squared.y, final_robust_mpc_y_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_position_cost.y, final_robust_mpc_y_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_velocity_cost.y, final_robust_mpc_y_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_stage_cost_stage1.y, final_robust_mpc_y_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_control_cost.y, final_robust_mpc_y_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_position_z.y, position_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_z.y, position_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_velocity_z.y, velocity_error_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_z.y, velocity_error_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, linear_position_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, linear_velocity_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_z.y, linear_previous_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_position_term_z.y, linear_solution_z_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_velocity_term_z.y, linear_solution_z_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z_stage1.y, linear_solution_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_previous_term_z.y, linear_solution_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, robust_horizon_velocity_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, robust_surface_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_horizon_velocity_z.y, robust_surface_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_z.y, robust_surface_scale_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_surface_scale_z.y, robust_tanh_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_tanh_z.y1, robust_bound_term_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, robust_solution_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_term_z.y, robust_solution_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_solution_z.y, unconstrained_command_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(reference_acceleration_z.y, unconstrained_command_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_z.y, absolute_acceleration_limit_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_acceleration_z.y, previous_lower_bound_z.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_z.y, increment_lower_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_z.y, increment_lower_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(previous_lower_bound_z.y, increment_upper_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_limit_z.y, increment_upper_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(absolute_acceleration_limit_z.y, increment_lower_clip_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_z.y, increment_lower_clip_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_lower_clip_z.y, increment_upper_clip_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_z.y, increment_upper_clip_z.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, previous_acceleration_z.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, gravity_compensation.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gravity.y, gravity_compensation.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, final_robust_mpc_z_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_robust_mpc_z_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, final_robust_mpc_z_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_h_ev.y, final_robust_mpc_z_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_predicted_position_error_stage1.y, final_robust_mpc_z_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_half_h2_acc.y, final_robust_mpc_z_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_robust_mpc_z_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, final_robust_mpc_z_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_h_acc.y, final_robust_mpc_z_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_predicted_position_error.y, final_robust_mpc_z_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_predicted_position_error.y, final_robust_mpc_z_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_predicted_velocity_error.y, final_robust_mpc_z_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_predicted_velocity_error.y, final_robust_mpc_z_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_robust_mpc_z_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_robust_mpc_z_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_position_error_squared.y, final_robust_mpc_z_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_velocity_error_squared.y, final_robust_mpc_z_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_acceleration_squared.y, final_robust_mpc_z_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_position_cost.y, final_robust_mpc_z_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_velocity_cost.y, final_robust_mpc_z_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_stage_cost_stage1.y, final_robust_mpc_z_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_control_cost.y, final_robust_mpc_z_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_x_stage_cost.y, solver_cost_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_y_stage_cost.y, solver_cost_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_robust_mpc_z_stage_cost.y, solver_cost_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, desired_acceleration_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, desired_acceleration_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gravity_compensation.y, desired_acceleration_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_x.y, unconstrained_acceleration_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_y.y, unconstrained_acceleration_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(unconstrained_command_z.y, unconstrained_acceleration_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_debug_x.y, auxiliary_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_debug_y.y, auxiliary_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(robust_bound_debug_z.y, auxiliary_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(solver_cost_sum.y, solver_cost)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fixed_solver_budget.y, solver_iterations)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  end MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL;