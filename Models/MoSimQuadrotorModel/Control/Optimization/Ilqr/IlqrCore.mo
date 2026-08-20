within MoSimQuadrotorModel.Control.Optimization.Ilqr;
model IlqrCore "P4 native graphical fixed-budget MPC controller core: ilqr"
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
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-420, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-420, 400}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-346, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-312, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-420, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-346, 338}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-340, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-340, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-340, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-266, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-232, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter1_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-260, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter1_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-186, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-335, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-335, 400}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-261, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-227, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-335, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-261, 338}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-255, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-255, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-255, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-181, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-147, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter2_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-175, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter2_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-101, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-250, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-250, 400}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-176, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-142, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-250, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-176, 338}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-170, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-170, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-170, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-96, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-62, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter3_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-90, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter3_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-16, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-165, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-165, 400}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-91, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-57, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-165, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-91, 338}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-85, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-85, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-85, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-11, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {23, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter4_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-5, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter4_update(inputs="+-") 
    annotation (Placement(transformation(origin = {69, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-80, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-80, 400}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-6, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {28, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-80, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-6, 338}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {0, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {0, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_ga(k=0.004) 
    annotation (Placement(transformation(origin = {0, 340}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {74, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {108, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_0_iter5_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {80, 380}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_0_iter5_update(inputs="+-")
    "P4 distinguishing native graphical path for ilqr" annotation (Placement(transformation(origin = {154, 318}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, 240}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, 195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_x_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, 208}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_x_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, 186}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, 140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_x_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, 118}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_x_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 230}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_x_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 175}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_x_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_position_cost(k=1.0) 
    annotation (Placement(transformation(origin = {1240, 230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_velocity_cost(k=0.08) 
    annotation (Placement(transformation(origin = {1240, 175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_x_control_cost(k=0.002) 
    annotation (Placement(transformation(origin = {1240, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_x_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, 153}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_x_stage_cost(inputs="++") 
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
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-420, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-420, -30}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-346, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-312, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-420, -70}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-346, -92}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-340, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-340, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-340, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-266, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-232, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter1_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-260, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter1_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-186, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-335, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-335, -30}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-261, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-227, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-335, -70}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-261, -92}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-255, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-255, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-255, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-181, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-147, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter2_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-175, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter2_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-101, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-250, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-250, -30}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-176, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-142, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-250, -70}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-176, -92}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-170, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-170, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-170, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-96, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-62, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter3_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-90, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter3_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-16, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-165, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-165, -30}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-91, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-57, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-165, -70}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-91, -92}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {-85, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {-85, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_ga(k=0.004) 
    annotation (Placement(transformation(origin = {-85, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-11, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {23, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter4_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {-5, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter4_update(inputs="+-") 
    annotation (Placement(transformation(origin = {69, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-80, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-80, -30}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-6, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {28, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-80, -70}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-6, -92}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_gp(k=-0.0625) 
    annotation (Placement(transformation(origin = {0, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_gv(k=-0.04) 
    annotation (Placement(transformation(origin = {0, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_ga(k=0.004) 
    annotation (Placement(transformation(origin = {0, -90}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {74, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {108, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_1_iter5_newton_step(k=40.74436826640549) 
    annotation (Placement(transformation(origin = {80, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_1_iter5_update(inputs="+-") 
    annotation (Placement(transformation(origin = {154, -112}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, -235}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_y_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, -222}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_y_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, -244}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, -290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_y_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, -312}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_y_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -200}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_y_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -255}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_y_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_position_cost(k=1.0) 
    annotation (Placement(transformation(origin = {1240, -200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_velocity_cost(k=0.08) 
    annotation (Placement(transformation(origin = {1240, -255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_y_control_cost(k=0.002) 
    annotation (Placement(transformation(origin = {1240, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_y_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, -277}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_y_stage_cost(inputs="++") 
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
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-420, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-420, -460}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-346, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-312, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-420, -500}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-346, -522}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_gp(k=-0.075) 
    annotation (Placement(transformation(origin = {-340, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_gv(k=-0.05) 
    annotation (Placement(transformation(origin = {-340, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_ga(k=0.006) 
    annotation (Placement(transformation(origin = {-340, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-266, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-232, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter1_newton_step(k=31.184407796101947) 
    annotation (Placement(transformation(origin = {-260, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter1_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-186, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-335, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-335, -460}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-261, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-227, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-335, -500}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-261, -522}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_gp(k=-0.075) 
    annotation (Placement(transformation(origin = {-255, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_gv(k=-0.05) 
    annotation (Placement(transformation(origin = {-255, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_ga(k=0.006) 
    annotation (Placement(transformation(origin = {-255, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-181, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-147, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter2_newton_step(k=31.184407796101947) 
    annotation (Placement(transformation(origin = {-175, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter2_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-101, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-250, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-250, -460}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-176, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-142, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-250, -500}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-176, -522}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_gp(k=-0.075) 
    annotation (Placement(transformation(origin = {-170, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_gv(k=-0.05) 
    annotation (Placement(transformation(origin = {-170, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_ga(k=0.006) 
    annotation (Placement(transformation(origin = {-170, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-96, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {-62, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter3_newton_step(k=31.184407796101947) 
    annotation (Placement(transformation(origin = {-90, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter3_update(inputs="+-") 
    annotation (Placement(transformation(origin = {-16, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-165, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-165, -460}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-91, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {-57, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-165, -500}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-91, -522}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_gp(k=-0.075) 
    annotation (Placement(transformation(origin = {-85, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_gv(k=-0.05) 
    annotation (Placement(transformation(origin = {-85, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_ga(k=0.006) 
    annotation (Placement(transformation(origin = {-85, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-11, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {23, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter4_newton_step(k=31.184407796101947) 
    annotation (Placement(transformation(origin = {-5, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter4_update(inputs="+-") 
    annotation (Placement(transformation(origin = {69, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {-80, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {-80, -460}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_pe_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {-6, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_pe(inputs="+-") 
    annotation (Placement(transformation(origin = {28, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {-80, -500}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_ve(inputs="+-") 
    annotation (Placement(transformation(origin = {-6, -522}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_gp(k=-0.075) 
    annotation (Placement(transformation(origin = {0, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_gv(k=-0.05) 
    annotation (Placement(transformation(origin = {0, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_ga(k=0.006) 
    annotation (Placement(transformation(origin = {0, -520}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_gradient_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {74, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_gradient(inputs="++") 
    annotation (Placement(transformation(origin = {108, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain ilqr_2_iter5_newton_step(k=31.184407796101947) 
    annotation (Placement(transformation(origin = {80, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum ilqr_2_iter5_update(inputs="+-") 
    annotation (Placement(transformation(origin = {154, -542}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_h_ev(k=0.25) 
    annotation (Placement(transformation(origin = {985, -620}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_half_h2_acc(k=0.03125) 
    annotation (Placement(transformation(origin = {985, -665}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_z_predicted_position_error_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1104, -652}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_z_predicted_position_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1138, -674}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_h_acc(k=0.25) 
    annotation (Placement(transformation(origin = {985, -720}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_z_predicted_velocity_error(inputs="+-") 
    annotation (Placement(transformation(origin = {1104, -742}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_z_position_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -630}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_z_velocity_error_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -685}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product final_ilqr_z_acceleration_squared(inputs="**") 
    annotation (Placement(transformation(origin = {1155, -740}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_position_cost(k=1.2) 
    annotation (Placement(transformation(origin = {1240, -630}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_velocity_cost(k=0.1) 
    annotation (Placement(transformation(origin = {1240, -685}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain final_ilqr_z_control_cost(k=0.003) 
    annotation (Placement(transformation(origin = {1240, -740}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_z_stage_cost_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1359, -707}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum final_ilqr_z_stage_cost(inputs="++") 
    annotation (Placement(transformation(origin = {1393, -729}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum_stage1(inputs="++") 
    annotation (Placement(transformation(origin = {1544, -952}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum(inputs="++") 
    annotation (Placement(transformation(origin = {1578, -974}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant fixed_solver_budget(k=5.0) 
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
  connect(velocity_error_x.y, ilqr_0_iter1_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-583, 263}, {-583, 440}, {-433, 440}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, ilqr_0_iter1_half_h2_acc.u) 
    annotation(Line(points = {{-519, 296}, {-476, 296}, {-476, 400}, {-433, 400}}, color = {0, 0, 127}));
  connect(position_error_x.y, ilqr_0_iter1_pe_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-546, 373}, {-546, 398}, {-359, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_h_ev.y, ilqr_0_iter1_pe_stage1.u2) 
    annotation(Line(points = {{-407, 440}, {-383, 440}, {-383, 398}, {-359, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_pe_stage1.y, ilqr_0_iter1_pe.u1) 
    annotation(Line(points = {{-333, 398}, {-329, 398}, {-329, 376}, {-325, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_half_h2_acc.y, ilqr_0_iter1_pe.u2) 
    annotation(Line(points = {{-407, 400}, {-366, 400}, {-366, 376}, {-325, 376}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, ilqr_0_iter1_h_acc.u) 
    annotation(Line(points = {{-519, 296}, {-476, 296}, {-476, 360}, {-433, 360}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter1_ve.u1) 
    annotation(Line(points = {{-733, 263}, {-546, 263}, {-546, 338}, {-359, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_h_acc.y, ilqr_0_iter1_ve.u2) 
    annotation(Line(points = {{-407, 360}, {-383, 360}, {-383, 338}, {-359, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_pe.y, ilqr_0_iter1_gp.u) 
    annotation(Line(points = {{-312, 386}, {-312, 398}, {-340, 398}, {-340, 410}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_ve.y, ilqr_0_iter1_gv.u) 
    annotation(Line(points = {{-346, 348}, {-346, 359}, {-340, 359}, {-340, 370}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, ilqr_0_iter1_ga.u) 
    annotation(Line(points = {{-519, 296}, {-436, 296}, {-436, 340}, {-353, 340}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_gp.y, ilqr_0_iter1_gradient_stage1.u1) 
    annotation(Line(points = {{-327, 420}, {-303, 420}, {-303, 358}, {-279, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_gv.y, ilqr_0_iter1_gradient_stage1.u2) 
    annotation(Line(points = {{-327, 380}, {-303, 380}, {-303, 358}, {-279, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_gradient_stage1.y, ilqr_0_iter1_gradient.u1) 
    annotation(Line(points = {{-253, 358}, {-249, 358}, {-249, 336}, {-245, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_ga.y, ilqr_0_iter1_gradient.u2) 
    annotation(Line(points = {{-327, 340}, {-286, 340}, {-286, 336}, {-245, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_gradient.y, ilqr_0_iter1_newton_step.u) 
    annotation(Line(points = {{-232, 346}, {-232, 358}, {-260, 358}, {-260, 370}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, ilqr_0_iter1_update.u1) 
    annotation(Line(points = {{-519, 296}, {-359, 296}, {-359, 318}, {-199, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_newton_step.y, ilqr_0_iter1_update.u2) 
    annotation(Line(points = {{-247, 380}, {-223, 380}, {-223, 318}, {-199, 318}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter2_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-540.5, 263}, {-540.5, 440}, {-348, 440}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_half_h2_acc.u) 
    annotation(Line(points = {{-199, 318}, {-260.5, 318}, {-260.5, 400}, {-322, 400}}, color = {0, 0, 127}));
  connect(position_error_x.y, ilqr_0_iter2_pe_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-503.5, 373}, {-503.5, 398}, {-274, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_h_ev.y, ilqr_0_iter2_pe_stage1.u2) 
    annotation(Line(points = {{-322, 440}, {-298, 440}, {-298, 398}, {-274, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_pe_stage1.y, ilqr_0_iter2_pe.u1) 
    annotation(Line(points = {{-248, 398}, {-244, 398}, {-244, 376}, {-240, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_half_h2_acc.y, ilqr_0_iter2_pe.u2) 
    annotation(Line(points = {{-322, 400}, {-281, 400}, {-281, 376}, {-240, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_h_acc.u) 
    annotation(Line(points = {{-199, 318}, {-260.5, 318}, {-260.5, 360}, {-322, 360}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter2_ve.u1) 
    annotation(Line(points = {{-733, 263}, {-503.5, 263}, {-503.5, 338}, {-274, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_h_acc.y, ilqr_0_iter2_ve.u2) 
    annotation(Line(points = {{-322, 360}, {-298, 360}, {-298, 338}, {-274, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_pe.y, ilqr_0_iter2_gp.u) 
    annotation(Line(points = {{-227, 386}, {-227, 398}, {-255, 398}, {-255, 410}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_ve.y, ilqr_0_iter2_gv.u) 
    annotation(Line(points = {{-261, 348}, {-261, 359}, {-255, 359}, {-255, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_ga.u) 
    annotation(Line(points = {{-199, 318}, {-220.5, 318}, {-220.5, 340}, {-242, 340}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_gp.y, ilqr_0_iter2_gradient_stage1.u1) 
    annotation(Line(points = {{-242, 420}, {-218, 420}, {-218, 358}, {-194, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_gv.y, ilqr_0_iter2_gradient_stage1.u2) 
    annotation(Line(points = {{-242, 380}, {-218, 380}, {-218, 358}, {-194, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_gradient_stage1.y, ilqr_0_iter2_gradient.u1) 
    annotation(Line(points = {{-168, 358}, {-164, 358}, {-164, 336}, {-160, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_ga.y, ilqr_0_iter2_gradient.u2) 
    annotation(Line(points = {{-242, 340}, {-201, 340}, {-201, 336}, {-160, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_gradient.y, ilqr_0_iter2_newton_step.u) 
    annotation(Line(points = {{-147, 346}, {-147, 358}, {-175, 358}, {-175, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_update.u1) 
    annotation(Line(points = {{-173, 318}, {-114, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_newton_step.y, ilqr_0_iter2_update.u2) 
    annotation(Line(points = {{-162, 380}, {-138, 380}, {-138, 318}, {-114, 318}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter3_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-498, 263}, {-498, 440}, {-263, 440}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_half_h2_acc.u) 
    annotation(Line(points = {{-114, 318}, {-175.5, 318}, {-175.5, 400}, {-237, 400}}, color = {0, 0, 127}));
  connect(position_error_x.y, ilqr_0_iter3_pe_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-461, 373}, {-461, 398}, {-189, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_h_ev.y, ilqr_0_iter3_pe_stage1.u2) 
    annotation(Line(points = {{-237, 440}, {-213, 440}, {-213, 398}, {-189, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_pe_stage1.y, ilqr_0_iter3_pe.u1) 
    annotation(Line(points = {{-163, 398}, {-159, 398}, {-159, 376}, {-155, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_half_h2_acc.y, ilqr_0_iter3_pe.u2) 
    annotation(Line(points = {{-237, 400}, {-196, 400}, {-196, 376}, {-155, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_h_acc.u) 
    annotation(Line(points = {{-114, 318}, {-175.5, 318}, {-175.5, 360}, {-237, 360}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter3_ve.u1) 
    annotation(Line(points = {{-733, 263}, {-461, 263}, {-461, 338}, {-189, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_h_acc.y, ilqr_0_iter3_ve.u2) 
    annotation(Line(points = {{-237, 360}, {-213, 360}, {-213, 338}, {-189, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_pe.y, ilqr_0_iter3_gp.u) 
    annotation(Line(points = {{-142, 386}, {-142, 398}, {-170, 398}, {-170, 410}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_ve.y, ilqr_0_iter3_gv.u) 
    annotation(Line(points = {{-176, 348}, {-176, 359}, {-170, 359}, {-170, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_ga.u) 
    annotation(Line(points = {{-114, 318}, {-135.5, 318}, {-135.5, 340}, {-157, 340}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_gp.y, ilqr_0_iter3_gradient_stage1.u1) 
    annotation(Line(points = {{-157, 420}, {-133, 420}, {-133, 358}, {-109, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_gv.y, ilqr_0_iter3_gradient_stage1.u2) 
    annotation(Line(points = {{-157, 380}, {-133, 380}, {-133, 358}, {-109, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_gradient_stage1.y, ilqr_0_iter3_gradient.u1) 
    annotation(Line(points = {{-83, 358}, {-79, 358}, {-79, 336}, {-75, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_ga.y, ilqr_0_iter3_gradient.u2) 
    annotation(Line(points = {{-157, 340}, {-116, 340}, {-116, 336}, {-75, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_gradient.y, ilqr_0_iter3_newton_step.u) 
    annotation(Line(points = {{-62, 346}, {-62, 358}, {-90, 358}, {-90, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_update.u1) 
    annotation(Line(points = {{-88, 318}, {-29, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_newton_step.y, ilqr_0_iter3_update.u2) 
    annotation(Line(points = {{-77, 380}, {-53, 380}, {-53, 318}, {-29, 318}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter4_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-455.5, 263}, {-455.5, 440}, {-178, 440}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_half_h2_acc.u) 
    annotation(Line(points = {{-29, 318}, {-90.5, 318}, {-90.5, 400}, {-152, 400}}, color = {0, 0, 127}));
  connect(position_error_x.y, ilqr_0_iter4_pe_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-418.5, 373}, {-418.5, 398}, {-104, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_h_ev.y, ilqr_0_iter4_pe_stage1.u2) 
    annotation(Line(points = {{-152, 440}, {-128, 440}, {-128, 398}, {-104, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_pe_stage1.y, ilqr_0_iter4_pe.u1) 
    annotation(Line(points = {{-78, 398}, {-74, 398}, {-74, 376}, {-70, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_half_h2_acc.y, ilqr_0_iter4_pe.u2) 
    annotation(Line(points = {{-152, 400}, {-111, 400}, {-111, 376}, {-70, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_h_acc.u) 
    annotation(Line(points = {{-29, 318}, {-90.5, 318}, {-90.5, 360}, {-152, 360}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter4_ve.u1) 
    annotation(Line(points = {{-733, 263}, {-418.5, 263}, {-418.5, 338}, {-104, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_h_acc.y, ilqr_0_iter4_ve.u2) 
    annotation(Line(points = {{-152, 360}, {-128, 360}, {-128, 338}, {-104, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_pe.y, ilqr_0_iter4_gp.u) 
    annotation(Line(points = {{-57, 386}, {-57, 398}, {-85, 398}, {-85, 410}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_ve.y, ilqr_0_iter4_gv.u) 
    annotation(Line(points = {{-91, 348}, {-91, 359}, {-85, 359}, {-85, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_ga.u) 
    annotation(Line(points = {{-29, 318}, {-50.5, 318}, {-50.5, 340}, {-72, 340}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_gp.y, ilqr_0_iter4_gradient_stage1.u1) 
    annotation(Line(points = {{-72, 420}, {-48, 420}, {-48, 358}, {-24, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_gv.y, ilqr_0_iter4_gradient_stage1.u2) 
    annotation(Line(points = {{-72, 380}, {-48, 380}, {-48, 358}, {-24, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_gradient_stage1.y, ilqr_0_iter4_gradient.u1) 
    annotation(Line(points = {{2, 358}, {6, 358}, {6, 336}, {10, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_ga.y, ilqr_0_iter4_gradient.u2) 
    annotation(Line(points = {{-72, 340}, {-31, 340}, {-31, 336}, {10, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_gradient.y, ilqr_0_iter4_newton_step.u) 
    annotation(Line(points = {{23, 346}, {23, 358}, {-5, 358}, {-5, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_update.u1) 
    annotation(Line(points = {{-3, 318}, {56, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_newton_step.y, ilqr_0_iter4_update.u2) 
    annotation(Line(points = {{8, 380}, {32, 380}, {32, 318}, {56, 318}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter5_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-413, 263}, {-413, 440}, {-93, 440}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_half_h2_acc.u) 
    annotation(Line(points = {{56, 318}, {-5.5, 318}, {-5.5, 400}, {-67, 400}}, color = {0, 0, 127}));
  connect(position_error_x.y, ilqr_0_iter5_pe_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-376, 373}, {-376, 398}, {-19, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_h_ev.y, ilqr_0_iter5_pe_stage1.u2) 
    annotation(Line(points = {{-67, 440}, {-43, 440}, {-43, 398}, {-19, 398}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_pe_stage1.y, ilqr_0_iter5_pe.u1) 
    annotation(Line(points = {{7, 398}, {11, 398}, {11, 376}, {15, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_half_h2_acc.y, ilqr_0_iter5_pe.u2) 
    annotation(Line(points = {{-67, 400}, {-26, 400}, {-26, 376}, {15, 376}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_h_acc.u) 
    annotation(Line(points = {{56, 318}, {-5.5, 318}, {-5.5, 360}, {-67, 360}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, ilqr_0_iter5_ve.u1) 
    annotation(Line(points = {{-733, 263}, {-376, 263}, {-376, 338}, {-19, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_h_acc.y, ilqr_0_iter5_ve.u2) 
    annotation(Line(points = {{-67, 360}, {-43, 360}, {-43, 338}, {-19, 338}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_pe.y, ilqr_0_iter5_gp.u) 
    annotation(Line(points = {{28, 386}, {28, 398}, {0, 398}, {0, 410}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_ve.y, ilqr_0_iter5_gv.u) 
    annotation(Line(points = {{-6, 348}, {-6, 359}, {0, 359}, {0, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_ga.u) 
    annotation(Line(points = {{56, 318}, {34.5, 318}, {34.5, 340}, {13, 340}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_gp.y, ilqr_0_iter5_gradient_stage1.u1) 
    annotation(Line(points = {{13, 420}, {37, 420}, {37, 358}, {61, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_gv.y, ilqr_0_iter5_gradient_stage1.u2) 
    annotation(Line(points = {{13, 380}, {37, 380}, {37, 358}, {61, 358}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_gradient_stage1.y, ilqr_0_iter5_gradient.u1) 
    annotation(Line(points = {{87, 358}, {91, 358}, {91, 336}, {95, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_ga.y, ilqr_0_iter5_gradient.u2) 
    annotation(Line(points = {{13, 340}, {54, 340}, {54, 336}, {95, 336}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_gradient.y, ilqr_0_iter5_newton_step.u) 
    annotation(Line(points = {{108, 346}, {108, 358}, {80, 358}, {80, 370}}, color = {0, 0, 127}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_update.u1) 
    annotation(Line(points = {{82, 318}, {141, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_newton_step.y, ilqr_0_iter5_update.u2) 
    annotation(Line(points = {{93, 380}, {117, 380}, {117, 318}, {141, 318}}, color = {0, 0, 127}));
  connect(ilqr_0_iter5_update.y, unconstrained_command_x.u1) 
    annotation(Line(points = {{167, 318}, {1006, 318}}, color = {0, 0, 127}));
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
  connect(velocity_error_x.y, final_ilqr_x_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {119.5, 263}, {119.5, 240}, {972, 240}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_ilqr_x_half_h2_acc.u) 
    annotation(Line(points = {{1312, 340}, {1155, 340}, {1155, 195}, {998, 195}}, color = {0, 0, 127}));
  connect(position_error_x.y, final_ilqr_x_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {179, 373}, {179, 208}, {1091, 208}}, color = {0, 0, 127}));
  connect(final_ilqr_x_h_ev.y, final_ilqr_x_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, 240}, {1044.5, 240}, {1044.5, 208}, {1091, 208}}, color = {0, 0, 127}));
  connect(final_ilqr_x_predicted_position_error_stage1.y, final_ilqr_x_predicted_position_error.u1) 
    annotation(Line(points = {{1117, 208}, {1121, 208}, {1121, 186}, {1125, 186}}, color = {0, 0, 127}));
  connect(final_ilqr_x_half_h2_acc.y, final_ilqr_x_predicted_position_error.u2) 
    annotation(Line(points = {{998, 195}, {1061.5, 195}, {1061.5, 186}, {1125, 186}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_ilqr_x_h_acc.u) 
    annotation(Line(points = {{1312, 340}, {1155, 340}, {1155, 140}, {998, 140}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, final_ilqr_x_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {179, 263}, {179, 118}, {1091, 118}}, color = {0, 0, 127}));
  connect(final_ilqr_x_h_acc.y, final_ilqr_x_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, 140}, {1044.5, 140}, {1044.5, 118}, {1091, 118}}, color = {0, 0, 127}));
  connect(final_ilqr_x_predicted_position_error.y, final_ilqr_x_position_error_squared.u1) 
    annotation(Line(points = {{1138, 196}, {1138, 208}, {1155, 208}, {1155, 220}}, color = {0, 0, 127}));
  connect(final_ilqr_x_predicted_position_error.y, final_ilqr_x_position_error_squared.u2) 
    annotation(Line(points = {{1138, 196}, {1138, 208}, {1155, 208}, {1155, 220}}, color = {0, 0, 127}));
  connect(final_ilqr_x_predicted_velocity_error.y, final_ilqr_x_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, 128}, {1104, 146.5}, {1155, 146.5}, {1155, 165}}, color = {0, 0, 127}));
  connect(final_ilqr_x_predicted_velocity_error.y, final_ilqr_x_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, 128}, {1104, 146.5}, {1155, 146.5}, {1155, 165}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_ilqr_x_acceleration_squared.u1) 
    annotation(Line(points = {{1325, 330}, {1325, 230}, {1155, 230}, {1155, 130}}, color = {0, 0, 127}));
  connect(increment_upper_clip_x.y, final_ilqr_x_acceleration_squared.u2) 
    annotation(Line(points = {{1325, 330}, {1325, 230}, {1155, 230}, {1155, 130}}, color = {0, 0, 127}));
  connect(final_ilqr_x_position_error_squared.y, final_ilqr_x_position_cost.u) 
    annotation(Line(points = {{1168, 230}, {1227, 230}}, color = {0, 0, 127}));
  connect(final_ilqr_x_velocity_error_squared.y, final_ilqr_x_velocity_cost.u) 
    annotation(Line(points = {{1168, 175}, {1227, 175}}, color = {0, 0, 127}));
  connect(final_ilqr_x_acceleration_squared.y, final_ilqr_x_control_cost.u) 
    annotation(Line(points = {{1168, 120}, {1227, 120}}, color = {0, 0, 127}));
  connect(final_ilqr_x_position_cost.y, final_ilqr_x_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, 230}, {1299.5, 230}, {1299.5, 153}, {1346, 153}}, color = {0, 0, 127}));
  connect(final_ilqr_x_velocity_cost.y, final_ilqr_x_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, 175}, {1299.5, 175}, {1299.5, 153}, {1346, 153}}, color = {0, 0, 127}));
  connect(final_ilqr_x_stage_cost_stage1.y, final_ilqr_x_stage_cost.u1) 
    annotation(Line(points = {{1372, 153}, {1376, 153}, {1376, 131}, {1380, 131}}, color = {0, 0, 127}));
  connect(final_ilqr_x_control_cost.y, final_ilqr_x_stage_cost.u2) 
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
  connect(velocity_error_y.y, ilqr_1_iter1_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-583, -167}, {-583, 10}, {-433, 10}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, ilqr_1_iter1_half_h2_acc.u) 
    annotation(Line(points = {{-519, -134}, {-476, -134}, {-476, -30}, {-433, -30}}, color = {0, 0, 127}));
  connect(position_error_y.y, ilqr_1_iter1_pe_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-546, -57}, {-546, -32}, {-359, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_h_ev.y, ilqr_1_iter1_pe_stage1.u2) 
    annotation(Line(points = {{-407, 10}, {-383, 10}, {-383, -32}, {-359, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_pe_stage1.y, ilqr_1_iter1_pe.u1) 
    annotation(Line(points = {{-333, -32}, {-329, -32}, {-329, -54}, {-325, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_half_h2_acc.y, ilqr_1_iter1_pe.u2) 
    annotation(Line(points = {{-407, -30}, {-366, -30}, {-366, -54}, {-325, -54}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, ilqr_1_iter1_h_acc.u) 
    annotation(Line(points = {{-519, -134}, {-476, -134}, {-476, -70}, {-433, -70}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter1_ve.u1) 
    annotation(Line(points = {{-733, -167}, {-546, -167}, {-546, -92}, {-359, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_h_acc.y, ilqr_1_iter1_ve.u2) 
    annotation(Line(points = {{-407, -70}, {-383, -70}, {-383, -92}, {-359, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_pe.y, ilqr_1_iter1_gp.u) 
    annotation(Line(points = {{-312, -44}, {-312, -32}, {-340, -32}, {-340, -20}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_ve.y, ilqr_1_iter1_gv.u) 
    annotation(Line(points = {{-346, -82}, {-346, -71}, {-340, -71}, {-340, -60}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, ilqr_1_iter1_ga.u) 
    annotation(Line(points = {{-519, -134}, {-436, -134}, {-436, -90}, {-353, -90}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_gp.y, ilqr_1_iter1_gradient_stage1.u1) 
    annotation(Line(points = {{-327, -10}, {-303, -10}, {-303, -72}, {-279, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_gv.y, ilqr_1_iter1_gradient_stage1.u2) 
    annotation(Line(points = {{-327, -50}, {-303, -50}, {-303, -72}, {-279, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_gradient_stage1.y, ilqr_1_iter1_gradient.u1) 
    annotation(Line(points = {{-253, -72}, {-249, -72}, {-249, -94}, {-245, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_ga.y, ilqr_1_iter1_gradient.u2) 
    annotation(Line(points = {{-327, -90}, {-286, -90}, {-286, -94}, {-245, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_gradient.y, ilqr_1_iter1_newton_step.u) 
    annotation(Line(points = {{-232, -84}, {-232, -72}, {-260, -72}, {-260, -60}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, ilqr_1_iter1_update.u1) 
    annotation(Line(points = {{-519, -134}, {-359, -134}, {-359, -112}, {-199, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_newton_step.y, ilqr_1_iter1_update.u2) 
    annotation(Line(points = {{-247, -50}, {-223, -50}, {-223, -112}, {-199, -112}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter2_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-540.5, -167}, {-540.5, 10}, {-348, 10}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_half_h2_acc.u) 
    annotation(Line(points = {{-199, -112}, {-260.5, -112}, {-260.5, -30}, {-322, -30}}, color = {0, 0, 127}));
  connect(position_error_y.y, ilqr_1_iter2_pe_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-503.5, -57}, {-503.5, -32}, {-274, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_h_ev.y, ilqr_1_iter2_pe_stage1.u2) 
    annotation(Line(points = {{-322, 10}, {-298, 10}, {-298, -32}, {-274, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_pe_stage1.y, ilqr_1_iter2_pe.u1) 
    annotation(Line(points = {{-248, -32}, {-244, -32}, {-244, -54}, {-240, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_half_h2_acc.y, ilqr_1_iter2_pe.u2) 
    annotation(Line(points = {{-322, -30}, {-281, -30}, {-281, -54}, {-240, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_h_acc.u) 
    annotation(Line(points = {{-199, -112}, {-260.5, -112}, {-260.5, -70}, {-322, -70}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter2_ve.u1) 
    annotation(Line(points = {{-733, -167}, {-503.5, -167}, {-503.5, -92}, {-274, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_h_acc.y, ilqr_1_iter2_ve.u2) 
    annotation(Line(points = {{-322, -70}, {-298, -70}, {-298, -92}, {-274, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_pe.y, ilqr_1_iter2_gp.u) 
    annotation(Line(points = {{-227, -44}, {-227, -32}, {-255, -32}, {-255, -20}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_ve.y, ilqr_1_iter2_gv.u) 
    annotation(Line(points = {{-261, -82}, {-261, -71}, {-255, -71}, {-255, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_ga.u) 
    annotation(Line(points = {{-199, -112}, {-220.5, -112}, {-220.5, -90}, {-242, -90}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_gp.y, ilqr_1_iter2_gradient_stage1.u1) 
    annotation(Line(points = {{-242, -10}, {-218, -10}, {-218, -72}, {-194, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_gv.y, ilqr_1_iter2_gradient_stage1.u2) 
    annotation(Line(points = {{-242, -50}, {-218, -50}, {-218, -72}, {-194, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_gradient_stage1.y, ilqr_1_iter2_gradient.u1) 
    annotation(Line(points = {{-168, -72}, {-164, -72}, {-164, -94}, {-160, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_ga.y, ilqr_1_iter2_gradient.u2) 
    annotation(Line(points = {{-242, -90}, {-201, -90}, {-201, -94}, {-160, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_gradient.y, ilqr_1_iter2_newton_step.u) 
    annotation(Line(points = {{-147, -84}, {-147, -72}, {-175, -72}, {-175, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_update.u1) 
    annotation(Line(points = {{-173, -112}, {-114, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_newton_step.y, ilqr_1_iter2_update.u2) 
    annotation(Line(points = {{-162, -50}, {-138, -50}, {-138, -112}, {-114, -112}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter3_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-498, -167}, {-498, 10}, {-263, 10}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_half_h2_acc.u) 
    annotation(Line(points = {{-114, -112}, {-175.5, -112}, {-175.5, -30}, {-237, -30}}, color = {0, 0, 127}));
  connect(position_error_y.y, ilqr_1_iter3_pe_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-461, -57}, {-461, -32}, {-189, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_h_ev.y, ilqr_1_iter3_pe_stage1.u2) 
    annotation(Line(points = {{-237, 10}, {-213, 10}, {-213, -32}, {-189, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_pe_stage1.y, ilqr_1_iter3_pe.u1) 
    annotation(Line(points = {{-163, -32}, {-159, -32}, {-159, -54}, {-155, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_half_h2_acc.y, ilqr_1_iter3_pe.u2) 
    annotation(Line(points = {{-237, -30}, {-196, -30}, {-196, -54}, {-155, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_h_acc.u) 
    annotation(Line(points = {{-114, -112}, {-175.5, -112}, {-175.5, -70}, {-237, -70}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter3_ve.u1) 
    annotation(Line(points = {{-733, -167}, {-461, -167}, {-461, -92}, {-189, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_h_acc.y, ilqr_1_iter3_ve.u2) 
    annotation(Line(points = {{-237, -70}, {-213, -70}, {-213, -92}, {-189, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_pe.y, ilqr_1_iter3_gp.u) 
    annotation(Line(points = {{-142, -44}, {-142, -32}, {-170, -32}, {-170, -20}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_ve.y, ilqr_1_iter3_gv.u) 
    annotation(Line(points = {{-176, -82}, {-176, -71}, {-170, -71}, {-170, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_ga.u) 
    annotation(Line(points = {{-114, -112}, {-135.5, -112}, {-135.5, -90}, {-157, -90}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_gp.y, ilqr_1_iter3_gradient_stage1.u1) 
    annotation(Line(points = {{-157, -10}, {-133, -10}, {-133, -72}, {-109, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_gv.y, ilqr_1_iter3_gradient_stage1.u2) 
    annotation(Line(points = {{-157, -50}, {-133, -50}, {-133, -72}, {-109, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_gradient_stage1.y, ilqr_1_iter3_gradient.u1) 
    annotation(Line(points = {{-83, -72}, {-79, -72}, {-79, -94}, {-75, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_ga.y, ilqr_1_iter3_gradient.u2) 
    annotation(Line(points = {{-157, -90}, {-116, -90}, {-116, -94}, {-75, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_gradient.y, ilqr_1_iter3_newton_step.u) 
    annotation(Line(points = {{-62, -84}, {-62, -72}, {-90, -72}, {-90, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_update.u1) 
    annotation(Line(points = {{-88, -112}, {-29, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_newton_step.y, ilqr_1_iter3_update.u2) 
    annotation(Line(points = {{-77, -50}, {-53, -50}, {-53, -112}, {-29, -112}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter4_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-455.5, -167}, {-455.5, 10}, {-178, 10}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_half_h2_acc.u) 
    annotation(Line(points = {{-29, -112}, {-90.5, -112}, {-90.5, -30}, {-152, -30}}, color = {0, 0, 127}));
  connect(position_error_y.y, ilqr_1_iter4_pe_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-418.5, -57}, {-418.5, -32}, {-104, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_h_ev.y, ilqr_1_iter4_pe_stage1.u2) 
    annotation(Line(points = {{-152, 10}, {-128, 10}, {-128, -32}, {-104, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_pe_stage1.y, ilqr_1_iter4_pe.u1) 
    annotation(Line(points = {{-78, -32}, {-74, -32}, {-74, -54}, {-70, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_half_h2_acc.y, ilqr_1_iter4_pe.u2) 
    annotation(Line(points = {{-152, -30}, {-111, -30}, {-111, -54}, {-70, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_h_acc.u) 
    annotation(Line(points = {{-29, -112}, {-90.5, -112}, {-90.5, -70}, {-152, -70}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter4_ve.u1) 
    annotation(Line(points = {{-733, -167}, {-418.5, -167}, {-418.5, -92}, {-104, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_h_acc.y, ilqr_1_iter4_ve.u2) 
    annotation(Line(points = {{-152, -70}, {-128, -70}, {-128, -92}, {-104, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_pe.y, ilqr_1_iter4_gp.u) 
    annotation(Line(points = {{-57, -44}, {-57, -32}, {-85, -32}, {-85, -20}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_ve.y, ilqr_1_iter4_gv.u) 
    annotation(Line(points = {{-91, -82}, {-91, -71}, {-85, -71}, {-85, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_ga.u) 
    annotation(Line(points = {{-29, -112}, {-50.5, -112}, {-50.5, -90}, {-72, -90}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_gp.y, ilqr_1_iter4_gradient_stage1.u1) 
    annotation(Line(points = {{-72, -10}, {-48, -10}, {-48, -72}, {-24, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_gv.y, ilqr_1_iter4_gradient_stage1.u2) 
    annotation(Line(points = {{-72, -50}, {-48, -50}, {-48, -72}, {-24, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_gradient_stage1.y, ilqr_1_iter4_gradient.u1) 
    annotation(Line(points = {{2, -72}, {6, -72}, {6, -94}, {10, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_ga.y, ilqr_1_iter4_gradient.u2) 
    annotation(Line(points = {{-72, -90}, {-31, -90}, {-31, -94}, {10, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_gradient.y, ilqr_1_iter4_newton_step.u) 
    annotation(Line(points = {{23, -84}, {23, -72}, {-5, -72}, {-5, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_update.u1) 
    annotation(Line(points = {{-3, -112}, {56, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_newton_step.y, ilqr_1_iter4_update.u2) 
    annotation(Line(points = {{8, -50}, {32, -50}, {32, -112}, {56, -112}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter5_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-413, -167}, {-413, 10}, {-93, 10}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_half_h2_acc.u) 
    annotation(Line(points = {{56, -112}, {-5.5, -112}, {-5.5, -30}, {-67, -30}}, color = {0, 0, 127}));
  connect(position_error_y.y, ilqr_1_iter5_pe_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-376, -57}, {-376, -32}, {-19, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_h_ev.y, ilqr_1_iter5_pe_stage1.u2) 
    annotation(Line(points = {{-67, 10}, {-43, 10}, {-43, -32}, {-19, -32}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_pe_stage1.y, ilqr_1_iter5_pe.u1) 
    annotation(Line(points = {{7, -32}, {11, -32}, {11, -54}, {15, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_half_h2_acc.y, ilqr_1_iter5_pe.u2) 
    annotation(Line(points = {{-67, -30}, {-26, -30}, {-26, -54}, {15, -54}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_h_acc.u) 
    annotation(Line(points = {{56, -112}, {-5.5, -112}, {-5.5, -70}, {-67, -70}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, ilqr_1_iter5_ve.u1) 
    annotation(Line(points = {{-733, -167}, {-376, -167}, {-376, -92}, {-19, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_h_acc.y, ilqr_1_iter5_ve.u2) 
    annotation(Line(points = {{-67, -70}, {-43, -70}, {-43, -92}, {-19, -92}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_pe.y, ilqr_1_iter5_gp.u) 
    annotation(Line(points = {{28, -44}, {28, -32}, {0, -32}, {0, -20}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_ve.y, ilqr_1_iter5_gv.u) 
    annotation(Line(points = {{-6, -82}, {-6, -71}, {0, -71}, {0, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_ga.u) 
    annotation(Line(points = {{56, -112}, {34.5, -112}, {34.5, -90}, {13, -90}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_gp.y, ilqr_1_iter5_gradient_stage1.u1) 
    annotation(Line(points = {{13, -10}, {37, -10}, {37, -72}, {61, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_gv.y, ilqr_1_iter5_gradient_stage1.u2) 
    annotation(Line(points = {{13, -50}, {37, -50}, {37, -72}, {61, -72}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_gradient_stage1.y, ilqr_1_iter5_gradient.u1) 
    annotation(Line(points = {{87, -72}, {91, -72}, {91, -94}, {95, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_ga.y, ilqr_1_iter5_gradient.u2) 
    annotation(Line(points = {{13, -90}, {54, -90}, {54, -94}, {95, -94}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_gradient.y, ilqr_1_iter5_newton_step.u) 
    annotation(Line(points = {{108, -84}, {108, -72}, {80, -72}, {80, -60}}, color = {0, 0, 127}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_update.u1) 
    annotation(Line(points = {{82, -112}, {141, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_newton_step.y, ilqr_1_iter5_update.u2) 
    annotation(Line(points = {{93, -50}, {117, -50}, {117, -112}, {141, -112}}, color = {0, 0, 127}));
  connect(ilqr_1_iter5_update.y, unconstrained_command_y.u1) 
    annotation(Line(points = {{167, -112}, {1006, -112}}, color = {0, 0, 127}));
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
  connect(velocity_error_y.y, final_ilqr_y_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {119.5, -167}, {119.5, -190}, {972, -190}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_ilqr_y_half_h2_acc.u) 
    annotation(Line(points = {{1312, -90}, {1155, -90}, {1155, -235}, {998, -235}}, color = {0, 0, 127}));
  connect(position_error_y.y, final_ilqr_y_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {179, -57}, {179, -222}, {1091, -222}}, color = {0, 0, 127}));
  connect(final_ilqr_y_h_ev.y, final_ilqr_y_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, -190}, {1044.5, -190}, {1044.5, -222}, {1091, -222}}, color = {0, 0, 127}));
  connect(final_ilqr_y_predicted_position_error_stage1.y, final_ilqr_y_predicted_position_error.u1) 
    annotation(Line(points = {{1117, -222}, {1121, -222}, {1121, -244}, {1125, -244}}, color = {0, 0, 127}));
  connect(final_ilqr_y_half_h2_acc.y, final_ilqr_y_predicted_position_error.u2) 
    annotation(Line(points = {{998, -235}, {1061.5, -235}, {1061.5, -244}, {1125, -244}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_ilqr_y_h_acc.u) 
    annotation(Line(points = {{1312, -90}, {1155, -90}, {1155, -290}, {998, -290}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, final_ilqr_y_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {179, -167}, {179, -312}, {1091, -312}}, color = {0, 0, 127}));
  connect(final_ilqr_y_h_acc.y, final_ilqr_y_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, -290}, {1044.5, -290}, {1044.5, -312}, {1091, -312}}, color = {0, 0, 127}));
  connect(final_ilqr_y_predicted_position_error.y, final_ilqr_y_position_error_squared.u1) 
    annotation(Line(points = {{1138, -234}, {1138, -222}, {1155, -222}, {1155, -210}}, color = {0, 0, 127}));
  connect(final_ilqr_y_predicted_position_error.y, final_ilqr_y_position_error_squared.u2) 
    annotation(Line(points = {{1138, -234}, {1138, -222}, {1155, -222}, {1155, -210}}, color = {0, 0, 127}));
  connect(final_ilqr_y_predicted_velocity_error.y, final_ilqr_y_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, -302}, {1104, -283.5}, {1155, -283.5}, {1155, -265}}, color = {0, 0, 127}));
  connect(final_ilqr_y_predicted_velocity_error.y, final_ilqr_y_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, -302}, {1104, -283.5}, {1155, -283.5}, {1155, -265}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_ilqr_y_acceleration_squared.u1) 
    annotation(Line(points = {{1325, -100}, {1325, -200}, {1155, -200}, {1155, -300}}, color = {0, 0, 127}));
  connect(increment_upper_clip_y.y, final_ilqr_y_acceleration_squared.u2) 
    annotation(Line(points = {{1325, -100}, {1325, -200}, {1155, -200}, {1155, -300}}, color = {0, 0, 127}));
  connect(final_ilqr_y_position_error_squared.y, final_ilqr_y_position_cost.u) 
    annotation(Line(points = {{1168, -200}, {1227, -200}}, color = {0, 0, 127}));
  connect(final_ilqr_y_velocity_error_squared.y, final_ilqr_y_velocity_cost.u) 
    annotation(Line(points = {{1168, -255}, {1227, -255}}, color = {0, 0, 127}));
  connect(final_ilqr_y_acceleration_squared.y, final_ilqr_y_control_cost.u) 
    annotation(Line(points = {{1168, -310}, {1227, -310}}, color = {0, 0, 127}));
  connect(final_ilqr_y_position_cost.y, final_ilqr_y_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, -200}, {1299.5, -200}, {1299.5, -277}, {1346, -277}}, color = {0, 0, 127}));
  connect(final_ilqr_y_velocity_cost.y, final_ilqr_y_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, -255}, {1299.5, -255}, {1299.5, -277}, {1346, -277}}, color = {0, 0, 127}));
  connect(final_ilqr_y_stage_cost_stage1.y, final_ilqr_y_stage_cost.u1) 
    annotation(Line(points = {{1372, -277}, {1376, -277}, {1376, -299}, {1380, -299}}, color = {0, 0, 127}));
  connect(final_ilqr_y_control_cost.y, final_ilqr_y_stage_cost.u2) 
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
  connect(velocity_error_z.y, ilqr_2_iter1_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-583, -597}, {-583, -420}, {-433, -420}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, ilqr_2_iter1_half_h2_acc.u) 
    annotation(Line(points = {{-519, -564}, {-476, -564}, {-476, -460}, {-433, -460}}, color = {0, 0, 127}));
  connect(position_error_z.y, ilqr_2_iter1_pe_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-546, -487}, {-546, -462}, {-359, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_h_ev.y, ilqr_2_iter1_pe_stage1.u2) 
    annotation(Line(points = {{-407, -420}, {-383, -420}, {-383, -462}, {-359, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_pe_stage1.y, ilqr_2_iter1_pe.u1) 
    annotation(Line(points = {{-333, -462}, {-329, -462}, {-329, -484}, {-325, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_half_h2_acc.y, ilqr_2_iter1_pe.u2) 
    annotation(Line(points = {{-407, -460}, {-366, -460}, {-366, -484}, {-325, -484}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, ilqr_2_iter1_h_acc.u) 
    annotation(Line(points = {{-519, -564}, {-476, -564}, {-476, -500}, {-433, -500}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter1_ve.u1) 
    annotation(Line(points = {{-733, -597}, {-546, -597}, {-546, -522}, {-359, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_h_acc.y, ilqr_2_iter1_ve.u2) 
    annotation(Line(points = {{-407, -500}, {-383, -500}, {-383, -522}, {-359, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_pe.y, ilqr_2_iter1_gp.u) 
    annotation(Line(points = {{-312, -474}, {-312, -462}, {-340, -462}, {-340, -450}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_ve.y, ilqr_2_iter1_gv.u) 
    annotation(Line(points = {{-346, -512}, {-346, -501}, {-340, -501}, {-340, -490}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, ilqr_2_iter1_ga.u) 
    annotation(Line(points = {{-519, -564}, {-436, -564}, {-436, -520}, {-353, -520}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_gp.y, ilqr_2_iter1_gradient_stage1.u1) 
    annotation(Line(points = {{-327, -440}, {-303, -440}, {-303, -502}, {-279, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_gv.y, ilqr_2_iter1_gradient_stage1.u2) 
    annotation(Line(points = {{-327, -480}, {-303, -480}, {-303, -502}, {-279, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_gradient_stage1.y, ilqr_2_iter1_gradient.u1) 
    annotation(Line(points = {{-253, -502}, {-249, -502}, {-249, -524}, {-245, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_ga.y, ilqr_2_iter1_gradient.u2) 
    annotation(Line(points = {{-327, -520}, {-286, -520}, {-286, -524}, {-245, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_gradient.y, ilqr_2_iter1_newton_step.u) 
    annotation(Line(points = {{-232, -514}, {-232, -502}, {-260, -502}, {-260, -490}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, ilqr_2_iter1_update.u1) 
    annotation(Line(points = {{-519, -564}, {-359, -564}, {-359, -542}, {-199, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_newton_step.y, ilqr_2_iter1_update.u2) 
    annotation(Line(points = {{-247, -480}, {-223, -480}, {-223, -542}, {-199, -542}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter2_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-540.5, -597}, {-540.5, -420}, {-348, -420}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_half_h2_acc.u) 
    annotation(Line(points = {{-199, -542}, {-260.5, -542}, {-260.5, -460}, {-322, -460}}, color = {0, 0, 127}));
  connect(position_error_z.y, ilqr_2_iter2_pe_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-503.5, -487}, {-503.5, -462}, {-274, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_h_ev.y, ilqr_2_iter2_pe_stage1.u2) 
    annotation(Line(points = {{-322, -420}, {-298, -420}, {-298, -462}, {-274, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_pe_stage1.y, ilqr_2_iter2_pe.u1) 
    annotation(Line(points = {{-248, -462}, {-244, -462}, {-244, -484}, {-240, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_half_h2_acc.y, ilqr_2_iter2_pe.u2) 
    annotation(Line(points = {{-322, -460}, {-281, -460}, {-281, -484}, {-240, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_h_acc.u) 
    annotation(Line(points = {{-199, -542}, {-260.5, -542}, {-260.5, -500}, {-322, -500}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter2_ve.u1) 
    annotation(Line(points = {{-733, -597}, {-503.5, -597}, {-503.5, -522}, {-274, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_h_acc.y, ilqr_2_iter2_ve.u2) 
    annotation(Line(points = {{-322, -500}, {-298, -500}, {-298, -522}, {-274, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_pe.y, ilqr_2_iter2_gp.u) 
    annotation(Line(points = {{-227, -474}, {-227, -462}, {-255, -462}, {-255, -450}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_ve.y, ilqr_2_iter2_gv.u) 
    annotation(Line(points = {{-261, -512}, {-261, -501}, {-255, -501}, {-255, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_ga.u) 
    annotation(Line(points = {{-199, -542}, {-220.5, -542}, {-220.5, -520}, {-242, -520}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_gp.y, ilqr_2_iter2_gradient_stage1.u1) 
    annotation(Line(points = {{-242, -440}, {-218, -440}, {-218, -502}, {-194, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_gv.y, ilqr_2_iter2_gradient_stage1.u2) 
    annotation(Line(points = {{-242, -480}, {-218, -480}, {-218, -502}, {-194, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_gradient_stage1.y, ilqr_2_iter2_gradient.u1) 
    annotation(Line(points = {{-168, -502}, {-164, -502}, {-164, -524}, {-160, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_ga.y, ilqr_2_iter2_gradient.u2) 
    annotation(Line(points = {{-242, -520}, {-201, -520}, {-201, -524}, {-160, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_gradient.y, ilqr_2_iter2_newton_step.u) 
    annotation(Line(points = {{-147, -514}, {-147, -502}, {-175, -502}, {-175, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_update.u1) 
    annotation(Line(points = {{-173, -542}, {-114, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_newton_step.y, ilqr_2_iter2_update.u2) 
    annotation(Line(points = {{-162, -480}, {-138, -480}, {-138, -542}, {-114, -542}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter3_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-498, -597}, {-498, -420}, {-263, -420}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_half_h2_acc.u) 
    annotation(Line(points = {{-114, -542}, {-175.5, -542}, {-175.5, -460}, {-237, -460}}, color = {0, 0, 127}));
  connect(position_error_z.y, ilqr_2_iter3_pe_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-461, -487}, {-461, -462}, {-189, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_h_ev.y, ilqr_2_iter3_pe_stage1.u2) 
    annotation(Line(points = {{-237, -420}, {-213, -420}, {-213, -462}, {-189, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_pe_stage1.y, ilqr_2_iter3_pe.u1) 
    annotation(Line(points = {{-163, -462}, {-159, -462}, {-159, -484}, {-155, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_half_h2_acc.y, ilqr_2_iter3_pe.u2) 
    annotation(Line(points = {{-237, -460}, {-196, -460}, {-196, -484}, {-155, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_h_acc.u) 
    annotation(Line(points = {{-114, -542}, {-175.5, -542}, {-175.5, -500}, {-237, -500}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter3_ve.u1) 
    annotation(Line(points = {{-733, -597}, {-461, -597}, {-461, -522}, {-189, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_h_acc.y, ilqr_2_iter3_ve.u2) 
    annotation(Line(points = {{-237, -500}, {-213, -500}, {-213, -522}, {-189, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_pe.y, ilqr_2_iter3_gp.u) 
    annotation(Line(points = {{-142, -474}, {-142, -462}, {-170, -462}, {-170, -450}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_ve.y, ilqr_2_iter3_gv.u) 
    annotation(Line(points = {{-176, -512}, {-176, -501}, {-170, -501}, {-170, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_ga.u) 
    annotation(Line(points = {{-114, -542}, {-135.5, -542}, {-135.5, -520}, {-157, -520}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_gp.y, ilqr_2_iter3_gradient_stage1.u1) 
    annotation(Line(points = {{-157, -440}, {-133, -440}, {-133, -502}, {-109, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_gv.y, ilqr_2_iter3_gradient_stage1.u2) 
    annotation(Line(points = {{-157, -480}, {-133, -480}, {-133, -502}, {-109, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_gradient_stage1.y, ilqr_2_iter3_gradient.u1) 
    annotation(Line(points = {{-83, -502}, {-79, -502}, {-79, -524}, {-75, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_ga.y, ilqr_2_iter3_gradient.u2) 
    annotation(Line(points = {{-157, -520}, {-116, -520}, {-116, -524}, {-75, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_gradient.y, ilqr_2_iter3_newton_step.u) 
    annotation(Line(points = {{-62, -514}, {-62, -502}, {-90, -502}, {-90, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_update.u1) 
    annotation(Line(points = {{-88, -542}, {-29, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_newton_step.y, ilqr_2_iter3_update.u2) 
    annotation(Line(points = {{-77, -480}, {-53, -480}, {-53, -542}, {-29, -542}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter4_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-455.5, -597}, {-455.5, -420}, {-178, -420}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_half_h2_acc.u) 
    annotation(Line(points = {{-29, -542}, {-90.5, -542}, {-90.5, -460}, {-152, -460}}, color = {0, 0, 127}));
  connect(position_error_z.y, ilqr_2_iter4_pe_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-418.5, -487}, {-418.5, -462}, {-104, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_h_ev.y, ilqr_2_iter4_pe_stage1.u2) 
    annotation(Line(points = {{-152, -420}, {-128, -420}, {-128, -462}, {-104, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_pe_stage1.y, ilqr_2_iter4_pe.u1) 
    annotation(Line(points = {{-78, -462}, {-74, -462}, {-74, -484}, {-70, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_half_h2_acc.y, ilqr_2_iter4_pe.u2) 
    annotation(Line(points = {{-152, -460}, {-111, -460}, {-111, -484}, {-70, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_h_acc.u) 
    annotation(Line(points = {{-29, -542}, {-90.5, -542}, {-90.5, -500}, {-152, -500}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter4_ve.u1) 
    annotation(Line(points = {{-733, -597}, {-418.5, -597}, {-418.5, -522}, {-104, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_h_acc.y, ilqr_2_iter4_ve.u2) 
    annotation(Line(points = {{-152, -500}, {-128, -500}, {-128, -522}, {-104, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_pe.y, ilqr_2_iter4_gp.u) 
    annotation(Line(points = {{-57, -474}, {-57, -462}, {-85, -462}, {-85, -450}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_ve.y, ilqr_2_iter4_gv.u) 
    annotation(Line(points = {{-91, -512}, {-91, -501}, {-85, -501}, {-85, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_ga.u) 
    annotation(Line(points = {{-29, -542}, {-50.5, -542}, {-50.5, -520}, {-72, -520}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_gp.y, ilqr_2_iter4_gradient_stage1.u1) 
    annotation(Line(points = {{-72, -440}, {-48, -440}, {-48, -502}, {-24, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_gv.y, ilqr_2_iter4_gradient_stage1.u2) 
    annotation(Line(points = {{-72, -480}, {-48, -480}, {-48, -502}, {-24, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_gradient_stage1.y, ilqr_2_iter4_gradient.u1) 
    annotation(Line(points = {{2, -502}, {6, -502}, {6, -524}, {10, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_ga.y, ilqr_2_iter4_gradient.u2) 
    annotation(Line(points = {{-72, -520}, {-31, -520}, {-31, -524}, {10, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_gradient.y, ilqr_2_iter4_newton_step.u) 
    annotation(Line(points = {{23, -514}, {23, -502}, {-5, -502}, {-5, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_update.u1) 
    annotation(Line(points = {{-3, -542}, {56, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_newton_step.y, ilqr_2_iter4_update.u2) 
    annotation(Line(points = {{8, -480}, {32, -480}, {32, -542}, {56, -542}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter5_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-413, -597}, {-413, -420}, {-93, -420}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_half_h2_acc.u) 
    annotation(Line(points = {{56, -542}, {-5.5, -542}, {-5.5, -460}, {-67, -460}}, color = {0, 0, 127}));
  connect(position_error_z.y, ilqr_2_iter5_pe_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-376, -487}, {-376, -462}, {-19, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_h_ev.y, ilqr_2_iter5_pe_stage1.u2) 
    annotation(Line(points = {{-67, -420}, {-43, -420}, {-43, -462}, {-19, -462}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_pe_stage1.y, ilqr_2_iter5_pe.u1) 
    annotation(Line(points = {{7, -462}, {11, -462}, {11, -484}, {15, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_half_h2_acc.y, ilqr_2_iter5_pe.u2) 
    annotation(Line(points = {{-67, -460}, {-26, -460}, {-26, -484}, {15, -484}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_h_acc.u) 
    annotation(Line(points = {{56, -542}, {-5.5, -542}, {-5.5, -500}, {-67, -500}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, ilqr_2_iter5_ve.u1) 
    annotation(Line(points = {{-733, -597}, {-376, -597}, {-376, -522}, {-19, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_h_acc.y, ilqr_2_iter5_ve.u2) 
    annotation(Line(points = {{-67, -500}, {-43, -500}, {-43, -522}, {-19, -522}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_pe.y, ilqr_2_iter5_gp.u) 
    annotation(Line(points = {{28, -474}, {28, -462}, {0, -462}, {0, -450}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_ve.y, ilqr_2_iter5_gv.u) 
    annotation(Line(points = {{-6, -512}, {-6, -501}, {0, -501}, {0, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_ga.u) 
    annotation(Line(points = {{56, -542}, {34.5, -542}, {34.5, -520}, {13, -520}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_gp.y, ilqr_2_iter5_gradient_stage1.u1) 
    annotation(Line(points = {{13, -440}, {37, -440}, {37, -502}, {61, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_gv.y, ilqr_2_iter5_gradient_stage1.u2) 
    annotation(Line(points = {{13, -480}, {37, -480}, {37, -502}, {61, -502}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_gradient_stage1.y, ilqr_2_iter5_gradient.u1) 
    annotation(Line(points = {{87, -502}, {91, -502}, {91, -524}, {95, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_ga.y, ilqr_2_iter5_gradient.u2) 
    annotation(Line(points = {{13, -520}, {54, -520}, {54, -524}, {95, -524}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_gradient.y, ilqr_2_iter5_newton_step.u) 
    annotation(Line(points = {{108, -514}, {108, -502}, {80, -502}, {80, -490}}, color = {0, 0, 127}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_update.u1) 
    annotation(Line(points = {{82, -542}, {141, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_newton_step.y, ilqr_2_iter5_update.u2) 
    annotation(Line(points = {{93, -480}, {117, -480}, {117, -542}, {141, -542}}, color = {0, 0, 127}));
  connect(ilqr_2_iter5_update.y, unconstrained_command_z.u1) 
    annotation(Line(points = {{167, -542}, {1006, -542}}, color = {0, 0, 127}));
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
  connect(velocity_error_z.y, final_ilqr_z_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {119.5, -597}, {119.5, -620}, {972, -620}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_ilqr_z_half_h2_acc.u) 
    annotation(Line(points = {{1312, -520}, {1155, -520}, {1155, -665}, {998, -665}}, color = {0, 0, 127}));
  connect(position_error_z.y, final_ilqr_z_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {179, -487}, {179, -652}, {1091, -652}}, color = {0, 0, 127}));
  connect(final_ilqr_z_h_ev.y, final_ilqr_z_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{998, -620}, {1044.5, -620}, {1044.5, -652}, {1091, -652}}, color = {0, 0, 127}));
  connect(final_ilqr_z_predicted_position_error_stage1.y, final_ilqr_z_predicted_position_error.u1) 
    annotation(Line(points = {{1117, -652}, {1121, -652}, {1121, -674}, {1125, -674}}, color = {0, 0, 127}));
  connect(final_ilqr_z_half_h2_acc.y, final_ilqr_z_predicted_position_error.u2) 
    annotation(Line(points = {{998, -665}, {1061.5, -665}, {1061.5, -674}, {1125, -674}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_ilqr_z_h_acc.u) 
    annotation(Line(points = {{1312, -520}, {1155, -520}, {1155, -720}, {998, -720}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, final_ilqr_z_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {179, -597}, {179, -742}, {1091, -742}}, color = {0, 0, 127}));
  connect(final_ilqr_z_h_acc.y, final_ilqr_z_predicted_velocity_error.u2) 
    annotation(Line(points = {{998, -720}, {1044.5, -720}, {1044.5, -742}, {1091, -742}}, color = {0, 0, 127}));
  connect(final_ilqr_z_predicted_position_error.y, final_ilqr_z_position_error_squared.u1) 
    annotation(Line(points = {{1138, -664}, {1138, -652}, {1155, -652}, {1155, -640}}, color = {0, 0, 127}));
  connect(final_ilqr_z_predicted_position_error.y, final_ilqr_z_position_error_squared.u2) 
    annotation(Line(points = {{1138, -664}, {1138, -652}, {1155, -652}, {1155, -640}}, color = {0, 0, 127}));
  connect(final_ilqr_z_predicted_velocity_error.y, final_ilqr_z_velocity_error_squared.u1) 
    annotation(Line(points = {{1104, -732}, {1104, -713.5}, {1155, -713.5}, {1155, -695}}, color = {0, 0, 127}));
  connect(final_ilqr_z_predicted_velocity_error.y, final_ilqr_z_velocity_error_squared.u2) 
    annotation(Line(points = {{1104, -732}, {1104, -713.5}, {1155, -713.5}, {1155, -695}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_ilqr_z_acceleration_squared.u1) 
    annotation(Line(points = {{1325, -530}, {1325, -630}, {1155, -630}, {1155, -730}}, color = {0, 0, 127}));
  connect(increment_upper_clip_z.y, final_ilqr_z_acceleration_squared.u2) 
    annotation(Line(points = {{1325, -530}, {1325, -630}, {1155, -630}, {1155, -730}}, color = {0, 0, 127}));
  connect(final_ilqr_z_position_error_squared.y, final_ilqr_z_position_cost.u) 
    annotation(Line(points = {{1168, -630}, {1227, -630}}, color = {0, 0, 127}));
  connect(final_ilqr_z_velocity_error_squared.y, final_ilqr_z_velocity_cost.u) 
    annotation(Line(points = {{1168, -685}, {1227, -685}}, color = {0, 0, 127}));
  connect(final_ilqr_z_acceleration_squared.y, final_ilqr_z_control_cost.u) 
    annotation(Line(points = {{1168, -740}, {1227, -740}}, color = {0, 0, 127}));
  connect(final_ilqr_z_position_cost.y, final_ilqr_z_stage_cost_stage1.u1) 
    annotation(Line(points = {{1253, -630}, {1299.5, -630}, {1299.5, -707}, {1346, -707}}, color = {0, 0, 127}));
  connect(final_ilqr_z_velocity_cost.y, final_ilqr_z_stage_cost_stage1.u2) 
    annotation(Line(points = {{1253, -685}, {1299.5, -685}, {1299.5, -707}, {1346, -707}}, color = {0, 0, 127}));
  connect(final_ilqr_z_stage_cost_stage1.y, final_ilqr_z_stage_cost.u1) 
    annotation(Line(points = {{1372, -707}, {1376, -707}, {1376, -729}, {1380, -729}}, color = {0, 0, 127}));
  connect(final_ilqr_z_control_cost.y, final_ilqr_z_stage_cost.u2) 
    annotation(Line(points = {{1253, -740}, {1316.5, -740}, {1316.5, -729}, {1380, -729}}, color = {0, 0, 127}));
  connect(final_ilqr_x_stage_cost.y, solver_cost_sum_stage1.u1) 
    annotation(Line(points = {{1393, 121}, {1393, -410.5}, {1544, -410.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(final_ilqr_y_stage_cost.y, solver_cost_sum_stage1.u2) 
    annotation(Line(points = {{1393, -309}, {1393, -625.5}, {1544, -625.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1) 
    annotation(Line(points = {{1557, -952}, {1561, -952}, {1561, -974}, {1565, -974}}, color = {0, 0, 127}));
  connect(final_ilqr_z_stage_cost.y, solver_cost_sum.u2) 
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

end IlqrCore;
