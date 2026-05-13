model AWFF_LinearMPCMultiFaultAllocationController_Sysblock
  "Linear MPC-style outer loop with four-rotor online fault isolation and allocation"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3,eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-340,-240},{320,240}},grid={2,2})));

  parameter Real eta_min_est = 0.50;
  parameter Real eta_max_est = 1.00;
  parameter Real eta_est_filter_T = 5.0;
  parameter Real eta_signature_deadband = 0.015;
  parameter Real eta_signature_gain = 2.65;
  parameter Real fault_lock_margin = 0.012;
  parameter Real allocation_blend = 0.52;
  parameter Real output_limit = 20.0;
  parameter Real position_signature_filter_T = 0.05;

  SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={280,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={280,140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={280,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={280,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={280,-20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={280,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={280,-120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={280,-170},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={280,-220},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock base_mpc annotation(Placement(transformation(origin={-35,20},extent={{-80,-80},{80,80}})));

  Real x_error_filter(start = 0, fixed = true);
  Real y_error_filter(start = 0, fixed = true);
  Real sig1;
  Real sig2;
  Real sig3;
  Real sig4;
  Real eta_target1;
  Real eta_target2;
  Real eta_target3;
  Real eta_target4;
  Real eta_hat1_state(start = 1.0, fixed = true);
  Real eta_hat2_state(start = 1.0, fixed = true);
  Real eta_hat3_state(start = 1.0, fixed = true);
  Real eta_hat4_state(start = 1.0, fixed = true);
  Real gain_alloc1;
  Real gain_alloc2;
  Real gain_alloc3;
  Real gain_alloc4;
  Real u1_allocated_raw;
  Real u2_allocated_raw;
  Real u3_allocated_raw;
  Real u4_allocated_raw;
  Real max_sig;
  Real second_sig;
  Real fault_candidate;
  Real fault_index_state(start = 0, fixed = true);

  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

equation
  connect(x_error, base_mpc.x_error);
  connect(y_error, base_mpc.y_error);
  connect(z_error, base_mpc.z_error);
  connect(z_ref_rate, base_mpc.z_ref_rate);
  connect(roll_mea, base_mpc.roll_mea);
  connect(pitch_mea, base_mpc.pitch_mea);
  connect(yaw_mea, base_mpc.yaw_mea);
  connect(yaw_ref, base_mpc.yaw_ref);

  der(x_error_filter) = (x_error - x_error_filter) / position_signature_filter_T;
  der(y_error_filter) = (y_error - y_error_filter) / position_signature_filter_T;

  sig1 = if (-x_error_filter + y_error_filter) / 2 > eta_signature_deadband then (-x_error_filter + y_error_filter) / 2 - eta_signature_deadband else 0;
  sig2 = if (-x_error_filter - y_error_filter) / 2 > eta_signature_deadband then (-x_error_filter - y_error_filter) / 2 - eta_signature_deadband else 0;
  sig3 = if (x_error_filter - y_error_filter) / 2 > eta_signature_deadband then (x_error_filter - y_error_filter) / 2 - eta_signature_deadband else 0;
  sig4 = if (x_error_filter + y_error_filter) / 2 > eta_signature_deadband then (x_error_filter + y_error_filter) / 2 - eta_signature_deadband else 0;
  eta_target1 = if 1 - eta_signature_gain * sig1 < eta_min_est then eta_min_est else if 1 - eta_signature_gain * sig1 > eta_max_est then eta_max_est else 1 - eta_signature_gain * sig1;
  eta_target2 = if 1 - eta_signature_gain * sig2 < eta_min_est then eta_min_est else if 1 - eta_signature_gain * sig2 > eta_max_est then eta_max_est else 1 - eta_signature_gain * sig2;
  eta_target3 = if 1 - eta_signature_gain * sig3 < eta_min_est then eta_min_est else if 1 - eta_signature_gain * sig3 > eta_max_est then eta_max_est else 1 - eta_signature_gain * sig3;
  eta_target4 = if 1 - eta_signature_gain * sig4 < eta_min_est then eta_min_est else if 1 - eta_signature_gain * sig4 > eta_max_est then eta_max_est else 1 - eta_signature_gain * sig4;
  der(eta_hat1_state) = (eta_target1 - eta_hat1_state) / eta_est_filter_T;
  der(eta_hat2_state) = (eta_target2 - eta_hat2_state) / eta_est_filter_T;
  der(eta_hat3_state) = (eta_target3 - eta_hat3_state) / eta_est_filter_T;
  der(eta_hat4_state) = (eta_target4 - eta_hat4_state) / eta_est_filter_T;
  eta_hat1 = if eta_hat1_state < eta_min_est then eta_min_est else if eta_hat1_state > eta_max_est then eta_max_est else eta_hat1_state;
  eta_hat2 = if eta_hat2_state < eta_min_est then eta_min_est else if eta_hat2_state > eta_max_est then eta_max_est else eta_hat2_state;
  eta_hat3 = if eta_hat3_state < eta_min_est then eta_min_est else if eta_hat3_state > eta_max_est then eta_max_est else eta_hat3_state;
  eta_hat4 = if eta_hat4_state < eta_min_est then eta_min_est else if eta_hat4_state > eta_max_est then eta_max_est else eta_hat4_state;

  gain_alloc1 = 1 + allocation_blend * (1 / eta_hat1 - 1);
  gain_alloc2 = 1 + allocation_blend * (1 / eta_hat2 - 1);
  gain_alloc3 = 1 + allocation_blend * (1 / eta_hat3 - 1);
  gain_alloc4 = 1 + allocation_blend * (1 / eta_hat4 - 1);
  u1_allocated_raw = base_mpc.y * gain_alloc1;
  u2_allocated_raw = base_mpc.y1 * gain_alloc2;
  u3_allocated_raw = base_mpc.y2 * gain_alloc3;
  u4_allocated_raw = base_mpc.y3 * gain_alloc4;

  max_sig = max(max(sig1, sig2), max(sig3, sig4));
  second_sig = if sig1 >= sig2 and sig1 >= sig3 and sig1 >= sig4 then max(max(sig2, sig3), sig4) else if sig2 >= sig1 and sig2 >= sig3 and sig2 >= sig4 then max(max(sig1, sig3), sig4) else if sig3 >= sig1 and sig3 >= sig2 and sig3 >= sig4 then max(max(sig1, sig2), sig4) else max(max(sig1, sig2), sig3);
  fault_candidate = if max_sig <= 0 then 0 else if sig1 >= sig2 and sig1 >= sig3 and sig1 >= sig4 then 1 else if sig2 >= sig1 and sig2 >= sig3 and sig2 >= sig4 then 2 else if sig3 >= sig1 and sig3 >= sig2 and sig3 >= sig4 then 3 else 4;
  der(fault_index_state) = 0;
  when fault_index_state < 0.5 and max_sig > eta_signature_deadband and max_sig - second_sig > fault_lock_margin then
    reinit(fault_index_state, fault_candidate);
  end when;
  fault_index = fault_index_state;

  y = if u1_allocated_raw > output_limit then output_limit else if u1_allocated_raw < -output_limit then -output_limit else u1_allocated_raw;
  y1 = if u2_allocated_raw > output_limit then output_limit else if u2_allocated_raw < -output_limit then -output_limit else u2_allocated_raw;
  y2 = if u3_allocated_raw > output_limit then output_limit else if u3_allocated_raw < -output_limit then -output_limit else u3_allocated_raw;
  y3 = if u4_allocated_raw > output_limit then output_limit else if u4_allocated_raw < -output_limit then -output_limit else u4_allocated_raw;
end AWFF_LinearMPCMultiFaultAllocationController_Sysblock;
