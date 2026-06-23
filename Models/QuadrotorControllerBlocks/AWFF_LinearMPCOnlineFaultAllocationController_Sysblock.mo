model AWFF_LinearMPCOnlineFaultAllocationController_Sysblock
  "Linear MPC-style outer loop with online rotor-1 efficiency allocation compensation"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3,eta_hat)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{300,220}},grid={2,2})));

  parameter Real eta_min_est = 0.50;
  parameter Real eta_max_est = 1.00;
  parameter Real eta_est_filter_T = 5.0;
  parameter Real eta_signature_deadband = 0.015;
  parameter Real eta_signature_gain = 2.65;
  parameter Real rotor1_allocation_blend = 0.52;
  parameter Real output_limit = 20.0;
  parameter Real position_signature_filter_T = 0.05;
  parameter Real steady_xy_integral_gain = 0.28;
  parameter Real steady_xy_integral_limit = 0.22;

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

  AWFF_LinearMPCOuterLoopControllerEquation_Sysblock base_mpc annotation(Placement(transformation(origin={-20,10},extent={{-80,-80},{80,80}})));

  Real x_error_filter(start = 0, fixed = true);
  Real y_error_filter(start = 0, fixed = true);
  Real x_bias_integral(start = 0, fixed = true);
  Real y_bias_integral(start = 0, fixed = true);
  Real x_bias_comp;
  Real y_bias_comp;
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
  der(x_bias_integral) = x_error;
  der(y_bias_integral) = y_error;
  x_bias_comp = steady_xy_integral_gain * (if x_bias_integral > steady_xy_integral_limit then steady_xy_integral_limit else if x_bias_integral < -steady_xy_integral_limit then -steady_xy_integral_limit else x_bias_integral);
  y_bias_comp = steady_xy_integral_gain * (if y_bias_integral > steady_xy_integral_limit then steady_xy_integral_limit else if y_bias_integral < -steady_xy_integral_limit then -steady_xy_integral_limit else y_bias_integral);
  base_mpc.x_error = x_error + x_bias_comp;
  base_mpc.y_error = y_error + y_bias_comp;
  connect(z_error, base_mpc.z_error);
  connect(z_ref_rate, base_mpc.z_ref_rate);
  connect(roll_mea, base_mpc.roll_mea);
  connect(pitch_mea, base_mpc.pitch_mea);
  connect(yaw_mea, base_mpc.yaw_mea);
  connect(yaw_ref, base_mpc.yaw_ref);

  connect(base_mpc.y1, y1);
  connect(base_mpc.y2, y2);
  connect(base_mpc.y3, y3);

  der(x_error_filter) = (x_error - x_error_filter) / position_signature_filter_T;
  der(y_error_filter) = (y_error - y_error_filter) / position_signature_filter_T;
  eta_signature = if (-x_error_filter + y_error_filter) / 2 > eta_signature_deadband then (-x_error_filter + y_error_filter) / 2 - eta_signature_deadband else 0;
  eta_target_raw = 1 - eta_signature_gain * eta_signature;
  eta_target = if eta_target_raw < eta_min_est then eta_min_est else if eta_target_raw > eta_max_est then eta_max_est else eta_target_raw;
  der(eta_hat_state) = (eta_target - eta_hat_state) / eta_est_filter_T;
  eta_hat = if eta_hat_state < eta_min_est then eta_min_est else if eta_hat_state > eta_max_est then eta_max_est else eta_hat_state;

  rotor1_eff_safe = if eta_hat < eta_min_est then eta_min_est else eta_hat;
  rotor1_allocation_gain = 1 + rotor1_allocation_blend * (1 / rotor1_eff_safe - 1);
  u1_allocated_raw = base_mpc.y * rotor1_allocation_gain;
  y = if u1_allocated_raw > output_limit then output_limit else if u1_allocated_raw < -output_limit then -output_limit else u1_allocated_raw;
end AWFF_LinearMPCOnlineFaultAllocationController_Sysblock;