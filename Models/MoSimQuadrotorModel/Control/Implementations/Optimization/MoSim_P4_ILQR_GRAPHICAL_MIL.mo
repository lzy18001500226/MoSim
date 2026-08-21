within MoSimQuadrotorModel.Control.Implementations.Optimization;

model MoSim_P4_ILQR_GRAPHICAL_MIL "P4 native graphical fixed-budget MPC controller core: ilqr"
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
  connect(velocity_error_x.y, ilqr_0_iter1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, ilqr_0_iter1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, ilqr_0_iter1_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_h_ev.y, ilqr_0_iter1_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_pe_stage1.y, ilqr_0_iter1_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_half_h2_acc.y, ilqr_0_iter1_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, ilqr_0_iter1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter1_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_h_acc.y, ilqr_0_iter1_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_pe.y, ilqr_0_iter1_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_ve.y, ilqr_0_iter1_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, ilqr_0_iter1_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_gp.y, ilqr_0_iter1_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_gv.y, ilqr_0_iter1_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_gradient_stage1.y, ilqr_0_iter1_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_ga.y, ilqr_0_iter1_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_gradient.y, ilqr_0_iter1_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, ilqr_0_iter1_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_newton_step.y, ilqr_0_iter1_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, ilqr_0_iter2_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_h_ev.y, ilqr_0_iter2_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_pe_stage1.y, ilqr_0_iter2_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_half_h2_acc.y, ilqr_0_iter2_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter2_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_h_acc.y, ilqr_0_iter2_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_pe.y, ilqr_0_iter2_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_ve.y, ilqr_0_iter2_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_gp.y, ilqr_0_iter2_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_gv.y, ilqr_0_iter2_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_gradient_stage1.y, ilqr_0_iter2_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_ga.y, ilqr_0_iter2_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_gradient.y, ilqr_0_iter2_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter1_update.y, ilqr_0_iter2_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_newton_step.y, ilqr_0_iter2_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, ilqr_0_iter3_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_h_ev.y, ilqr_0_iter3_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_pe_stage1.y, ilqr_0_iter3_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_half_h2_acc.y, ilqr_0_iter3_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter3_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_h_acc.y, ilqr_0_iter3_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_pe.y, ilqr_0_iter3_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_ve.y, ilqr_0_iter3_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_gp.y, ilqr_0_iter3_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_gv.y, ilqr_0_iter3_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_gradient_stage1.y, ilqr_0_iter3_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_ga.y, ilqr_0_iter3_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_gradient.y, ilqr_0_iter3_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter2_update.y, ilqr_0_iter3_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_newton_step.y, ilqr_0_iter3_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, ilqr_0_iter4_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_h_ev.y, ilqr_0_iter4_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_pe_stage1.y, ilqr_0_iter4_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_half_h2_acc.y, ilqr_0_iter4_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter4_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_h_acc.y, ilqr_0_iter4_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_pe.y, ilqr_0_iter4_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_ve.y, ilqr_0_iter4_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_gp.y, ilqr_0_iter4_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_gv.y, ilqr_0_iter4_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_gradient_stage1.y, ilqr_0_iter4_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_ga.y, ilqr_0_iter4_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_gradient.y, ilqr_0_iter4_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter3_update.y, ilqr_0_iter4_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_newton_step.y, ilqr_0_iter4_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, ilqr_0_iter5_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_h_ev.y, ilqr_0_iter5_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_pe_stage1.y, ilqr_0_iter5_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_half_h2_acc.y, ilqr_0_iter5_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, ilqr_0_iter5_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_h_acc.y, ilqr_0_iter5_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_pe.y, ilqr_0_iter5_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_ve.y, ilqr_0_iter5_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_gp.y, ilqr_0_iter5_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_gv.y, ilqr_0_iter5_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_gradient_stage1.y, ilqr_0_iter5_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_ga.y, ilqr_0_iter5_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_gradient.y, ilqr_0_iter5_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter4_update.y, ilqr_0_iter5_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_newton_step.y, ilqr_0_iter5_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_0_iter5_update.y, unconstrained_command_x.u1)
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
  connect(velocity_error_x.y, final_ilqr_x_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_ilqr_x_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, final_ilqr_x_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_h_ev.y, final_ilqr_x_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_predicted_position_error_stage1.y, final_ilqr_x_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_half_h2_acc.y, final_ilqr_x_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_ilqr_x_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, final_ilqr_x_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_h_acc.y, final_ilqr_x_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_predicted_position_error.y, final_ilqr_x_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_predicted_position_error.y, final_ilqr_x_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_predicted_velocity_error.y, final_ilqr_x_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_predicted_velocity_error.y, final_ilqr_x_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_ilqr_x_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_x.y, final_ilqr_x_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_position_error_squared.y, final_ilqr_x_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_velocity_error_squared.y, final_ilqr_x_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_acceleration_squared.y, final_ilqr_x_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_position_cost.y, final_ilqr_x_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_velocity_cost.y, final_ilqr_x_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_stage_cost_stage1.y, final_ilqr_x_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_control_cost.y, final_ilqr_x_stage_cost.u2)
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
  connect(velocity_error_y.y, ilqr_1_iter1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, ilqr_1_iter1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, ilqr_1_iter1_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_h_ev.y, ilqr_1_iter1_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_pe_stage1.y, ilqr_1_iter1_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_half_h2_acc.y, ilqr_1_iter1_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, ilqr_1_iter1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter1_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_h_acc.y, ilqr_1_iter1_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_pe.y, ilqr_1_iter1_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_ve.y, ilqr_1_iter1_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, ilqr_1_iter1_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_gp.y, ilqr_1_iter1_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_gv.y, ilqr_1_iter1_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_gradient_stage1.y, ilqr_1_iter1_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_ga.y, ilqr_1_iter1_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_gradient.y, ilqr_1_iter1_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, ilqr_1_iter1_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_newton_step.y, ilqr_1_iter1_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, ilqr_1_iter2_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_h_ev.y, ilqr_1_iter2_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_pe_stage1.y, ilqr_1_iter2_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_half_h2_acc.y, ilqr_1_iter2_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter2_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_h_acc.y, ilqr_1_iter2_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_pe.y, ilqr_1_iter2_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_ve.y, ilqr_1_iter2_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_gp.y, ilqr_1_iter2_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_gv.y, ilqr_1_iter2_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_gradient_stage1.y, ilqr_1_iter2_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_ga.y, ilqr_1_iter2_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_gradient.y, ilqr_1_iter2_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter1_update.y, ilqr_1_iter2_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_newton_step.y, ilqr_1_iter2_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, ilqr_1_iter3_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_h_ev.y, ilqr_1_iter3_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_pe_stage1.y, ilqr_1_iter3_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_half_h2_acc.y, ilqr_1_iter3_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter3_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_h_acc.y, ilqr_1_iter3_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_pe.y, ilqr_1_iter3_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_ve.y, ilqr_1_iter3_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_gp.y, ilqr_1_iter3_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_gv.y, ilqr_1_iter3_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_gradient_stage1.y, ilqr_1_iter3_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_ga.y, ilqr_1_iter3_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_gradient.y, ilqr_1_iter3_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter2_update.y, ilqr_1_iter3_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_newton_step.y, ilqr_1_iter3_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, ilqr_1_iter4_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_h_ev.y, ilqr_1_iter4_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_pe_stage1.y, ilqr_1_iter4_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_half_h2_acc.y, ilqr_1_iter4_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter4_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_h_acc.y, ilqr_1_iter4_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_pe.y, ilqr_1_iter4_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_ve.y, ilqr_1_iter4_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_gp.y, ilqr_1_iter4_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_gv.y, ilqr_1_iter4_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_gradient_stage1.y, ilqr_1_iter4_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_ga.y, ilqr_1_iter4_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_gradient.y, ilqr_1_iter4_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter3_update.y, ilqr_1_iter4_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_newton_step.y, ilqr_1_iter4_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, ilqr_1_iter5_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_h_ev.y, ilqr_1_iter5_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_pe_stage1.y, ilqr_1_iter5_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_half_h2_acc.y, ilqr_1_iter5_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, ilqr_1_iter5_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_h_acc.y, ilqr_1_iter5_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_pe.y, ilqr_1_iter5_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_ve.y, ilqr_1_iter5_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_gp.y, ilqr_1_iter5_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_gv.y, ilqr_1_iter5_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_gradient_stage1.y, ilqr_1_iter5_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_ga.y, ilqr_1_iter5_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_gradient.y, ilqr_1_iter5_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter4_update.y, ilqr_1_iter5_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_newton_step.y, ilqr_1_iter5_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_1_iter5_update.y, unconstrained_command_y.u1)
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
  connect(velocity_error_y.y, final_ilqr_y_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_ilqr_y_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, final_ilqr_y_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_h_ev.y, final_ilqr_y_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_predicted_position_error_stage1.y, final_ilqr_y_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_half_h2_acc.y, final_ilqr_y_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_ilqr_y_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, final_ilqr_y_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_h_acc.y, final_ilqr_y_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_predicted_position_error.y, final_ilqr_y_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_predicted_position_error.y, final_ilqr_y_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_predicted_velocity_error.y, final_ilqr_y_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_predicted_velocity_error.y, final_ilqr_y_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_ilqr_y_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_y.y, final_ilqr_y_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_position_error_squared.y, final_ilqr_y_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_velocity_error_squared.y, final_ilqr_y_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_acceleration_squared.y, final_ilqr_y_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_position_cost.y, final_ilqr_y_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_velocity_cost.y, final_ilqr_y_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_stage_cost_stage1.y, final_ilqr_y_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_control_cost.y, final_ilqr_y_stage_cost.u2)
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
  connect(velocity_error_z.y, ilqr_2_iter1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, ilqr_2_iter1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, ilqr_2_iter1_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_h_ev.y, ilqr_2_iter1_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_pe_stage1.y, ilqr_2_iter1_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_half_h2_acc.y, ilqr_2_iter1_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, ilqr_2_iter1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter1_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_h_acc.y, ilqr_2_iter1_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_pe.y, ilqr_2_iter1_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_ve.y, ilqr_2_iter1_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, ilqr_2_iter1_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_gp.y, ilqr_2_iter1_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_gv.y, ilqr_2_iter1_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_gradient_stage1.y, ilqr_2_iter1_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_ga.y, ilqr_2_iter1_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_gradient.y, ilqr_2_iter1_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, ilqr_2_iter1_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_newton_step.y, ilqr_2_iter1_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, ilqr_2_iter2_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_h_ev.y, ilqr_2_iter2_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_pe_stage1.y, ilqr_2_iter2_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_half_h2_acc.y, ilqr_2_iter2_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter2_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_h_acc.y, ilqr_2_iter2_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_pe.y, ilqr_2_iter2_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_ve.y, ilqr_2_iter2_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_gp.y, ilqr_2_iter2_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_gv.y, ilqr_2_iter2_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_gradient_stage1.y, ilqr_2_iter2_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_ga.y, ilqr_2_iter2_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_gradient.y, ilqr_2_iter2_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter1_update.y, ilqr_2_iter2_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_newton_step.y, ilqr_2_iter2_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, ilqr_2_iter3_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_h_ev.y, ilqr_2_iter3_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_pe_stage1.y, ilqr_2_iter3_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_half_h2_acc.y, ilqr_2_iter3_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter3_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_h_acc.y, ilqr_2_iter3_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_pe.y, ilqr_2_iter3_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_ve.y, ilqr_2_iter3_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_gp.y, ilqr_2_iter3_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_gv.y, ilqr_2_iter3_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_gradient_stage1.y, ilqr_2_iter3_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_ga.y, ilqr_2_iter3_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_gradient.y, ilqr_2_iter3_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter2_update.y, ilqr_2_iter3_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_newton_step.y, ilqr_2_iter3_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, ilqr_2_iter4_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_h_ev.y, ilqr_2_iter4_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_pe_stage1.y, ilqr_2_iter4_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_half_h2_acc.y, ilqr_2_iter4_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter4_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_h_acc.y, ilqr_2_iter4_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_pe.y, ilqr_2_iter4_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_ve.y, ilqr_2_iter4_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_gp.y, ilqr_2_iter4_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_gv.y, ilqr_2_iter4_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_gradient_stage1.y, ilqr_2_iter4_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_ga.y, ilqr_2_iter4_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_gradient.y, ilqr_2_iter4_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter3_update.y, ilqr_2_iter4_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_newton_step.y, ilqr_2_iter4_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, ilqr_2_iter5_pe_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_h_ev.y, ilqr_2_iter5_pe_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_pe_stage1.y, ilqr_2_iter5_pe.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_half_h2_acc.y, ilqr_2_iter5_pe.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, ilqr_2_iter5_ve.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_h_acc.y, ilqr_2_iter5_ve.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_pe.y, ilqr_2_iter5_gp.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_ve.y, ilqr_2_iter5_gv.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_ga.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_gp.y, ilqr_2_iter5_gradient_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_gv.y, ilqr_2_iter5_gradient_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_gradient_stage1.y, ilqr_2_iter5_gradient.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_ga.y, ilqr_2_iter5_gradient.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_gradient.y, ilqr_2_iter5_newton_step.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter4_update.y, ilqr_2_iter5_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_newton_step.y, ilqr_2_iter5_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ilqr_2_iter5_update.y, unconstrained_command_z.u1)
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
  connect(velocity_error_z.y, final_ilqr_z_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_ilqr_z_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, final_ilqr_z_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_h_ev.y, final_ilqr_z_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_predicted_position_error_stage1.y, final_ilqr_z_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_half_h2_acc.y, final_ilqr_z_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_ilqr_z_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, final_ilqr_z_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_h_acc.y, final_ilqr_z_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_predicted_position_error.y, final_ilqr_z_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_predicted_position_error.y, final_ilqr_z_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_predicted_velocity_error.y, final_ilqr_z_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_predicted_velocity_error.y, final_ilqr_z_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_ilqr_z_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(increment_upper_clip_z.y, final_ilqr_z_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_position_error_squared.y, final_ilqr_z_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_velocity_error_squared.y, final_ilqr_z_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_acceleration_squared.y, final_ilqr_z_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_position_cost.y, final_ilqr_z_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_velocity_cost.y, final_ilqr_z_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_stage_cost_stage1.y, final_ilqr_z_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_control_cost.y, final_ilqr_z_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_x_stage_cost.y, solver_cost_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_y_stage_cost.y, solver_cost_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(final_ilqr_z_stage_cost.y, solver_cost_sum.u2)
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
  connect(auxiliary_zero_x.y, auxiliary_x)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(auxiliary_zero_y.y, auxiliary_y)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(auxiliary_zero_z.y, auxiliary_z)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(solver_cost_sum.y, solver_cost)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fixed_solver_budget.y, solver_iterations)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_P4_ILQR_GRAPHICAL_MIL;
