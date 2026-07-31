within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model AWFF_PidLinearEsoControllerEquation_Sysblock
  "AWFF PID outer loop with bounded linear ESO disturbance compensation"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),
Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,
      Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-340,-260},{300,240}},grid={2,2})));

  parameter Real kp_x = 1.65;
  parameter Real kd_x = 1.0;
  parameter Real kp_y = 1.65;
  parameter Real kd_y = 1.0;
  parameter Real kp_z = 8.0;
  parameter Real ki_z = 6.0;
  parameter Real kd_z = 4.0;
  parameter Real kff_z = 0.35;
  parameter Real kp_roll = 14.142;
  parameter Real kd_roll = 1.70;
  parameter Real kp_pitch = 14.142;
  parameter Real kd_pitch = 1.70;
  parameter Real kp_yaw = 5.0;
  parameter Real roll_pitch_cmd_limit = 12 / 57.3;
  parameter Real attitude_cmd_limit = 6.5;
  parameter Real yaw_cmd_limit = 6.5;
  parameter Real output_limit = 20.0;
  parameter Real position_derivative_filter_T = 0.05;
  parameter Real altitude_derivative_filter_T = 0.08;
  parameter Real attitude_derivative_filter_T = 0.03;

  parameter Real eso_bandwidth_xy(min = 0.1) = 3.0
    "Linear ESO bandwidth for horizontal command-domain disturbances";
  parameter Real eso_bandwidth_z(min = 0.1) = 2.0
    "Linear ESO bandwidth for vertical command-domain disturbances";
  parameter Real eso_b0_xy(min = 0.01) = 1.0
    "Effective horizontal command-domain input gain";
  parameter Real eso_b0_z(min = 0.01) = 1.0
    "Effective vertical command-domain input gain";
  parameter Real eso_comp_limit_xy(min = 0) = 0.06
    "Bounded horizontal ESO compensation in rad";
  parameter Real eso_comp_limit_z(min = 0) = 1.0
    "Bounded vertical ESO compensation in N";
  parameter Real eso_enable(min = 0, max = 1) = 1.0
    "Set to zero for an apples-to-apples AWFF PID bypass";

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,190},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,140},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,90},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,40},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-20},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-70},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-120},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-170},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={270,165},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={270,55},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={270,-55},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-25},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={270,-165},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-75},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  Real pitch_ref;
  Real roll_ref;
  Real thrust_ref;
  Real pitch_ref_raw;
  Real roll_ref_raw;
  Real thrust_ref_raw;
  Real x_error_filter(start = 0, fixed = true);
  Real y_error_filter(start = 0, fixed = true);
  Real x_error_rate;
  Real y_error_rate;
  Real z_error_filter(start = 0, fixed = true);
  Real z_error_rate;
  Real z_integral(start = 0, fixed = true);
  Real roll_error;
  Real pitch_error;
  Real yaw_error;
  Real roll_error_filter(start = 0, fixed = true);
  Real pitch_error_filter(start = 0, fixed = true);
  Real roll_error_rate;
  Real pitch_error_rate;
  Real roll_cmd_raw;
  Real pitch_cmd_raw;
  Real yaw_cmd_raw;
  Real roll_cmd;
  Real pitch_cmd;
  Real yaw_cmd;
  Real yaw_mix;
  Real pitch_mix;
  Real roll_mix;
  Real u1_raw;
  Real u2_raw;
  Real u3_raw;
  Real u4_raw;

  Real eso_x1(start = 0, fixed = true);
  Real eso_x2(start = 0, fixed = true);
  Real eso_x3(start = 0, fixed = true);
  Real eso_y1(start = 0, fixed = true);
  Real eso_y2(start = 0, fixed = true);
  Real eso_y3(start = 0, fixed = true);
  Real eso_z1(start = 0, fixed = true);
  Real eso_z2(start = 0, fixed = true);
  Real eso_z3(start = 0, fixed = true);
  Real eso_x_innovation;
  Real eso_y_innovation;
  Real eso_z_innovation;
  Real eso_x_comp;
  Real eso_y_comp;
  Real eso_z_comp;
  Real x_command_nominal;
  Real y_command_nominal;
  Real z_command_nominal;
  Real beta1_xy;
  Real beta2_xy;
  Real beta3_xy;
  Real beta1_z;
  Real beta2_z;
  Real beta3_z;

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  beta1_xy = 3 * eso_bandwidth_xy;
  beta2_xy = 3 * eso_bandwidth_xy ^ 2;
  beta3_xy = eso_bandwidth_xy ^ 3;
  beta1_z = 3 * eso_bandwidth_z;
  beta2_z = 3 * eso_bandwidth_z ^ 2;
  beta3_z = eso_bandwidth_z ^ 3;

  der(x_error_filter) = (x_error - x_error_filter) / position_derivative_filter_T;
  der(y_error_filter) = (y_error - y_error_filter) / position_derivative_filter_T;
  x_error_rate = (x_error - x_error_filter) / position_derivative_filter_T;
  y_error_rate = (y_error - y_error_filter) / position_derivative_filter_T;
  der(z_error_filter) = (z_error - z_error_filter) / altitude_derivative_filter_T;
  z_error_rate = (z_error - z_error_filter) / altitude_derivative_filter_T;

  x_command_nominal = 0.1 * (kp_x * x_error + kd_x * x_error_rate);
  y_command_nominal = 0.1 * (kp_y * y_error + kd_y * y_error_rate);
  z_command_nominal = kp_z * z_error + ki_z * z_integral + kd_z * z_error_rate
    + kff_z * z_ref_rate;

  eso_x_innovation = x_error - eso_x1;
  eso_y_innovation = y_error - eso_y1;
  eso_z_innovation = z_error - eso_z1;
  der(eso_x1) = eso_x2 + beta1_xy * eso_x_innovation;
  der(eso_x2) = eso_x3 + eso_b0_xy * x_command_nominal
    + beta2_xy * eso_x_innovation;
  der(eso_x3) = beta3_xy * eso_x_innovation;
  der(eso_y1) = eso_y2 + beta1_xy * eso_y_innovation;
  der(eso_y2) = eso_y3 + eso_b0_xy * y_command_nominal
    + beta2_xy * eso_y_innovation;
  der(eso_y3) = beta3_xy * eso_y_innovation;
  der(eso_z1) = eso_z2 + beta1_z * eso_z_innovation;
  der(eso_z2) = eso_z3 + eso_b0_z * z_command_nominal
    + beta2_z * eso_z_innovation;
  der(eso_z3) = beta3_z * eso_z_innovation;

  eso_x_comp = min(max(eso_enable * eso_x3 / eso_b0_xy,
    -eso_comp_limit_xy), eso_comp_limit_xy);
  eso_y_comp = min(max(eso_enable * eso_y3 / eso_b0_xy,
    -eso_comp_limit_xy), eso_comp_limit_xy);
  eso_z_comp = min(max(eso_enable * eso_z3 / eso_b0_z,
    -eso_comp_limit_z), eso_comp_limit_z);

  pitch_ref_raw = x_command_nominal - eso_x_comp;
  roll_ref_raw = y_command_nominal - eso_y_comp;
  thrust_ref_raw = z_command_nominal - eso_z_comp;
  pitch_ref = if pitch_ref_raw > roll_pitch_cmd_limit then roll_pitch_cmd_limit
    else if pitch_ref_raw < -roll_pitch_cmd_limit then -roll_pitch_cmd_limit
    else pitch_ref_raw;
  roll_ref = if roll_ref_raw > roll_pitch_cmd_limit then roll_pitch_cmd_limit
    else if roll_ref_raw < -roll_pitch_cmd_limit then -roll_pitch_cmd_limit
    else roll_ref_raw;
  thrust_ref = if thrust_ref_raw > output_limit then output_limit
    else if thrust_ref_raw < -output_limit then -output_limit
    else thrust_ref_raw;
  der(z_integral) = if abs(thrust_ref_raw) < output_limit
    or z_error * thrust_ref_raw < 0 then z_error else 0;

  roll_error = roll_ref + roll_mea;
  pitch_error = pitch_ref - pitch_mea;
  yaw_error = yaw_ref - yaw_mea;
  der(roll_error_filter) = (roll_error - roll_error_filter) / attitude_derivative_filter_T;
  der(pitch_error_filter) = (pitch_error - pitch_error_filter) / attitude_derivative_filter_T;
  roll_error_rate = (roll_error - roll_error_filter) / attitude_derivative_filter_T;
  pitch_error_rate = (pitch_error - pitch_error_filter) / attitude_derivative_filter_T;
  roll_cmd_raw = kp_roll * roll_error + kd_roll * roll_error_rate;
  pitch_cmd_raw = kp_pitch * pitch_error + kd_pitch * pitch_error_rate;
  yaw_cmd_raw = kp_yaw * yaw_error;
  roll_cmd = if roll_cmd_raw > attitude_cmd_limit then attitude_cmd_limit
    else if roll_cmd_raw < -attitude_cmd_limit then -attitude_cmd_limit else roll_cmd_raw;
  pitch_cmd = if pitch_cmd_raw > attitude_cmd_limit then attitude_cmd_limit
    else if pitch_cmd_raw < -attitude_cmd_limit then -attitude_cmd_limit else pitch_cmd_raw;
  yaw_cmd = if yaw_cmd_raw > yaw_cmd_limit then yaw_cmd_limit
    else if yaw_cmd_raw < -yaw_cmd_limit then -yaw_cmd_limit else yaw_cmd_raw;

  yaw_mix = 0.707 * yaw_cmd;
  pitch_mix = 0.707 * pitch_cmd;
  roll_mix = 0.707 * roll_cmd;
  u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix);
  u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix));
  u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix);
  u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix));
  y = if u1_raw > output_limit then output_limit else if u1_raw < -output_limit then -output_limit else u1_raw;
  y1 = if u2_raw > output_limit then output_limit else if u2_raw < -output_limit then -output_limit else u2_raw;
  y2 = if u3_raw > output_limit then output_limit else if u3_raw < -output_limit then -output_limit else u3_raw;
  y3 = if u4_raw > output_limit then output_limit else if u4_raw < -output_limit then -output_limit else u4_raw;
end AWFF_PidLinearEsoControllerEquation_Sysblock;
