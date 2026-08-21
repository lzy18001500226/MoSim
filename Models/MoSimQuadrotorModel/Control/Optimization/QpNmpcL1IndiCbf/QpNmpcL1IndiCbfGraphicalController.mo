within MoSimQuadrotorModel.Control.Optimization.QpNmpcL1IndiCbf;
model QpNmpcL1IndiCbfGraphicalController
  "Verified LinearMPC base controller with online QP/NMPC safety projection and mode events"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref,elapsed_time), Right(y,y1,y2,y3,controller_mode,safety_active,event_code,return_ref_x,return_ref_y,return_ref_z)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
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
  SysplorerEmbeddedCoder.Port.Inport elapsed_time annotation(Placement(transformation(origin={-320,-215},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

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
    annotation(Placement(transformation(origin={-40,20},extent={{-80,-80},{80,80}})));
  MoSimQuadrotorModel.Control.Optimization.QpNmpcL1IndiCbf.QpNmpcL1IndiCbfSafetyProjectionGraphical safety_projection(
    qp_output_limit=qp_output_limit, qp_r_motor=qp_r_motor, qp_rho=qp_rho, qp_step=qp_step,
    nmpc_yaw_coupling=nmpc_yaw_coupling, altitude_tracking_error_margin=altitude_tracking_error_margin,
    altitude_cbf_gain=altitude_cbf_gain, max_tilt_rad=max_tilt_rad,
    safety_error_threshold_m=safety_error_threshold_m, emergency_error_threshold_m=emergency_error_threshold_m,
    return_trigger_time_s=return_trigger_time_s, land_trigger_time_s=land_trigger_time_s,
    landing_altitude_m=landing_altitude_m) 
    annotation(Placement(transformation(origin={170,20},extent={{-90,-125},{90,125}})), __MWORKS(SECInstance=true));

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
  connect(x_error, safety_projection.x_error);
  connect(y_error, safety_projection.y_error);
  connect(z_error, safety_projection.z_error);
  connect(roll_mea, safety_projection.roll_mea);
  connect(pitch_mea, safety_projection.pitch_mea);
  connect(yaw_mea, safety_projection.yaw_mea);
  connect(elapsed_time, safety_projection.elapsed_time);
  connect(nominal_mpc.y, safety_projection.nominal_y);
  connect(nominal_mpc.y1, safety_projection.nominal_y1);
  connect(nominal_mpc.y2, safety_projection.nominal_y2);
  connect(nominal_mpc.y3, safety_projection.nominal_y3);
  connect(safety_projection.y, y);
  connect(safety_projection.y1, y1);
  connect(safety_projection.y2, y2);
  connect(safety_projection.y3, y3);
  connect(safety_projection.controller_mode, controller_mode);
  connect(safety_projection.safety_active, safety_active);
  connect(safety_projection.event_code, event_code);
  connect(safety_projection.return_ref_x, return_ref_x);
  connect(safety_projection.return_ref_y, return_ref_y);
  connect(safety_projection.return_ref_z, return_ref_z);
end QpNmpcL1IndiCbfGraphicalController;