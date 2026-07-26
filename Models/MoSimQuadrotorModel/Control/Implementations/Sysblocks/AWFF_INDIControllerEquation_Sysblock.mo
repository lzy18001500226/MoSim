within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model AWFF_INDIControllerEquation_Sysblock
  "AWFF outer loop with L1-inspired residual compensation and INDI-like attitude inner loop"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{280,220}},grid={2,2})));

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
  parameter Real l1_model_decay = 1.25;
  parameter Real l1_filter_T = 0.20;
  parameter Real l1_gain_xy = 0.32;
  parameter Real l1_gain_z = 0.35;
  parameter Real l1_comp_limit_xy = 2.0;
  parameter Real l1_comp_limit_z = 2.0;
  parameter Real attitude_rate_filter_T = 0.035;
  parameter Real angular_accel_filter_T = 0.08;
  parameter Real indi_roll_gain = 0.015;
  parameter Real indi_pitch_gain = 0.015;
  parameter Real indi_yaw_gain = 0.005;
  parameter Real indi_increment_limit = 0.15;
  parameter Real attitude_feedback_blend = 1.00;

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-300,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-300,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-300,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-300,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={250,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={250,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={250,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={250,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

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
  Real roll_mea_filter(start = 0, fixed = true);
  Real pitch_mea_filter(start = 0, fixed = true);
  Real yaw_mea_filter(start = 0, fixed = true);
  Real roll_rate;
  Real pitch_rate;
  Real yaw_rate;
  Real roll_rate_filter(start = 0, fixed = true);
  Real pitch_rate_filter(start = 0, fixed = true);
  Real yaw_rate_filter(start = 0, fixed = true);
  Real roll_accel_hat;
  Real pitch_accel_hat;
  Real yaw_accel_hat;
  Real roll_accel_cmd;
  Real pitch_accel_cmd;
  Real yaw_accel_cmd;
  Real roll_increment_raw;
  Real pitch_increment_raw;
  Real yaw_increment_raw;
  Real roll_increment;
  Real pitch_increment;
  Real yaw_increment;
  Real roll_cmd_fb;
  Real pitch_cmd_fb;
  Real yaw_cmd_fb;
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
  der(roll_error_filter) = (roll_error - roll_error_filter) / attitude_rate_filter_T;
  der(pitch_error_filter) = (pitch_error - pitch_error_filter) / attitude_rate_filter_T;
  roll_error_rate = (roll_error - roll_error_filter) / attitude_rate_filter_T;
  pitch_error_rate = (pitch_error - pitch_error_filter) / attitude_rate_filter_T;

  der(roll_mea_filter) = (roll_mea - roll_mea_filter) / attitude_rate_filter_T;
  der(pitch_mea_filter) = (pitch_mea - pitch_mea_filter) / attitude_rate_filter_T;
  der(yaw_mea_filter) = (yaw_mea - yaw_mea_filter) / attitude_rate_filter_T;
  roll_rate = (roll_mea - roll_mea_filter) / attitude_rate_filter_T;
  pitch_rate = (pitch_mea - pitch_mea_filter) / attitude_rate_filter_T;
  yaw_rate = (yaw_mea - yaw_mea_filter) / attitude_rate_filter_T;
  der(roll_rate_filter) = (roll_rate - roll_rate_filter) / angular_accel_filter_T;
  der(pitch_rate_filter) = (pitch_rate - pitch_rate_filter) / angular_accel_filter_T;
  der(yaw_rate_filter) = (yaw_rate - yaw_rate_filter) / angular_accel_filter_T;
  roll_accel_hat = (roll_rate - roll_rate_filter) / angular_accel_filter_T;
  pitch_accel_hat = (pitch_rate - pitch_rate_filter) / angular_accel_filter_T;
  yaw_accel_hat = (yaw_rate - yaw_rate_filter) / angular_accel_filter_T;

  roll_cmd_fb = kp_roll * roll_error + kd_roll * roll_error_rate;
  pitch_cmd_fb = kp_pitch * pitch_error + kd_pitch * pitch_error_rate;
  yaw_cmd_fb = kp_yaw * yaw_error;
  roll_accel_cmd = roll_cmd_fb;
  pitch_accel_cmd = pitch_cmd_fb;
  yaw_accel_cmd = yaw_cmd_fb;
  roll_increment_raw = indi_roll_gain * (roll_accel_cmd - roll_accel_hat);
  pitch_increment_raw = indi_pitch_gain * (pitch_accel_cmd - pitch_accel_hat);
  yaw_increment_raw = indi_yaw_gain * (yaw_accel_cmd - yaw_accel_hat);
  roll_increment = if roll_increment_raw > indi_increment_limit then indi_increment_limit else if roll_increment_raw < -indi_increment_limit then -indi_increment_limit else roll_increment_raw;
  pitch_increment = if pitch_increment_raw > indi_increment_limit then indi_increment_limit else if pitch_increment_raw < -indi_increment_limit then -indi_increment_limit else pitch_increment_raw;
  yaw_increment = if yaw_increment_raw > indi_increment_limit then indi_increment_limit else if yaw_increment_raw < -indi_increment_limit then -indi_increment_limit else yaw_increment_raw;

  roll_cmd_raw = attitude_feedback_blend * roll_cmd_fb + roll_increment;
  pitch_cmd_raw = attitude_feedback_blend * pitch_cmd_fb + pitch_increment;
  yaw_cmd_raw = attitude_feedback_blend * yaw_cmd_fb + yaw_increment;

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

  y = if u1_raw > output_limit then output_limit else if u1_raw < -output_limit then -output_limit else u1_raw;
  y1 = if u2_raw > output_limit then output_limit else if u2_raw < -output_limit then -output_limit else u2_raw;
  y2 = if u3_raw > output_limit then output_limit else if u3_raw < -output_limit then -output_limit else u3_raw;
  y3 = if u4_raw > output_limit then output_limit else if u4_raw < -output_limit then -output_limit else u4_raw;
end AWFF_INDIControllerEquation_Sysblock;