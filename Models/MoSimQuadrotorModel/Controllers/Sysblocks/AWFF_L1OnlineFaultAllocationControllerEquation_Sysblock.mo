within MoSimQuadrotorModel.Controllers.Sysblocks;
model AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock
  "AWFF L1 residual controller with residual-driven online rotor-1 efficiency estimate"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3,eta_hat)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{300,220}},grid={2,2})));

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
  parameter Real l1_model_decay = 1.25;
  parameter Real l1_filter_T = 0.20;
  parameter Real l1_gain_xy = 0.32;
  parameter Real l1_gain_z = 0.35;
  parameter Real l1_comp_limit_xy = 2.0;
  parameter Real l1_comp_limit_z = 2.0;
  parameter Real eta_min_est = 0.50;
  parameter Real eta_max_est = 1.00;
  parameter Real eta_est_filter_T = 5.0;
  parameter Real eta_signature_deadband = 0.015;
  parameter Real eta_signature_gain = 2.65;
  parameter Real rotor1_allocation_blend = 0.52;

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,130},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,80},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,30},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-300,-30},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-12.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-300,-80},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-37.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-300,-130},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-62.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-300,-180},extent={{-10,-10},{10,10}}),iconTransformation(origin={-101.8,-87.5},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={250,160},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,80},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={250,80},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,40},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={250,0},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,0},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={250,-80},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-40},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat annotation(Placement(transformation(origin={250,-160},extent={{-10,-10},{10,10}}),iconTransformation(origin={101.8,-80},extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

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
  Real residual_x;
  Real residual_y;
  Real residual_z;
  Real d_hat_x(start = 0, fixed = true);
  Real d_hat_y(start = 0, fixed = true);
  Real d_hat_z(start = 0, fixed = true);
  Real comp_x;
  Real comp_y;
  Real comp_z;
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
  Real eta_signature;
  Real eta_target_raw;
  Real eta_target;
  Real eta_hat_state(start = 1.0, fixed = true);
  Real rotor1_eff_safe;
  Real rotor1_allocation_gain;
  Real u1_allocated_raw;

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  der(x_error_filter) = (x_error - x_error_filter) / position_derivative_filter_T;
  der(y_error_filter) = (y_error - y_error_filter) / position_derivative_filter_T;
  x_error_rate = (x_error - x_error_filter) / position_derivative_filter_T;
  y_error_rate = (y_error - y_error_filter) / position_derivative_filter_T;
  residual_x = x_error_rate + l1_model_decay * x_error;
  residual_y = y_error_rate + l1_model_decay * y_error;
  der(d_hat_x) = (l1_gain_xy * residual_x - d_hat_x) / l1_filter_T;
  der(d_hat_y) = (l1_gain_xy * residual_y - d_hat_y) / l1_filter_T;
  comp_x = if d_hat_x > l1_comp_limit_xy then l1_comp_limit_xy else if d_hat_x < -l1_comp_limit_xy then -l1_comp_limit_xy else d_hat_x;
  comp_y = if d_hat_y > l1_comp_limit_xy then l1_comp_limit_xy else if d_hat_y < -l1_comp_limit_xy then -l1_comp_limit_xy else d_hat_y;
  pitch_ref_raw = 0.1 * (kp_x * x_error + kd_x * x_error_rate + comp_x);
  roll_ref_raw = 0.1 * (kp_y * y_error + kd_y * y_error_rate + comp_y);

  der(z_error_filter) = (z_error - z_error_filter) / altitude_derivative_filter_T;
  z_error_rate = (z_error - z_error_filter) / altitude_derivative_filter_T;
  residual_z = z_error_rate + l1_model_decay * z_error;
  der(d_hat_z) = (l1_gain_z * residual_z - d_hat_z) / l1_filter_T;
  comp_z = if d_hat_z > l1_comp_limit_z then l1_comp_limit_z else if d_hat_z < -l1_comp_limit_z then -l1_comp_limit_z else d_hat_z;
  thrust_ref_raw = kp_z * z_error + ki_z * z_integral + kd_z * z_error_rate + kff_z * z_ref_rate + comp_z;

  pitch_ref = if pitch_ref_raw > roll_pitch_cmd_limit then roll_pitch_cmd_limit else if pitch_ref_raw < -roll_pitch_cmd_limit then -roll_pitch_cmd_limit else pitch_ref_raw;
  roll_ref = if roll_ref_raw > roll_pitch_cmd_limit then roll_pitch_cmd_limit else if roll_ref_raw < -roll_pitch_cmd_limit then -roll_pitch_cmd_limit else roll_ref_raw;
  thrust_ref = if thrust_ref_raw > output_limit then output_limit else if thrust_ref_raw < -output_limit then -output_limit else thrust_ref_raw;
  der(z_integral) = if abs(thrust_ref_raw) < output_limit or z_error * thrust_ref_raw < 0 then z_error else 0;

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

  roll_cmd = if roll_cmd_raw > attitude_cmd_limit then attitude_cmd_limit else if roll_cmd_raw < -attitude_cmd_limit then -attitude_cmd_limit else roll_cmd_raw;
  pitch_cmd = if pitch_cmd_raw > attitude_cmd_limit then attitude_cmd_limit else if pitch_cmd_raw < -attitude_cmd_limit then -attitude_cmd_limit else pitch_cmd_raw;
  yaw_cmd = if yaw_cmd_raw > yaw_cmd_limit then yaw_cmd_limit else if yaw_cmd_raw < -yaw_cmd_limit then -yaw_cmd_limit else yaw_cmd_raw;

  yaw_mix = 0.707 * yaw_cmd;
  pitch_mix = 0.707 * pitch_cmd;
  roll_mix = 0.707 * roll_cmd;

  u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix);
  u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix));
  u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix);
  u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix));

  eta_signature = if (-x_error_filter + y_error_filter) / 2 > eta_signature_deadband then (-x_error_filter + y_error_filter) / 2 - eta_signature_deadband else 0;
  eta_target_raw = 1 - eta_signature_gain * eta_signature;
  eta_target = if eta_target_raw < eta_min_est then eta_min_est else if eta_target_raw > eta_max_est then eta_max_est else eta_target_raw;
  der(eta_hat_state) = (eta_target - eta_hat_state) / eta_est_filter_T;
  eta_hat = if eta_hat_state < eta_min_est then eta_min_est else if eta_hat_state > eta_max_est then eta_max_est else eta_hat_state;

  rotor1_eff_safe = if eta_hat < eta_min_est then eta_min_est else eta_hat;
  rotor1_allocation_gain = 1 + rotor1_allocation_blend * (1 / rotor1_eff_safe - 1);
  u1_allocated_raw = u1_raw * rotor1_allocation_gain;

  y = if u1_allocated_raw > output_limit then output_limit else if u1_allocated_raw < -output_limit then -output_limit else u1_allocated_raw;
  y1 = if u2_raw > output_limit then output_limit else if u2_raw < -output_limit then -output_limit else u2_raw;
  y2 = if u3_raw > output_limit then output_limit else if u3_raw < -output_limit then -output_limit else u3_raw;
  y3 = if u4_raw > output_limit then output_limit else if u4_raw < -output_limit then -output_limit else u4_raw;
end AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock;