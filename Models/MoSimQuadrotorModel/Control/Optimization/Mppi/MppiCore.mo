within MoSimQuadrotorModel.Control.Optimization.Mppi;
model MppiCore "P4 native graphical fixed-budget MPC controller core: mppi"
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
  connect(linear_solution_x.y, mppi_0_sample0_candidate.u1) 
    annotation(Line(points = {{-532, 306}, {-532, 412}, {-361, 412}, {-361, 518}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_noise.y, mppi_0_sample0_candidate.u2) 
    annotation(Line(points = {{-467, 550}, {-420.5, 550}, {-420.5, 528}, {-374, 528}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample0_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 615}, {-323, 615}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_half_h2_acc.u) 
    annotation(Line(points = {{-348, 528}, {-335.5, 528}, {-335.5, 570}, {-323, 570}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample0_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 583}, {-204, 583}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_h_ev.y, mppi_0_sample0_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 615}, {-250.5, 615}, {-250.5, 583}, {-204, 583}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_predicted_position_error_stage1.y, mppi_0_sample0_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 583}, {-174, 583}, {-174, 561}, {-170, 561}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_half_h2_acc.y, mppi_0_sample0_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 570}, {-233.5, 570}, {-233.5, 561}, {-170, 561}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_h_acc.u) 
    annotation(Line(points = {{-348, 528}, {-335.5, 528}, {-335.5, 515}, {-323, 515}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample0_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 493}, {-204, 493}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_h_acc.y, mppi_0_sample0_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 515}, {-250.5, 515}, {-250.5, 493}, {-204, 493}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_predicted_position_error.y, mppi_0_sample0_position_error_squared.u1) 
    annotation(Line(points = {{-157, 571}, {-157, 583}, {-140, 583}, {-140, 595}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_predicted_position_error.y, mppi_0_sample0_position_error_squared.u2) 
    annotation(Line(points = {{-157, 571}, {-157, 583}, {-140, 583}, {-140, 595}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_predicted_velocity_error.y, mppi_0_sample0_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 503}, {-191, 521.5}, {-140, 521.5}, {-140, 540}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_predicted_velocity_error.y, mppi_0_sample0_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 503}, {-191, 521.5}, {-140, 521.5}, {-140, 540}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 528}, {-250.5, 528}, {-250.5, 495}, {-153, 495}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 528}, {-250.5, 528}, {-250.5, 495}, {-153, 495}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_position_error_squared.y, mppi_0_sample0_position_cost.u) 
    annotation(Line(points = {{-127, 605}, {-68, 605}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_velocity_error_squared.y, mppi_0_sample0_velocity_cost.u) 
    annotation(Line(points = {{-127, 550}, {-68, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_acceleration_squared.y, mppi_0_sample0_control_cost.u) 
    annotation(Line(points = {{-127, 495}, {-68, 495}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_position_cost.y, mppi_0_sample0_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 605}, {4.5, 605}, {4.5, 528}, {51, 528}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_velocity_cost.y, mppi_0_sample0_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 550}, {4.5, 550}, {4.5, 528}, {51, 528}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_stage_cost_stage1.y, mppi_0_sample0_stage_cost.u1) 
    annotation(Line(points = {{77, 528}, {81, 528}, {81, 506}, {85, 506}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_control_cost.y, mppi_0_sample0_stage_cost.u2) 
    annotation(Line(points = {{-42, 495}, {21.5, 495}, {21.5, 506}, {85, 506}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample1_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 463}, {-374, 463}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_noise.y, mppi_0_sample1_candidate.u2) 
    annotation(Line(points = {{-467, 485}, {-420.5, 485}, {-420.5, 463}, {-374, 463}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample1_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 550}, {-323, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_half_h2_acc.u) 
    annotation(Line(points = {{-348, 463}, {-335.5, 463}, {-335.5, 505}, {-323, 505}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample1_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 518}, {-204, 518}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_h_ev.y, mppi_0_sample1_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 550}, {-250.5, 550}, {-250.5, 518}, {-204, 518}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_predicted_position_error_stage1.y, mppi_0_sample1_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 518}, {-174, 518}, {-174, 496}, {-170, 496}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_half_h2_acc.y, mppi_0_sample1_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 505}, {-233.5, 505}, {-233.5, 496}, {-170, 496}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_h_acc.u) 
    annotation(Line(points = {{-348, 463}, {-335.5, 463}, {-335.5, 450}, {-323, 450}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample1_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 428}, {-204, 428}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_h_acc.y, mppi_0_sample1_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 450}, {-250.5, 450}, {-250.5, 428}, {-204, 428}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_predicted_position_error.y, mppi_0_sample1_position_error_squared.u1) 
    annotation(Line(points = {{-157, 506}, {-157, 518}, {-140, 518}, {-140, 530}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_predicted_position_error.y, mppi_0_sample1_position_error_squared.u2) 
    annotation(Line(points = {{-157, 506}, {-157, 518}, {-140, 518}, {-140, 530}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_predicted_velocity_error.y, mppi_0_sample1_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 438}, {-191, 456.5}, {-140, 456.5}, {-140, 475}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_predicted_velocity_error.y, mppi_0_sample1_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 438}, {-191, 456.5}, {-140, 456.5}, {-140, 475}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 463}, {-250.5, 463}, {-250.5, 430}, {-153, 430}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 463}, {-250.5, 463}, {-250.5, 430}, {-153, 430}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_position_error_squared.y, mppi_0_sample1_position_cost.u) 
    annotation(Line(points = {{-127, 540}, {-68, 540}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_velocity_error_squared.y, mppi_0_sample1_velocity_cost.u) 
    annotation(Line(points = {{-127, 485}, {-68, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_acceleration_squared.y, mppi_0_sample1_control_cost.u) 
    annotation(Line(points = {{-127, 430}, {-68, 430}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_position_cost.y, mppi_0_sample1_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 540}, {4.5, 540}, {4.5, 463}, {51, 463}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_velocity_cost.y, mppi_0_sample1_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 485}, {4.5, 485}, {4.5, 463}, {51, 463}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_stage_cost_stage1.y, mppi_0_sample1_stage_cost.u1) 
    annotation(Line(points = {{77, 463}, {81, 463}, {81, 441}, {85, 441}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_control_cost.y, mppi_0_sample1_stage_cost.u2) 
    annotation(Line(points = {{-42, 430}, {21.5, 430}, {21.5, 441}, {85, 441}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample2_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 398}, {-374, 398}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_noise.y, mppi_0_sample2_candidate.u2) 
    annotation(Line(points = {{-467, 420}, {-420.5, 420}, {-420.5, 398}, {-374, 398}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample2_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 485}, {-323, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_half_h2_acc.u) 
    annotation(Line(points = {{-348, 398}, {-335.5, 398}, {-335.5, 440}, {-323, 440}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample2_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 453}, {-204, 453}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_h_ev.y, mppi_0_sample2_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 485}, {-250.5, 485}, {-250.5, 453}, {-204, 453}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_predicted_position_error_stage1.y, mppi_0_sample2_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 453}, {-174, 453}, {-174, 431}, {-170, 431}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_half_h2_acc.y, mppi_0_sample2_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 440}, {-233.5, 440}, {-233.5, 431}, {-170, 431}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_h_acc.u) 
    annotation(Line(points = {{-348, 398}, {-335.5, 398}, {-335.5, 385}, {-323, 385}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample2_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 363}, {-204, 363}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_h_acc.y, mppi_0_sample2_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 385}, {-250.5, 385}, {-250.5, 363}, {-204, 363}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_predicted_position_error.y, mppi_0_sample2_position_error_squared.u1) 
    annotation(Line(points = {{-157, 441}, {-157, 453}, {-140, 453}, {-140, 465}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_predicted_position_error.y, mppi_0_sample2_position_error_squared.u2) 
    annotation(Line(points = {{-157, 441}, {-157, 453}, {-140, 453}, {-140, 465}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_predicted_velocity_error.y, mppi_0_sample2_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 373}, {-191, 391.5}, {-140, 391.5}, {-140, 410}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_predicted_velocity_error.y, mppi_0_sample2_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 373}, {-191, 391.5}, {-140, 391.5}, {-140, 410}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 398}, {-250.5, 398}, {-250.5, 365}, {-153, 365}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 398}, {-250.5, 398}, {-250.5, 365}, {-153, 365}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_position_error_squared.y, mppi_0_sample2_position_cost.u) 
    annotation(Line(points = {{-127, 475}, {-68, 475}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_velocity_error_squared.y, mppi_0_sample2_velocity_cost.u) 
    annotation(Line(points = {{-127, 420}, {-68, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_acceleration_squared.y, mppi_0_sample2_control_cost.u) 
    annotation(Line(points = {{-127, 365}, {-68, 365}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_position_cost.y, mppi_0_sample2_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 475}, {4.5, 475}, {4.5, 398}, {51, 398}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_velocity_cost.y, mppi_0_sample2_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 420}, {4.5, 420}, {4.5, 398}, {51, 398}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_stage_cost_stage1.y, mppi_0_sample2_stage_cost.u1) 
    annotation(Line(points = {{77, 398}, {81, 398}, {81, 376}, {85, 376}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_control_cost.y, mppi_0_sample2_stage_cost.u2) 
    annotation(Line(points = {{-42, 365}, {21.5, 365}, {21.5, 376}, {85, 376}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample3_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 333}, {-374, 333}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_noise.y, mppi_0_sample3_candidate.u2) 
    annotation(Line(points = {{-467, 355}, {-420.5, 355}, {-420.5, 333}, {-374, 333}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample3_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 420}, {-323, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_half_h2_acc.u) 
    annotation(Line(points = {{-348, 333}, {-335.5, 333}, {-335.5, 375}, {-323, 375}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample3_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 388}, {-204, 388}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_h_ev.y, mppi_0_sample3_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 420}, {-250.5, 420}, {-250.5, 388}, {-204, 388}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_predicted_position_error_stage1.y, mppi_0_sample3_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 388}, {-174, 388}, {-174, 366}, {-170, 366}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_half_h2_acc.y, mppi_0_sample3_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 375}, {-233.5, 375}, {-233.5, 366}, {-170, 366}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_h_acc.u) 
    annotation(Line(points = {{-348, 333}, {-335.5, 333}, {-335.5, 320}, {-323, 320}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample3_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 298}, {-204, 298}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_h_acc.y, mppi_0_sample3_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 320}, {-250.5, 320}, {-250.5, 298}, {-204, 298}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_predicted_position_error.y, mppi_0_sample3_position_error_squared.u1) 
    annotation(Line(points = {{-157, 376}, {-157, 388}, {-140, 388}, {-140, 400}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_predicted_position_error.y, mppi_0_sample3_position_error_squared.u2) 
    annotation(Line(points = {{-157, 376}, {-157, 388}, {-140, 388}, {-140, 400}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_predicted_velocity_error.y, mppi_0_sample3_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 308}, {-191, 326.5}, {-140, 326.5}, {-140, 345}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_predicted_velocity_error.y, mppi_0_sample3_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 308}, {-191, 326.5}, {-140, 326.5}, {-140, 345}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 333}, {-250.5, 333}, {-250.5, 300}, {-153, 300}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 333}, {-250.5, 333}, {-250.5, 300}, {-153, 300}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_position_error_squared.y, mppi_0_sample3_position_cost.u) 
    annotation(Line(points = {{-127, 410}, {-68, 410}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_velocity_error_squared.y, mppi_0_sample3_velocity_cost.u) 
    annotation(Line(points = {{-127, 355}, {-68, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_acceleration_squared.y, mppi_0_sample3_control_cost.u) 
    annotation(Line(points = {{-127, 300}, {-68, 300}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_position_cost.y, mppi_0_sample3_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 410}, {4.5, 410}, {4.5, 333}, {51, 333}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_velocity_cost.y, mppi_0_sample3_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 355}, {4.5, 355}, {4.5, 333}, {51, 333}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_stage_cost_stage1.y, mppi_0_sample3_stage_cost.u1) 
    annotation(Line(points = {{77, 333}, {81, 333}, {81, 311}, {85, 311}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_control_cost.y, mppi_0_sample3_stage_cost.u2) 
    annotation(Line(points = {{-42, 300}, {21.5, 300}, {21.5, 311}, {85, 311}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample4_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 268}, {-374, 268}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_noise.y, mppi_0_sample4_candidate.u2) 
    annotation(Line(points = {{-467, 290}, {-420.5, 290}, {-420.5, 268}, {-374, 268}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample4_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 355}, {-323, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_half_h2_acc.u) 
    annotation(Line(points = {{-348, 268}, {-335.5, 268}, {-335.5, 310}, {-323, 310}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample4_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 323}, {-204, 323}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_h_ev.y, mppi_0_sample4_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 355}, {-250.5, 355}, {-250.5, 323}, {-204, 323}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_predicted_position_error_stage1.y, mppi_0_sample4_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 323}, {-174, 323}, {-174, 301}, {-170, 301}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_half_h2_acc.y, mppi_0_sample4_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 310}, {-233.5, 310}, {-233.5, 301}, {-170, 301}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_h_acc.u) 
    annotation(Line(points = {{-348, 268}, {-335.5, 268}, {-335.5, 255}, {-323, 255}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample4_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 233}, {-204, 233}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_h_acc.y, mppi_0_sample4_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 255}, {-250.5, 255}, {-250.5, 233}, {-204, 233}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_predicted_position_error.y, mppi_0_sample4_position_error_squared.u1) 
    annotation(Line(points = {{-157, 311}, {-157, 323}, {-140, 323}, {-140, 335}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_predicted_position_error.y, mppi_0_sample4_position_error_squared.u2) 
    annotation(Line(points = {{-157, 311}, {-157, 323}, {-140, 323}, {-140, 335}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_predicted_velocity_error.y, mppi_0_sample4_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 243}, {-191, 261.5}, {-140, 261.5}, {-140, 280}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_predicted_velocity_error.y, mppi_0_sample4_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 243}, {-191, 261.5}, {-140, 261.5}, {-140, 280}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 268}, {-250.5, 268}, {-250.5, 235}, {-153, 235}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 268}, {-250.5, 268}, {-250.5, 235}, {-153, 235}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_position_error_squared.y, mppi_0_sample4_position_cost.u) 
    annotation(Line(points = {{-127, 345}, {-68, 345}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_velocity_error_squared.y, mppi_0_sample4_velocity_cost.u) 
    annotation(Line(points = {{-127, 290}, {-68, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_acceleration_squared.y, mppi_0_sample4_control_cost.u) 
    annotation(Line(points = {{-127, 235}, {-68, 235}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_position_cost.y, mppi_0_sample4_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 345}, {4.5, 345}, {4.5, 268}, {51, 268}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_velocity_cost.y, mppi_0_sample4_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 290}, {4.5, 290}, {4.5, 268}, {51, 268}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_stage_cost_stage1.y, mppi_0_sample4_stage_cost.u1) 
    annotation(Line(points = {{77, 268}, {81, 268}, {81, 246}, {85, 246}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_control_cost.y, mppi_0_sample4_stage_cost.u2) 
    annotation(Line(points = {{-42, 235}, {21.5, 235}, {21.5, 246}, {85, 246}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample5_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 203}, {-374, 203}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_noise.y, mppi_0_sample5_candidate.u2) 
    annotation(Line(points = {{-467, 225}, {-420.5, 225}, {-420.5, 203}, {-374, 203}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample5_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 290}, {-323, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_half_h2_acc.u) 
    annotation(Line(points = {{-348, 203}, {-335.5, 203}, {-335.5, 245}, {-323, 245}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample5_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 258}, {-204, 258}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_h_ev.y, mppi_0_sample5_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 290}, {-250.5, 290}, {-250.5, 258}, {-204, 258}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_predicted_position_error_stage1.y, mppi_0_sample5_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 258}, {-174, 258}, {-174, 236}, {-170, 236}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_half_h2_acc.y, mppi_0_sample5_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 245}, {-233.5, 245}, {-233.5, 236}, {-170, 236}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_h_acc.u) 
    annotation(Line(points = {{-348, 203}, {-335.5, 203}, {-335.5, 190}, {-323, 190}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample5_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 168}, {-204, 168}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_h_acc.y, mppi_0_sample5_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 190}, {-250.5, 190}, {-250.5, 168}, {-204, 168}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_predicted_position_error.y, mppi_0_sample5_position_error_squared.u1) 
    annotation(Line(points = {{-157, 246}, {-157, 258}, {-140, 258}, {-140, 270}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_predicted_position_error.y, mppi_0_sample5_position_error_squared.u2) 
    annotation(Line(points = {{-157, 246}, {-157, 258}, {-140, 258}, {-140, 270}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_predicted_velocity_error.y, mppi_0_sample5_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 178}, {-191, 196.5}, {-140, 196.5}, {-140, 215}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_predicted_velocity_error.y, mppi_0_sample5_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 178}, {-191, 196.5}, {-140, 196.5}, {-140, 215}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 203}, {-250.5, 203}, {-250.5, 170}, {-153, 170}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 203}, {-250.5, 203}, {-250.5, 170}, {-153, 170}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_position_error_squared.y, mppi_0_sample5_position_cost.u) 
    annotation(Line(points = {{-127, 280}, {-68, 280}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_velocity_error_squared.y, mppi_0_sample5_velocity_cost.u) 
    annotation(Line(points = {{-127, 225}, {-68, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_acceleration_squared.y, mppi_0_sample5_control_cost.u) 
    annotation(Line(points = {{-127, 170}, {-68, 170}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_position_cost.y, mppi_0_sample5_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 280}, {4.5, 280}, {4.5, 203}, {51, 203}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_velocity_cost.y, mppi_0_sample5_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 225}, {4.5, 225}, {4.5, 203}, {51, 203}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_stage_cost_stage1.y, mppi_0_sample5_stage_cost.u1) 
    annotation(Line(points = {{77, 203}, {81, 203}, {81, 181}, {85, 181}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_control_cost.y, mppi_0_sample5_stage_cost.u2) 
    annotation(Line(points = {{-42, 170}, {21.5, 170}, {21.5, 181}, {85, 181}}, color = {0, 0, 127}));
  connect(linear_solution_x.y, mppi_0_sample6_candidate.u1) 
    annotation(Line(points = {{-519, 296}, {-446.5, 296}, {-446.5, 138}, {-374, 138}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_noise.y, mppi_0_sample6_candidate.u2) 
    annotation(Line(points = {{-467, 160}, {-420.5, 160}, {-420.5, 138}, {-374, 138}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample6_h_ev.u) 
    annotation(Line(points = {{-733, 263}, {-528, 263}, {-528, 225}, {-323, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_half_h2_acc.u) 
    annotation(Line(points = {{-348, 138}, {-335.5, 138}, {-335.5, 180}, {-323, 180}}, color = {0, 0, 127}));
  connect(position_error_x.y, mppi_0_sample6_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, 373}, {-468.5, 373}, {-468.5, 193}, {-204, 193}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_h_ev.y, mppi_0_sample6_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 225}, {-250.5, 225}, {-250.5, 193}, {-204, 193}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_predicted_position_error_stage1.y, mppi_0_sample6_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 193}, {-174, 193}, {-174, 171}, {-170, 171}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_half_h2_acc.y, mppi_0_sample6_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 180}, {-233.5, 180}, {-233.5, 171}, {-170, 171}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_h_acc.u) 
    annotation(Line(points = {{-348, 138}, {-335.5, 138}, {-335.5, 125}, {-323, 125}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, mppi_0_sample6_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, 263}, {-468.5, 263}, {-468.5, 103}, {-204, 103}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_h_acc.y, mppi_0_sample6_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 125}, {-250.5, 125}, {-250.5, 103}, {-204, 103}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_predicted_position_error.y, mppi_0_sample6_position_error_squared.u1) 
    annotation(Line(points = {{-157, 181}, {-157, 193}, {-140, 193}, {-140, 205}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_predicted_position_error.y, mppi_0_sample6_position_error_squared.u2) 
    annotation(Line(points = {{-157, 181}, {-157, 193}, {-140, 193}, {-140, 205}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_predicted_velocity_error.y, mppi_0_sample6_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 113}, {-191, 131.5}, {-140, 131.5}, {-140, 150}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_predicted_velocity_error.y, mppi_0_sample6_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 113}, {-191, 131.5}, {-140, 131.5}, {-140, 150}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 138}, {-250.5, 138}, {-250.5, 105}, {-153, 105}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 138}, {-250.5, 138}, {-250.5, 105}, {-153, 105}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_position_error_squared.y, mppi_0_sample6_position_cost.u) 
    annotation(Line(points = {{-127, 215}, {-68, 215}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_velocity_error_squared.y, mppi_0_sample6_velocity_cost.u) 
    annotation(Line(points = {{-127, 160}, {-68, 160}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_acceleration_squared.y, mppi_0_sample6_control_cost.u) 
    annotation(Line(points = {{-127, 105}, {-68, 105}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_position_cost.y, mppi_0_sample6_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 215}, {4.5, 215}, {4.5, 138}, {51, 138}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_velocity_cost.y, mppi_0_sample6_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 160}, {4.5, 160}, {4.5, 138}, {51, 138}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_stage_cost_stage1.y, mppi_0_sample6_stage_cost.u1) 
    annotation(Line(points = {{77, 138}, {81, 138}, {81, 116}, {85, 116}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_control_cost.y, mppi_0_sample6_stage_cost.u2) 
    annotation(Line(points = {{-42, 105}, {21.5, 105}, {21.5, 116}, {85, 116}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_stage_cost.y, mppi_0_minimum_cost_stage1.u1) 
    annotation(Line(points = {{111, 506}, {265, 506}, {265, 537}, {419, 537}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_stage_cost.y, mppi_0_minimum_cost_stage1.u2) 
    annotation(Line(points = {{111, 441}, {265, 441}, {265, 537}, {419, 537}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage1.y, mppi_0_minimum_cost_stage2.u1) 
    annotation(Line(points = {{445, 537}, {453, 537}, {453, 509}, {461, 509}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_stage_cost.y, mppi_0_minimum_cost_stage2.u2) 
    annotation(Line(points = {{111, 376}, {286, 376}, {286, 509}, {461, 509}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage2.y, mppi_0_minimum_cost_stage3.u1) 
    annotation(Line(points = {{487, 509}, {495, 509}, {495, 481}, {503, 481}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_stage_cost.y, mppi_0_minimum_cost_stage3.u2) 
    annotation(Line(points = {{111, 311}, {307, 311}, {307, 481}, {503, 481}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage3.y, mppi_0_minimum_cost_stage4.u1) 
    annotation(Line(points = {{529, 481}, {537, 481}, {537, 453}, {545, 453}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_stage_cost.y, mppi_0_minimum_cost_stage4.u2) 
    annotation(Line(points = {{111, 246}, {328, 246}, {328, 453}, {545, 453}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage4.y, mppi_0_minimum_cost_stage5.u1) 
    annotation(Line(points = {{571, 453}, {579, 453}, {579, 425}, {587, 425}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_stage_cost.y, mppi_0_minimum_cost_stage5.u2) 
    annotation(Line(points = {{111, 181}, {349, 181}, {349, 425}, {587, 425}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage5.y, mppi_0_minimum_cost_stage6.u1) 
    annotation(Line(points = {{613, 425}, {621, 425}, {621, 397}, {629, 397}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_stage_cost.y, mppi_0_minimum_cost_stage6.u2) 
    annotation(Line(points = {{111, 116}, {370, 116}, {370, 397}, {629, 397}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_stage_cost.y, mppi_0_sample0_cost_delta.u1) 
    annotation(Line(points = {{111, 506}, {303.5, 506}, {303.5, 528}, {496, 528}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample0_cost_delta.u2) 
    annotation(Line(points = {{629, 397}, {575.5, 397}, {575.5, 528}, {522, 528}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_cost_delta.y, mppi_0_sample0_exponent.u) 
    annotation(Line(points = {{522, 528}, {534.5, 528}, {534.5, 550}, {547, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_exponent.y, mppi_0_sample0_weight.u1) 
    annotation(Line(points = {{573, 550}, {632, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_weight.y, mppi_0_sample0_weighted_candidate.u1) 
    annotation(Line(points = {{658, 550}, {717, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_candidate.y, mppi_0_sample0_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 528}, {184.5, 528}, {184.5, 550}, {717, 550}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_stage_cost.y, mppi_0_sample1_cost_delta.u1) 
    annotation(Line(points = {{111, 441}, {303.5, 441}, {303.5, 463}, {496, 463}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample1_cost_delta.u2) 
    annotation(Line(points = {{629, 397}, {575.5, 397}, {575.5, 463}, {522, 463}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_cost_delta.y, mppi_0_sample1_exponent.u) 
    annotation(Line(points = {{522, 463}, {534.5, 463}, {534.5, 485}, {547, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_exponent.y, mppi_0_sample1_weight.u1) 
    annotation(Line(points = {{573, 485}, {632, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_weight.y, mppi_0_sample1_weighted_candidate.u1) 
    annotation(Line(points = {{658, 485}, {717, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_candidate.y, mppi_0_sample1_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 463}, {184.5, 463}, {184.5, 485}, {717, 485}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_stage_cost.y, mppi_0_sample2_cost_delta.u1) 
    annotation(Line(points = {{111, 376}, {303.5, 376}, {303.5, 398}, {496, 398}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample2_cost_delta.u2) 
    annotation(Line(points = {{629, 397}, {575.5, 397}, {575.5, 398}, {522, 398}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_cost_delta.y, mppi_0_sample2_exponent.u) 
    annotation(Line(points = {{522, 398}, {534.5, 398}, {534.5, 420}, {547, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_exponent.y, mppi_0_sample2_weight.u1) 
    annotation(Line(points = {{573, 420}, {632, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_weight.y, mppi_0_sample2_weighted_candidate.u1) 
    annotation(Line(points = {{658, 420}, {717, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_candidate.y, mppi_0_sample2_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 398}, {184.5, 398}, {184.5, 420}, {717, 420}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_stage_cost.y, mppi_0_sample3_cost_delta.u1) 
    annotation(Line(points = {{111, 311}, {303.5, 311}, {303.5, 333}, {496, 333}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample3_cost_delta.u2) 
    annotation(Line(points = {{629, 397}, {575.5, 397}, {575.5, 333}, {522, 333}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_cost_delta.y, mppi_0_sample3_exponent.u) 
    annotation(Line(points = {{522, 333}, {534.5, 333}, {534.5, 355}, {547, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_exponent.y, mppi_0_sample3_weight.u1) 
    annotation(Line(points = {{573, 355}, {632, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_weight.y, mppi_0_sample3_weighted_candidate.u1) 
    annotation(Line(points = {{658, 355}, {717, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_candidate.y, mppi_0_sample3_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 333}, {184.5, 333}, {184.5, 355}, {717, 355}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_stage_cost.y, mppi_0_sample4_cost_delta.u1) 
    annotation(Line(points = {{111, 246}, {303.5, 246}, {303.5, 268}, {496, 268}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample4_cost_delta.u2) 
    annotation(Line(points = {{629, 397}, {575.5, 397}, {575.5, 268}, {522, 268}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_cost_delta.y, mppi_0_sample4_exponent.u) 
    annotation(Line(points = {{522, 268}, {534.5, 268}, {534.5, 290}, {547, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_exponent.y, mppi_0_sample4_weight.u1) 
    annotation(Line(points = {{573, 290}, {632, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_weight.y, mppi_0_sample4_weighted_candidate.u1) 
    annotation(Line(points = {{658, 290}, {717, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_candidate.y, mppi_0_sample4_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 268}, {184.5, 268}, {184.5, 290}, {717, 290}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_stage_cost.y, mppi_0_sample5_cost_delta.u1) 
    annotation(Line(points = {{111, 181}, {303.5, 181}, {303.5, 203}, {496, 203}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample5_cost_delta.u2) 
    annotation(Line(points = {{642, 387}, {642, 300}, {509, 300}, {509, 213}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_cost_delta.y, mppi_0_sample5_exponent.u) 
    annotation(Line(points = {{522, 203}, {534.5, 203}, {534.5, 225}, {547, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_exponent.y, mppi_0_sample5_weight.u1) 
    annotation(Line(points = {{573, 225}, {632, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_weight.y, mppi_0_sample5_weighted_candidate.u1) 
    annotation(Line(points = {{658, 225}, {717, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_candidate.y, mppi_0_sample5_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 203}, {184.5, 203}, {184.5, 225}, {717, 225}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_stage_cost.y, mppi_0_sample6_cost_delta.u1) 
    annotation(Line(points = {{111, 116}, {303.5, 116}, {303.5, 138}, {496, 138}}, color = {0, 0, 127}));
  connect(mppi_0_minimum_cost_stage6.y, mppi_0_sample6_cost_delta.u2) 
    annotation(Line(points = {{642, 387}, {642, 267.5}, {509, 267.5}, {509, 148}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_cost_delta.y, mppi_0_sample6_exponent.u) 
    annotation(Line(points = {{522, 138}, {534.5, 138}, {534.5, 160}, {547, 160}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_exponent.y, mppi_0_sample6_weight.u1) 
    annotation(Line(points = {{573, 160}, {632, 160}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_weight.y, mppi_0_sample6_weighted_candidate.u1) 
    annotation(Line(points = {{658, 160}, {717, 160}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_candidate.y, mppi_0_sample6_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 138}, {184.5, 138}, {184.5, 160}, {717, 160}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_weighted_candidate.y, mppi_0_weighted_sum_stage1.u1) 
    annotation(Line(points = {{730, 540}, {730, 454}, {849, 454}, {849, 368}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_weighted_candidate.y, mppi_0_weighted_sum_stage1.u2) 
    annotation(Line(points = {{730, 475}, {730, 421.5}, {849, 421.5}, {849, 368}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum_stage1.y, mppi_0_weighted_sum_stage2.u1) 
    annotation(Line(points = {{862, 358}, {866, 358}, {866, 336}, {870, 336}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_weighted_candidate.y, mppi_0_weighted_sum_stage2.u2) 
    annotation(Line(points = {{743, 420}, {806.5, 420}, {806.5, 336}, {870, 336}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum_stage2.y, mppi_0_weighted_sum_stage3.u1) 
    annotation(Line(points = {{896, 336}, {900, 336}, {900, 314}, {904, 314}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_weighted_candidate.y, mppi_0_weighted_sum_stage3.u2) 
    annotation(Line(points = {{743, 355}, {823.5, 355}, {823.5, 314}, {904, 314}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum_stage3.y, mppi_0_weighted_sum_stage4.u1) 
    annotation(Line(points = {{930, 314}, {934, 314}, {934, 292}, {938, 292}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_weighted_candidate.y, mppi_0_weighted_sum_stage4.u2) 
    annotation(Line(points = {{743, 290}, {840.5, 290}, {840.5, 292}, {938, 292}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum_stage4.y, mppi_0_weighted_sum_stage5.u1) 
    annotation(Line(points = {{964, 292}, {968, 292}, {968, 270}, {972, 270}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_weighted_candidate.y, mppi_0_weighted_sum_stage5.u2) 
    annotation(Line(points = {{743, 225}, {857.5, 225}, {857.5, 270}, {972, 270}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum_stage5.y, mppi_0_weighted_sum.u1) 
    annotation(Line(points = {{998, 270}, {1002, 270}, {1002, 248}, {1006, 248}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_weighted_candidate.y, mppi_0_weighted_sum.u2) 
    annotation(Line(points = {{743, 160}, {874.5, 160}, {874.5, 248}, {1006, 248}}, color = {0, 0, 127}));
  connect(mppi_0_sample0_weight.y, mppi_0_weight_sum_stage1.u1) 
    annotation(Line(points = {{645, 540}, {645, 414}, {849, 414}, {849, 288}}, color = {0, 0, 127}));
  connect(mppi_0_sample1_weight.y, mppi_0_weight_sum_stage1.u2) 
    annotation(Line(points = {{645, 475}, {645, 381.5}, {849, 381.5}, {849, 288}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum_stage1.y, mppi_0_weight_sum_stage2.u1) 
    annotation(Line(points = {{862, 278}, {866, 278}, {866, 256}, {870, 256}}, color = {0, 0, 127}));
  connect(mppi_0_sample2_weight.y, mppi_0_weight_sum_stage2.u2) 
    annotation(Line(points = {{658, 420}, {764, 420}, {764, 256}, {870, 256}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum_stage2.y, mppi_0_weight_sum_stage3.u1) 
    annotation(Line(points = {{896, 256}, {900, 256}, {900, 234}, {904, 234}}, color = {0, 0, 127}));
  connect(mppi_0_sample3_weight.y, mppi_0_weight_sum_stage3.u2) 
    annotation(Line(points = {{658, 355}, {781, 355}, {781, 234}, {904, 234}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum_stage3.y, mppi_0_weight_sum_stage4.u1) 
    annotation(Line(points = {{930, 234}, {934, 234}, {934, 212}, {938, 212}}, color = {0, 0, 127}));
  connect(mppi_0_sample4_weight.y, mppi_0_weight_sum_stage4.u2) 
    annotation(Line(points = {{658, 290}, {798, 290}, {798, 212}, {938, 212}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum_stage4.y, mppi_0_weight_sum_stage5.u1) 
    annotation(Line(points = {{964, 212}, {968, 212}, {968, 190}, {972, 190}}, color = {0, 0, 127}));
  connect(mppi_0_sample5_weight.y, mppi_0_weight_sum_stage5.u2) 
    annotation(Line(points = {{658, 225}, {815, 225}, {815, 190}, {972, 190}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum_stage5.y, mppi_0_weight_sum.u1) 
    annotation(Line(points = {{998, 190}, {1002, 190}, {1002, 168}, {1006, 168}}, color = {0, 0, 127}));
  connect(mppi_0_sample6_weight.y, mppi_0_weight_sum.u2) 
    annotation(Line(points = {{658, 160}, {832, 160}, {832, 168}, {1006, 168}}, color = {0, 0, 127}));
  connect(mppi_0_weighted_sum.y, mppi_0_solution.u1) 
    annotation(Line(points = {{1006, 248}, {959.5, 248}, {959.5, 340}, {913, 340}}, color = {0, 0, 127}));
  connect(mppi_0_weight_sum.y, mppi_0_solution.u2) 
    annotation(Line(points = {{1019, 178}, {1019, 254}, {900, 254}, {900, 330}}, color = {0, 0, 127}));
  connect(mppi_0_solution.y, unconstrained_command_x.u1) 
    annotation(Line(points = {{913, 340}, {959.5, 340}, {959.5, 318}, {1006, 318}}, color = {0, 0, 127}));
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
  connect(linear_solution_y.y, mppi_1_sample0_candidate.u1) 
    annotation(Line(points = {{-532, -124}, {-532, -18}, {-361, -18}, {-361, 88}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_noise.y, mppi_1_sample0_candidate.u2) 
    annotation(Line(points = {{-467, 120}, {-420.5, 120}, {-420.5, 98}, {-374, 98}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample0_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, 185}, {-323, 185}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_half_h2_acc.u) 
    annotation(Line(points = {{-348, 98}, {-335.5, 98}, {-335.5, 140}, {-323, 140}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample0_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, 153}, {-204, 153}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_h_ev.y, mppi_1_sample0_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 185}, {-250.5, 185}, {-250.5, 153}, {-204, 153}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_predicted_position_error_stage1.y, mppi_1_sample0_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 153}, {-174, 153}, {-174, 131}, {-170, 131}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_half_h2_acc.y, mppi_1_sample0_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 140}, {-233.5, 140}, {-233.5, 131}, {-170, 131}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_h_acc.u) 
    annotation(Line(points = {{-348, 98}, {-335.5, 98}, {-335.5, 85}, {-323, 85}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample0_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, 63}, {-204, 63}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_h_acc.y, mppi_1_sample0_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 85}, {-250.5, 85}, {-250.5, 63}, {-204, 63}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_predicted_position_error.y, mppi_1_sample0_position_error_squared.u1) 
    annotation(Line(points = {{-157, 141}, {-157, 153}, {-140, 153}, {-140, 165}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_predicted_position_error.y, mppi_1_sample0_position_error_squared.u2) 
    annotation(Line(points = {{-157, 141}, {-157, 153}, {-140, 153}, {-140, 165}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_predicted_velocity_error.y, mppi_1_sample0_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 73}, {-191, 91.5}, {-140, 91.5}, {-140, 110}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_predicted_velocity_error.y, mppi_1_sample0_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 73}, {-191, 91.5}, {-140, 91.5}, {-140, 110}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 98}, {-250.5, 98}, {-250.5, 65}, {-153, 65}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 98}, {-250.5, 98}, {-250.5, 65}, {-153, 65}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_position_error_squared.y, mppi_1_sample0_position_cost.u) 
    annotation(Line(points = {{-127, 175}, {-68, 175}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_velocity_error_squared.y, mppi_1_sample0_velocity_cost.u) 
    annotation(Line(points = {{-127, 120}, {-68, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_acceleration_squared.y, mppi_1_sample0_control_cost.u) 
    annotation(Line(points = {{-127, 65}, {-68, 65}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_position_cost.y, mppi_1_sample0_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 175}, {4.5, 175}, {4.5, 98}, {51, 98}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_velocity_cost.y, mppi_1_sample0_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 120}, {4.5, 120}, {4.5, 98}, {51, 98}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_stage_cost_stage1.y, mppi_1_sample0_stage_cost.u1) 
    annotation(Line(points = {{77, 98}, {81, 98}, {81, 76}, {85, 76}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_control_cost.y, mppi_1_sample0_stage_cost.u2) 
    annotation(Line(points = {{-42, 65}, {21.5, 65}, {21.5, 76}, {85, 76}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample1_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, 33}, {-374, 33}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_noise.y, mppi_1_sample1_candidate.u2) 
    annotation(Line(points = {{-467, 55}, {-420.5, 55}, {-420.5, 33}, {-374, 33}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample1_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, 120}, {-323, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_half_h2_acc.u) 
    annotation(Line(points = {{-348, 33}, {-335.5, 33}, {-335.5, 75}, {-323, 75}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample1_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, 88}, {-204, 88}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_h_ev.y, mppi_1_sample1_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 120}, {-250.5, 120}, {-250.5, 88}, {-204, 88}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_predicted_position_error_stage1.y, mppi_1_sample1_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 88}, {-174, 88}, {-174, 66}, {-170, 66}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_half_h2_acc.y, mppi_1_sample1_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 75}, {-233.5, 75}, {-233.5, 66}, {-170, 66}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_h_acc.u) 
    annotation(Line(points = {{-348, 33}, {-335.5, 33}, {-335.5, 20}, {-323, 20}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample1_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -2}, {-204, -2}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_h_acc.y, mppi_1_sample1_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, 20}, {-250.5, 20}, {-250.5, -2}, {-204, -2}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_predicted_position_error.y, mppi_1_sample1_position_error_squared.u1) 
    annotation(Line(points = {{-157, 76}, {-157, 88}, {-140, 88}, {-140, 100}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_predicted_position_error.y, mppi_1_sample1_position_error_squared.u2) 
    annotation(Line(points = {{-157, 76}, {-157, 88}, {-140, 88}, {-140, 100}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_predicted_velocity_error.y, mppi_1_sample1_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, 8}, {-191, 26.5}, {-140, 26.5}, {-140, 45}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_predicted_velocity_error.y, mppi_1_sample1_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, 8}, {-191, 26.5}, {-140, 26.5}, {-140, 45}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_acceleration_squared.u1) 
    annotation(Line(points = {{-348, 33}, {-250.5, 33}, {-250.5, 0}, {-153, 0}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_acceleration_squared.u2) 
    annotation(Line(points = {{-348, 33}, {-250.5, 33}, {-250.5, 0}, {-153, 0}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_position_error_squared.y, mppi_1_sample1_position_cost.u) 
    annotation(Line(points = {{-127, 110}, {-68, 110}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_velocity_error_squared.y, mppi_1_sample1_velocity_cost.u) 
    annotation(Line(points = {{-127, 55}, {-68, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_acceleration_squared.y, mppi_1_sample1_control_cost.u) 
    annotation(Line(points = {{-127, 0}, {-68, 0}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_position_cost.y, mppi_1_sample1_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 110}, {4.5, 110}, {4.5, 33}, {51, 33}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_velocity_cost.y, mppi_1_sample1_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, 55}, {4.5, 55}, {4.5, 33}, {51, 33}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_stage_cost_stage1.y, mppi_1_sample1_stage_cost.u1) 
    annotation(Line(points = {{77, 33}, {81, 33}, {81, 11}, {85, 11}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_control_cost.y, mppi_1_sample1_stage_cost.u2) 
    annotation(Line(points = {{-42, 0}, {21.5, 0}, {21.5, 11}, {85, 11}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample2_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, -32}, {-374, -32}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_noise.y, mppi_1_sample2_candidate.u2) 
    annotation(Line(points = {{-467, -10}, {-420.5, -10}, {-420.5, -32}, {-374, -32}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample2_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, 55}, {-323, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_half_h2_acc.u) 
    annotation(Line(points = {{-348, -32}, {-335.5, -32}, {-335.5, 10}, {-323, 10}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample2_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, 23}, {-204, 23}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_h_ev.y, mppi_1_sample2_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, 55}, {-250.5, 55}, {-250.5, 23}, {-204, 23}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_predicted_position_error_stage1.y, mppi_1_sample2_predicted_position_error.u1) 
    annotation(Line(points = {{-178, 23}, {-174, 23}, {-174, 1}, {-170, 1}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_half_h2_acc.y, mppi_1_sample2_predicted_position_error.u2) 
    annotation(Line(points = {{-297, 10}, {-233.5, 10}, {-233.5, 1}, {-170, 1}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_h_acc.u) 
    annotation(Line(points = {{-348, -32}, {-335.5, -32}, {-335.5, -45}, {-323, -45}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample2_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -67}, {-204, -67}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_h_acc.y, mppi_1_sample2_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -45}, {-250.5, -45}, {-250.5, -67}, {-204, -67}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_predicted_position_error.y, mppi_1_sample2_position_error_squared.u1) 
    annotation(Line(points = {{-157, 11}, {-157, 23}, {-140, 23}, {-140, 35}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_predicted_position_error.y, mppi_1_sample2_position_error_squared.u2) 
    annotation(Line(points = {{-157, 11}, {-157, 23}, {-140, 23}, {-140, 35}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_predicted_velocity_error.y, mppi_1_sample2_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -57}, {-191, -38.5}, {-140, -38.5}, {-140, -20}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_predicted_velocity_error.y, mppi_1_sample2_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -57}, {-191, -38.5}, {-140, -38.5}, {-140, -20}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -32}, {-250.5, -32}, {-250.5, -65}, {-153, -65}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -32}, {-250.5, -32}, {-250.5, -65}, {-153, -65}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_position_error_squared.y, mppi_1_sample2_position_cost.u) 
    annotation(Line(points = {{-127, 45}, {-68, 45}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_velocity_error_squared.y, mppi_1_sample2_velocity_cost.u) 
    annotation(Line(points = {{-127, -10}, {-68, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_acceleration_squared.y, mppi_1_sample2_control_cost.u) 
    annotation(Line(points = {{-127, -65}, {-68, -65}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_position_cost.y, mppi_1_sample2_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, 45}, {4.5, 45}, {4.5, -32}, {51, -32}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_velocity_cost.y, mppi_1_sample2_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -10}, {4.5, -10}, {4.5, -32}, {51, -32}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_stage_cost_stage1.y, mppi_1_sample2_stage_cost.u1) 
    annotation(Line(points = {{77, -32}, {81, -32}, {81, -54}, {85, -54}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_control_cost.y, mppi_1_sample2_stage_cost.u2) 
    annotation(Line(points = {{-42, -65}, {21.5, -65}, {21.5, -54}, {85, -54}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample3_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, -97}, {-374, -97}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_noise.y, mppi_1_sample3_candidate.u2) 
    annotation(Line(points = {{-467, -75}, {-420.5, -75}, {-420.5, -97}, {-374, -97}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample3_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, -10}, {-323, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_half_h2_acc.u) 
    annotation(Line(points = {{-348, -97}, {-335.5, -97}, {-335.5, -55}, {-323, -55}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample3_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, -42}, {-204, -42}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_h_ev.y, mppi_1_sample3_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -10}, {-250.5, -10}, {-250.5, -42}, {-204, -42}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_predicted_position_error_stage1.y, mppi_1_sample3_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -42}, {-174, -42}, {-174, -64}, {-170, -64}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_half_h2_acc.y, mppi_1_sample3_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -55}, {-233.5, -55}, {-233.5, -64}, {-170, -64}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_h_acc.u) 
    annotation(Line(points = {{-348, -97}, {-335.5, -97}, {-335.5, -110}, {-323, -110}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample3_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -132}, {-204, -132}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_h_acc.y, mppi_1_sample3_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -110}, {-250.5, -110}, {-250.5, -132}, {-204, -132}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_predicted_position_error.y, mppi_1_sample3_position_error_squared.u1) 
    annotation(Line(points = {{-157, -54}, {-157, -42}, {-140, -42}, {-140, -30}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_predicted_position_error.y, mppi_1_sample3_position_error_squared.u2) 
    annotation(Line(points = {{-157, -54}, {-157, -42}, {-140, -42}, {-140, -30}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_predicted_velocity_error.y, mppi_1_sample3_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -122}, {-191, -103.5}, {-140, -103.5}, {-140, -85}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_predicted_velocity_error.y, mppi_1_sample3_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -122}, {-191, -103.5}, {-140, -103.5}, {-140, -85}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -97}, {-250.5, -97}, {-250.5, -130}, {-153, -130}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -97}, {-250.5, -97}, {-250.5, -130}, {-153, -130}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_position_error_squared.y, mppi_1_sample3_position_cost.u) 
    annotation(Line(points = {{-127, -20}, {-68, -20}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_velocity_error_squared.y, mppi_1_sample3_velocity_cost.u) 
    annotation(Line(points = {{-127, -75}, {-68, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_acceleration_squared.y, mppi_1_sample3_control_cost.u) 
    annotation(Line(points = {{-127, -130}, {-68, -130}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_position_cost.y, mppi_1_sample3_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -20}, {4.5, -20}, {4.5, -97}, {51, -97}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_velocity_cost.y, mppi_1_sample3_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -75}, {4.5, -75}, {4.5, -97}, {51, -97}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_stage_cost_stage1.y, mppi_1_sample3_stage_cost.u1) 
    annotation(Line(points = {{77, -97}, {81, -97}, {81, -119}, {85, -119}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_control_cost.y, mppi_1_sample3_stage_cost.u2) 
    annotation(Line(points = {{-42, -130}, {21.5, -130}, {21.5, -119}, {85, -119}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample4_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, -162}, {-374, -162}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_noise.y, mppi_1_sample4_candidate.u2) 
    annotation(Line(points = {{-467, -140}, {-420.5, -140}, {-420.5, -162}, {-374, -162}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample4_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, -75}, {-323, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_half_h2_acc.u) 
    annotation(Line(points = {{-348, -162}, {-335.5, -162}, {-335.5, -120}, {-323, -120}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample4_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, -107}, {-204, -107}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_h_ev.y, mppi_1_sample4_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -75}, {-250.5, -75}, {-250.5, -107}, {-204, -107}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_predicted_position_error_stage1.y, mppi_1_sample4_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -107}, {-174, -107}, {-174, -129}, {-170, -129}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_half_h2_acc.y, mppi_1_sample4_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -120}, {-233.5, -120}, {-233.5, -129}, {-170, -129}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_h_acc.u) 
    annotation(Line(points = {{-348, -162}, {-335.5, -162}, {-335.5, -175}, {-323, -175}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample4_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -197}, {-204, -197}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_h_acc.y, mppi_1_sample4_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -175}, {-250.5, -175}, {-250.5, -197}, {-204, -197}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_predicted_position_error.y, mppi_1_sample4_position_error_squared.u1) 
    annotation(Line(points = {{-157, -119}, {-157, -107}, {-140, -107}, {-140, -95}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_predicted_position_error.y, mppi_1_sample4_position_error_squared.u2) 
    annotation(Line(points = {{-157, -119}, {-157, -107}, {-140, -107}, {-140, -95}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_predicted_velocity_error.y, mppi_1_sample4_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -187}, {-191, -168.5}, {-140, -168.5}, {-140, -150}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_predicted_velocity_error.y, mppi_1_sample4_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -187}, {-191, -168.5}, {-140, -168.5}, {-140, -150}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -162}, {-250.5, -162}, {-250.5, -195}, {-153, -195}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -162}, {-250.5, -162}, {-250.5, -195}, {-153, -195}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_position_error_squared.y, mppi_1_sample4_position_cost.u) 
    annotation(Line(points = {{-127, -85}, {-68, -85}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_velocity_error_squared.y, mppi_1_sample4_velocity_cost.u) 
    annotation(Line(points = {{-127, -140}, {-68, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_acceleration_squared.y, mppi_1_sample4_control_cost.u) 
    annotation(Line(points = {{-127, -195}, {-68, -195}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_position_cost.y, mppi_1_sample4_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -85}, {4.5, -85}, {4.5, -162}, {51, -162}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_velocity_cost.y, mppi_1_sample4_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -140}, {4.5, -140}, {4.5, -162}, {51, -162}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_stage_cost_stage1.y, mppi_1_sample4_stage_cost.u1) 
    annotation(Line(points = {{77, -162}, {81, -162}, {81, -184}, {85, -184}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_control_cost.y, mppi_1_sample4_stage_cost.u2) 
    annotation(Line(points = {{-42, -195}, {21.5, -195}, {21.5, -184}, {85, -184}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample5_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, -227}, {-374, -227}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_noise.y, mppi_1_sample5_candidate.u2) 
    annotation(Line(points = {{-467, -205}, {-420.5, -205}, {-420.5, -227}, {-374, -227}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample5_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, -140}, {-323, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_half_h2_acc.u) 
    annotation(Line(points = {{-348, -227}, {-335.5, -227}, {-335.5, -185}, {-323, -185}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample5_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, -172}, {-204, -172}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_h_ev.y, mppi_1_sample5_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -140}, {-250.5, -140}, {-250.5, -172}, {-204, -172}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_predicted_position_error_stage1.y, mppi_1_sample5_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -172}, {-174, -172}, {-174, -194}, {-170, -194}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_half_h2_acc.y, mppi_1_sample5_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -185}, {-233.5, -185}, {-233.5, -194}, {-170, -194}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_h_acc.u) 
    annotation(Line(points = {{-348, -227}, {-335.5, -227}, {-335.5, -240}, {-323, -240}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample5_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -262}, {-204, -262}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_h_acc.y, mppi_1_sample5_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -240}, {-250.5, -240}, {-250.5, -262}, {-204, -262}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_predicted_position_error.y, mppi_1_sample5_position_error_squared.u1) 
    annotation(Line(points = {{-157, -184}, {-157, -172}, {-140, -172}, {-140, -160}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_predicted_position_error.y, mppi_1_sample5_position_error_squared.u2) 
    annotation(Line(points = {{-157, -184}, {-157, -172}, {-140, -172}, {-140, -160}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_predicted_velocity_error.y, mppi_1_sample5_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -252}, {-191, -233.5}, {-140, -233.5}, {-140, -215}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_predicted_velocity_error.y, mppi_1_sample5_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -252}, {-191, -233.5}, {-140, -233.5}, {-140, -215}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -227}, {-250.5, -227}, {-250.5, -260}, {-153, -260}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -227}, {-250.5, -227}, {-250.5, -260}, {-153, -260}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_position_error_squared.y, mppi_1_sample5_position_cost.u) 
    annotation(Line(points = {{-127, -150}, {-68, -150}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_velocity_error_squared.y, mppi_1_sample5_velocity_cost.u) 
    annotation(Line(points = {{-127, -205}, {-68, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_acceleration_squared.y, mppi_1_sample5_control_cost.u) 
    annotation(Line(points = {{-127, -260}, {-68, -260}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_position_cost.y, mppi_1_sample5_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -150}, {4.5, -150}, {4.5, -227}, {51, -227}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_velocity_cost.y, mppi_1_sample5_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -205}, {4.5, -205}, {4.5, -227}, {51, -227}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_stage_cost_stage1.y, mppi_1_sample5_stage_cost.u1) 
    annotation(Line(points = {{77, -227}, {81, -227}, {81, -249}, {85, -249}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_control_cost.y, mppi_1_sample5_stage_cost.u2) 
    annotation(Line(points = {{-42, -260}, {21.5, -260}, {21.5, -249}, {85, -249}}, color = {0, 0, 127}));
  connect(linear_solution_y.y, mppi_1_sample6_candidate.u1) 
    annotation(Line(points = {{-519, -134}, {-446.5, -134}, {-446.5, -292}, {-374, -292}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_noise.y, mppi_1_sample6_candidate.u2) 
    annotation(Line(points = {{-467, -270}, {-420.5, -270}, {-420.5, -292}, {-374, -292}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample6_h_ev.u) 
    annotation(Line(points = {{-733, -167}, {-528, -167}, {-528, -205}, {-323, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_half_h2_acc.u) 
    annotation(Line(points = {{-348, -292}, {-335.5, -292}, {-335.5, -250}, {-323, -250}}, color = {0, 0, 127}));
  connect(position_error_y.y, mppi_1_sample6_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -57}, {-468.5, -57}, {-468.5, -237}, {-204, -237}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_h_ev.y, mppi_1_sample6_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -205}, {-250.5, -205}, {-250.5, -237}, {-204, -237}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_predicted_position_error_stage1.y, mppi_1_sample6_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -237}, {-174, -237}, {-174, -259}, {-170, -259}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_half_h2_acc.y, mppi_1_sample6_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -250}, {-233.5, -250}, {-233.5, -259}, {-170, -259}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_h_acc.u) 
    annotation(Line(points = {{-348, -292}, {-335.5, -292}, {-335.5, -305}, {-323, -305}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, mppi_1_sample6_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -167}, {-468.5, -167}, {-468.5, -327}, {-204, -327}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_h_acc.y, mppi_1_sample6_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -305}, {-250.5, -305}, {-250.5, -327}, {-204, -327}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_predicted_position_error.y, mppi_1_sample6_position_error_squared.u1) 
    annotation(Line(points = {{-157, -249}, {-157, -237}, {-140, -237}, {-140, -225}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_predicted_position_error.y, mppi_1_sample6_position_error_squared.u2) 
    annotation(Line(points = {{-157, -249}, {-157, -237}, {-140, -237}, {-140, -225}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_predicted_velocity_error.y, mppi_1_sample6_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -317}, {-191, -298.5}, {-140, -298.5}, {-140, -280}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_predicted_velocity_error.y, mppi_1_sample6_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -317}, {-191, -298.5}, {-140, -298.5}, {-140, -280}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -292}, {-250.5, -292}, {-250.5, -325}, {-153, -325}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -292}, {-250.5, -292}, {-250.5, -325}, {-153, -325}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_position_error_squared.y, mppi_1_sample6_position_cost.u) 
    annotation(Line(points = {{-127, -215}, {-68, -215}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_velocity_error_squared.y, mppi_1_sample6_velocity_cost.u) 
    annotation(Line(points = {{-127, -270}, {-68, -270}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_acceleration_squared.y, mppi_1_sample6_control_cost.u) 
    annotation(Line(points = {{-127, -325}, {-68, -325}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_position_cost.y, mppi_1_sample6_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -215}, {4.5, -215}, {4.5, -292}, {51, -292}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_velocity_cost.y, mppi_1_sample6_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -270}, {4.5, -270}, {4.5, -292}, {51, -292}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_stage_cost_stage1.y, mppi_1_sample6_stage_cost.u1) 
    annotation(Line(points = {{77, -292}, {81, -292}, {81, -314}, {85, -314}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_control_cost.y, mppi_1_sample6_stage_cost.u2) 
    annotation(Line(points = {{-42, -325}, {21.5, -325}, {21.5, -314}, {85, -314}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_stage_cost.y, mppi_1_minimum_cost_stage1.u1) 
    annotation(Line(points = {{111, 76}, {265, 76}, {265, 107}, {419, 107}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_stage_cost.y, mppi_1_minimum_cost_stage1.u2) 
    annotation(Line(points = {{111, 11}, {265, 11}, {265, 107}, {419, 107}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage1.y, mppi_1_minimum_cost_stage2.u1) 
    annotation(Line(points = {{445, 107}, {453, 107}, {453, 79}, {461, 79}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_stage_cost.y, mppi_1_minimum_cost_stage2.u2) 
    annotation(Line(points = {{111, -54}, {286, -54}, {286, 79}, {461, 79}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage2.y, mppi_1_minimum_cost_stage3.u1) 
    annotation(Line(points = {{487, 79}, {495, 79}, {495, 51}, {503, 51}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_stage_cost.y, mppi_1_minimum_cost_stage3.u2) 
    annotation(Line(points = {{111, -119}, {307, -119}, {307, 51}, {503, 51}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage3.y, mppi_1_minimum_cost_stage4.u1) 
    annotation(Line(points = {{529, 51}, {537, 51}, {537, 23}, {545, 23}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_stage_cost.y, mppi_1_minimum_cost_stage4.u2) 
    annotation(Line(points = {{111, -184}, {328, -184}, {328, 23}, {545, 23}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage4.y, mppi_1_minimum_cost_stage5.u1) 
    annotation(Line(points = {{571, 23}, {579, 23}, {579, -5}, {587, -5}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_stage_cost.y, mppi_1_minimum_cost_stage5.u2) 
    annotation(Line(points = {{111, -249}, {349, -249}, {349, -5}, {587, -5}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage5.y, mppi_1_minimum_cost_stage6.u1) 
    annotation(Line(points = {{613, -5}, {621, -5}, {621, -33}, {629, -33}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_stage_cost.y, mppi_1_minimum_cost_stage6.u2) 
    annotation(Line(points = {{111, -314}, {370, -314}, {370, -33}, {629, -33}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_stage_cost.y, mppi_1_sample0_cost_delta.u1) 
    annotation(Line(points = {{111, 76}, {303.5, 76}, {303.5, 98}, {496, 98}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample0_cost_delta.u2) 
    annotation(Line(points = {{629, -33}, {575.5, -33}, {575.5, 98}, {522, 98}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_cost_delta.y, mppi_1_sample0_exponent.u) 
    annotation(Line(points = {{522, 98}, {534.5, 98}, {534.5, 120}, {547, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_exponent.y, mppi_1_sample0_weight.u1) 
    annotation(Line(points = {{573, 120}, {632, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_weight.y, mppi_1_sample0_weighted_candidate.u1) 
    annotation(Line(points = {{658, 120}, {717, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_candidate.y, mppi_1_sample0_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 98}, {184.5, 98}, {184.5, 120}, {717, 120}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_stage_cost.y, mppi_1_sample1_cost_delta.u1) 
    annotation(Line(points = {{111, 11}, {303.5, 11}, {303.5, 33}, {496, 33}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample1_cost_delta.u2) 
    annotation(Line(points = {{629, -33}, {575.5, -33}, {575.5, 33}, {522, 33}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_cost_delta.y, mppi_1_sample1_exponent.u) 
    annotation(Line(points = {{522, 33}, {534.5, 33}, {534.5, 55}, {547, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_exponent.y, mppi_1_sample1_weight.u1) 
    annotation(Line(points = {{573, 55}, {632, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_weight.y, mppi_1_sample1_weighted_candidate.u1) 
    annotation(Line(points = {{658, 55}, {717, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_candidate.y, mppi_1_sample1_weighted_candidate.u2) 
    annotation(Line(points = {{-348, 33}, {184.5, 33}, {184.5, 55}, {717, 55}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_stage_cost.y, mppi_1_sample2_cost_delta.u1) 
    annotation(Line(points = {{111, -54}, {303.5, -54}, {303.5, -32}, {496, -32}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample2_cost_delta.u2) 
    annotation(Line(points = {{629, -33}, {575.5, -33}, {575.5, -32}, {522, -32}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_cost_delta.y, mppi_1_sample2_exponent.u) 
    annotation(Line(points = {{522, -32}, {534.5, -32}, {534.5, -10}, {547, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_exponent.y, mppi_1_sample2_weight.u1) 
    annotation(Line(points = {{573, -10}, {632, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_weight.y, mppi_1_sample2_weighted_candidate.u1) 
    annotation(Line(points = {{658, -10}, {717, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_candidate.y, mppi_1_sample2_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -32}, {184.5, -32}, {184.5, -10}, {717, -10}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_stage_cost.y, mppi_1_sample3_cost_delta.u1) 
    annotation(Line(points = {{111, -119}, {303.5, -119}, {303.5, -97}, {496, -97}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample3_cost_delta.u2) 
    annotation(Line(points = {{629, -33}, {575.5, -33}, {575.5, -97}, {522, -97}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_cost_delta.y, mppi_1_sample3_exponent.u) 
    annotation(Line(points = {{522, -97}, {534.5, -97}, {534.5, -75}, {547, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_exponent.y, mppi_1_sample3_weight.u1) 
    annotation(Line(points = {{573, -75}, {632, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_weight.y, mppi_1_sample3_weighted_candidate.u1) 
    annotation(Line(points = {{658, -75}, {717, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_candidate.y, mppi_1_sample3_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -97}, {184.5, -97}, {184.5, -75}, {717, -75}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_stage_cost.y, mppi_1_sample4_cost_delta.u1) 
    annotation(Line(points = {{111, -184}, {303.5, -184}, {303.5, -162}, {496, -162}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample4_cost_delta.u2) 
    annotation(Line(points = {{629, -33}, {575.5, -33}, {575.5, -162}, {522, -162}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_cost_delta.y, mppi_1_sample4_exponent.u) 
    annotation(Line(points = {{522, -162}, {534.5, -162}, {534.5, -140}, {547, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_exponent.y, mppi_1_sample4_weight.u1) 
    annotation(Line(points = {{573, -140}, {632, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_weight.y, mppi_1_sample4_weighted_candidate.u1) 
    annotation(Line(points = {{658, -140}, {717, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_candidate.y, mppi_1_sample4_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -162}, {184.5, -162}, {184.5, -140}, {717, -140}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_stage_cost.y, mppi_1_sample5_cost_delta.u1) 
    annotation(Line(points = {{111, -249}, {303.5, -249}, {303.5, -227}, {496, -227}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample5_cost_delta.u2) 
    annotation(Line(points = {{642, -43}, {642, -130}, {509, -130}, {509, -217}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_cost_delta.y, mppi_1_sample5_exponent.u) 
    annotation(Line(points = {{522, -227}, {534.5, -227}, {534.5, -205}, {547, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_exponent.y, mppi_1_sample5_weight.u1) 
    annotation(Line(points = {{573, -205}, {632, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_weight.y, mppi_1_sample5_weighted_candidate.u1) 
    annotation(Line(points = {{658, -205}, {717, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_candidate.y, mppi_1_sample5_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -227}, {184.5, -227}, {184.5, -205}, {717, -205}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_stage_cost.y, mppi_1_sample6_cost_delta.u1) 
    annotation(Line(points = {{111, -314}, {303.5, -314}, {303.5, -292}, {496, -292}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, mppi_1_sample6_cost_delta.u2) 
    annotation(Line(points = {{642, -43}, {642, -162.5}, {509, -162.5}, {509, -282}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_cost_delta.y, mppi_1_sample6_exponent.u) 
    annotation(Line(points = {{522, -292}, {534.5, -292}, {534.5, -270}, {547, -270}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_exponent.y, mppi_1_sample6_weight.u1) 
    annotation(Line(points = {{573, -270}, {632, -270}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_weight.y, mppi_1_sample6_weighted_candidate.u1) 
    annotation(Line(points = {{658, -270}, {717, -270}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_candidate.y, mppi_1_sample6_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -292}, {184.5, -292}, {184.5, -270}, {717, -270}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_weighted_candidate.y, mppi_1_weighted_sum_stage1.u1) 
    annotation(Line(points = {{730, 110}, {730, 24}, {849, 24}, {849, -62}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_weighted_candidate.y, mppi_1_weighted_sum_stage1.u2) 
    annotation(Line(points = {{730, 45}, {730, -8.5}, {849, -8.5}, {849, -62}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum_stage1.y, mppi_1_weighted_sum_stage2.u1) 
    annotation(Line(points = {{862, -72}, {866, -72}, {866, -94}, {870, -94}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_weighted_candidate.y, mppi_1_weighted_sum_stage2.u2) 
    annotation(Line(points = {{743, -10}, {806.5, -10}, {806.5, -94}, {870, -94}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum_stage2.y, mppi_1_weighted_sum_stage3.u1) 
    annotation(Line(points = {{896, -94}, {900, -94}, {900, -116}, {904, -116}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_weighted_candidate.y, mppi_1_weighted_sum_stage3.u2) 
    annotation(Line(points = {{743, -75}, {823.5, -75}, {823.5, -116}, {904, -116}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum_stage3.y, mppi_1_weighted_sum_stage4.u1) 
    annotation(Line(points = {{930, -116}, {934, -116}, {934, -138}, {938, -138}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_weighted_candidate.y, mppi_1_weighted_sum_stage4.u2) 
    annotation(Line(points = {{743, -140}, {840.5, -140}, {840.5, -138}, {938, -138}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum_stage4.y, mppi_1_weighted_sum_stage5.u1) 
    annotation(Line(points = {{964, -138}, {968, -138}, {968, -160}, {972, -160}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_weighted_candidate.y, mppi_1_weighted_sum_stage5.u2) 
    annotation(Line(points = {{743, -205}, {857.5, -205}, {857.5, -160}, {972, -160}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum_stage5.y, mppi_1_weighted_sum.u1) 
    annotation(Line(points = {{998, -160}, {1002, -160}, {1002, -182}, {1006, -182}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_weighted_candidate.y, mppi_1_weighted_sum.u2) 
    annotation(Line(points = {{743, -270}, {874.5, -270}, {874.5, -182}, {1006, -182}}, color = {0, 0, 127}));
  connect(mppi_1_sample0_weight.y, mppi_1_weight_sum_stage1.u1) 
    annotation(Line(points = {{645, 110}, {645, -16}, {849, -16}, {849, -142}}, color = {0, 0, 127}));
  connect(mppi_1_sample1_weight.y, mppi_1_weight_sum_stage1.u2) 
    annotation(Line(points = {{645, 45}, {645, -48.5}, {849, -48.5}, {849, -142}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum_stage1.y, mppi_1_weight_sum_stage2.u1) 
    annotation(Line(points = {{862, -152}, {866, -152}, {866, -174}, {870, -174}}, color = {0, 0, 127}));
  connect(mppi_1_sample2_weight.y, mppi_1_weight_sum_stage2.u2) 
    annotation(Line(points = {{658, -10}, {764, -10}, {764, -174}, {870, -174}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum_stage2.y, mppi_1_weight_sum_stage3.u1) 
    annotation(Line(points = {{896, -174}, {900, -174}, {900, -196}, {904, -196}}, color = {0, 0, 127}));
  connect(mppi_1_sample3_weight.y, mppi_1_weight_sum_stage3.u2) 
    annotation(Line(points = {{658, -75}, {781, -75}, {781, -196}, {904, -196}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum_stage3.y, mppi_1_weight_sum_stage4.u1) 
    annotation(Line(points = {{930, -196}, {934, -196}, {934, -218}, {938, -218}}, color = {0, 0, 127}));
  connect(mppi_1_sample4_weight.y, mppi_1_weight_sum_stage4.u2) 
    annotation(Line(points = {{658, -140}, {798, -140}, {798, -218}, {938, -218}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum_stage4.y, mppi_1_weight_sum_stage5.u1) 
    annotation(Line(points = {{964, -218}, {968, -218}, {968, -240}, {972, -240}}, color = {0, 0, 127}));
  connect(mppi_1_sample5_weight.y, mppi_1_weight_sum_stage5.u2) 
    annotation(Line(points = {{658, -205}, {815, -205}, {815, -240}, {972, -240}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum_stage5.y, mppi_1_weight_sum.u1) 
    annotation(Line(points = {{998, -240}, {1002, -240}, {1002, -262}, {1006, -262}}, color = {0, 0, 127}));
  connect(mppi_1_sample6_weight.y, mppi_1_weight_sum.u2) 
    annotation(Line(points = {{658, -270}, {832, -270}, {832, -262}, {1006, -262}}, color = {0, 0, 127}));
  connect(mppi_1_weighted_sum.y, mppi_1_solution.u1) 
    annotation(Line(points = {{1006, -182}, {959.5, -182}, {959.5, -90}, {913, -90}}, color = {0, 0, 127}));
  connect(mppi_1_weight_sum.y, mppi_1_solution.u2) 
    annotation(Line(points = {{1019, -252}, {1019, -176}, {900, -176}, {900, -100}}, color = {0, 0, 127}));
  connect(mppi_1_solution.y, unconstrained_command_y.u1) 
    annotation(Line(points = {{913, -90}, {959.5, -90}, {959.5, -112}, {1006, -112}}, color = {0, 0, 127}));
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
  connect(linear_solution_z.y, mppi_2_sample0_candidate.u1) 
    annotation(Line(points = {{-532, -554}, {-532, -448}, {-361, -448}, {-361, -342}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_noise.y, mppi_2_sample0_candidate.u2) 
    annotation(Line(points = {{-467, -310}, {-420.5, -310}, {-420.5, -332}, {-374, -332}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample0_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -245}, {-323, -245}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_half_h2_acc.u) 
    annotation(Line(points = {{-348, -332}, {-335.5, -332}, {-335.5, -290}, {-323, -290}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample0_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -277}, {-204, -277}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_h_ev.y, mppi_2_sample0_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -245}, {-250.5, -245}, {-250.5, -277}, {-204, -277}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_predicted_position_error_stage1.y, mppi_2_sample0_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -277}, {-174, -277}, {-174, -299}, {-170, -299}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_half_h2_acc.y, mppi_2_sample0_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -290}, {-233.5, -290}, {-233.5, -299}, {-170, -299}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_h_acc.u) 
    annotation(Line(points = {{-348, -332}, {-335.5, -332}, {-335.5, -345}, {-323, -345}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample0_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -367}, {-204, -367}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_h_acc.y, mppi_2_sample0_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -345}, {-250.5, -345}, {-250.5, -367}, {-204, -367}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_predicted_position_error.y, mppi_2_sample0_position_error_squared.u1) 
    annotation(Line(points = {{-157, -289}, {-157, -277}, {-140, -277}, {-140, -265}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_predicted_position_error.y, mppi_2_sample0_position_error_squared.u2) 
    annotation(Line(points = {{-157, -289}, {-157, -277}, {-140, -277}, {-140, -265}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_predicted_velocity_error.y, mppi_2_sample0_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -357}, {-191, -338.5}, {-140, -338.5}, {-140, -320}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_predicted_velocity_error.y, mppi_2_sample0_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -357}, {-191, -338.5}, {-140, -338.5}, {-140, -320}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -332}, {-250.5, -332}, {-250.5, -365}, {-153, -365}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -332}, {-250.5, -332}, {-250.5, -365}, {-153, -365}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_position_error_squared.y, mppi_2_sample0_position_cost.u) 
    annotation(Line(points = {{-127, -255}, {-68, -255}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_velocity_error_squared.y, mppi_2_sample0_velocity_cost.u) 
    annotation(Line(points = {{-127, -310}, {-68, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_acceleration_squared.y, mppi_2_sample0_control_cost.u) 
    annotation(Line(points = {{-127, -365}, {-68, -365}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_position_cost.y, mppi_2_sample0_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -255}, {4.5, -255}, {4.5, -332}, {51, -332}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_velocity_cost.y, mppi_2_sample0_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -310}, {4.5, -310}, {4.5, -332}, {51, -332}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_stage_cost_stage1.y, mppi_2_sample0_stage_cost.u1) 
    annotation(Line(points = {{77, -332}, {81, -332}, {81, -354}, {85, -354}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_control_cost.y, mppi_2_sample0_stage_cost.u2) 
    annotation(Line(points = {{-42, -365}, {21.5, -365}, {21.5, -354}, {85, -354}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample1_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -397}, {-374, -397}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_noise.y, mppi_2_sample1_candidate.u2) 
    annotation(Line(points = {{-467, -375}, {-420.5, -375}, {-420.5, -397}, {-374, -397}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample1_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -310}, {-323, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_half_h2_acc.u) 
    annotation(Line(points = {{-348, -397}, {-335.5, -397}, {-335.5, -355}, {-323, -355}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample1_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -342}, {-204, -342}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_h_ev.y, mppi_2_sample1_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -310}, {-250.5, -310}, {-250.5, -342}, {-204, -342}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_predicted_position_error_stage1.y, mppi_2_sample1_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -342}, {-174, -342}, {-174, -364}, {-170, -364}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_half_h2_acc.y, mppi_2_sample1_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -355}, {-233.5, -355}, {-233.5, -364}, {-170, -364}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_h_acc.u) 
    annotation(Line(points = {{-348, -397}, {-335.5, -397}, {-335.5, -410}, {-323, -410}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample1_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -432}, {-204, -432}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_h_acc.y, mppi_2_sample1_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -410}, {-250.5, -410}, {-250.5, -432}, {-204, -432}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_predicted_position_error.y, mppi_2_sample1_position_error_squared.u1) 
    annotation(Line(points = {{-157, -354}, {-157, -342}, {-140, -342}, {-140, -330}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_predicted_position_error.y, mppi_2_sample1_position_error_squared.u2) 
    annotation(Line(points = {{-157, -354}, {-157, -342}, {-140, -342}, {-140, -330}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_predicted_velocity_error.y, mppi_2_sample1_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -422}, {-191, -403.5}, {-140, -403.5}, {-140, -385}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_predicted_velocity_error.y, mppi_2_sample1_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -422}, {-191, -403.5}, {-140, -403.5}, {-140, -385}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -397}, {-250.5, -397}, {-250.5, -430}, {-153, -430}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -397}, {-250.5, -397}, {-250.5, -430}, {-153, -430}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_position_error_squared.y, mppi_2_sample1_position_cost.u) 
    annotation(Line(points = {{-127, -320}, {-68, -320}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_velocity_error_squared.y, mppi_2_sample1_velocity_cost.u) 
    annotation(Line(points = {{-127, -375}, {-68, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_acceleration_squared.y, mppi_2_sample1_control_cost.u) 
    annotation(Line(points = {{-127, -430}, {-68, -430}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_position_cost.y, mppi_2_sample1_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -320}, {4.5, -320}, {4.5, -397}, {51, -397}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_velocity_cost.y, mppi_2_sample1_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -375}, {4.5, -375}, {4.5, -397}, {51, -397}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_stage_cost_stage1.y, mppi_2_sample1_stage_cost.u1) 
    annotation(Line(points = {{77, -397}, {81, -397}, {81, -419}, {85, -419}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_control_cost.y, mppi_2_sample1_stage_cost.u2) 
    annotation(Line(points = {{-42, -430}, {21.5, -430}, {21.5, -419}, {85, -419}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample2_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -462}, {-374, -462}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_noise.y, mppi_2_sample2_candidate.u2) 
    annotation(Line(points = {{-467, -440}, {-420.5, -440}, {-420.5, -462}, {-374, -462}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample2_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -375}, {-323, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_half_h2_acc.u) 
    annotation(Line(points = {{-348, -462}, {-335.5, -462}, {-335.5, -420}, {-323, -420}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample2_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -407}, {-204, -407}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_h_ev.y, mppi_2_sample2_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -375}, {-250.5, -375}, {-250.5, -407}, {-204, -407}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_predicted_position_error_stage1.y, mppi_2_sample2_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -407}, {-174, -407}, {-174, -429}, {-170, -429}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_half_h2_acc.y, mppi_2_sample2_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -420}, {-233.5, -420}, {-233.5, -429}, {-170, -429}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_h_acc.u) 
    annotation(Line(points = {{-348, -462}, {-335.5, -462}, {-335.5, -475}, {-323, -475}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample2_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -497}, {-204, -497}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_h_acc.y, mppi_2_sample2_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -475}, {-250.5, -475}, {-250.5, -497}, {-204, -497}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_predicted_position_error.y, mppi_2_sample2_position_error_squared.u1) 
    annotation(Line(points = {{-157, -419}, {-157, -407}, {-140, -407}, {-140, -395}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_predicted_position_error.y, mppi_2_sample2_position_error_squared.u2) 
    annotation(Line(points = {{-157, -419}, {-157, -407}, {-140, -407}, {-140, -395}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_predicted_velocity_error.y, mppi_2_sample2_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -487}, {-191, -468.5}, {-140, -468.5}, {-140, -450}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_predicted_velocity_error.y, mppi_2_sample2_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -487}, {-191, -468.5}, {-140, -468.5}, {-140, -450}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -462}, {-250.5, -462}, {-250.5, -495}, {-153, -495}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -462}, {-250.5, -462}, {-250.5, -495}, {-153, -495}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_position_error_squared.y, mppi_2_sample2_position_cost.u) 
    annotation(Line(points = {{-127, -385}, {-68, -385}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_velocity_error_squared.y, mppi_2_sample2_velocity_cost.u) 
    annotation(Line(points = {{-127, -440}, {-68, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_acceleration_squared.y, mppi_2_sample2_control_cost.u) 
    annotation(Line(points = {{-127, -495}, {-68, -495}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_position_cost.y, mppi_2_sample2_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -385}, {4.5, -385}, {4.5, -462}, {51, -462}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_velocity_cost.y, mppi_2_sample2_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -440}, {4.5, -440}, {4.5, -462}, {51, -462}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_stage_cost_stage1.y, mppi_2_sample2_stage_cost.u1) 
    annotation(Line(points = {{77, -462}, {81, -462}, {81, -484}, {85, -484}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_control_cost.y, mppi_2_sample2_stage_cost.u2) 
    annotation(Line(points = {{-42, -495}, {21.5, -495}, {21.5, -484}, {85, -484}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample3_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -527}, {-374, -527}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_noise.y, mppi_2_sample3_candidate.u2) 
    annotation(Line(points = {{-467, -505}, {-420.5, -505}, {-420.5, -527}, {-374, -527}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample3_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -440}, {-323, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_half_h2_acc.u) 
    annotation(Line(points = {{-348, -527}, {-335.5, -527}, {-335.5, -485}, {-323, -485}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample3_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -472}, {-204, -472}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_h_ev.y, mppi_2_sample3_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -440}, {-250.5, -440}, {-250.5, -472}, {-204, -472}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_predicted_position_error_stage1.y, mppi_2_sample3_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -472}, {-174, -472}, {-174, -494}, {-170, -494}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_half_h2_acc.y, mppi_2_sample3_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -485}, {-233.5, -485}, {-233.5, -494}, {-170, -494}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_h_acc.u) 
    annotation(Line(points = {{-348, -527}, {-335.5, -527}, {-335.5, -540}, {-323, -540}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample3_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -562}, {-204, -562}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_h_acc.y, mppi_2_sample3_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -540}, {-250.5, -540}, {-250.5, -562}, {-204, -562}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_predicted_position_error.y, mppi_2_sample3_position_error_squared.u1) 
    annotation(Line(points = {{-157, -484}, {-157, -472}, {-140, -472}, {-140, -460}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_predicted_position_error.y, mppi_2_sample3_position_error_squared.u2) 
    annotation(Line(points = {{-157, -484}, {-157, -472}, {-140, -472}, {-140, -460}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_predicted_velocity_error.y, mppi_2_sample3_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -552}, {-191, -533.5}, {-140, -533.5}, {-140, -515}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_predicted_velocity_error.y, mppi_2_sample3_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -552}, {-191, -533.5}, {-140, -533.5}, {-140, -515}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -527}, {-250.5, -527}, {-250.5, -560}, {-153, -560}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -527}, {-250.5, -527}, {-250.5, -560}, {-153, -560}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_position_error_squared.y, mppi_2_sample3_position_cost.u) 
    annotation(Line(points = {{-127, -450}, {-68, -450}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_velocity_error_squared.y, mppi_2_sample3_velocity_cost.u) 
    annotation(Line(points = {{-127, -505}, {-68, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_acceleration_squared.y, mppi_2_sample3_control_cost.u) 
    annotation(Line(points = {{-127, -560}, {-68, -560}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_position_cost.y, mppi_2_sample3_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -450}, {4.5, -450}, {4.5, -527}, {51, -527}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_velocity_cost.y, mppi_2_sample3_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -505}, {4.5, -505}, {4.5, -527}, {51, -527}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_stage_cost_stage1.y, mppi_2_sample3_stage_cost.u1) 
    annotation(Line(points = {{77, -527}, {81, -527}, {81, -549}, {85, -549}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_control_cost.y, mppi_2_sample3_stage_cost.u2) 
    annotation(Line(points = {{-42, -560}, {21.5, -560}, {21.5, -549}, {85, -549}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample4_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -592}, {-374, -592}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_noise.y, mppi_2_sample4_candidate.u2) 
    annotation(Line(points = {{-467, -570}, {-420.5, -570}, {-420.5, -592}, {-374, -592}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample4_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -505}, {-323, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_half_h2_acc.u) 
    annotation(Line(points = {{-348, -592}, {-335.5, -592}, {-335.5, -550}, {-323, -550}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample4_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -537}, {-204, -537}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_h_ev.y, mppi_2_sample4_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -505}, {-250.5, -505}, {-250.5, -537}, {-204, -537}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_predicted_position_error_stage1.y, mppi_2_sample4_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -537}, {-174, -537}, {-174, -559}, {-170, -559}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_half_h2_acc.y, mppi_2_sample4_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -550}, {-233.5, -550}, {-233.5, -559}, {-170, -559}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_h_acc.u) 
    annotation(Line(points = {{-348, -592}, {-335.5, -592}, {-335.5, -605}, {-323, -605}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample4_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -627}, {-204, -627}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_h_acc.y, mppi_2_sample4_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -605}, {-250.5, -605}, {-250.5, -627}, {-204, -627}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_predicted_position_error.y, mppi_2_sample4_position_error_squared.u1) 
    annotation(Line(points = {{-157, -549}, {-157, -537}, {-140, -537}, {-140, -525}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_predicted_position_error.y, mppi_2_sample4_position_error_squared.u2) 
    annotation(Line(points = {{-157, -549}, {-157, -537}, {-140, -537}, {-140, -525}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_predicted_velocity_error.y, mppi_2_sample4_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -617}, {-191, -598.5}, {-140, -598.5}, {-140, -580}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_predicted_velocity_error.y, mppi_2_sample4_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -617}, {-191, -598.5}, {-140, -598.5}, {-140, -580}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -592}, {-250.5, -592}, {-250.5, -625}, {-153, -625}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -592}, {-250.5, -592}, {-250.5, -625}, {-153, -625}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_position_error_squared.y, mppi_2_sample4_position_cost.u) 
    annotation(Line(points = {{-127, -515}, {-68, -515}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_velocity_error_squared.y, mppi_2_sample4_velocity_cost.u) 
    annotation(Line(points = {{-127, -570}, {-68, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_acceleration_squared.y, mppi_2_sample4_control_cost.u) 
    annotation(Line(points = {{-127, -625}, {-68, -625}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_position_cost.y, mppi_2_sample4_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -515}, {4.5, -515}, {4.5, -592}, {51, -592}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_velocity_cost.y, mppi_2_sample4_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -570}, {4.5, -570}, {4.5, -592}, {51, -592}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_stage_cost_stage1.y, mppi_2_sample4_stage_cost.u1) 
    annotation(Line(points = {{77, -592}, {81, -592}, {81, -614}, {85, -614}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_control_cost.y, mppi_2_sample4_stage_cost.u2) 
    annotation(Line(points = {{-42, -625}, {21.5, -625}, {21.5, -614}, {85, -614}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample5_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -657}, {-374, -657}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_noise.y, mppi_2_sample5_candidate.u2) 
    annotation(Line(points = {{-467, -635}, {-420.5, -635}, {-420.5, -657}, {-374, -657}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample5_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -570}, {-323, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_half_h2_acc.u) 
    annotation(Line(points = {{-348, -657}, {-335.5, -657}, {-335.5, -615}, {-323, -615}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample5_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -602}, {-204, -602}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_h_ev.y, mppi_2_sample5_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -570}, {-250.5, -570}, {-250.5, -602}, {-204, -602}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_predicted_position_error_stage1.y, mppi_2_sample5_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -602}, {-174, -602}, {-174, -624}, {-170, -624}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_half_h2_acc.y, mppi_2_sample5_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -615}, {-233.5, -615}, {-233.5, -624}, {-170, -624}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_h_acc.u) 
    annotation(Line(points = {{-348, -657}, {-335.5, -657}, {-335.5, -670}, {-323, -670}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample5_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -692}, {-204, -692}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_h_acc.y, mppi_2_sample5_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -670}, {-250.5, -670}, {-250.5, -692}, {-204, -692}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_predicted_position_error.y, mppi_2_sample5_position_error_squared.u1) 
    annotation(Line(points = {{-157, -614}, {-157, -602}, {-140, -602}, {-140, -590}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_predicted_position_error.y, mppi_2_sample5_position_error_squared.u2) 
    annotation(Line(points = {{-157, -614}, {-157, -602}, {-140, -602}, {-140, -590}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_predicted_velocity_error.y, mppi_2_sample5_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -682}, {-191, -663.5}, {-140, -663.5}, {-140, -645}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_predicted_velocity_error.y, mppi_2_sample5_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -682}, {-191, -663.5}, {-140, -663.5}, {-140, -645}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -657}, {-250.5, -657}, {-250.5, -690}, {-153, -690}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -657}, {-250.5, -657}, {-250.5, -690}, {-153, -690}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_position_error_squared.y, mppi_2_sample5_position_cost.u) 
    annotation(Line(points = {{-127, -580}, {-68, -580}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_velocity_error_squared.y, mppi_2_sample5_velocity_cost.u) 
    annotation(Line(points = {{-127, -635}, {-68, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_acceleration_squared.y, mppi_2_sample5_control_cost.u) 
    annotation(Line(points = {{-127, -690}, {-68, -690}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_position_cost.y, mppi_2_sample5_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -580}, {4.5, -580}, {4.5, -657}, {51, -657}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_velocity_cost.y, mppi_2_sample5_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -635}, {4.5, -635}, {4.5, -657}, {51, -657}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_stage_cost_stage1.y, mppi_2_sample5_stage_cost.u1) 
    annotation(Line(points = {{77, -657}, {81, -657}, {81, -679}, {85, -679}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_control_cost.y, mppi_2_sample5_stage_cost.u2) 
    annotation(Line(points = {{-42, -690}, {21.5, -690}, {21.5, -679}, {85, -679}}, color = {0, 0, 127}));
  connect(linear_solution_z.y, mppi_2_sample6_candidate.u1) 
    annotation(Line(points = {{-519, -564}, {-446.5, -564}, {-446.5, -722}, {-374, -722}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_noise.y, mppi_2_sample6_candidate.u2) 
    annotation(Line(points = {{-467, -700}, {-420.5, -700}, {-420.5, -722}, {-374, -722}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample6_h_ev.u) 
    annotation(Line(points = {{-733, -597}, {-528, -597}, {-528, -635}, {-323, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_half_h2_acc.u) 
    annotation(Line(points = {{-348, -722}, {-335.5, -722}, {-335.5, -680}, {-323, -680}}, color = {0, 0, 127}));
  connect(position_error_z.y, mppi_2_sample6_predicted_position_error_stage1.u1) 
    annotation(Line(points = {{-733, -487}, {-468.5, -487}, {-468.5, -667}, {-204, -667}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_h_ev.y, mppi_2_sample6_predicted_position_error_stage1.u2) 
    annotation(Line(points = {{-297, -635}, {-250.5, -635}, {-250.5, -667}, {-204, -667}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_predicted_position_error_stage1.y, mppi_2_sample6_predicted_position_error.u1) 
    annotation(Line(points = {{-178, -667}, {-174, -667}, {-174, -689}, {-170, -689}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_half_h2_acc.y, mppi_2_sample6_predicted_position_error.u2) 
    annotation(Line(points = {{-297, -680}, {-233.5, -680}, {-233.5, -689}, {-170, -689}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_h_acc.u) 
    annotation(Line(points = {{-348, -722}, {-335.5, -722}, {-335.5, -735}, {-323, -735}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, mppi_2_sample6_predicted_velocity_error.u1) 
    annotation(Line(points = {{-733, -597}, {-468.5, -597}, {-468.5, -757}, {-204, -757}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_h_acc.y, mppi_2_sample6_predicted_velocity_error.u2) 
    annotation(Line(points = {{-297, -735}, {-250.5, -735}, {-250.5, -757}, {-204, -757}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_predicted_position_error.y, mppi_2_sample6_position_error_squared.u1) 
    annotation(Line(points = {{-157, -679}, {-157, -667}, {-140, -667}, {-140, -655}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_predicted_position_error.y, mppi_2_sample6_position_error_squared.u2) 
    annotation(Line(points = {{-157, -679}, {-157, -667}, {-140, -667}, {-140, -655}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_predicted_velocity_error.y, mppi_2_sample6_velocity_error_squared.u1) 
    annotation(Line(points = {{-191, -747}, {-191, -728.5}, {-140, -728.5}, {-140, -710}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_predicted_velocity_error.y, mppi_2_sample6_velocity_error_squared.u2) 
    annotation(Line(points = {{-191, -747}, {-191, -728.5}, {-140, -728.5}, {-140, -710}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_acceleration_squared.u1) 
    annotation(Line(points = {{-348, -722}, {-250.5, -722}, {-250.5, -755}, {-153, -755}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_acceleration_squared.u2) 
    annotation(Line(points = {{-348, -722}, {-250.5, -722}, {-250.5, -755}, {-153, -755}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_position_error_squared.y, mppi_2_sample6_position_cost.u) 
    annotation(Line(points = {{-127, -645}, {-68, -645}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_velocity_error_squared.y, mppi_2_sample6_velocity_cost.u) 
    annotation(Line(points = {{-127, -700}, {-68, -700}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_acceleration_squared.y, mppi_2_sample6_control_cost.u) 
    annotation(Line(points = {{-127, -755}, {-68, -755}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_position_cost.y, mppi_2_sample6_stage_cost_stage1.u1) 
    annotation(Line(points = {{-42, -645}, {4.5, -645}, {4.5, -722}, {51, -722}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_velocity_cost.y, mppi_2_sample6_stage_cost_stage1.u2) 
    annotation(Line(points = {{-42, -700}, {4.5, -700}, {4.5, -722}, {51, -722}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_stage_cost_stage1.y, mppi_2_sample6_stage_cost.u1) 
    annotation(Line(points = {{77, -722}, {81, -722}, {81, -744}, {85, -744}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_control_cost.y, mppi_2_sample6_stage_cost.u2) 
    annotation(Line(points = {{-42, -755}, {21.5, -755}, {21.5, -744}, {85, -744}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_stage_cost.y, mppi_2_minimum_cost_stage1.u1) 
    annotation(Line(points = {{111, -354}, {265, -354}, {265, -323}, {419, -323}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_stage_cost.y, mppi_2_minimum_cost_stage1.u2) 
    annotation(Line(points = {{111, -419}, {265, -419}, {265, -323}, {419, -323}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage1.y, mppi_2_minimum_cost_stage2.u1) 
    annotation(Line(points = {{445, -323}, {453, -323}, {453, -351}, {461, -351}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_stage_cost.y, mppi_2_minimum_cost_stage2.u2) 
    annotation(Line(points = {{111, -484}, {286, -484}, {286, -351}, {461, -351}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage2.y, mppi_2_minimum_cost_stage3.u1) 
    annotation(Line(points = {{487, -351}, {495, -351}, {495, -379}, {503, -379}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_stage_cost.y, mppi_2_minimum_cost_stage3.u2) 
    annotation(Line(points = {{111, -549}, {307, -549}, {307, -379}, {503, -379}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage3.y, mppi_2_minimum_cost_stage4.u1) 
    annotation(Line(points = {{529, -379}, {537, -379}, {537, -407}, {545, -407}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_stage_cost.y, mppi_2_minimum_cost_stage4.u2) 
    annotation(Line(points = {{111, -614}, {328, -614}, {328, -407}, {545, -407}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage4.y, mppi_2_minimum_cost_stage5.u1) 
    annotation(Line(points = {{571, -407}, {579, -407}, {579, -435}, {587, -435}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_stage_cost.y, mppi_2_minimum_cost_stage5.u2) 
    annotation(Line(points = {{111, -679}, {349, -679}, {349, -435}, {587, -435}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage5.y, mppi_2_minimum_cost_stage6.u1) 
    annotation(Line(points = {{613, -435}, {621, -435}, {621, -463}, {629, -463}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_stage_cost.y, mppi_2_minimum_cost_stage6.u2) 
    annotation(Line(points = {{111, -744}, {370, -744}, {370, -463}, {629, -463}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_stage_cost.y, mppi_2_sample0_cost_delta.u1) 
    annotation(Line(points = {{111, -354}, {303.5, -354}, {303.5, -332}, {496, -332}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample0_cost_delta.u2) 
    annotation(Line(points = {{629, -463}, {575.5, -463}, {575.5, -332}, {522, -332}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_cost_delta.y, mppi_2_sample0_exponent.u) 
    annotation(Line(points = {{522, -332}, {534.5, -332}, {534.5, -310}, {547, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_exponent.y, mppi_2_sample0_weight.u1) 
    annotation(Line(points = {{573, -310}, {632, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_weight.y, mppi_2_sample0_weighted_candidate.u1) 
    annotation(Line(points = {{658, -310}, {717, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_candidate.y, mppi_2_sample0_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -332}, {184.5, -332}, {184.5, -310}, {717, -310}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_stage_cost.y, mppi_2_sample1_cost_delta.u1) 
    annotation(Line(points = {{111, -419}, {303.5, -419}, {303.5, -397}, {496, -397}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample1_cost_delta.u2) 
    annotation(Line(points = {{629, -463}, {575.5, -463}, {575.5, -397}, {522, -397}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_cost_delta.y, mppi_2_sample1_exponent.u) 
    annotation(Line(points = {{522, -397}, {534.5, -397}, {534.5, -375}, {547, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_exponent.y, mppi_2_sample1_weight.u1) 
    annotation(Line(points = {{573, -375}, {632, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_weight.y, mppi_2_sample1_weighted_candidate.u1) 
    annotation(Line(points = {{658, -375}, {717, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_candidate.y, mppi_2_sample1_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -397}, {184.5, -397}, {184.5, -375}, {717, -375}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_stage_cost.y, mppi_2_sample2_cost_delta.u1) 
    annotation(Line(points = {{111, -484}, {303.5, -484}, {303.5, -462}, {496, -462}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample2_cost_delta.u2) 
    annotation(Line(points = {{629, -463}, {575.5, -463}, {575.5, -462}, {522, -462}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_cost_delta.y, mppi_2_sample2_exponent.u) 
    annotation(Line(points = {{522, -462}, {534.5, -462}, {534.5, -440}, {547, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_exponent.y, mppi_2_sample2_weight.u1) 
    annotation(Line(points = {{573, -440}, {632, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_weight.y, mppi_2_sample2_weighted_candidate.u1) 
    annotation(Line(points = {{658, -440}, {717, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_candidate.y, mppi_2_sample2_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -462}, {184.5, -462}, {184.5, -440}, {717, -440}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_stage_cost.y, mppi_2_sample3_cost_delta.u1) 
    annotation(Line(points = {{111, -549}, {303.5, -549}, {303.5, -527}, {496, -527}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample3_cost_delta.u2) 
    annotation(Line(points = {{629, -463}, {575.5, -463}, {575.5, -527}, {522, -527}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_cost_delta.y, mppi_2_sample3_exponent.u) 
    annotation(Line(points = {{522, -527}, {534.5, -527}, {534.5, -505}, {547, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_exponent.y, mppi_2_sample3_weight.u1) 
    annotation(Line(points = {{573, -505}, {632, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_weight.y, mppi_2_sample3_weighted_candidate.u1) 
    annotation(Line(points = {{658, -505}, {717, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_candidate.y, mppi_2_sample3_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -527}, {184.5, -527}, {184.5, -505}, {717, -505}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_stage_cost.y, mppi_2_sample4_cost_delta.u1) 
    annotation(Line(points = {{111, -614}, {303.5, -614}, {303.5, -592}, {496, -592}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample4_cost_delta.u2) 
    annotation(Line(points = {{629, -463}, {575.5, -463}, {575.5, -592}, {522, -592}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_cost_delta.y, mppi_2_sample4_exponent.u) 
    annotation(Line(points = {{522, -592}, {534.5, -592}, {534.5, -570}, {547, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_exponent.y, mppi_2_sample4_weight.u1) 
    annotation(Line(points = {{573, -570}, {632, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_weight.y, mppi_2_sample4_weighted_candidate.u1) 
    annotation(Line(points = {{658, -570}, {717, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_candidate.y, mppi_2_sample4_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -592}, {184.5, -592}, {184.5, -570}, {717, -570}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_stage_cost.y, mppi_2_sample5_cost_delta.u1) 
    annotation(Line(points = {{111, -679}, {303.5, -679}, {303.5, -657}, {496, -657}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample5_cost_delta.u2) 
    annotation(Line(points = {{642, -473}, {642, -560}, {509, -560}, {509, -647}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_cost_delta.y, mppi_2_sample5_exponent.u) 
    annotation(Line(points = {{522, -657}, {534.5, -657}, {534.5, -635}, {547, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_exponent.y, mppi_2_sample5_weight.u1) 
    annotation(Line(points = {{573, -635}, {632, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_weight.y, mppi_2_sample5_weighted_candidate.u1) 
    annotation(Line(points = {{658, -635}, {717, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_candidate.y, mppi_2_sample5_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -657}, {184.5, -657}, {184.5, -635}, {717, -635}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_stage_cost.y, mppi_2_sample6_cost_delta.u1) 
    annotation(Line(points = {{111, -744}, {303.5, -744}, {303.5, -722}, {496, -722}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, mppi_2_sample6_cost_delta.u2) 
    annotation(Line(points = {{642, -473}, {642, -592.5}, {509, -592.5}, {509, -712}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_cost_delta.y, mppi_2_sample6_exponent.u) 
    annotation(Line(points = {{522, -722}, {534.5, -722}, {534.5, -700}, {547, -700}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_exponent.y, mppi_2_sample6_weight.u1) 
    annotation(Line(points = {{573, -700}, {632, -700}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_weight.y, mppi_2_sample6_weighted_candidate.u1) 
    annotation(Line(points = {{658, -700}, {717, -700}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_candidate.y, mppi_2_sample6_weighted_candidate.u2) 
    annotation(Line(points = {{-348, -722}, {184.5, -722}, {184.5, -700}, {717, -700}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_weighted_candidate.y, mppi_2_weighted_sum_stage1.u1) 
    annotation(Line(points = {{730, -320}, {730, -406}, {849, -406}, {849, -492}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_weighted_candidate.y, mppi_2_weighted_sum_stage1.u2) 
    annotation(Line(points = {{730, -385}, {730, -438.5}, {849, -438.5}, {849, -492}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum_stage1.y, mppi_2_weighted_sum_stage2.u1) 
    annotation(Line(points = {{862, -502}, {866, -502}, {866, -524}, {870, -524}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_weighted_candidate.y, mppi_2_weighted_sum_stage2.u2) 
    annotation(Line(points = {{743, -440}, {806.5, -440}, {806.5, -524}, {870, -524}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum_stage2.y, mppi_2_weighted_sum_stage3.u1) 
    annotation(Line(points = {{896, -524}, {900, -524}, {900, -546}, {904, -546}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_weighted_candidate.y, mppi_2_weighted_sum_stage3.u2) 
    annotation(Line(points = {{743, -505}, {823.5, -505}, {823.5, -546}, {904, -546}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum_stage3.y, mppi_2_weighted_sum_stage4.u1) 
    annotation(Line(points = {{930, -546}, {934, -546}, {934, -568}, {938, -568}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_weighted_candidate.y, mppi_2_weighted_sum_stage4.u2) 
    annotation(Line(points = {{743, -570}, {840.5, -570}, {840.5, -568}, {938, -568}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum_stage4.y, mppi_2_weighted_sum_stage5.u1) 
    annotation(Line(points = {{964, -568}, {968, -568}, {968, -590}, {972, -590}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_weighted_candidate.y, mppi_2_weighted_sum_stage5.u2) 
    annotation(Line(points = {{743, -635}, {857.5, -635}, {857.5, -590}, {972, -590}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum_stage5.y, mppi_2_weighted_sum.u1) 
    annotation(Line(points = {{998, -590}, {1002, -590}, {1002, -612}, {1006, -612}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_weighted_candidate.y, mppi_2_weighted_sum.u2) 
    annotation(Line(points = {{743, -700}, {874.5, -700}, {874.5, -612}, {1006, -612}}, color = {0, 0, 127}));
  connect(mppi_2_sample0_weight.y, mppi_2_weight_sum_stage1.u1) 
    annotation(Line(points = {{645, -320}, {645, -446}, {849, -446}, {849, -572}}, color = {0, 0, 127}));
  connect(mppi_2_sample1_weight.y, mppi_2_weight_sum_stage1.u2) 
    annotation(Line(points = {{645, -385}, {645, -478.5}, {849, -478.5}, {849, -572}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum_stage1.y, mppi_2_weight_sum_stage2.u1) 
    annotation(Line(points = {{862, -582}, {866, -582}, {866, -604}, {870, -604}}, color = {0, 0, 127}));
  connect(mppi_2_sample2_weight.y, mppi_2_weight_sum_stage2.u2) 
    annotation(Line(points = {{658, -440}, {764, -440}, {764, -604}, {870, -604}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum_stage2.y, mppi_2_weight_sum_stage3.u1) 
    annotation(Line(points = {{896, -604}, {900, -604}, {900, -626}, {904, -626}}, color = {0, 0, 127}));
  connect(mppi_2_sample3_weight.y, mppi_2_weight_sum_stage3.u2) 
    annotation(Line(points = {{658, -505}, {781, -505}, {781, -626}, {904, -626}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum_stage3.y, mppi_2_weight_sum_stage4.u1) 
    annotation(Line(points = {{930, -626}, {934, -626}, {934, -648}, {938, -648}}, color = {0, 0, 127}));
  connect(mppi_2_sample4_weight.y, mppi_2_weight_sum_stage4.u2) 
    annotation(Line(points = {{658, -570}, {798, -570}, {798, -648}, {938, -648}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum_stage4.y, mppi_2_weight_sum_stage5.u1) 
    annotation(Line(points = {{964, -648}, {968, -648}, {968, -670}, {972, -670}}, color = {0, 0, 127}));
  connect(mppi_2_sample5_weight.y, mppi_2_weight_sum_stage5.u2) 
    annotation(Line(points = {{658, -635}, {815, -635}, {815, -670}, {972, -670}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum_stage5.y, mppi_2_weight_sum.u1) 
    annotation(Line(points = {{998, -670}, {1002, -670}, {1002, -692}, {1006, -692}}, color = {0, 0, 127}));
  connect(mppi_2_sample6_weight.y, mppi_2_weight_sum.u2) 
    annotation(Line(points = {{658, -700}, {832, -700}, {832, -692}, {1006, -692}}, color = {0, 0, 127}));
  connect(mppi_2_weighted_sum.y, mppi_2_solution.u1) 
    annotation(Line(points = {{1006, -612}, {959.5, -612}, {959.5, -520}, {913, -520}}, color = {0, 0, 127}));
  connect(mppi_2_weight_sum.y, mppi_2_solution.u2) 
    annotation(Line(points = {{1019, -682}, {1019, -606}, {900, -606}, {900, -530}}, color = {0, 0, 127}));
  connect(mppi_2_solution.y, unconstrained_command_z.u1) 
    annotation(Line(points = {{913, -520}, {959.5, -520}, {959.5, -542}, {1006, -542}}, color = {0, 0, 127}));
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
  connect(mppi_0_minimum_cost_stage6.y, solver_cost_sum_stage1.u1) 
    annotation(Line(points = {{642, 387}, {642, -277.5}, {1544, -277.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(mppi_1_minimum_cost_stage6.y, solver_cost_sum_stage1.u2) 
    annotation(Line(points = {{642, -43}, {642, -492.5}, {1544, -492.5}, {1544, -942}}, color = {0, 0, 127}));
  connect(solver_cost_sum_stage1.y, solver_cost_sum.u1) 
    annotation(Line(points = {{1557, -952}, {1561, -952}, {1561, -974}, {1565, -974}}, color = {0, 0, 127}));
  connect(mppi_2_minimum_cost_stage6.y, solver_cost_sum.u2) 
    annotation(Line(points = {{655, -463}, {1110, -463}, {1110, -974}, {1565, -974}}, color = {0, 0, 127}));
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
  end MppiCore;
