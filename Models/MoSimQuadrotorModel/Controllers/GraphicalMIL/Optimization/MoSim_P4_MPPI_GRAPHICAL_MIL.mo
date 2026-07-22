within MoSimQuadrotorModel.Controllers.GraphicalMIL.Optimization;

model MoSim_P4_MPPI_GRAPHICAL_MIL "P4 native graphical fixed-budget MPC controller core: mppi"
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
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample0_noise(k=-0.5249999999999999)
    annotation (Placement(transformation(origin = {-480, 550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 528}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 615}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 583}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 561}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 515}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 493}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample0_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 605}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample0_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 550}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample0_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 495}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 605}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 495}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 528}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 506}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample1_noise(k=-0.35)
    annotation (Placement(transformation(origin = {-480, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 463}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 518}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 496}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 450}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 428}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample1_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 540}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample1_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 485}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample1_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 430}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 540}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 463}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 441}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample2_noise(k=-0.175)
    annotation (Placement(transformation(origin = {-480, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 453}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 431}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 385}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 363}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample2_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 475}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample2_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 420}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample2_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 365}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 475}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 365}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 376}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample3_noise(k=0.0)
    annotation (Placement(transformation(origin = {-480, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 333}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 388}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 366}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 320}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 298}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample3_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 410}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample3_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 355}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample3_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 300}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 410}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 300}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 333}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 311}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample4_noise(k=0.175)
    annotation (Placement(transformation(origin = {-480, 290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 268}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 323}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 301}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 233}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample4_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 345}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample4_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 290}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample4_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 235}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 345}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 235}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 268}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 246}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample5_noise(k=0.35)
    annotation (Placement(transformation(origin = {-480, 225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 203}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 245}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 258}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 236}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 168}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample5_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 280}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample5_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 225}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample5_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 170}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 280}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 170}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 203}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 181}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_0_sample6_noise(k=0.5249999999999999)
    annotation (Placement(transformation(origin = {-480, 160}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 138}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 180}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 193}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 171}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 125}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 103}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample6_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 215}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample6_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 160}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample6_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 105}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 215}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 160}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 105}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 138}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 116}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage1(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {432, 537}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage2(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {474, 509}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage3(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {516, 481}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage4(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {558, 453}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage5(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {600, 425}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_0_minimum_cost_stage6(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    "P4 distinguishing native graphical path for mppi" annotation (Placement(transformation(origin = {642, 397}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample0_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 528}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample0_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample0_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample0_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 550}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample1_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 463}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample1_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample1_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample1_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 485}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample2_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 398}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample2_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample2_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample2_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 420}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample3_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 333}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample3_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample3_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample3_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 355}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample4_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 268}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample4_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample4_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample4_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 290}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample5_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 203}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample5_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample5_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample5_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 225}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_sample6_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 138}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_0_sample6_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 160}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_0_sample6_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 160}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_sample6_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 160}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, 358}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, 336}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, 314}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, 292}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, 270}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weighted_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, 248}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, 278}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, 256}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, 234}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, 212}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, 190}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_0_weight_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, 168}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_0_solution(inputs="*/")
    annotation (Placement(transformation(origin = {900, 340}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample0_noise(k=-0.5249999999999999)
    annotation (Placement(transformation(origin = {-480, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 98}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 185}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 153}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 131}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 85}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, 63}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample0_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 175}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample0_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample0_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 65}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 65}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 98}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 76}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample1_noise(k=-0.35)
    annotation (Placement(transformation(origin = {-480, 55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, 33}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 88}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 66}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, 20}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -2}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample1_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 110}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample1_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 55}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample1_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 0}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 110}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, 55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, 0}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, 33}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, 11}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample2_noise(k=-0.175)
    annotation (Placement(transformation(origin = {-480, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, 55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, 10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, 23}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, 1}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -45}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -67}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample2_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, 45}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample2_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -10}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample2_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -65}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, 45}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, -65}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -54}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample3_noise(k=0.0)
    annotation (Placement(transformation(origin = {-480, -75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -97}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -42}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -64}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -110}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -132}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample3_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -20}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample3_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -75}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample3_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -130}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, -20}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, -75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, -130}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -97}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -119}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample4_noise(k=0.175)
    annotation (Placement(transformation(origin = {-480, -140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -162}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -107}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -129}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -197}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample4_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -85}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample4_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -140}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample4_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -195}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, -85}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, -140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, -195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -162}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -184}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample5_noise(k=0.35)
    annotation (Placement(transformation(origin = {-480, -205}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -227}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -185}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -172}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -194}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -240}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -262}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample5_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -150}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample5_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -205}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample5_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, -150}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, -205}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, -260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -227}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -249}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_1_sample6_noise(k=0.5249999999999999)
    annotation (Placement(transformation(origin = {-480, -270}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -292}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -205}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -250}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -237}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -259}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -305}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -327}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample6_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -215}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample6_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -270}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample6_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -325}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_position_cost(k=1.0)
    annotation (Placement(transformation(origin = {-55, -215}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_velocity_cost(k=0.08)
    annotation (Placement(transformation(origin = {-55, -270}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_control_cost(k=0.002)
    annotation (Placement(transformation(origin = {-55, -325}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -292}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -314}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage1(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {432, 107}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage2(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {474, 79}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage3(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {516, 51}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage4(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {558, 23}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage5(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {600, -5}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_1_minimum_cost_stage6(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {642, -33}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample0_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 98}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample0_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample0_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample0_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample1_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, 33}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample1_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, 55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample1_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, 55}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample1_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, 55}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample2_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -32}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample2_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample2_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -10}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample2_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -10}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample3_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -97}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample3_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample3_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -75}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample3_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -75}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample4_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -162}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample4_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample4_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample4_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -140}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample5_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -227}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample5_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -205}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample5_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -205}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample5_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -205}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_sample6_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -292}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_1_sample6_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -270}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_1_sample6_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -270}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_sample6_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -270}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, -72}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, -94}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, -116}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, -138}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, -160}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weighted_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, -182}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, -152}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, -174}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, -196}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, -218}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, -240}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_1_weight_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, -262}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_1_solution(inputs="*/")
    annotation (Placement(transformation(origin = {900, -90}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample0_noise(k=-0.375)
    annotation (Placement(transformation(origin = {-480, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -332}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -245}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -290}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -277}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -299}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -345}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -367}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample0_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -255}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample0_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample0_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -365}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -365}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -332}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -354}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample1_noise(k=-0.25)
    annotation (Placement(transformation(origin = {-480, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -397}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -342}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -364}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -410}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -432}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample1_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -320}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample1_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -375}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample1_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -430}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -320}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -397}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -419}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample2_noise(k=-0.125)
    annotation (Placement(transformation(origin = {-480, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -407}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -429}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -475}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -497}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample2_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -385}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample2_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -440}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample2_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -495}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -385}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -495}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -484}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample3_noise(k=0.0)
    annotation (Placement(transformation(origin = {-480, -505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -527}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -472}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -494}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -540}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -562}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample3_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -450}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample3_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -505}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample3_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -560}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -450}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -560}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -527}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -549}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample4_noise(k=0.125)
    annotation (Placement(transformation(origin = {-480, -570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -592}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -550}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -537}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -559}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -605}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -627}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample4_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -515}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample4_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -570}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample4_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -625}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -515}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -625}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -592}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -614}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample5_noise(k=0.25)
    annotation (Placement(transformation(origin = {-480, -635}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -657}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -615}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -602}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -624}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -670}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -692}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample5_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -580}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample5_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -635}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample5_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -690}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -580}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -635}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -690}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -657}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -679}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant mppi_2_sample6_noise(k=0.375)
    annotation (Placement(transformation(origin = {-480, -700}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_candidate(inputs="++")
    annotation (Placement(transformation(origin = {-361, -722}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_h_ev(k=0.25)
    annotation (Placement(transformation(origin = {-310, -635}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_half_h2_acc(k=0.03125)
    annotation (Placement(transformation(origin = {-310, -680}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_predicted_position_error_stage1(inputs="++")
    annotation (Placement(transformation(origin = {-191, -667}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_predicted_position_error(inputs="+-")
    annotation (Placement(transformation(origin = {-157, -689}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_h_acc(k=0.25)
    annotation (Placement(transformation(origin = {-310, -735}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_predicted_velocity_error(inputs="+-")
    annotation (Placement(transformation(origin = {-191, -757}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample6_position_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -645}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample6_velocity_error_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -700}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample6_acceleration_squared(inputs="**")
    annotation (Placement(transformation(origin = {-140, -755}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_position_cost(k=1.2)
    annotation (Placement(transformation(origin = {-55, -645}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_velocity_cost(k=0.1)
    annotation (Placement(transformation(origin = {-55, -700}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_control_cost(k=0.003)
    annotation (Placement(transformation(origin = {-55, -755}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_stage_cost_stage1(inputs="++")
    annotation (Placement(transformation(origin = {64, -722}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_stage_cost(inputs="++")
    annotation (Placement(transformation(origin = {98, -744}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage1(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {432, -323}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage2(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {474, -351}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage3(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {516, -379}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage4(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {558, -407}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage5(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {600, -435}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin mppi_2_minimum_cost_stage6(maxMinType=SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min)
    annotation (Placement(transformation(origin = {642, -463}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample0_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -332}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample0_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample0_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample0_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample1_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -397}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample1_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample1_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -375}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample1_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -375}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample2_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -462}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample2_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample2_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -440}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample2_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -440}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample3_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -527}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample3_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample3_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -505}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample3_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -505}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample4_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -592}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample4_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample4_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -570}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample4_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -570}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample5_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -657}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample5_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -635}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample5_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -635}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample5_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -635}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_sample6_cost_delta(inputs="+-")
    annotation (Placement(transformation(origin = {509, -722}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain mppi_2_sample6_exponent(k=-3.3333333333333335)
    annotation (Placement(transformation(origin = {560, -700}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction mppi_2_sample6_weight(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp)
    annotation (Placement(transformation(origin = {645, -700}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_sample6_weighted_candidate(inputs="**")
    annotation (Placement(transformation(origin = {730, -700}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, -502}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, -524}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, -546}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, -568}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, -590}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weighted_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, -612}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {849, -582}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum_stage2(inputs="++")
    annotation (Placement(transformation(origin = {883, -604}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum_stage3(inputs="++")
    annotation (Placement(transformation(origin = {917, -626}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum_stage4(inputs="++")
    annotation (Placement(transformation(origin = {951, -648}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum_stage5(inputs="++")
    annotation (Placement(transformation(origin = {985, -670}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mppi_2_weight_sum(inputs="++")
    annotation (Placement(transformation(origin = {1019, -692}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product mppi_2_solution(inputs="*/")
    annotation (Placement(transformation(origin = {900, -520}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum_stage1(inputs="++")
    annotation (Placement(transformation(origin = {1544, -952}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum solver_cost_sum(inputs="++")
    annotation (Placement(transformation(origin = {1578, -974}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant fixed_solver_budget(k=7.0)
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
  connect(linear_solution_x.y, mppi_0_sample0_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_noise.y, mppi_0_sample0_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample0_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample0_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_h_ev.y, mppi_0_sample0_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_predicted_position_error_stage1.y, mppi_0_sample0_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_half_h2_acc.y, mppi_0_sample0_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample0_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_h_acc.y, mppi_0_sample0_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_predicted_position_error.y, mppi_0_sample0_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_predicted_position_error.y, mppi_0_sample0_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_predicted_velocity_error.y, mppi_0_sample0_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_predicted_velocity_error.y, mppi_0_sample0_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_position_error_squared.y, mppi_0_sample0_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_velocity_error_squared.y, mppi_0_sample0_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_acceleration_squared.y, mppi_0_sample0_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_position_cost.y, mppi_0_sample0_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_velocity_cost.y, mppi_0_sample0_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_stage_cost_stage1.y, mppi_0_sample0_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_control_cost.y, mppi_0_sample0_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample1_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_noise.y, mppi_0_sample1_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample1_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_h_ev.y, mppi_0_sample1_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_predicted_position_error_stage1.y, mppi_0_sample1_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_half_h2_acc.y, mppi_0_sample1_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample1_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_h_acc.y, mppi_0_sample1_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_predicted_position_error.y, mppi_0_sample1_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_predicted_position_error.y, mppi_0_sample1_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_predicted_velocity_error.y, mppi_0_sample1_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_predicted_velocity_error.y, mppi_0_sample1_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_position_error_squared.y, mppi_0_sample1_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_velocity_error_squared.y, mppi_0_sample1_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_acceleration_squared.y, mppi_0_sample1_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_position_cost.y, mppi_0_sample1_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_velocity_cost.y, mppi_0_sample1_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_stage_cost_stage1.y, mppi_0_sample1_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_control_cost.y, mppi_0_sample1_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample2_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_noise.y, mppi_0_sample2_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample2_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_h_ev.y, mppi_0_sample2_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_predicted_position_error_stage1.y, mppi_0_sample2_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_half_h2_acc.y, mppi_0_sample2_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample2_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_h_acc.y, mppi_0_sample2_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_predicted_position_error.y, mppi_0_sample2_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_predicted_position_error.y, mppi_0_sample2_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_predicted_velocity_error.y, mppi_0_sample2_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_predicted_velocity_error.y, mppi_0_sample2_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_position_error_squared.y, mppi_0_sample2_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_velocity_error_squared.y, mppi_0_sample2_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_acceleration_squared.y, mppi_0_sample2_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_position_cost.y, mppi_0_sample2_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_velocity_cost.y, mppi_0_sample2_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_stage_cost_stage1.y, mppi_0_sample2_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_control_cost.y, mppi_0_sample2_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample3_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_noise.y, mppi_0_sample3_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample3_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_h_ev.y, mppi_0_sample3_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_predicted_position_error_stage1.y, mppi_0_sample3_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_half_h2_acc.y, mppi_0_sample3_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample3_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_h_acc.y, mppi_0_sample3_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_predicted_position_error.y, mppi_0_sample3_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_predicted_position_error.y, mppi_0_sample3_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_predicted_velocity_error.y, mppi_0_sample3_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_predicted_velocity_error.y, mppi_0_sample3_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_position_error_squared.y, mppi_0_sample3_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_velocity_error_squared.y, mppi_0_sample3_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_acceleration_squared.y, mppi_0_sample3_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_position_cost.y, mppi_0_sample3_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_velocity_cost.y, mppi_0_sample3_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_stage_cost_stage1.y, mppi_0_sample3_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_control_cost.y, mppi_0_sample3_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample4_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_noise.y, mppi_0_sample4_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample4_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_h_ev.y, mppi_0_sample4_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_predicted_position_error_stage1.y, mppi_0_sample4_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_half_h2_acc.y, mppi_0_sample4_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample4_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_h_acc.y, mppi_0_sample4_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_predicted_position_error.y, mppi_0_sample4_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_predicted_position_error.y, mppi_0_sample4_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_predicted_velocity_error.y, mppi_0_sample4_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_predicted_velocity_error.y, mppi_0_sample4_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_position_error_squared.y, mppi_0_sample4_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_velocity_error_squared.y, mppi_0_sample4_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_acceleration_squared.y, mppi_0_sample4_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_position_cost.y, mppi_0_sample4_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_velocity_cost.y, mppi_0_sample4_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_stage_cost_stage1.y, mppi_0_sample4_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_control_cost.y, mppi_0_sample4_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample5_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_noise.y, mppi_0_sample5_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample5_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_h_ev.y, mppi_0_sample5_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_predicted_position_error_stage1.y, mppi_0_sample5_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_half_h2_acc.y, mppi_0_sample5_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample5_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_h_acc.y, mppi_0_sample5_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_predicted_position_error.y, mppi_0_sample5_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_predicted_position_error.y, mppi_0_sample5_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_predicted_velocity_error.y, mppi_0_sample5_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_predicted_velocity_error.y, mppi_0_sample5_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_position_error_squared.y, mppi_0_sample5_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_velocity_error_squared.y, mppi_0_sample5_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_acceleration_squared.y, mppi_0_sample5_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_position_cost.y, mppi_0_sample5_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_velocity_cost.y, mppi_0_sample5_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_stage_cost_stage1.y, mppi_0_sample5_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_control_cost.y, mppi_0_sample5_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_x.y, mppi_0_sample6_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_noise.y, mppi_0_sample6_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample6_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_x.y, mppi_0_sample6_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_h_ev.y, mppi_0_sample6_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_predicted_position_error_stage1.y, mppi_0_sample6_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_half_h2_acc.y, mppi_0_sample6_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_x.y, mppi_0_sample6_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_h_acc.y, mppi_0_sample6_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_predicted_position_error.y, mppi_0_sample6_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_predicted_position_error.y, mppi_0_sample6_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_predicted_velocity_error.y, mppi_0_sample6_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_predicted_velocity_error.y, mppi_0_sample6_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_position_error_squared.y, mppi_0_sample6_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_velocity_error_squared.y, mppi_0_sample6_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_acceleration_squared.y, mppi_0_sample6_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_position_cost.y, mppi_0_sample6_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_velocity_cost.y, mppi_0_sample6_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_stage_cost_stage1.y, mppi_0_sample6_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_control_cost.y, mppi_0_sample6_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_stage_cost.y, mppi_0_minimum_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_stage_cost.y, mppi_0_minimum_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage1.y, mppi_0_minimum_cost_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_stage_cost.y, mppi_0_minimum_cost_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage2.y, mppi_0_minimum_cost_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_stage_cost.y, mppi_0_minimum_cost_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage3.y, mppi_0_minimum_cost_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_stage_cost.y, mppi_0_minimum_cost_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage4.y, mppi_0_minimum_cost_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_stage_cost.y, mppi_0_minimum_cost_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage5.y, mppi_0_minimum_cost_stage6.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_stage_cost.y, mppi_0_minimum_cost_stage6.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_stage_cost.y, mppi_0_sample0_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample0_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_cost_delta.y, mppi_0_sample0_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_exponent.y, mppi_0_sample0_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_weight.y, mppi_0_sample0_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_stage_cost.y, mppi_0_sample1_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample1_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_cost_delta.y, mppi_0_sample1_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_exponent.y, mppi_0_sample1_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_weight.y, mppi_0_sample1_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_stage_cost.y, mppi_0_sample2_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample2_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_cost_delta.y, mppi_0_sample2_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_exponent.y, mppi_0_sample2_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_weight.y, mppi_0_sample2_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_stage_cost.y, mppi_0_sample3_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample3_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_cost_delta.y, mppi_0_sample3_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_exponent.y, mppi_0_sample3_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_weight.y, mppi_0_sample3_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_stage_cost.y, mppi_0_sample4_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample4_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_cost_delta.y, mppi_0_sample4_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_exponent.y, mppi_0_sample4_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_weight.y, mppi_0_sample4_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_stage_cost.y, mppi_0_sample5_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample5_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_cost_delta.y, mppi_0_sample5_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_exponent.y, mppi_0_sample5_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_weight.y, mppi_0_sample5_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_stage_cost.y, mppi_0_sample6_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample6_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_cost_delta.y, mppi_0_sample6_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_exponent.y, mppi_0_sample6_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_weight.y, mppi_0_sample6_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_weighted_candidate.y, mppi_0_weighted_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_weighted_candidate.y, mppi_0_weighted_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum_stage1.y, mppi_0_weighted_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_weighted_candidate.y, mppi_0_weighted_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum_stage2.y, mppi_0_weighted_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_weighted_candidate.y, mppi_0_weighted_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum_stage3.y, mppi_0_weighted_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_weighted_candidate.y, mppi_0_weighted_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum_stage4.y, mppi_0_weighted_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_weighted_candidate.y, mppi_0_weighted_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum_stage5.y, mppi_0_weighted_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_weighted_candidate.y, mppi_0_weighted_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample0_weight.y, mppi_0_weight_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample1_weight.y, mppi_0_weight_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum_stage1.y, mppi_0_weight_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample2_weight.y, mppi_0_weight_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum_stage2.y, mppi_0_weight_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample3_weight.y, mppi_0_weight_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum_stage3.y, mppi_0_weight_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample4_weight.y, mppi_0_weight_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum_stage4.y, mppi_0_weight_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample5_weight.y, mppi_0_weight_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum_stage5.y, mppi_0_weight_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_sample6_weight.y, mppi_0_weight_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weighted_sum.y, mppi_0_solution.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_weight_sum.y, mppi_0_solution.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_0_solution.y, unconstrained_command_x.u1)
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
  connect(linear_solution_y.y, mppi_1_sample0_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_noise.y, mppi_1_sample0_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample0_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample0_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_h_ev.y, mppi_1_sample0_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_predicted_position_error_stage1.y, mppi_1_sample0_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_half_h2_acc.y, mppi_1_sample0_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample0_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_h_acc.y, mppi_1_sample0_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_predicted_position_error.y, mppi_1_sample0_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_predicted_position_error.y, mppi_1_sample0_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_predicted_velocity_error.y, mppi_1_sample0_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_predicted_velocity_error.y, mppi_1_sample0_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_position_error_squared.y, mppi_1_sample0_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_velocity_error_squared.y, mppi_1_sample0_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_acceleration_squared.y, mppi_1_sample0_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_position_cost.y, mppi_1_sample0_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_velocity_cost.y, mppi_1_sample0_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_stage_cost_stage1.y, mppi_1_sample0_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_control_cost.y, mppi_1_sample0_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample1_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_noise.y, mppi_1_sample1_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample1_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_h_ev.y, mppi_1_sample1_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_predicted_position_error_stage1.y, mppi_1_sample1_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_half_h2_acc.y, mppi_1_sample1_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample1_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_h_acc.y, mppi_1_sample1_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_predicted_position_error.y, mppi_1_sample1_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_predicted_position_error.y, mppi_1_sample1_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_predicted_velocity_error.y, mppi_1_sample1_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_predicted_velocity_error.y, mppi_1_sample1_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_position_error_squared.y, mppi_1_sample1_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_velocity_error_squared.y, mppi_1_sample1_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_acceleration_squared.y, mppi_1_sample1_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_position_cost.y, mppi_1_sample1_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_velocity_cost.y, mppi_1_sample1_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_stage_cost_stage1.y, mppi_1_sample1_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_control_cost.y, mppi_1_sample1_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample2_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_noise.y, mppi_1_sample2_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample2_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_h_ev.y, mppi_1_sample2_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_predicted_position_error_stage1.y, mppi_1_sample2_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_half_h2_acc.y, mppi_1_sample2_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample2_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_h_acc.y, mppi_1_sample2_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_predicted_position_error.y, mppi_1_sample2_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_predicted_position_error.y, mppi_1_sample2_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_predicted_velocity_error.y, mppi_1_sample2_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_predicted_velocity_error.y, mppi_1_sample2_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_position_error_squared.y, mppi_1_sample2_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_velocity_error_squared.y, mppi_1_sample2_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_acceleration_squared.y, mppi_1_sample2_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_position_cost.y, mppi_1_sample2_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_velocity_cost.y, mppi_1_sample2_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_stage_cost_stage1.y, mppi_1_sample2_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_control_cost.y, mppi_1_sample2_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample3_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_noise.y, mppi_1_sample3_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample3_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_h_ev.y, mppi_1_sample3_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_predicted_position_error_stage1.y, mppi_1_sample3_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_half_h2_acc.y, mppi_1_sample3_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample3_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_h_acc.y, mppi_1_sample3_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_predicted_position_error.y, mppi_1_sample3_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_predicted_position_error.y, mppi_1_sample3_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_predicted_velocity_error.y, mppi_1_sample3_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_predicted_velocity_error.y, mppi_1_sample3_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_position_error_squared.y, mppi_1_sample3_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_velocity_error_squared.y, mppi_1_sample3_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_acceleration_squared.y, mppi_1_sample3_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_position_cost.y, mppi_1_sample3_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_velocity_cost.y, mppi_1_sample3_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_stage_cost_stage1.y, mppi_1_sample3_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_control_cost.y, mppi_1_sample3_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample4_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_noise.y, mppi_1_sample4_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample4_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_h_ev.y, mppi_1_sample4_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_predicted_position_error_stage1.y, mppi_1_sample4_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_half_h2_acc.y, mppi_1_sample4_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample4_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_h_acc.y, mppi_1_sample4_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_predicted_position_error.y, mppi_1_sample4_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_predicted_position_error.y, mppi_1_sample4_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_predicted_velocity_error.y, mppi_1_sample4_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_predicted_velocity_error.y, mppi_1_sample4_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_position_error_squared.y, mppi_1_sample4_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_velocity_error_squared.y, mppi_1_sample4_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_acceleration_squared.y, mppi_1_sample4_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_position_cost.y, mppi_1_sample4_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_velocity_cost.y, mppi_1_sample4_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_stage_cost_stage1.y, mppi_1_sample4_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_control_cost.y, mppi_1_sample4_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample5_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_noise.y, mppi_1_sample5_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample5_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_h_ev.y, mppi_1_sample5_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_predicted_position_error_stage1.y, mppi_1_sample5_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_half_h2_acc.y, mppi_1_sample5_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample5_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_h_acc.y, mppi_1_sample5_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_predicted_position_error.y, mppi_1_sample5_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_predicted_position_error.y, mppi_1_sample5_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_predicted_velocity_error.y, mppi_1_sample5_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_predicted_velocity_error.y, mppi_1_sample5_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_position_error_squared.y, mppi_1_sample5_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_velocity_error_squared.y, mppi_1_sample5_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_acceleration_squared.y, mppi_1_sample5_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_position_cost.y, mppi_1_sample5_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_velocity_cost.y, mppi_1_sample5_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_stage_cost_stage1.y, mppi_1_sample5_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_control_cost.y, mppi_1_sample5_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_y.y, mppi_1_sample6_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_noise.y, mppi_1_sample6_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample6_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_y.y, mppi_1_sample6_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_h_ev.y, mppi_1_sample6_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_predicted_position_error_stage1.y, mppi_1_sample6_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_half_h2_acc.y, mppi_1_sample6_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_y.y, mppi_1_sample6_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_h_acc.y, mppi_1_sample6_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_predicted_position_error.y, mppi_1_sample6_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_predicted_position_error.y, mppi_1_sample6_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_predicted_velocity_error.y, mppi_1_sample6_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_predicted_velocity_error.y, mppi_1_sample6_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_position_error_squared.y, mppi_1_sample6_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_velocity_error_squared.y, mppi_1_sample6_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_acceleration_squared.y, mppi_1_sample6_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_position_cost.y, mppi_1_sample6_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_velocity_cost.y, mppi_1_sample6_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_stage_cost_stage1.y, mppi_1_sample6_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_control_cost.y, mppi_1_sample6_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_stage_cost.y, mppi_1_minimum_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_stage_cost.y, mppi_1_minimum_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage1.y, mppi_1_minimum_cost_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_stage_cost.y, mppi_1_minimum_cost_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage2.y, mppi_1_minimum_cost_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_stage_cost.y, mppi_1_minimum_cost_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage3.y, mppi_1_minimum_cost_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_stage_cost.y, mppi_1_minimum_cost_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage4.y, mppi_1_minimum_cost_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_stage_cost.y, mppi_1_minimum_cost_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage5.y, mppi_1_minimum_cost_stage6.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_stage_cost.y, mppi_1_minimum_cost_stage6.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_stage_cost.y, mppi_1_sample0_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample0_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_cost_delta.y, mppi_1_sample0_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_exponent.y, mppi_1_sample0_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_weight.y, mppi_1_sample0_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_stage_cost.y, mppi_1_sample1_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample1_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_cost_delta.y, mppi_1_sample1_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_exponent.y, mppi_1_sample1_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_weight.y, mppi_1_sample1_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_stage_cost.y, mppi_1_sample2_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample2_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_cost_delta.y, mppi_1_sample2_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_exponent.y, mppi_1_sample2_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_weight.y, mppi_1_sample2_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_stage_cost.y, mppi_1_sample3_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample3_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_cost_delta.y, mppi_1_sample3_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_exponent.y, mppi_1_sample3_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_weight.y, mppi_1_sample3_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_stage_cost.y, mppi_1_sample4_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample4_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_cost_delta.y, mppi_1_sample4_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_exponent.y, mppi_1_sample4_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_weight.y, mppi_1_sample4_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_stage_cost.y, mppi_1_sample5_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample5_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_cost_delta.y, mppi_1_sample5_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_exponent.y, mppi_1_sample5_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_weight.y, mppi_1_sample5_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_stage_cost.y, mppi_1_sample6_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample6_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_cost_delta.y, mppi_1_sample6_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_exponent.y, mppi_1_sample6_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_weight.y, mppi_1_sample6_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_weighted_candidate.y, mppi_1_weighted_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_weighted_candidate.y, mppi_1_weighted_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum_stage1.y, mppi_1_weighted_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_weighted_candidate.y, mppi_1_weighted_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum_stage2.y, mppi_1_weighted_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_weighted_candidate.y, mppi_1_weighted_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum_stage3.y, mppi_1_weighted_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_weighted_candidate.y, mppi_1_weighted_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum_stage4.y, mppi_1_weighted_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_weighted_candidate.y, mppi_1_weighted_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum_stage5.y, mppi_1_weighted_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_weighted_candidate.y, mppi_1_weighted_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample0_weight.y, mppi_1_weight_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample1_weight.y, mppi_1_weight_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum_stage1.y, mppi_1_weight_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample2_weight.y, mppi_1_weight_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum_stage2.y, mppi_1_weight_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample3_weight.y, mppi_1_weight_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum_stage3.y, mppi_1_weight_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample4_weight.y, mppi_1_weight_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum_stage4.y, mppi_1_weight_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample5_weight.y, mppi_1_weight_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum_stage5.y, mppi_1_weight_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_sample6_weight.y, mppi_1_weight_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weighted_sum.y, mppi_1_solution.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_weight_sum.y, mppi_1_solution.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_solution.y, unconstrained_command_y.u1)
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
  connect(linear_solution_z.y, mppi_2_sample0_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_noise.y, mppi_2_sample0_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample0_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample0_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_h_ev.y, mppi_2_sample0_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_predicted_position_error_stage1.y, mppi_2_sample0_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_half_h2_acc.y, mppi_2_sample0_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample0_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_h_acc.y, mppi_2_sample0_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_predicted_position_error.y, mppi_2_sample0_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_predicted_position_error.y, mppi_2_sample0_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_predicted_velocity_error.y, mppi_2_sample0_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_predicted_velocity_error.y, mppi_2_sample0_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_position_error_squared.y, mppi_2_sample0_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_velocity_error_squared.y, mppi_2_sample0_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_acceleration_squared.y, mppi_2_sample0_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_position_cost.y, mppi_2_sample0_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_velocity_cost.y, mppi_2_sample0_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_stage_cost_stage1.y, mppi_2_sample0_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_control_cost.y, mppi_2_sample0_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample1_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_noise.y, mppi_2_sample1_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample1_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample1_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_h_ev.y, mppi_2_sample1_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_predicted_position_error_stage1.y, mppi_2_sample1_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_half_h2_acc.y, mppi_2_sample1_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample1_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_h_acc.y, mppi_2_sample1_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_predicted_position_error.y, mppi_2_sample1_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_predicted_position_error.y, mppi_2_sample1_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_predicted_velocity_error.y, mppi_2_sample1_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_predicted_velocity_error.y, mppi_2_sample1_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_position_error_squared.y, mppi_2_sample1_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_velocity_error_squared.y, mppi_2_sample1_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_acceleration_squared.y, mppi_2_sample1_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_position_cost.y, mppi_2_sample1_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_velocity_cost.y, mppi_2_sample1_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_stage_cost_stage1.y, mppi_2_sample1_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_control_cost.y, mppi_2_sample1_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample2_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_noise.y, mppi_2_sample2_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample2_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample2_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_h_ev.y, mppi_2_sample2_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_predicted_position_error_stage1.y, mppi_2_sample2_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_half_h2_acc.y, mppi_2_sample2_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample2_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_h_acc.y, mppi_2_sample2_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_predicted_position_error.y, mppi_2_sample2_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_predicted_position_error.y, mppi_2_sample2_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_predicted_velocity_error.y, mppi_2_sample2_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_predicted_velocity_error.y, mppi_2_sample2_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_position_error_squared.y, mppi_2_sample2_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_velocity_error_squared.y, mppi_2_sample2_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_acceleration_squared.y, mppi_2_sample2_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_position_cost.y, mppi_2_sample2_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_velocity_cost.y, mppi_2_sample2_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_stage_cost_stage1.y, mppi_2_sample2_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_control_cost.y, mppi_2_sample2_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample3_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_noise.y, mppi_2_sample3_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample3_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample3_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_h_ev.y, mppi_2_sample3_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_predicted_position_error_stage1.y, mppi_2_sample3_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_half_h2_acc.y, mppi_2_sample3_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample3_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_h_acc.y, mppi_2_sample3_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_predicted_position_error.y, mppi_2_sample3_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_predicted_position_error.y, mppi_2_sample3_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_predicted_velocity_error.y, mppi_2_sample3_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_predicted_velocity_error.y, mppi_2_sample3_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_position_error_squared.y, mppi_2_sample3_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_velocity_error_squared.y, mppi_2_sample3_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_acceleration_squared.y, mppi_2_sample3_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_position_cost.y, mppi_2_sample3_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_velocity_cost.y, mppi_2_sample3_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_stage_cost_stage1.y, mppi_2_sample3_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_control_cost.y, mppi_2_sample3_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample4_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_noise.y, mppi_2_sample4_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample4_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample4_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_h_ev.y, mppi_2_sample4_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_predicted_position_error_stage1.y, mppi_2_sample4_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_half_h2_acc.y, mppi_2_sample4_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample4_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_h_acc.y, mppi_2_sample4_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_predicted_position_error.y, mppi_2_sample4_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_predicted_position_error.y, mppi_2_sample4_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_predicted_velocity_error.y, mppi_2_sample4_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_predicted_velocity_error.y, mppi_2_sample4_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_position_error_squared.y, mppi_2_sample4_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_velocity_error_squared.y, mppi_2_sample4_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_acceleration_squared.y, mppi_2_sample4_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_position_cost.y, mppi_2_sample4_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_velocity_cost.y, mppi_2_sample4_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_stage_cost_stage1.y, mppi_2_sample4_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_control_cost.y, mppi_2_sample4_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample5_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_noise.y, mppi_2_sample5_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample5_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample5_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_h_ev.y, mppi_2_sample5_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_predicted_position_error_stage1.y, mppi_2_sample5_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_half_h2_acc.y, mppi_2_sample5_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample5_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_h_acc.y, mppi_2_sample5_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_predicted_position_error.y, mppi_2_sample5_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_predicted_position_error.y, mppi_2_sample5_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_predicted_velocity_error.y, mppi_2_sample5_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_predicted_velocity_error.y, mppi_2_sample5_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_position_error_squared.y, mppi_2_sample5_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_velocity_error_squared.y, mppi_2_sample5_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_acceleration_squared.y, mppi_2_sample5_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_position_cost.y, mppi_2_sample5_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_velocity_cost.y, mppi_2_sample5_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_stage_cost_stage1.y, mppi_2_sample5_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_control_cost.y, mppi_2_sample5_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(linear_solution_z.y, mppi_2_sample6_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_noise.y, mppi_2_sample6_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample6_h_ev.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_half_h2_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(position_error_z.y, mppi_2_sample6_predicted_position_error_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_h_ev.y, mppi_2_sample6_predicted_position_error_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_predicted_position_error_stage1.y, mppi_2_sample6_predicted_position_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_half_h2_acc.y, mppi_2_sample6_predicted_position_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_h_acc.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(velocity_error_z.y, mppi_2_sample6_predicted_velocity_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_h_acc.y, mppi_2_sample6_predicted_velocity_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_predicted_position_error.y, mppi_2_sample6_position_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_predicted_position_error.y, mppi_2_sample6_position_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_predicted_velocity_error.y, mppi_2_sample6_velocity_error_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_predicted_velocity_error.y, mppi_2_sample6_velocity_error_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_acceleration_squared.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_acceleration_squared.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_position_error_squared.y, mppi_2_sample6_position_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_velocity_error_squared.y, mppi_2_sample6_velocity_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_acceleration_squared.y, mppi_2_sample6_control_cost.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_position_cost.y, mppi_2_sample6_stage_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_velocity_cost.y, mppi_2_sample6_stage_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_stage_cost_stage1.y, mppi_2_sample6_stage_cost.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_control_cost.y, mppi_2_sample6_stage_cost.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_stage_cost.y, mppi_2_minimum_cost_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_stage_cost.y, mppi_2_minimum_cost_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage1.y, mppi_2_minimum_cost_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_stage_cost.y, mppi_2_minimum_cost_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage2.y, mppi_2_minimum_cost_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_stage_cost.y, mppi_2_minimum_cost_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage3.y, mppi_2_minimum_cost_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_stage_cost.y, mppi_2_minimum_cost_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage4.y, mppi_2_minimum_cost_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_stage_cost.y, mppi_2_minimum_cost_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage5.y, mppi_2_minimum_cost_stage6.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_stage_cost.y, mppi_2_minimum_cost_stage6.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_stage_cost.y, mppi_2_sample0_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample0_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_cost_delta.y, mppi_2_sample0_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_exponent.y, mppi_2_sample0_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_weight.y, mppi_2_sample0_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_stage_cost.y, mppi_2_sample1_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample1_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_cost_delta.y, mppi_2_sample1_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_exponent.y, mppi_2_sample1_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_weight.y, mppi_2_sample1_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_stage_cost.y, mppi_2_sample2_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample2_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_cost_delta.y, mppi_2_sample2_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_exponent.y, mppi_2_sample2_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_weight.y, mppi_2_sample2_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_stage_cost.y, mppi_2_sample3_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample3_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_cost_delta.y, mppi_2_sample3_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_exponent.y, mppi_2_sample3_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_weight.y, mppi_2_sample3_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_stage_cost.y, mppi_2_sample4_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample4_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_cost_delta.y, mppi_2_sample4_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_exponent.y, mppi_2_sample4_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_weight.y, mppi_2_sample4_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_stage_cost.y, mppi_2_sample5_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample5_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_cost_delta.y, mppi_2_sample5_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_exponent.y, mppi_2_sample5_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_weight.y, mppi_2_sample5_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_stage_cost.y, mppi_2_sample6_cost_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample6_cost_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_cost_delta.y, mppi_2_sample6_exponent.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_exponent.y, mppi_2_sample6_weight.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_weight.y, mppi_2_sample6_weighted_candidate.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_weighted_candidate.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_weighted_candidate.y, mppi_2_weighted_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_weighted_candidate.y, mppi_2_weighted_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum_stage1.y, mppi_2_weighted_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_weighted_candidate.y, mppi_2_weighted_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum_stage2.y, mppi_2_weighted_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_weighted_candidate.y, mppi_2_weighted_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum_stage3.y, mppi_2_weighted_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_weighted_candidate.y, mppi_2_weighted_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum_stage4.y, mppi_2_weighted_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_weighted_candidate.y, mppi_2_weighted_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum_stage5.y, mppi_2_weighted_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_weighted_candidate.y, mppi_2_weighted_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample0_weight.y, mppi_2_weight_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample1_weight.y, mppi_2_weight_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum_stage1.y, mppi_2_weight_sum_stage2.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample2_weight.y, mppi_2_weight_sum_stage2.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum_stage2.y, mppi_2_weight_sum_stage3.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample3_weight.y, mppi_2_weight_sum_stage3.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum_stage3.y, mppi_2_weight_sum_stage4.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample4_weight.y, mppi_2_weight_sum_stage4.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum_stage4.y, mppi_2_weight_sum_stage5.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample5_weight.y, mppi_2_weight_sum_stage5.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum_stage5.y, mppi_2_weight_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_sample6_weight.y, mppi_2_weight_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weighted_sum.y, mppi_2_solution.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_weight_sum.y, mppi_2_solution.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_solution.y, unconstrained_command_z.u1)
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
  connect(mppi_0_minimum_cost_stage6.y, solver_cost_sum_stage1.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_1_minimum_cost_stage6.y, solver_cost_sum_stage1.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(mppi_2_minimum_cost_stage6.y, solver_cost_sum.u2)
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
  end MoSim_P4_MPPI_GRAPHICAL_MIL;
