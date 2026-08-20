within MoSimQuadrotorModel.Control.Optimization.QpNmpcL1IndiCbf;
model QpNmpcL1IndiCbfGraphicalController
  "Verified LinearMPC base controller with online QP/NMPC safety projection and mode events"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3,controller_mode,safety_active,event_code,return_ref_x,return_ref_y,return_ref_z)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

  parameter Real qp_output_limit = 20.0;
  parameter Real qp_r_motor = 0.0;
  parameter Real qp_rho = 1.0;
  parameter Real qp_step = 0.50;
  parameter Real nmpc_tilt_softening = 0.02;
  parameter Real nmpc_yaw_coupling = 0.0;
  parameter Real altitude_tracking_error_margin = 0.35;
  parameter Real altitude_cbf_gain = 0.25;
  parameter Real max_tilt_rad = 0.55;
  parameter Real safety_error_threshold_m = 0.75;
  parameter Real emergency_error_threshold_m = 1.60;
  parameter Real return_trigger_time_s = 1e9;
  parameter Real land_trigger_time_s = 1e9;
  parameter Real landing_altitude_m = 0.15;

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={280,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={280,145},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={280,100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={280,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport controller_mode annotation(Placement(transformation(origin={280,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport safety_active annotation(Placement(transformation(origin={280,-45},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport event_code annotation(Placement(transformation(origin={280,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_x annotation(Placement(transformation(origin={280,-135},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_y annotation(Placement(transformation(origin={280,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport return_ref_z annotation(Placement(transformation(origin={280,-220},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  // Keep the nominal MPC path graphical so the safety projection is composed
  // from a current, checkable Sysblock controller rather than a removed bridge.
  MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi.LinearMpcL1IndiGraphicalController nominal_mpc 
    annotation(Placement(transformation(origin={-40,20},extent={{-80,-80},{80,80}})), __MWORKS(SECInstance=true));

  Real position_error_norm;
  Real tilt_norm;
  Real nmpc_scale;
  Real altitude_boost;
  Real u1_nominal;
  Real u2_nominal;
  Real u3_nominal;
  Real u4_nominal;
  Real u1_qp1;
  Real u2_qp1;
  Real u3_qp1;
  Real u4_qp1;
  Real u1_qp2;
  Real u2_qp2;
  Real u3_qp2;
  Real u4_qp2;
  Real u1_safe_raw;
  Real u2_safe_raw;
  Real u3_safe_raw;
  Real u4_safe_raw;

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, nominal_mpc.x_error);
  connect(y_error, nominal_mpc.y_error);
  connect(z_error, nominal_mpc.z_error);
  connect(z_ref_rate, nominal_mpc.z_ref_rate);
  connect(roll_mea, nominal_mpc.roll_mea);
  connect(pitch_mea, nominal_mpc.pitch_mea);
  connect(yaw_mea, nominal_mpc.yaw_mea);
  connect(yaw_ref, nominal_mpc.yaw_ref);

  position_error_norm = sqrt(x_error * x_error + y_error * y_error + z_error * z_error);
  tilt_norm = sqrt(roll_mea * roll_mea + pitch_mea * pitch_mea);
  nmpc_scale = 1 / (1 + nmpc_tilt_softening * tilt_norm * tilt_norm);
  altitude_boost = if z_error > altitude_tracking_error_margin then altitude_cbf_gain * (z_error - altitude_tracking_error_margin) else 0;

  u1_nominal = nmpc_scale * nominal_mpc.y + nmpc_yaw_coupling * yaw_mea + altitude_boost;
  u2_nominal = nmpc_scale * nominal_mpc.y1 - nmpc_yaw_coupling * yaw_mea - altitude_boost;
  u3_nominal = nmpc_scale * nominal_mpc.y2 + nmpc_yaw_coupling * yaw_mea + altitude_boost;
  u4_nominal = nmpc_scale * nominal_mpc.y3 - nmpc_yaw_coupling * yaw_mea - altitude_boost;

  u1_qp1 = u1_nominal - qp_step * (qp_r_motor * u1_nominal + qp_rho * (if u1_nominal > qp_output_limit then u1_nominal - qp_output_limit else if u1_nominal < -qp_output_limit then u1_nominal + qp_output_limit else 0));
  u2_qp1 = u2_nominal - qp_step * (qp_r_motor * u2_nominal + qp_rho * (if u2_nominal > qp_output_limit then u2_nominal - qp_output_limit else if u2_nominal < -qp_output_limit then u2_nominal + qp_output_limit else 0));
  u3_qp1 = u3_nominal - qp_step * (qp_r_motor * u3_nominal + qp_rho * (if u3_nominal > qp_output_limit then u3_nominal - qp_output_limit else if u3_nominal < -qp_output_limit then u3_nominal + qp_output_limit else 0));
  u4_qp1 = u4_nominal - qp_step * (qp_r_motor * u4_nominal + qp_rho * (if u4_nominal > qp_output_limit then u4_nominal - qp_output_limit else if u4_nominal < -qp_output_limit then u4_nominal + qp_output_limit else 0));
  u1_qp2 = u1_qp1 - qp_step * (qp_r_motor * u1_qp1 + qp_rho * (if u1_qp1 > qp_output_limit then u1_qp1 - qp_output_limit else if u1_qp1 < -qp_output_limit then u1_qp1 + qp_output_limit else 0));
  u2_qp2 = u2_qp1 - qp_step * (qp_r_motor * u2_qp1 + qp_rho * (if u2_qp1 > qp_output_limit then u2_qp1 - qp_output_limit else if u2_qp1 < -qp_output_limit then u2_qp1 + qp_output_limit else 0));
  u3_qp2 = u3_qp1 - qp_step * (qp_r_motor * u3_qp1 + qp_rho * (if u3_qp1 > qp_output_limit then u3_qp1 - qp_output_limit else if u3_qp1 < -qp_output_limit then u3_qp1 + qp_output_limit else 0));
  u4_qp2 = u4_qp1 - qp_step * (qp_r_motor * u4_qp1 + qp_rho * (if u4_qp1 > qp_output_limit then u4_qp1 - qp_output_limit else if u4_qp1 < -qp_output_limit then u4_qp1 + qp_output_limit else 0));

  safety_active = if position_error_norm > safety_error_threshold_m or tilt_norm > max_tilt_rad then 1 else 0;
  controller_mode = if time >= land_trigger_time_s or position_error_norm > emergency_error_threshold_m then 4 else if time >= return_trigger_time_s then 3 else if safety_active > 0.5 then 2 else 1;
  event_code = if controller_mode >= 4 then 40 else if controller_mode >= 3 then 30 else if safety_active > 0.5 then 20 else 10;
  return_ref_x = if controller_mode >= 3 then 0 else x_error;
  return_ref_y = if controller_mode >= 3 then 0 else y_error;
  return_ref_z = if controller_mode >= 4 then landing_altitude_m else if controller_mode >= 3 then 1.0 else z_error;

  u1_safe_raw = u1_qp2;
  u2_safe_raw = u2_qp2;
  u3_safe_raw = u3_qp2;
  u4_safe_raw = u4_qp2;
  y = if u1_safe_raw > qp_output_limit then qp_output_limit else if u1_safe_raw < -qp_output_limit then -qp_output_limit else u1_safe_raw;
  y1 = if u2_safe_raw > qp_output_limit then qp_output_limit else if u2_safe_raw < -qp_output_limit then -qp_output_limit else u2_safe_raw;
  y2 = if u3_safe_raw > qp_output_limit then qp_output_limit else if u3_safe_raw < -qp_output_limit then -qp_output_limit else u3_safe_raw;
  y3 = if u4_safe_raw > qp_output_limit then qp_output_limit else if u4_safe_raw < -qp_output_limit then -qp_output_limit else u4_safe_raw;
end QpNmpcL1IndiCbfGraphicalController;
