within MoSimQuadrotorModel.Control.SlidingMode.SuperTwistingSmc;
model SuperTwistingSmcCore "P3 native graphical sliding-mode controller core: super_twisting_smc"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(desired_acceleration_x, desired_acceleration_y, desired_acceleration_z, sliding_surface_x, sliding_surface_y, sliding_surface_z, auxiliary_state_x, auxiliary_state_y, auxiliary_state_z, effective_reaching_gain_x, effective_reaching_gain_y, effective_reaching_gain_z)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant position_x(k=0.2) 
    annotation (Placement(transformation(origin = {-700, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_y(k=-0.1) 
    annotation (Placement(transformation(origin = {-645, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_z(k=0.7) 
    annotation (Placement(transformation(origin = {-590, 420}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_x(k=-0.3) 
    annotation (Placement(transformation(origin = {-700, 365}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_y(k=0.2) 
    annotation (Placement(transformation(origin = {-645, 365}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant velocity_z(k=-0.1) 
    annotation (Placement(transformation(origin = {-590, 365}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_x(k=1.0) 
    annotation (Placement(transformation(origin = {-700, 310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_y(k=0.5) 
    annotation (Placement(transformation(origin = {-645, 310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_position_z(k=1.2) 
    annotation (Placement(transformation(origin = {-590, 310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_x(k=0.1) 
    annotation (Placement(transformation(origin = {-700, 255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_y(k=-0.2) 
    annotation (Placement(transformation(origin = {-645, 255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_velocity_z(k=0.0) 
    annotation (Placement(transformation(origin = {-590, 255}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_x(k=0.05) 
    annotation (Placement(transformation(origin = {-700, 200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_y(k=-0.04) 
    annotation (Placement(transformation(origin = {-645, 200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant reference_acceleration_z(k=0.02) 
    annotation (Placement(transformation(origin = {-590, 200}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, 310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, 210}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_position_x(k=1.2) 
    annotation (Placement(transformation(origin = {-445, 310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_sliding_surface_x(inputs="++") 
    annotation (Placement(transformation(origin = {-360, 260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant zero_x(k=0.0) 
    annotation (Placement(transformation(origin = {235, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant nominal_reaching_gain_x(k=2.2) 
    annotation (Placement(transformation(origin = {-95, 390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_x(k=8.333333333333334) 
    annotation (Placement(transformation(origin = {5, 260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_x(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, 260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay super_twisting_integral_x(initCond=0.0)
    "P3 distinguishing state or nonlinear surface for super_twisting_smc" annotation (Placement(transformation(origin = {5, 395}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_increment_x(k=0.012) 
    annotation (Placement(transformation(origin = {90, 395}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_next_raw_x(inputs="++") 
    annotation (Placement(transformation(origin = {175, 395}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation super_twisting_limit_x(lowLimit=-5.0,upLimit=5.0) 
    annotation (Placement(transformation(origin = {260, 395}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_x 
    annotation (Placement(transformation(origin = {5, 165}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction sliding_sqrt_x(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {90, 165}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant sliding_sqrt_x_exponent(k=0.5) 
    annotation (Placement(transformation(origin = {60, 135}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_sliding_root_x(inputs="**") 
    annotation (Placement(transformation(origin = {175, 185}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_root_gain_x(k=1.6) 
    annotation (Placement(transformation(origin = {260, 185}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_robust_x(inputs="++") 
    annotation (Placement(transformation(origin = {345, 260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant super_twisting_gain_x(k=1.6) 
    annotation (Placement(transformation(origin = {345, 355}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_velocity_x(k=1.2) 
    annotation (Placement(transformation(origin = {430, 140}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_surface_gain_x(k=0.8) 
    annotation (Placement(transformation(origin = {430, 190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedforward_velocity_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {500, 125}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_robust_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {500, 195}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_x(inputs="++") 
    annotation (Placement(transformation(origin = {585, 165}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, 0}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, -100}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_position_y(k=1.2) 
    annotation (Placement(transformation(origin = {-445, 0}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_sliding_surface_y(inputs="++") 
    annotation (Placement(transformation(origin = {-360, -50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant zero_y(k=0.0) 
    annotation (Placement(transformation(origin = {235, 45}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant nominal_reaching_gain_y(k=2.2) 
    annotation (Placement(transformation(origin = {-95, 80}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_y(k=8.333333333333334) 
    annotation (Placement(transformation(origin = {5, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_y(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay super_twisting_integral_y(initCond=0.0) 
    annotation (Placement(transformation(origin = {5, 85}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_increment_y(k=0.012) 
    annotation (Placement(transformation(origin = {90, 85}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_next_raw_y(inputs="++") 
    annotation (Placement(transformation(origin = {175, 85}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation super_twisting_limit_y(lowLimit=-5.0,upLimit=5.0) 
    annotation (Placement(transformation(origin = {260, 85}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_y 
    annotation (Placement(transformation(origin = {5, -145}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction sliding_sqrt_y(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {90, -145}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant sliding_sqrt_y_exponent(k=0.5) 
    annotation (Placement(transformation(origin = {60, -175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_sliding_root_y(inputs="**") 
    annotation (Placement(transformation(origin = {175, -125}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_root_gain_y(k=1.6) 
    annotation (Placement(transformation(origin = {260, -125}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_robust_y(inputs="++") 
    annotation (Placement(transformation(origin = {345, -50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant super_twisting_gain_y(k=1.6) 
    annotation (Placement(transformation(origin = {345, 45}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_velocity_y(k=1.2) 
    annotation (Placement(transformation(origin = {430, -170}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_surface_gain_y(k=0.8) 
    annotation (Placement(transformation(origin = {430, -120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedforward_velocity_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {500, -185}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_robust_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {500, -115}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_y(inputs="++") 
    annotation (Placement(transformation(origin = {585, -145}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, -310}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(inputs="+-") 
    annotation (Placement(transformation(origin = {-530, -410}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_position_z(k=1.4) 
    annotation (Placement(transformation(origin = {-445, -310}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_sliding_surface_z(inputs="++") 
    annotation (Placement(transformation(origin = {-360, -360}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant zero_z(k=0.0) 
    annotation (Placement(transformation(origin = {235, -265}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant nominal_reaching_gain_z(k=2.8) 
    annotation (Placement(transformation(origin = {-95, -230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_z(k=6.666666666666667) 
    annotation (Placement(transformation(origin = {5, -360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_z(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, -360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay super_twisting_integral_z(initCond=0.0) 
    annotation (Placement(transformation(origin = {5, -225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_increment_z(k=0.015) 
    annotation (Placement(transformation(origin = {90, -225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_next_raw_z(inputs="++") 
    annotation (Placement(transformation(origin = {175, -225}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation super_twisting_limit_z(lowLimit=-6.0,upLimit=6.0) 
    annotation (Placement(transformation(origin = {260, -225}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_z 
    annotation (Placement(transformation(origin = {5, -455}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction sliding_sqrt_z(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {90, -455}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant sliding_sqrt_z_exponent(k=0.5) 
    annotation (Placement(transformation(origin = {60, -485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_sliding_root_z(inputs="**") 
    annotation (Placement(transformation(origin = {175, -435}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain super_twisting_root_gain_z(k=2.0) 
    annotation (Placement(transformation(origin = {260, -435}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum super_twisting_robust_z(inputs="++") 
    annotation (Placement(transformation(origin = {345, -360}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant super_twisting_gain_z(k=2.0) 
    annotation (Placement(transformation(origin = {345, -265}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain lambda_velocity_z(k=1.4) 
    annotation (Placement(transformation(origin = {430, -480}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain linear_surface_gain_z(k=1.0) 
    annotation (Placement(transformation(origin = {430, -430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum feedforward_velocity_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {500, -495}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum linear_robust_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {500, -425}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum acceleration_sum_z(inputs="++") 
    annotation (Placement(transformation(origin = {585, -455}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant gravity(k=9.80665) 
    annotation (Placement(transformation(origin = {535, -315}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum gravity_compensation(inputs="++") 
    annotation (Placement(transformation(origin = {620, -370}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_x 
    annotation (Placement(transformation(origin = {720, 390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_y 
    annotation (Placement(transformation(origin = {720, 325}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acceleration_z 
    annotation (Placement(transformation(origin = {720, 260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_x 
    annotation (Placement(transformation(origin = {720, 195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_y 
    annotation (Placement(transformation(origin = {720, 130}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport sliding_surface_z 
    annotation (Placement(transformation(origin = {720, 65}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_x 
    annotation (Placement(transformation(origin = {720, 0}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_y 
    annotation (Placement(transformation(origin = {720, -65}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport auxiliary_state_z 
    annotation (Placement(transformation(origin = {720, -130}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_x 
    annotation (Placement(transformation(origin = {720, -195}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_y 
    annotation (Placement(transformation(origin = {720, -260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Port.Outport effective_reaching_gain_z 
    annotation (Placement(transformation(origin = {720, -325}, extent = {{-13, -10}, {13, 10}})));
equation
  connect(reference_position_x.y, position_error_x.u1) 
    annotation(Line(points = {{-687, 310}, {-543, 310}}, color = {0, 0, 127}));
  connect(position_x.y, position_error_x.u2) 
    annotation(Line(points = {{-687, 420}, {-615, 420}, {-615, 310}, {-543, 310}}, color = {0, 0, 127}));
  connect(reference_velocity_x.y, velocity_error_x.u1) 
    annotation(Line(points = {{-687, 255}, {-615, 255}, {-615, 210}, {-543, 210}}, color = {0, 0, 127}));
  connect(velocity_x.y, velocity_error_x.u2) 
    annotation(Line(points = {{-687, 365}, {-615, 365}, {-615, 210}, {-543, 210}}, color = {0, 0, 127}));
  connect(position_error_x.y, lambda_position_x.u) 
    annotation(Line(points = {{-517, 310}, {-458, 310}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, linear_sliding_surface_x.u1) 
    annotation(Line(points = {{-517, 210}, {-445, 210}, {-445, 260}, {-373, 260}}, color = {0, 0, 127}));
  connect(lambda_position_x.y, linear_sliding_surface_x.u2) 
    annotation(Line(points = {{-432, 310}, {-402.5, 310}, {-402.5, 260}, {-373, 260}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_x.y, boundary_normalization_x.u) 
    annotation(Line(points = {{-347, 260}, {-8, 260}}, color = {0, 0, 127}));
  connect(boundary_normalization_x.y, boundary_layer_x.u) 
    annotation(Line(points = {{18, 260}, {77, 260}}, color = {0, 0, 127}));
  connect(boundary_layer_x.y, super_twisting_increment_x.u) 
    annotation(Line(points = {{90, 270}, {90, 385}}, color = {0, 0, 127}));
  connect(super_twisting_integral_x.y, super_twisting_next_raw_x.u1) 
    annotation(Line(points = {{18, 395}, {162, 395}}, color = {0, 0, 127}));
  connect(super_twisting_increment_x.y, super_twisting_next_raw_x.u2) 
    annotation(Line(points = {{103, 395}, {162, 395}}, color = {0, 0, 127}));
  connect(super_twisting_next_raw_x.y, super_twisting_limit_x.u) 
    annotation(Line(points = {{188, 395}, {247, 395}}, color = {0, 0, 127}));
  connect(super_twisting_limit_x.y, super_twisting_integral_x.u1) 
    annotation(Line(points = {{247, 395}, {18, 395}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_x.y, sliding_abs_x.u) 
    annotation(Line(points = {{-347, 260}, {-177.5, 260}, {-177.5, 165}, {-8, 165}}, color = {0, 0, 127}));
  connect(sliding_abs_x.y, sliding_sqrt_x.u1) 
    annotation(Line(points = {{18, 165}, {77, 165}}, color = {0, 0, 127}));
  connect(sliding_sqrt_x_exponent.y, sliding_sqrt_x.u2) 
    annotation(Line(points = {{73, 135}, {75, 135}, {75, 165}, {77, 165}}, color = {0, 0, 127}));
  connect(sliding_sqrt_x.y, signed_sliding_root_x.u1) 
    annotation(Line(points = {{103, 165}, {132.5, 165}, {132.5, 185}, {162, 185}}, color = {0, 0, 127}));
  connect(boundary_layer_x.y, signed_sliding_root_x.u2) 
    annotation(Line(points = {{103, 260}, {132.5, 260}, {132.5, 185}, {162, 185}}, color = {0, 0, 127}));
  connect(signed_sliding_root_x.y, super_twisting_root_gain_x.u) 
    annotation(Line(points = {{188, 185}, {247, 185}}, color = {0, 0, 127}));
  connect(super_twisting_root_gain_x.y, super_twisting_robust_x.u1) 
    annotation(Line(points = {{273, 185}, {302.5, 185}, {302.5, 260}, {332, 260}}, color = {0, 0, 127}));
  connect(super_twisting_limit_x.y, super_twisting_robust_x.u2) 
    annotation(Line(points = {{260, 385}, {260, 327.5}, {345, 327.5}, {345, 270}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, lambda_velocity_x.u) 
    annotation(Line(points = {{-517, 210}, {-50, 210}, {-50, 140}, {417, 140}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_x.y, linear_surface_gain_x.u) 
    annotation(Line(points = {{-347, 260}, {35, 260}, {35, 190}, {417, 190}}, color = {0, 0, 127}));
  connect(reference_acceleration_x.y, feedforward_velocity_sum_x.u1) 
    annotation(Line(points = {{-687, 200}, {-100, 200}, {-100, 125}, {487, 125}}, color = {0, 0, 127}));
  connect(lambda_velocity_x.y, feedforward_velocity_sum_x.u2) 
    annotation(Line(points = {{443, 140}, {465, 140}, {465, 125}, {487, 125}}, color = {0, 0, 127}));
  connect(linear_surface_gain_x.y, linear_robust_sum_x.u1) 
    annotation(Line(points = {{443, 190}, {465, 190}, {465, 195}, {487, 195}}, color = {0, 0, 127}));
  connect(super_twisting_robust_x.y, linear_robust_sum_x.u2) 
    annotation(Line(points = {{358, 260}, {422.5, 260}, {422.5, 195}, {487, 195}}, color = {0, 0, 127}));
  connect(feedforward_velocity_sum_x.y, acceleration_sum_x.u1) 
    annotation(Line(points = {{513, 125}, {542.5, 125}, {542.5, 165}, {572, 165}}, color = {0, 0, 127}));
  connect(linear_robust_sum_x.y, acceleration_sum_x.u2) 
    annotation(Line(points = {{513, 195}, {542.5, 195}, {542.5, 165}, {572, 165}}, color = {0, 0, 127}));
  connect(reference_position_y.y, position_error_y.u1) 
    annotation(Line(points = {{-645, 300}, {-645, 155}, {-530, 155}, {-530, 10}}, color = {0, 0, 127}));
  connect(position_y.y, position_error_y.u2) 
    annotation(Line(points = {{-645, 410}, {-645, 210}, {-530, 210}, {-530, 10}}, color = {0, 0, 127}));
  connect(reference_velocity_y.y, velocity_error_y.u1) 
    annotation(Line(points = {{-645, 245}, {-645, 77.5}, {-530, 77.5}, {-530, -90}}, color = {0, 0, 127}));
  connect(velocity_y.y, velocity_error_y.u2) 
    annotation(Line(points = {{-645, 355}, {-645, 132.5}, {-530, 132.5}, {-530, -90}}, color = {0, 0, 127}));
  connect(position_error_y.y, lambda_position_y.u) 
    annotation(Line(points = {{-517, 0}, {-458, 0}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, linear_sliding_surface_y.u1) 
    annotation(Line(points = {{-517, -100}, {-445, -100}, {-445, -50}, {-373, -50}}, color = {0, 0, 127}));
  connect(lambda_position_y.y, linear_sliding_surface_y.u2) 
    annotation(Line(points = {{-432, 0}, {-402.5, 0}, {-402.5, -50}, {-373, -50}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_y.y, boundary_normalization_y.u) 
    annotation(Line(points = {{-347, -50}, {-8, -50}}, color = {0, 0, 127}));
  connect(boundary_normalization_y.y, boundary_layer_y.u) 
    annotation(Line(points = {{18, -50}, {77, -50}}, color = {0, 0, 127}));
  connect(boundary_layer_y.y, super_twisting_increment_y.u) 
    annotation(Line(points = {{90, -40}, {90, 75}}, color = {0, 0, 127}));
  connect(super_twisting_integral_y.y, super_twisting_next_raw_y.u1) 
    annotation(Line(points = {{18, 85}, {162, 85}}, color = {0, 0, 127}));
  connect(super_twisting_increment_y.y, super_twisting_next_raw_y.u2) 
    annotation(Line(points = {{103, 85}, {162, 85}}, color = {0, 0, 127}));
  connect(super_twisting_next_raw_y.y, super_twisting_limit_y.u) 
    annotation(Line(points = {{188, 85}, {247, 85}}, color = {0, 0, 127}));
  connect(super_twisting_limit_y.y, super_twisting_integral_y.u1) 
    annotation(Line(points = {{247, 85}, {18, 85}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_y.y, sliding_abs_y.u) 
    annotation(Line(points = {{-347, -50}, {-177.5, -50}, {-177.5, -145}, {-8, -145}}, color = {0, 0, 127}));
  connect(sliding_abs_y.y, sliding_sqrt_y.u1) 
    annotation(Line(points = {{18, -145}, {77, -145}}, color = {0, 0, 127}));
  connect(sliding_sqrt_y_exponent.y, sliding_sqrt_y.u2) 
    annotation(Line(points = {{73, -175}, {75, -175}, {75, -145}, {77, -145}}, color = {0, 0, 127}));
  connect(sliding_sqrt_y.y, signed_sliding_root_y.u1) 
    annotation(Line(points = {{103, -145}, {132.5, -145}, {132.5, -125}, {162, -125}}, color = {0, 0, 127}));
  connect(boundary_layer_y.y, signed_sliding_root_y.u2) 
    annotation(Line(points = {{103, -50}, {132.5, -50}, {132.5, -125}, {162, -125}}, color = {0, 0, 127}));
  connect(signed_sliding_root_y.y, super_twisting_root_gain_y.u) 
    annotation(Line(points = {{188, -125}, {247, -125}}, color = {0, 0, 127}));
  connect(super_twisting_root_gain_y.y, super_twisting_robust_y.u1) 
    annotation(Line(points = {{273, -125}, {302.5, -125}, {302.5, -50}, {332, -50}}, color = {0, 0, 127}));
  connect(super_twisting_limit_y.y, super_twisting_robust_y.u2) 
    annotation(Line(points = {{260, 75}, {260, 17.5}, {345, 17.5}, {345, -40}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, lambda_velocity_y.u) 
    annotation(Line(points = {{-517, -100}, {-50, -100}, {-50, -170}, {417, -170}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_y.y, linear_surface_gain_y.u) 
    annotation(Line(points = {{-347, -50}, {35, -50}, {35, -120}, {417, -120}}, color = {0, 0, 127}));
  connect(reference_acceleration_y.y, feedforward_velocity_sum_y.u1) 
    annotation(Line(points = {{-632, 200}, {-72.5, 200}, {-72.5, -185}, {487, -185}}, color = {0, 0, 127}));
  connect(lambda_velocity_y.y, feedforward_velocity_sum_y.u2) 
    annotation(Line(points = {{443, -170}, {465, -170}, {465, -185}, {487, -185}}, color = {0, 0, 127}));
  connect(linear_surface_gain_y.y, linear_robust_sum_y.u1) 
    annotation(Line(points = {{443, -120}, {465, -120}, {465, -115}, {487, -115}}, color = {0, 0, 127}));
  connect(super_twisting_robust_y.y, linear_robust_sum_y.u2) 
    annotation(Line(points = {{358, -50}, {422.5, -50}, {422.5, -115}, {487, -115}}, color = {0, 0, 127}));
  connect(feedforward_velocity_sum_y.y, acceleration_sum_y.u1) 
    annotation(Line(points = {{513, -185}, {542.5, -185}, {542.5, -145}, {572, -145}}, color = {0, 0, 127}));
  connect(linear_robust_sum_y.y, acceleration_sum_y.u2) 
    annotation(Line(points = {{513, -115}, {542.5, -115}, {542.5, -145}, {572, -145}}, color = {0, 0, 127}));
  connect(reference_position_z.y, position_error_z.u1) 
    annotation(Line(points = {{-590, 300}, {-590, 0}, {-530, 0}, {-530, -300}}, color = {0, 0, 127}));
  connect(position_z.y, position_error_z.u2) 
    annotation(Line(points = {{-590, 410}, {-590, 55}, {-530, 55}, {-530, -300}}, color = {0, 0, 127}));
  connect(reference_velocity_z.y, velocity_error_z.u1) 
    annotation(Line(points = {{-590, 245}, {-590, -77.5}, {-530, -77.5}, {-530, -400}}, color = {0, 0, 127}));
  connect(velocity_z.y, velocity_error_z.u2) 
    annotation(Line(points = {{-590, 355}, {-590, -22.5}, {-530, -22.5}, {-530, -400}}, color = {0, 0, 127}));
  connect(position_error_z.y, lambda_position_z.u) 
    annotation(Line(points = {{-517, -310}, {-458, -310}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, linear_sliding_surface_z.u1) 
    annotation(Line(points = {{-517, -410}, {-445, -410}, {-445, -360}, {-373, -360}}, color = {0, 0, 127}));
  connect(lambda_position_z.y, linear_sliding_surface_z.u2) 
    annotation(Line(points = {{-432, -310}, {-402.5, -310}, {-402.5, -360}, {-373, -360}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_z.y, boundary_normalization_z.u) 
    annotation(Line(points = {{-347, -360}, {-8, -360}}, color = {0, 0, 127}));
  connect(boundary_normalization_z.y, boundary_layer_z.u) 
    annotation(Line(points = {{18, -360}, {77, -360}}, color = {0, 0, 127}));
  connect(boundary_layer_z.y, super_twisting_increment_z.u) 
    annotation(Line(points = {{90, -350}, {90, -235}}, color = {0, 0, 127}));
  connect(super_twisting_integral_z.y, super_twisting_next_raw_z.u1) 
    annotation(Line(points = {{18, -225}, {162, -225}}, color = {0, 0, 127}));
  connect(super_twisting_increment_z.y, super_twisting_next_raw_z.u2) 
    annotation(Line(points = {{103, -225}, {162, -225}}, color = {0, 0, 127}));
  connect(super_twisting_next_raw_z.y, super_twisting_limit_z.u) 
    annotation(Line(points = {{188, -225}, {247, -225}}, color = {0, 0, 127}));
  connect(super_twisting_limit_z.y, super_twisting_integral_z.u1) 
    annotation(Line(points = {{247, -225}, {18, -225}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_z.y, sliding_abs_z.u) 
    annotation(Line(points = {{-347, -360}, {-177.5, -360}, {-177.5, -455}, {-8, -455}}, color = {0, 0, 127}));
  connect(sliding_abs_z.y, sliding_sqrt_z.u1) 
    annotation(Line(points = {{18, -455}, {77, -455}}, color = {0, 0, 127}));
  connect(sliding_sqrt_z_exponent.y, sliding_sqrt_z.u2) 
    annotation(Line(points = {{73, -485}, {75, -485}, {75, -455}, {77, -455}}, color = {0, 0, 127}));
  connect(sliding_sqrt_z.y, signed_sliding_root_z.u1) 
    annotation(Line(points = {{103, -455}, {132.5, -455}, {132.5, -435}, {162, -435}}, color = {0, 0, 127}));
  connect(boundary_layer_z.y, signed_sliding_root_z.u2) 
    annotation(Line(points = {{103, -360}, {132.5, -360}, {132.5, -435}, {162, -435}}, color = {0, 0, 127}));
  connect(signed_sliding_root_z.y, super_twisting_root_gain_z.u) 
    annotation(Line(points = {{188, -435}, {247, -435}}, color = {0, 0, 127}));
  connect(super_twisting_root_gain_z.y, super_twisting_robust_z.u1) 
    annotation(Line(points = {{273, -435}, {302.5, -435}, {302.5, -360}, {332, -360}}, color = {0, 0, 127}));
  connect(super_twisting_limit_z.y, super_twisting_robust_z.u2) 
    annotation(Line(points = {{260, -235}, {260, -292.5}, {345, -292.5}, {345, -350}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, lambda_velocity_z.u) 
    annotation(Line(points = {{-517, -410}, {-50, -410}, {-50, -480}, {417, -480}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_z.y, linear_surface_gain_z.u) 
    annotation(Line(points = {{-347, -360}, {35, -360}, {35, -430}, {417, -430}}, color = {0, 0, 127}));
  connect(reference_acceleration_z.y, feedforward_velocity_sum_z.u1) 
    annotation(Line(points = {{-577, 200}, {-45, 200}, {-45, -495}, {487, -495}}, color = {0, 0, 127}));
  connect(lambda_velocity_z.y, feedforward_velocity_sum_z.u2) 
    annotation(Line(points = {{443, -480}, {465, -480}, {465, -495}, {487, -495}}, color = {0, 0, 127}));
  connect(linear_surface_gain_z.y, linear_robust_sum_z.u1) 
    annotation(Line(points = {{443, -430}, {465, -430}, {465, -425}, {487, -425}}, color = {0, 0, 127}));
  connect(super_twisting_robust_z.y, linear_robust_sum_z.u2) 
    annotation(Line(points = {{358, -360}, {422.5, -360}, {422.5, -425}, {487, -425}}, color = {0, 0, 127}));
  connect(feedforward_velocity_sum_z.y, acceleration_sum_z.u1) 
    annotation(Line(points = {{513, -495}, {542.5, -495}, {542.5, -455}, {572, -455}}, color = {0, 0, 127}));
  connect(linear_robust_sum_z.y, acceleration_sum_z.u2) 
    annotation(Line(points = {{513, -425}, {542.5, -425}, {542.5, -455}, {572, -455}}, color = {0, 0, 127}));
  connect(acceleration_sum_z.y, gravity_compensation.u1) 
    annotation(Line(points = {{585, -445}, {585, -412.5}, {620, -412.5}, {620, -380}}, color = {0, 0, 127}));
  connect(gravity.y, gravity_compensation.u2) 
    annotation(Line(points = {{548, -315}, {577.5, -315}, {577.5, -370}, {607, -370}}, color = {0, 0, 127}));
  connect(acceleration_sum_x.y, desired_acceleration_x) 
    annotation(Line(points = {{585, 175}, {585, 277.5}, {720, 277.5}, {720, 380}}, color = {0, 0, 127}));
  connect(acceleration_sum_y.y, desired_acceleration_y) 
    annotation(Line(points = {{585, -135}, {585, 90}, {720, 90}, {720, 315}}, color = {0, 0, 127}));
  connect(gravity_compensation.y, desired_acceleration_z) 
    annotation(Line(points = {{620, -360}, {620, -55}, {720, -55}, {720, 250}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_x.y, sliding_surface_x) 
    annotation(Line(points = {{-347, 260}, {180, 260}, {180, 195}, {707, 195}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_y.y, sliding_surface_y) 
    annotation(Line(points = {{-347, -50}, {180, -50}, {180, 130}, {707, 130}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_z.y, sliding_surface_z) 
    annotation(Line(points = {{-347, -360}, {180, -360}, {180, 65}, {707, 65}}, color = {0, 0, 127}));
  connect(super_twisting_limit_x.y, auxiliary_state_x) 
    annotation(Line(points = {{273, 395}, {490, 395}, {490, 0}, {707, 0}}, color = {0, 0, 127}));
  connect(super_twisting_limit_y.y, auxiliary_state_y) 
    annotation(Line(points = {{273, 85}, {490, 85}, {490, -65}, {707, -65}}, color = {0, 0, 127}));
  connect(super_twisting_limit_z.y, auxiliary_state_z) 
    annotation(Line(points = {{273, -225}, {490, -225}, {490, -130}, {707, -130}}, color = {0, 0, 127}));
  connect(super_twisting_gain_x.y, effective_reaching_gain_x) 
    annotation(Line(points = {{345, 345}, {345, 80}, {720, 80}, {720, -185}}, color = {0, 0, 127}));
  connect(super_twisting_gain_y.y, effective_reaching_gain_y) 
    annotation(Line(points = {{358, 45}, {532.5, 45}, {532.5, -260}, {707, -260}}, color = {0, 0, 127}));
  connect(super_twisting_gain_z.y, effective_reaching_gain_z) 
    annotation(Line(points = {{358, -265}, {532.5, -265}, {532.5, -325}, {707, -325}}, color = {0, 0, 127}));

end SuperTwistingSmcCore;
