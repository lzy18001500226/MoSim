within MoSimQuadrotorModel.Control.SlidingMode.FuzzySmc;
model FuzzySmcCore "P3 native graphical sliding-mode controller core: fuzzy_smc"
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
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_x 
    annotation (Placement(transformation(origin = {-80, 430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_normalization_x(k=2.0833333333333335) 
    annotation (Placement(transformation(origin = {5, 430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation fuzzy_membership_x(lowLimit=0.0,upLimit=1.0)
    "P3 distinguishing state or nonlinear surface for fuzzy_smc" annotation (Placement(transformation(origin = {90, 430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_two_x(k=2.0) 
    annotation (Placement(transformation(origin = {90, 485}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_complement_x(inputs="+-") 
    annotation (Placement(transformation(origin = {175, 460}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_shape_x(inputs="**") 
    annotation (Placement(transformation(origin = {260, 430}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_gain_delta_x(k=1.0) 
    annotation (Placement(transformation(origin = {345, 430}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_reaching_gain_x(inputs="++") 
    annotation (Placement(transformation(origin = {430, 390}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_robust_x(inputs="**") 
    annotation (Placement(transformation(origin = {430, 260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_y 
    annotation (Placement(transformation(origin = {-80, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_normalization_y(k=2.0833333333333335) 
    annotation (Placement(transformation(origin = {5, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation fuzzy_membership_y(lowLimit=0.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_two_y(k=2.0) 
    annotation (Placement(transformation(origin = {90, 175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_complement_y(inputs="+-") 
    annotation (Placement(transformation(origin = {175, 150}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_shape_y(inputs="**") 
    annotation (Placement(transformation(origin = {260, 120}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_gain_delta_y(k=1.0) 
    annotation (Placement(transformation(origin = {345, 120}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_reaching_gain_y(inputs="++") 
    annotation (Placement(transformation(origin = {430, 80}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_robust_y(inputs="**") 
    annotation (Placement(transformation(origin = {430, -50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Abs sliding_abs_z 
    annotation (Placement(transformation(origin = {-80, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_normalization_z(k=1.6666666666666667) 
    annotation (Placement(transformation(origin = {5, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation fuzzy_membership_z(lowLimit=0.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_two_z(k=2.0) 
    annotation (Placement(transformation(origin = {90, -135}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_complement_z(inputs="+-") 
    annotation (Placement(transformation(origin = {175, -160}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_shape_z(inputs="**") 
    annotation (Placement(transformation(origin = {260, -190}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_gain_delta_z(k=1.2) 
    annotation (Placement(transformation(origin = {345, -190}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum fuzzy_reaching_gain_z(inputs="++") 
    annotation (Placement(transformation(origin = {430, -230}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product fuzzy_robust_z(inputs="**") 
    annotation (Placement(transformation(origin = {430, -360}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  connect(linear_sliding_surface_x.y, sliding_abs_x.u) 
    annotation(Line(points = {{-347, 260}, {-220, 260}, {-220, 430}, {-93, 430}}, color = {0, 0, 127}));
  connect(sliding_abs_x.y, fuzzy_normalization_x.u) 
    annotation(Line(points = {{-67, 430}, {-8, 430}}, color = {0, 0, 127}));
  connect(fuzzy_normalization_x.y, fuzzy_membership_x.u) 
    annotation(Line(points = {{18, 430}, {77, 430}}, color = {0, 0, 127}));
  connect(fuzzy_two_x.y, fuzzy_complement_x.u1) 
    annotation(Line(points = {{103, 485}, {132.5, 485}, {132.5, 460}, {162, 460}}, color = {0, 0, 127}));
  connect(fuzzy_membership_x.y, fuzzy_complement_x.u2) 
    annotation(Line(points = {{103, 430}, {132.5, 430}, {132.5, 460}, {162, 460}}, color = {0, 0, 127}));
  connect(fuzzy_membership_x.y, fuzzy_shape_x.u1) 
    annotation(Line(points = {{103, 430}, {247, 430}}, color = {0, 0, 127}));
  connect(fuzzy_complement_x.y, fuzzy_shape_x.u2) 
    annotation(Line(points = {{188, 460}, {217.5, 460}, {217.5, 430}, {247, 430}}, color = {0, 0, 127}));
  connect(fuzzy_shape_x.y, fuzzy_gain_delta_x.u) 
    annotation(Line(points = {{273, 430}, {332, 430}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_x.y, fuzzy_reaching_gain_x.u1) 
    annotation(Line(points = {{-82, 390}, {417, 390}}, color = {0, 0, 127}));
  connect(fuzzy_gain_delta_x.y, fuzzy_reaching_gain_x.u2) 
    annotation(Line(points = {{358, 430}, {387.5, 430}, {387.5, 390}, {417, 390}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_x.y, fuzzy_robust_x.u1) 
    annotation(Line(points = {{430, 380}, {430, 270}}, color = {0, 0, 127}));
  connect(boundary_layer_x.y, fuzzy_robust_x.u2) 
    annotation(Line(points = {{103, 260}, {417, 260}}, color = {0, 0, 127}));
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
  connect(fuzzy_robust_x.y, linear_robust_sum_x.u2) 
    annotation(Line(points = {{443, 260}, {465, 260}, {465, 195}, {487, 195}}, color = {0, 0, 127}));
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
  connect(linear_sliding_surface_y.y, sliding_abs_y.u) 
    annotation(Line(points = {{-347, -50}, {-220, -50}, {-220, 120}, {-93, 120}}, color = {0, 0, 127}));
  connect(sliding_abs_y.y, fuzzy_normalization_y.u) 
    annotation(Line(points = {{-67, 120}, {-8, 120}}, color = {0, 0, 127}));
  connect(fuzzy_normalization_y.y, fuzzy_membership_y.u) 
    annotation(Line(points = {{18, 120}, {77, 120}}, color = {0, 0, 127}));
  connect(fuzzy_two_y.y, fuzzy_complement_y.u1) 
    annotation(Line(points = {{103, 175}, {132.5, 175}, {132.5, 150}, {162, 150}}, color = {0, 0, 127}));
  connect(fuzzy_membership_y.y, fuzzy_complement_y.u2) 
    annotation(Line(points = {{103, 120}, {132.5, 120}, {132.5, 150}, {162, 150}}, color = {0, 0, 127}));
  connect(fuzzy_membership_y.y, fuzzy_shape_y.u1) 
    annotation(Line(points = {{103, 120}, {247, 120}}, color = {0, 0, 127}));
  connect(fuzzy_complement_y.y, fuzzy_shape_y.u2) 
    annotation(Line(points = {{188, 150}, {217.5, 150}, {217.5, 120}, {247, 120}}, color = {0, 0, 127}));
  connect(fuzzy_shape_y.y, fuzzy_gain_delta_y.u) 
    annotation(Line(points = {{273, 120}, {332, 120}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_y.y, fuzzy_reaching_gain_y.u1) 
    annotation(Line(points = {{-82, 80}, {417, 80}}, color = {0, 0, 127}));
  connect(fuzzy_gain_delta_y.y, fuzzy_reaching_gain_y.u2) 
    annotation(Line(points = {{358, 120}, {387.5, 120}, {387.5, 80}, {417, 80}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_y.y, fuzzy_robust_y.u1) 
    annotation(Line(points = {{430, 70}, {430, -40}}, color = {0, 0, 127}));
  connect(boundary_layer_y.y, fuzzy_robust_y.u2) 
    annotation(Line(points = {{103, -50}, {417, -50}}, color = {0, 0, 127}));
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
  connect(fuzzy_robust_y.y, linear_robust_sum_y.u2) 
    annotation(Line(points = {{443, -50}, {465, -50}, {465, -115}, {487, -115}}, color = {0, 0, 127}));
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
  connect(linear_sliding_surface_z.y, sliding_abs_z.u) 
    annotation(Line(points = {{-347, -360}, {-220, -360}, {-220, -190}, {-93, -190}}, color = {0, 0, 127}));
  connect(sliding_abs_z.y, fuzzy_normalization_z.u) 
    annotation(Line(points = {{-67, -190}, {-8, -190}}, color = {0, 0, 127}));
  connect(fuzzy_normalization_z.y, fuzzy_membership_z.u) 
    annotation(Line(points = {{18, -190}, {77, -190}}, color = {0, 0, 127}));
  connect(fuzzy_two_z.y, fuzzy_complement_z.u1) 
    annotation(Line(points = {{103, -135}, {132.5, -135}, {132.5, -160}, {162, -160}}, color = {0, 0, 127}));
  connect(fuzzy_membership_z.y, fuzzy_complement_z.u2) 
    annotation(Line(points = {{103, -190}, {132.5, -190}, {132.5, -160}, {162, -160}}, color = {0, 0, 127}));
  connect(fuzzy_membership_z.y, fuzzy_shape_z.u1) 
    annotation(Line(points = {{103, -190}, {247, -190}}, color = {0, 0, 127}));
  connect(fuzzy_complement_z.y, fuzzy_shape_z.u2) 
    annotation(Line(points = {{188, -160}, {217.5, -160}, {217.5, -190}, {247, -190}}, color = {0, 0, 127}));
  connect(fuzzy_shape_z.y, fuzzy_gain_delta_z.u) 
    annotation(Line(points = {{273, -190}, {332, -190}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_z.y, fuzzy_reaching_gain_z.u1) 
    annotation(Line(points = {{-82, -230}, {417, -230}}, color = {0, 0, 127}));
  connect(fuzzy_gain_delta_z.y, fuzzy_reaching_gain_z.u2) 
    annotation(Line(points = {{358, -190}, {387.5, -190}, {387.5, -230}, {417, -230}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_z.y, fuzzy_robust_z.u1) 
    annotation(Line(points = {{430, -240}, {430, -350}}, color = {0, 0, 127}));
  connect(boundary_layer_z.y, fuzzy_robust_z.u2) 
    annotation(Line(points = {{103, -360}, {417, -360}}, color = {0, 0, 127}));
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
  connect(fuzzy_robust_z.y, linear_robust_sum_z.u2) 
    annotation(Line(points = {{443, -360}, {465, -360}, {465, -425}, {487, -425}}, color = {0, 0, 127}));
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
  connect(zero_x.y, auxiliary_state_x) 
    annotation(Line(points = {{248, 355}, {477.5, 355}, {477.5, 0}, {707, 0}}, color = {0, 0, 127}));
  connect(zero_y.y, auxiliary_state_y) 
    annotation(Line(points = {{248, 45}, {477.5, 45}, {477.5, -65}, {707, -65}}, color = {0, 0, 127}));
  connect(zero_z.y, auxiliary_state_z) 
    annotation(Line(points = {{248, -265}, {477.5, -265}, {477.5, -130}, {707, -130}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_x.y, effective_reaching_gain_x) 
    annotation(Line(points = {{430, 380}, {430, 97.5}, {720, 97.5}, {720, -185}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_y.y, effective_reaching_gain_y) 
    annotation(Line(points = {{430, 70}, {430, -90}, {720, -90}, {720, -250}}, color = {0, 0, 127}));
  connect(fuzzy_reaching_gain_z.y, effective_reaching_gain_z) 
    annotation(Line(points = {{443, -230}, {575, -230}, {575, -325}, {707, -325}}, color = {0, 0, 127}));

end FuzzySmcCore;
