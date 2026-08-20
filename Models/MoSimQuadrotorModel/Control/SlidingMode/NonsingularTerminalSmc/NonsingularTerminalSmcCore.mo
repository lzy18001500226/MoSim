within MoSimQuadrotorModel.Control.SlidingMode.NonsingularTerminalSmc;
model NonsingularTerminalSmcCore "P3 native graphical sliding-mode controller core: nonsingular_terminal_smc"
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
  SysplorerEmbeddedCoder.MathOperation.Abs position_error_abs_x 
    annotation (Placement(transformation(origin = {-445, 390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction position_error_power_x(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {-350, 390}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_power_x_exponent(k=1.5) 
    annotation (Placement(transformation(origin = {-380, 360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sign position_error_sign_x 
    annotation (Placement(transformation(origin = {-350, 445}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_position_power_x(inputs="**") 
    annotation (Placement(transformation(origin = {-255, 405}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain terminal_shape_gain_x(k=0.35)
    "P3 distinguishing state or nonlinear surface for nonsingular_terminal_smc" annotation (Placement(transformation(origin = {-170, 405}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum terminal_sliding_surface_x(inputs="++") 
    annotation (Placement(transformation(origin = {-85, 360}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_x(k=8.333333333333334) 
    annotation (Placement(transformation(origin = {5, 260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_x(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, 260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product reaching_term_x(inputs="**") 
    annotation (Placement(transformation(origin = {175, 260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Abs position_error_abs_y 
    annotation (Placement(transformation(origin = {-445, 80}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction position_error_power_y(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {-350, 80}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_power_y_exponent(k=1.5) 
    annotation (Placement(transformation(origin = {-380, 50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sign position_error_sign_y 
    annotation (Placement(transformation(origin = {-350, 135}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_position_power_y(inputs="**") 
    annotation (Placement(transformation(origin = {-255, 95}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain terminal_shape_gain_y(k=0.35) 
    annotation (Placement(transformation(origin = {-170, 95}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum terminal_sliding_surface_y(inputs="++") 
    annotation (Placement(transformation(origin = {-85, 50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_y(k=8.333333333333334) 
    annotation (Placement(transformation(origin = {5, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_y(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, -50}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product reaching_term_y(inputs="**") 
    annotation (Placement(transformation(origin = {175, -50}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  SysplorerEmbeddedCoder.MathOperation.Abs position_error_abs_z 
    annotation (Placement(transformation(origin = {-445, -230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.MathFunction position_error_power_z(operatorType=SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow) 
    annotation (Placement(transformation(origin = {-350, -230}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Sources.Constant position_error_power_z_exponent(k=1.5) 
    annotation (Placement(transformation(origin = {-380, -260}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sign position_error_sign_z 
    annotation (Placement(transformation(origin = {-350, -175}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product signed_position_power_z(inputs="**") 
    annotation (Placement(transformation(origin = {-255, -215}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain terminal_shape_gain_z(k=0.4) 
    annotation (Placement(transformation(origin = {-170, -215}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Sum terminal_sliding_surface_z(inputs="++") 
    annotation (Placement(transformation(origin = {-85, -260}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain boundary_normalization_z(k=6.666666666666667) 
    annotation (Placement(transformation(origin = {5, -360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation boundary_layer_z(lowLimit=-1.0,upLimit=1.0) 
    annotation (Placement(transformation(origin = {90, -360}, extent = {{-13, -10}, {13, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Product reaching_term_z(inputs="**") 
    annotation (Placement(transformation(origin = {175, -360}, extent = {{-13, -10}, {13, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
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
  connect(position_error_x.y, position_error_abs_x.u) 
    annotation(Line(points = {{-517, 310}, {-487.5, 310}, {-487.5, 390}, {-458, 390}}, color = {0, 0, 127}));
  connect(position_error_abs_x.y, position_error_power_x.u1) 
    annotation(Line(points = {{-432, 390}, {-363, 390}}, color = {0, 0, 127}));
  connect(position_error_power_x_exponent.y, position_error_power_x.u2) 
    annotation(Line(points = {{-367, 360}, {-365, 360}, {-365, 390}, {-363, 390}}, color = {0, 0, 127}));
  connect(position_error_x.y, position_error_sign_x.u) 
    annotation(Line(points = {{-517, 310}, {-440, 310}, {-440, 445}, {-363, 445}}, color = {0, 0, 127}));
  connect(position_error_power_x.y, signed_position_power_x.u1) 
    annotation(Line(points = {{-337, 390}, {-302.5, 390}, {-302.5, 405}, {-268, 405}}, color = {0, 0, 127}));
  connect(position_error_sign_x.y, signed_position_power_x.u2) 
    annotation(Line(points = {{-337, 445}, {-302.5, 445}, {-302.5, 405}, {-268, 405}}, color = {0, 0, 127}));
  connect(signed_position_power_x.y, terminal_shape_gain_x.u) 
    annotation(Line(points = {{-242, 405}, {-183, 405}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_x.y, terminal_sliding_surface_x.u1) 
    annotation(Line(points = {{-347, 260}, {-222.5, 260}, {-222.5, 360}, {-98, 360}}, color = {0, 0, 127}));
  connect(terminal_shape_gain_x.y, terminal_sliding_surface_x.u2) 
    annotation(Line(points = {{-157, 405}, {-127.5, 405}, {-127.5, 360}, {-98, 360}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_x.y, boundary_normalization_x.u) 
    annotation(Line(points = {{-85, 350}, {-85, 310}, {5, 310}, {5, 270}}, color = {0, 0, 127}));
  connect(boundary_normalization_x.y, boundary_layer_x.u) 
    annotation(Line(points = {{18, 260}, {77, 260}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_x.y, reaching_term_x.u1) 
    annotation(Line(points = {{-82, 390}, {40, 390}, {40, 260}, {162, 260}}, color = {0, 0, 127}));
  connect(boundary_layer_x.y, reaching_term_x.u2) 
    annotation(Line(points = {{103, 260}, {162, 260}}, color = {0, 0, 127}));
  connect(velocity_error_x.y, lambda_velocity_x.u) 
    annotation(Line(points = {{-517, 210}, {-50, 210}, {-50, 140}, {417, 140}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_x.y, linear_surface_gain_x.u) 
    annotation(Line(points = {{-72, 360}, {172.5, 360}, {172.5, 190}, {417, 190}}, color = {0, 0, 127}));
  connect(reference_acceleration_x.y, feedforward_velocity_sum_x.u1) 
    annotation(Line(points = {{-687, 200}, {-100, 200}, {-100, 125}, {487, 125}}, color = {0, 0, 127}));
  connect(lambda_velocity_x.y, feedforward_velocity_sum_x.u2) 
    annotation(Line(points = {{443, 140}, {465, 140}, {465, 125}, {487, 125}}, color = {0, 0, 127}));
  connect(linear_surface_gain_x.y, linear_robust_sum_x.u1) 
    annotation(Line(points = {{443, 190}, {465, 190}, {465, 195}, {487, 195}}, color = {0, 0, 127}));
  connect(reaching_term_x.y, linear_robust_sum_x.u2) 
    annotation(Line(points = {{188, 260}, {337.5, 260}, {337.5, 195}, {487, 195}}, color = {0, 0, 127}));
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
  connect(position_error_y.y, position_error_abs_y.u) 
    annotation(Line(points = {{-517, 0}, {-487.5, 0}, {-487.5, 80}, {-458, 80}}, color = {0, 0, 127}));
  connect(position_error_abs_y.y, position_error_power_y.u1) 
    annotation(Line(points = {{-432, 80}, {-363, 80}}, color = {0, 0, 127}));
  connect(position_error_power_y_exponent.y, position_error_power_y.u2) 
    annotation(Line(points = {{-367, 50}, {-365, 50}, {-365, 80}, {-363, 80}}, color = {0, 0, 127}));
  connect(position_error_y.y, position_error_sign_y.u) 
    annotation(Line(points = {{-517, 0}, {-440, 0}, {-440, 135}, {-363, 135}}, color = {0, 0, 127}));
  connect(position_error_power_y.y, signed_position_power_y.u1) 
    annotation(Line(points = {{-337, 80}, {-302.5, 80}, {-302.5, 95}, {-268, 95}}, color = {0, 0, 127}));
  connect(position_error_sign_y.y, signed_position_power_y.u2) 
    annotation(Line(points = {{-337, 135}, {-302.5, 135}, {-302.5, 95}, {-268, 95}}, color = {0, 0, 127}));
  connect(signed_position_power_y.y, terminal_shape_gain_y.u) 
    annotation(Line(points = {{-242, 95}, {-183, 95}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_y.y, terminal_sliding_surface_y.u1) 
    annotation(Line(points = {{-347, -50}, {-222.5, -50}, {-222.5, 50}, {-98, 50}}, color = {0, 0, 127}));
  connect(terminal_shape_gain_y.y, terminal_sliding_surface_y.u2) 
    annotation(Line(points = {{-157, 95}, {-127.5, 95}, {-127.5, 50}, {-98, 50}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_y.y, boundary_normalization_y.u) 
    annotation(Line(points = {{-85, 40}, {-85, 0}, {5, 0}, {5, -40}}, color = {0, 0, 127}));
  connect(boundary_normalization_y.y, boundary_layer_y.u) 
    annotation(Line(points = {{18, -50}, {77, -50}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_y.y, reaching_term_y.u1) 
    annotation(Line(points = {{-82, 80}, {40, 80}, {40, -50}, {162, -50}}, color = {0, 0, 127}));
  connect(boundary_layer_y.y, reaching_term_y.u2) 
    annotation(Line(points = {{103, -50}, {162, -50}}, color = {0, 0, 127}));
  connect(velocity_error_y.y, lambda_velocity_y.u) 
    annotation(Line(points = {{-517, -100}, {-50, -100}, {-50, -170}, {417, -170}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_y.y, linear_surface_gain_y.u) 
    annotation(Line(points = {{-72, 50}, {172.5, 50}, {172.5, -120}, {417, -120}}, color = {0, 0, 127}));
  connect(reference_acceleration_y.y, feedforward_velocity_sum_y.u1) 
    annotation(Line(points = {{-632, 200}, {-72.5, 200}, {-72.5, -185}, {487, -185}}, color = {0, 0, 127}));
  connect(lambda_velocity_y.y, feedforward_velocity_sum_y.u2) 
    annotation(Line(points = {{443, -170}, {465, -170}, {465, -185}, {487, -185}}, color = {0, 0, 127}));
  connect(linear_surface_gain_y.y, linear_robust_sum_y.u1) 
    annotation(Line(points = {{443, -120}, {465, -120}, {465, -115}, {487, -115}}, color = {0, 0, 127}));
  connect(reaching_term_y.y, linear_robust_sum_y.u2) 
    annotation(Line(points = {{188, -50}, {337.5, -50}, {337.5, -115}, {487, -115}}, color = {0, 0, 127}));
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
  connect(position_error_z.y, position_error_abs_z.u) 
    annotation(Line(points = {{-517, -310}, {-487.5, -310}, {-487.5, -230}, {-458, -230}}, color = {0, 0, 127}));
  connect(position_error_abs_z.y, position_error_power_z.u1) 
    annotation(Line(points = {{-432, -230}, {-363, -230}}, color = {0, 0, 127}));
  connect(position_error_power_z_exponent.y, position_error_power_z.u2) 
    annotation(Line(points = {{-367, -260}, {-365, -260}, {-365, -230}, {-363, -230}}, color = {0, 0, 127}));
  connect(position_error_z.y, position_error_sign_z.u) 
    annotation(Line(points = {{-517, -310}, {-440, -310}, {-440, -175}, {-363, -175}}, color = {0, 0, 127}));
  connect(position_error_power_z.y, signed_position_power_z.u1) 
    annotation(Line(points = {{-337, -230}, {-302.5, -230}, {-302.5, -215}, {-268, -215}}, color = {0, 0, 127}));
  connect(position_error_sign_z.y, signed_position_power_z.u2) 
    annotation(Line(points = {{-337, -175}, {-302.5, -175}, {-302.5, -215}, {-268, -215}}, color = {0, 0, 127}));
  connect(signed_position_power_z.y, terminal_shape_gain_z.u) 
    annotation(Line(points = {{-242, -215}, {-183, -215}}, color = {0, 0, 127}));
  connect(linear_sliding_surface_z.y, terminal_sliding_surface_z.u1) 
    annotation(Line(points = {{-347, -360}, {-222.5, -360}, {-222.5, -260}, {-98, -260}}, color = {0, 0, 127}));
  connect(terminal_shape_gain_z.y, terminal_sliding_surface_z.u2) 
    annotation(Line(points = {{-157, -215}, {-127.5, -215}, {-127.5, -260}, {-98, -260}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_z.y, boundary_normalization_z.u) 
    annotation(Line(points = {{-85, -270}, {-85, -310}, {5, -310}, {5, -350}}, color = {0, 0, 127}));
  connect(boundary_normalization_z.y, boundary_layer_z.u) 
    annotation(Line(points = {{18, -360}, {77, -360}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_z.y, reaching_term_z.u1) 
    annotation(Line(points = {{-82, -230}, {40, -230}, {40, -360}, {162, -360}}, color = {0, 0, 127}));
  connect(boundary_layer_z.y, reaching_term_z.u2) 
    annotation(Line(points = {{103, -360}, {162, -360}}, color = {0, 0, 127}));
  connect(velocity_error_z.y, lambda_velocity_z.u) 
    annotation(Line(points = {{-517, -410}, {-50, -410}, {-50, -480}, {417, -480}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_z.y, linear_surface_gain_z.u) 
    annotation(Line(points = {{-72, -260}, {172.5, -260}, {172.5, -430}, {417, -430}}, color = {0, 0, 127}));
  connect(reference_acceleration_z.y, feedforward_velocity_sum_z.u1) 
    annotation(Line(points = {{-577, 200}, {-45, 200}, {-45, -495}, {487, -495}}, color = {0, 0, 127}));
  connect(lambda_velocity_z.y, feedforward_velocity_sum_z.u2) 
    annotation(Line(points = {{443, -480}, {465, -480}, {465, -495}, {487, -495}}, color = {0, 0, 127}));
  connect(linear_surface_gain_z.y, linear_robust_sum_z.u1) 
    annotation(Line(points = {{443, -430}, {465, -430}, {465, -425}, {487, -425}}, color = {0, 0, 127}));
  connect(reaching_term_z.y, linear_robust_sum_z.u2) 
    annotation(Line(points = {{188, -360}, {337.5, -360}, {337.5, -425}, {487, -425}}, color = {0, 0, 127}));
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
  connect(terminal_sliding_surface_x.y, sliding_surface_x) 
    annotation(Line(points = {{-72, 360}, {317.5, 360}, {317.5, 195}, {707, 195}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_y.y, sliding_surface_y) 
    annotation(Line(points = {{-72, 50}, {317.5, 50}, {317.5, 130}, {707, 130}}, color = {0, 0, 127}));
  connect(terminal_sliding_surface_z.y, sliding_surface_z) 
    annotation(Line(points = {{-72, -260}, {317.5, -260}, {317.5, 65}, {707, 65}}, color = {0, 0, 127}));
  connect(zero_x.y, auxiliary_state_x) 
    annotation(Line(points = {{248, 355}, {477.5, 355}, {477.5, 0}, {707, 0}}, color = {0, 0, 127}));
  connect(zero_y.y, auxiliary_state_y) 
    annotation(Line(points = {{248, 45}, {477.5, 45}, {477.5, -65}, {707, -65}}, color = {0, 0, 127}));
  connect(zero_z.y, auxiliary_state_z) 
    annotation(Line(points = {{248, -265}, {477.5, -265}, {477.5, -130}, {707, -130}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_x.y, effective_reaching_gain_x) 
    annotation(Line(points = {{-82, 390}, {312.5, 390}, {312.5, -195}, {707, -195}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_y.y, effective_reaching_gain_y) 
    annotation(Line(points = {{-82, 80}, {312.5, 80}, {312.5, -260}, {707, -260}}, color = {0, 0, 127}));
  connect(nominal_reaching_gain_z.y, effective_reaching_gain_z) 
    annotation(Line(points = {{-82, -230}, {312.5, -230}, {312.5, -325}, {707, -325}}, color = {0, 0, 127}));

end NonsingularTerminalSmcCore;
