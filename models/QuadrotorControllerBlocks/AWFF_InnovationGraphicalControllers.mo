model AWFF_InnovationGraphicalControllers
  "Openable overview for graphical L1, INDI, and rotor fault-isolation Sysblock controllers"
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  extends ModelWorkspace;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false),graphics={
      Rectangle(extent={{-100,-100},{100,100}},lineColor={45,80,120},fillColor={238,246,255},fillPattern=FillPattern.Solid,radius=8),
      Text(extent={{-90,34},{90,-2}},textString="AWFF",lineColor={20,45,75}),
      Text(extent={{-90,-10},{90,-44}},textString="Innovation",lineColor={20,45,75}),
      Text(extent={{-90,-52},{90,-82}},textString="L1 / INDI / Fault",lineColor={85,105,125})}),
    Diagram(coordinateSystem(extent={{-340,-220},{340,220}},grid={2,2})));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;

  model SymmetricLimiterKernelBlock
    "Equation kernel for symmetric saturation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(u),Right(y)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={115,115,115},fillColor={250,250,250},fillPattern=FillPattern.Solid,radius=6),
        Text(extent={{-90,24},{90,-24}},textString="sat eq",lineColor={70,70,70})}),
      Diagram(coordinateSystem(extent={{-120,-80},{120,80}},grid={2,2})));
    parameter Real limit=1.0;
    SysplorerEmbeddedCoder.Port.Inport u annotation(Placement(transformation(origin={-100,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={100,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
  equation
    y = min(max(u,-limit),limit);
  end SymmetricLimiterKernelBlock;

  model SymmetricLimiterBlock
    "Primitive graphical limiter with real signal ports"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(u),Right(y)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={100,100,100},fillColor={245,245,245},fillPattern=FillPattern.Solid,radius=6),
        Text(extent={{-84,24},{84,-24}},textString="limit",lineColor={60,60,60})}),
      Diagram(coordinateSystem(extent={{-120,-80},{120,80}},grid={2,2})));

    parameter Real limit=1.0;
    SysplorerEmbeddedCoder.Port.Inport u annotation(Placement(transformation(origin={-100,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={100,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SymmetricLimiterKernelBlock limiter_kernel(limit=limit) annotation(Placement(transformation(origin={0,0},extent={{-30,-20},{30,20}})));
  equation
    connect(u,limiter_kernel.u) annotation(Line(points={{-90,0},{-31,0}},color={0,0,0}));
    connect(limiter_kernel.y,y) annotation(Line(points={{31,0},{90,0}},color={0,0,0}));
  end SymmetricLimiterBlock;

  model EfficiencyCompensationKernelBlock
    "Equation kernel for efficiency-aware rotor allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(raw_cmd,eta_hat),Right(y)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={130,80,65},fillColor={255,246,242},fillPattern=FillPattern.Solid,radius=6),
        Text(extent={{-90,24},{90,-24}},textString="eta alloc",lineColor={95,50,35})}),
      Diagram(coordinateSystem(extent={{-140,-80},{140,80}},grid={2,2})));
    parameter Real output_limit=20.0;
    parameter Real allocation_blend=0.52;
    parameter Real min_rotor_efficiency=0.50;
    SysplorerEmbeddedCoder.Port.Inport raw_cmd annotation(Placement(transformation(origin={-120,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat annotation(Placement(transformation(origin={-120,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={120,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    Real eta_safe;
  equation
    eta_safe = max(eta_hat,min_rotor_efficiency);
    y = min(max(raw_cmd * (1 + allocation_blend * (1 / eta_safe - 1)),-output_limit),output_limit);
  end EfficiencyCompensationKernelBlock;

  model FaultSignatureEstimatorKernelBlock
    "Equation kernel for four-rotor fault signature estimation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error),Right(eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={145,55,55},fillColor={255,244,244},fillPattern=FillPattern.Solid,radius=6),
        Text(extent={{-90,24},{90,-8}},textString="signature",lineColor={105,40,40}),
        Text(extent={{-90,-12},{90,-42}},textString="estimate",lineColor={105,40,40})}),
      Diagram(coordinateSystem(extent={{-160,-120},{160,120}},grid={2,2})));
    parameter Real eta_min_est=0.50;
    parameter Real eta_max_est=1.00;
    parameter Real eta_signature_deadband=0.015;
    parameter Real eta_signature_gain=2.65;
    parameter Real fault_lock_margin=0.012;
    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-140,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-140,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={140,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={140,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={140,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={140,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={140,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    Real x_error_filter(start=0,fixed=true);
    Real y_error_filter(start=0,fixed=true);
    Real sig1;
    Real sig2;
    Real sig3;
    Real sig4;
    Real eta_hat1_state(start=1.0,fixed=true);
    Real eta_hat2_state(start=1.0,fixed=true);
    Real eta_hat3_state(start=1.0,fixed=true);
    Real eta_hat4_state(start=1.0,fixed=true);
    Real max_sig;
    Real second_sig;
    Real fault_candidate;
    Real fault_index_state(start=0,fixed=true);
  equation
    x_error_filter = x_error;
    y_error_filter = y_error;
    sig1 = max((-x_error_filter + y_error_filter) / 2 - eta_signature_deadband,0);
    sig2 = max((-x_error_filter - y_error_filter) / 2 - eta_signature_deadband,0);
    sig3 = max((x_error_filter - y_error_filter) / 2 - eta_signature_deadband,0);
    sig4 = max((x_error_filter + y_error_filter) / 2 - eta_signature_deadband,0);
    eta_hat1_state = min(max(1 - eta_signature_gain * sig1,eta_min_est),eta_max_est);
    eta_hat2_state = min(max(1 - eta_signature_gain * sig2,eta_min_est),eta_max_est);
    eta_hat3_state = min(max(1 - eta_signature_gain * sig3,eta_min_est),eta_max_est);
    eta_hat4_state = min(max(1 - eta_signature_gain * sig4,eta_min_est),eta_max_est);
    eta_hat1 = min(max(eta_hat1_state,eta_min_est),eta_max_est);
    eta_hat2 = min(max(eta_hat2_state,eta_min_est),eta_max_est);
    eta_hat3 = min(max(eta_hat3_state,eta_min_est),eta_max_est);
    eta_hat4 = min(max(eta_hat4_state,eta_min_est),eta_max_est);
    max_sig = max(max(sig1,sig2),max(sig3,sig4));
    second_sig = if sig1 >= sig2 and sig1 >= sig3 and sig1 >= sig4 then max(max(sig2,sig3),sig4) else if sig2 >= sig1 and sig2 >= sig3 and sig2 >= sig4 then max(max(sig1,sig3),sig4) else if sig3 >= sig1 and sig3 >= sig2 and sig3 >= sig4 then max(max(sig1,sig2),sig4) else max(max(sig1,sig2),sig3);
    fault_candidate = if max_sig <= 0 then 0 else if sig1 >= sig2 and sig1 >= sig3 and sig1 >= sig4 then 1 else if sig2 >= sig1 and sig2 >= sig3 and sig2 >= sig4 then 2 else if sig3 >= sig1 and sig3 >= sig2 and sig3 >= sig4 then 3 else 4;
    fault_index_state = if max_sig > eta_signature_deadband and max_sig - second_sig > fault_lock_margin then fault_candidate else 0;
    fault_index = fault_index_state;
  end FaultSignatureEstimatorKernelBlock;

  model L1ResidualOuterLoopBlock
    "L1-inspired residual compensated position outer loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate),Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={45,85,130},fillColor={238,246,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,30},{90,-4}},textString="L1 Residual",lineColor={20,45,75}),
        Text(extent={{-90,-12},{90,-46}},textString="Outer Loop",lineColor={20,45,75}),
        Text(extent={{-90,-54},{90,-82}},textString="e,r -> attitude,T",lineColor={85,105,125})}),
      Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));

    parameter Real kp_x=1.65;
    parameter Real kd_x=1.0;
    parameter Real kp_y=1.65;
    parameter Real kd_y=1.0;
    parameter Real kp_z=8.0;
    parameter Real ki_z=6.0;
    parameter Real kd_z=4.0;
    parameter Real kff_z=0.35;
    parameter Real roll_pitch_cmd_limit=12/57.3;
    parameter Real output_limit=20.0;
    parameter Real position_derivative_filter_T=0.05;
    parameter Real altitude_derivative_filter_T=0.08;
    parameter Real l1_model_decay=1.25;
    parameter Real l1_filter_T=0.20;
    parameter Real l1_gain_xy=0.32;
    parameter Real l1_gain_z=0.35;
    parameter Real l1_comp_limit_xy=2.0;
    parameter Real l1_comp_limit_z=2.0;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(Placement(transformation(origin={200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport thrust_ref annotation(Placement(transformation(origin={200,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Gain x_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,75},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-45,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock x_comp_limit(limit=l1_comp_limit_xy) annotation(Placement(transformation(origin={5,90},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kp_gain(k=kp_x) annotation(Placement(transformation(origin={-95,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kd_gain(k=kd_x) annotation(Placement(transformation(origin={-45,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_raw_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={55,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_scale(k=0.1) annotation(Placement(transformation(origin={105,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock pitch_cmd_limit(limit=roll_pitch_cmd_limit) annotation(Placement(transformation(origin={155,110},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Gain y_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-45,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock y_comp_limit(limit=l1_comp_limit_xy) annotation(Placement(transformation(origin={5,20},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kp_gain(k=kp_y) annotation(Placement(transformation(origin={-95,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kd_gain(k=kd_y) annotation(Placement(transformation(origin={-45,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_raw_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={55,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_scale(k=0.1) annotation(Placement(transformation(origin={105,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock roll_cmd_limit(limit=roll_pitch_cmd_limit) annotation(Placement(transformation(origin={155,40},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Gain z_rate_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-145,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-95,-55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_l1_gain(k=l1_gain_z) annotation(Placement(transformation(origin={-45,-55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock z_comp_limit(limit=l1_comp_limit_z) annotation(Placement(transformation(origin={5,-55},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kp_gain(k=kp_z) annotation(Placement(transformation(origin={-95,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kd_gain(k=kd_z) annotation(Placement(transformation(origin={-45,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ff_gain(k=kff_z) annotation(Placement(transformation(origin={-45,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Sources.Constant z_integral_zero(k=0) annotation(Placement(transformation(origin={-45,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_pid_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={35,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_l1_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={90,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock thrust_cmd_limit(limit=output_limit) annotation(Placement(transformation(origin={145,-85},extent={{-10,-10},{10,10}})));

  equation
    connect(x_error,x_rate_gain.u) annotation(Line(points={{-190,90},{-175,90},{-175,105},{-157,105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_decay_gain.u) annotation(Line(points={{-190,90},{-175,90},{-175,75},{-157,75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_kp_gain.u) annotation(Line(points={{-190,90},{-128,90},{-128,125},{-107,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_rate_gain.y,x_l1_sum.u1) annotation(Line(points={{-133,105},{-118,105},{-118,96},{-107,96}},color={0,0,0}));
    connect(x_decay_gain.y,x_l1_sum.u2) annotation(Line(points={{-133,75},{-118,75},{-118,84},{-107,84}},color={0,0,0}));
    connect(x_l1_sum.y,x_l1_gain.u) annotation(Line(points={{-83,90},{-57,90}},color={0,0,0}));
    connect(x_l1_gain.y,x_comp_limit.u) annotation(Line(points={{-33,90},{-7,90}},color={0,0,0}));
    connect(x_rate_gain.y,x_kd_gain.u) annotation(Line(points={{-133,105},{-118,105},{-118,125},{-57,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_kp_gain.y,pitch_raw_sum.u1) annotation(Line(points={{-83,125},{34,125},{34,118},{43,118}},color={0,0,0}));
    connect(x_kd_gain.y,pitch_raw_sum.u2) annotation(Line(points={{-33,125},{30,125},{30,110},{43,110}},color={0,0,0}));
    connect(x_comp_limit.y,pitch_raw_sum.u3) annotation(Line(points={{17,90},{34,90},{34,102},{43,102}},color={0,0,0}));
    connect(pitch_raw_sum.y,pitch_scale.u) annotation(Line(points={{67,110},{93,110}},color={0,0,0}));
    connect(pitch_scale.y,pitch_cmd_limit.u) annotation(Line(points={{117,110},{143,110}},color={0,0,0}));
    connect(pitch_cmd_limit.y,pitch_ref) annotation(Line(points={{167,110},{185,110},{185,70},{190,70}},color={0,0,0}));

    connect(y_error,y_rate_gain.u) annotation(Line(points={{-190,30},{-175,30},{-175,35},{-157,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_decay_gain.u) annotation(Line(points={{-190,30},{-175,30},{-175,5},{-157,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_kp_gain.u) annotation(Line(points={{-190,30},{-128,30},{-128,55},{-107,55}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_rate_gain.y,y_l1_sum.u1) annotation(Line(points={{-133,35},{-118,35},{-118,26},{-107,26}},color={0,0,0}));
    connect(y_decay_gain.y,y_l1_sum.u2) annotation(Line(points={{-133,5},{-118,5},{-118,14},{-107,14}},color={0,0,0}));
    connect(y_l1_sum.y,y_l1_gain.u) annotation(Line(points={{-83,20},{-57,20}},color={0,0,0}));
    connect(y_l1_gain.y,y_comp_limit.u) annotation(Line(points={{-33,20},{-7,20}},color={0,0,0}));
    connect(y_rate_gain.y,y_kd_gain.u) annotation(Line(points={{-133,35},{-118,35},{-118,55},{-57,55}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_kp_gain.y,roll_raw_sum.u1) annotation(Line(points={{-83,55},{34,55},{34,48},{43,48}},color={0,0,0}));
    connect(y_kd_gain.y,roll_raw_sum.u2) annotation(Line(points={{-33,55},{30,55},{30,40},{43,40}},color={0,0,0}));
    connect(y_comp_limit.y,roll_raw_sum.u3) annotation(Line(points={{17,20},{34,20},{34,32},{43,32}},color={0,0,0}));
    connect(roll_raw_sum.y,roll_scale.u) annotation(Line(points={{67,40},{93,40}},color={0,0,0}));
    connect(roll_scale.y,roll_cmd_limit.u) annotation(Line(points={{117,40},{143,40}},color={0,0,0}));
    connect(roll_cmd_limit.y,roll_ref) annotation(Line(points={{167,40},{185,40},{185,0},{190,0}},color={0,0,0}));

    connect(z_error,z_rate_gain.u) annotation(Line(points={{-190,-30},{-175,-30},{-175,-40},{-157,-40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_decay_gain.u) annotation(Line(points={{-190,-30},{-175,-30},{-175,-70},{-157,-70}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_kp_gain.u) annotation(Line(points={{-190,-30},{-128,-30},{-128,-105},{-107,-105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_rate_gain.y,z_l1_sum.u1) annotation(Line(points={{-133,-40},{-118,-40},{-118,-49},{-107,-49}},color={0,0,0}));
    connect(z_decay_gain.y,z_l1_sum.u2) annotation(Line(points={{-133,-70},{-118,-70},{-118,-61},{-107,-61}},color={0,0,0}));
    connect(z_l1_sum.y,z_l1_gain.u) annotation(Line(points={{-83,-55},{-57,-55}},color={0,0,0}));
    connect(z_l1_gain.y,z_comp_limit.u) annotation(Line(points={{-33,-55},{-7,-55}},color={0,0,0}));
    connect(z_rate_gain.y,z_kd_gain.u) annotation(Line(points={{-133,-40},{-120,-40},{-120,-105},{-57,-105}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_ref_rate,z_ff_gain.u) annotation(Line(points={{-190,-90},{-82,-90},{-82,-130},{-57,-130}},color={0,0,0}));
    connect(z_kp_gain.y,thrust_pid_sum.u1) annotation(Line(points={{-83,-105},{14,-105},{14,-107},{23,-107}},color={0,0,0}));
    connect(z_integral_zero.y,thrust_pid_sum.u2) annotation(Line(points={{-33,-80},{14,-80},{14,-99},{23,-99}},color={0,0,0}));
    connect(z_kd_gain.y,thrust_pid_sum.u3) annotation(Line(points={{-33,-105},{10,-105},{10,-91},{23,-91}},color={0,0,0}));
    connect(z_ff_gain.y,thrust_pid_sum.u4) annotation(Line(points={{-33,-130},{14,-130},{14,-83},{23,-83}},color={0,0,0}));
    connect(thrust_pid_sum.y,thrust_l1_sum.u1) annotation(Line(points={{47,-95},{72,-95},{72,-91},{78,-91}},color={0,0,0}));
    connect(z_comp_limit.y,thrust_l1_sum.u2) annotation(Line(points={{17,-55},{70,-55},{70,-79},{78,-79}},color={0,0,0}));
    connect(thrust_l1_sum.y,thrust_cmd_limit.u) annotation(Line(points={{102,-85},{133,-85}},color={0,0,0}));
    connect(thrust_cmd_limit.y,thrust_ref) annotation(Line(points={{157,-85},{180,-85},{180,-70},{190,-70}},color={0,0,0}));
  end L1ResidualOuterLoopBlock;

  model PIDAttitudeInnerLoopBlock
    "PID attitude inner loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={120,70,35},fillColor={255,244,232},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,28},{90,-6}},textString="PID",lineColor={80,45,20}),
        Text(extent={{-90,-12},{90,-46}},textString="Attitude",lineColor={80,45,20})}),
      Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));

    parameter Real kp_roll=14.142;
    parameter Real kd_roll=1.70;
    parameter Real kp_pitch=14.142;
    parameter Real kd_pitch=1.70;
    parameter Real kp_yaw=5.0;
    parameter Real attitude_derivative_filter_T=0.03;
    parameter Real attitude_cmd_limit=6.5;
    parameter Real yaw_cmd_limit=6.5;

    SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-200,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-200,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-200,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-200,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Sum roll_error_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-135,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_kp_gain(k=kp_roll) annotation(Placement(transformation(origin={-65,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_kd_over_filter_gain(k=kd_roll / attitude_derivative_filter_T) annotation(Placement(transformation(origin={-65,85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_cmd_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={10,105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock roll_cmd_limit_block(limit=attitude_cmd_limit) annotation(Placement(transformation(origin={100,105},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum pitch_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp_gain(k=kp_pitch) annotation(Placement(transformation(origin={-65,45},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd_over_filter_gain(k=kd_pitch / attitude_derivative_filter_T) annotation(Placement(transformation(origin={-65,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_cmd_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={10,25},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock pitch_cmd_limit_block(limit=attitude_cmd_limit) annotation(Placement(transformation(origin={100,25},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum yaw_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp_gain(k=kp_yaw) annotation(Placement(transformation(origin={-45,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock yaw_cmd_limit_block(limit=yaw_cmd_limit) annotation(Placement(transformation(origin={100,-85},extent={{-10,-10},{10,10}})));

  equation
    connect(roll_ref,roll_error_sum.u1) annotation(Line(points={{-190,120},{-160,120},{-160,111},{-147,111}},color={0,0,0}));
    connect(roll_mea,roll_error_sum.u2) annotation(Line(points={{-190,-40},{-170,-40},{-170,99},{-147,99}},color={0,0,0}));
    connect(roll_error_sum.y,roll_kp_gain.u) annotation(Line(points={{-123,105},{-100,105},{-100,125},{-77,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_error_sum.y,roll_kd_over_filter_gain.u) annotation(Line(points={{-123,105},{-100,105},{-100,85},{-77,85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_kp_gain.y,roll_cmd_raw_sum.u1) annotation(Line(points={{-53,125},{-14,125},{-14,111},{-2,111}},color={0,0,0}));
    connect(roll_kd_over_filter_gain.y,roll_cmd_raw_sum.u2) annotation(Line(points={{-53,85},{-14,85},{-14,99},{-2,99}},color={0,0,0}));
    connect(roll_cmd_raw_sum.y,roll_cmd_limit_block.u) annotation(Line(points={{22,105},{88,105}},color={0,0,0}));
    connect(roll_cmd_limit_block.y,roll_cmd) annotation(Line(points={{112,105},{160,105},{160,90},{190,90}},color={0,0,0}));

    connect(pitch_ref,pitch_error_sum.u1) annotation(Line(points={{-190,70},{-160,70},{-160,31},{-147,31}},color={0,0,0}));
    connect(pitch_mea,pitch_error_sum.u2) annotation(Line(points={{-190,-90},{-170,-90},{-170,19},{-147,19}},color={0,0,0}));
    connect(pitch_error_sum.y,pitch_kp_gain.u) annotation(Line(points={{-123,25},{-100,25},{-100,45},{-77,45}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_error_sum.y,pitch_kd_over_filter_gain.u) annotation(Line(points={{-123,25},{-100,25},{-100,5},{-77,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_kp_gain.y,pitch_cmd_raw_sum.u1) annotation(Line(points={{-53,45},{-14,45},{-14,31},{-2,31}},color={0,0,0}));
    connect(pitch_kd_over_filter_gain.y,pitch_cmd_raw_sum.u2) annotation(Line(points={{-53,5},{-14,5},{-14,19},{-2,19}},color={0,0,0}));
    connect(pitch_cmd_raw_sum.y,pitch_cmd_limit_block.u) annotation(Line(points={{22,25},{88,25}},color={0,0,0}));
    connect(pitch_cmd_limit_block.y,pitch_cmd) annotation(Line(points={{112,25},{160,25},{160,0},{190,0}},color={0,0,0}));

    connect(yaw_ref,yaw_error_sum.u1) annotation(Line(points={{-190,20},{-160,20},{-160,-79},{-147,-79}},color={0,0,0}));
    connect(yaw_mea,yaw_error_sum.u2) annotation(Line(points={{-190,-140},{-170,-140},{-170,-91},{-147,-91}},color={0,0,0}));
    connect(yaw_error_sum.y,yaw_kp_gain.u) annotation(Line(points={{-123,-85},{-57,-85}},color={0,0,0}));
    connect(yaw_kp_gain.y,yaw_cmd_limit_block.u) annotation(Line(points={{-33,-85},{88,-85}},color={0,0,0}));
    connect(yaw_cmd_limit_block.y,yaw_cmd) annotation(Line(points={{112,-85},{160,-85},{160,-90},{190,-90}},color={0,0,0}));
  end PIDAttitudeInnerLoopBlock;

  model INDIAttitudeInnerLoopBlock
    "INDI-like incremental attitude inner loop"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(roll_ref,pitch_ref,yaw_ref,roll_mea,pitch_mea,yaw_mea),Right(roll_cmd,pitch_cmd,yaw_cmd)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={130,65,135},fillColor={250,238,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,28},{90,-6}},textString="INDI",lineColor={85,40,95}),
        Text(extent={{-90,-12},{90,-46}},textString="Attitude",lineColor={85,40,95})}),
      Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));
    parameter Real kp_roll=14.142;
    parameter Real kd_roll=1.70;
    parameter Real kp_pitch=14.142;
    parameter Real kd_pitch=1.70;
    parameter Real kp_yaw=5.0;
    parameter Real attitude_cmd_limit=6.5;
    parameter Real yaw_cmd_limit=6.5;
    parameter Real attitude_rate_filter_T=0.035;
    parameter Real angular_accel_filter_T=0.08;
    parameter Real indi_roll_gain=0.015;
    parameter Real indi_pitch_gain=0.015;
    parameter Real indi_yaw_gain=0.005;
    parameter Real indi_increment_limit=0.15;
    parameter Real attitude_feedback_blend=1.00;
    SysplorerEmbeddedCoder.Port.Inport roll_ref annotation(Placement(transformation(origin={-200,120},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_ref annotation(Placement(transformation(origin={-200,70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-200,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-200,-40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-200,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_cmd annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_cmd annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport yaw_cmd annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_error_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-135,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_kp_gain(k=kp_roll) annotation(Placement(transformation(origin={-70,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_kd_over_rate_gain(k=kd_roll / attitude_rate_filter_T) annotation(Placement(transformation(origin={-70,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-5,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={50,125},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_indi_gain_block(k=indi_roll_gain) annotation(Placement(transformation(origin={50,95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock roll_inc_limit(limit=indi_increment_limit) annotation(Placement(transformation(origin={95,95},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum roll_indi_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={135,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock roll_cmd_limit_block(limit=attitude_cmd_limit) annotation(Placement(transformation(origin={170,110},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum pitch_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp_gain(k=kp_pitch) annotation(Placement(transformation(origin={-70,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd_over_rate_gain(k=kd_pitch / attitude_rate_filter_T) annotation(Placement(transformation(origin={-70,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-5,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={50,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_indi_gain_block(k=indi_pitch_gain) annotation(Placement(transformation(origin={50,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock pitch_inc_limit(limit=indi_increment_limit) annotation(Placement(transformation(origin={95,5},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_indi_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock pitch_cmd_limit_block(limit=attitude_cmd_limit) annotation(Placement(transformation(origin={170,20},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum yaw_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp_gain(k=kp_yaw) annotation(Placement(transformation(origin={-70,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={5,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_indi_gain_block(k=indi_yaw_gain) annotation(Placement(transformation(origin={5,-115},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock yaw_inc_limit(limit=indi_increment_limit) annotation(Placement(transformation(origin={55,-115},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum yaw_indi_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={110,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock yaw_cmd_limit_block(limit=yaw_cmd_limit) annotation(Placement(transformation(origin={165,-100},extent={{-10,-10},{10,10}})));
  equation
    connect(roll_ref,roll_error_sum.u1) annotation(Line(points={{-190,120},{-160,120},{-160,116},{-147,116}},color={0,0,0}));
    connect(roll_mea,roll_error_sum.u2) annotation(Line(points={{-190,-40},{-170,-40},{-170,104},{-147,104}},color={0,0,0}));
    connect(roll_error_sum.y,roll_kp_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,130},{-82,130}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_error_sum.y,roll_kd_over_rate_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,90},{-82,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_kp_gain.y,roll_raw_sum.u1) annotation(Line(points={{-58,130},{-26,130},{-26,116},{-17,116}},color={0,0,0}));
    connect(roll_kd_over_rate_gain.y,roll_raw_sum.u2) annotation(Line(points={{-58,90},{-26,90},{-26,104},{-17,104}},color={0,0,0}));
    connect(roll_raw_sum.y,roll_feedback_gain.u) annotation(Line(points={{7,110},{24,110},{24,125},{38,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_raw_sum.y,roll_indi_gain_block.u) annotation(Line(points={{7,110},{24,110},{24,95},{38,95}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_indi_gain_block.y,roll_inc_limit.u) annotation(Line(points={{62,95},{83,95}},color={0,0,0}));
    connect(roll_feedback_gain.y,roll_indi_sum.u1) annotation(Line(points={{62,125},{116,125},{116,116},{123,116}},color={0,0,0}));
    connect(roll_inc_limit.y,roll_indi_sum.u2) annotation(Line(points={{107,95},{116,95},{116,104},{123,104}},color={0,0,0}));
    connect(roll_indi_sum.y,roll_cmd_limit_block.u) annotation(Line(points={{147,110},{158,110}},color={0,0,0}));
    connect(roll_cmd_limit_block.y,roll_cmd) annotation(Line(points={{182,110},{190,110},{190,90}},color={0,0,0}));

    connect(pitch_ref,pitch_error_sum.u1) annotation(Line(points={{-190,70},{-160,70},{-160,26},{-147,26}},color={0,0,0}));
    connect(pitch_mea,pitch_error_sum.u2) annotation(Line(points={{-190,-90},{-170,-90},{-170,14},{-147,14}},color={0,0,0}));
    connect(pitch_error_sum.y,pitch_kp_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,40},{-82,40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_error_sum.y,pitch_kd_over_rate_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,0},{-82,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_kp_gain.y,pitch_raw_sum.u1) annotation(Line(points={{-58,40},{-26,40},{-26,26},{-17,26}},color={0,0,0}));
    connect(pitch_kd_over_rate_gain.y,pitch_raw_sum.u2) annotation(Line(points={{-58,0},{-26,0},{-26,14},{-17,14}},color={0,0,0}));
    connect(pitch_raw_sum.y,pitch_feedback_gain.u) annotation(Line(points={{7,20},{24,20},{24,35},{38,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_raw_sum.y,pitch_indi_gain_block.u) annotation(Line(points={{7,20},{24,20},{24,5},{38,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_indi_gain_block.y,pitch_inc_limit.u) annotation(Line(points={{62,5},{83,5}},color={0,0,0}));
    connect(pitch_feedback_gain.y,pitch_indi_sum.u1) annotation(Line(points={{62,35},{116,35},{116,26},{123,26}},color={0,0,0}));
    connect(pitch_inc_limit.y,pitch_indi_sum.u2) annotation(Line(points={{107,5},{116,5},{116,14},{123,14}},color={0,0,0}));
    connect(pitch_indi_sum.y,pitch_cmd_limit_block.u) annotation(Line(points={{147,20},{158,20}},color={0,0,0}));
    connect(pitch_cmd_limit_block.y,pitch_cmd) annotation(Line(points={{182,20},{190,20},{190,0}},color={0,0,0}));

    connect(yaw_ref,yaw_error_sum.u1) annotation(Line(points={{-190,20},{-160,20},{-160,-94},{-147,-94}},color={0,0,0}));
    connect(yaw_mea,yaw_error_sum.u2) annotation(Line(points={{-190,-140},{-170,-140},{-170,-106},{-147,-106}},color={0,0,0}));
    connect(yaw_error_sum.y,yaw_kp_gain.u) annotation(Line(points={{-123,-100},{-82,-100}},color={0,0,0}));
    connect(yaw_kp_gain.y,yaw_feedback_gain.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-85},{-7,-85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_kp_gain.y,yaw_indi_gain_block.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-115},{-7,-115}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_indi_gain_block.y,yaw_inc_limit.u) annotation(Line(points={{17,-115},{43,-115}},color={0,0,0}));
    connect(yaw_feedback_gain.y,yaw_indi_sum.u1) annotation(Line(points={{17,-85},{86,-85},{86,-94},{98,-94}},color={0,0,0}));
    connect(yaw_inc_limit.y,yaw_indi_sum.u2) annotation(Line(points={{67,-115},{86,-115},{86,-106},{98,-106}},color={0,0,0}));
    connect(yaw_indi_sum.y,yaw_cmd_limit_block.u) annotation(Line(points={{122,-100},{153,-100}},color={0,0,0}));
    connect(yaw_cmd_limit_block.y,yaw_cmd) annotation(Line(points={{177,-100},{190,-100},{190,-90}},color={0,0,0}));
  end INDIAttitudeInnerLoopBlock;

  model MotorMixerBlock
    "Quadrotor motor mixer"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={60,110,80},fillColor={238,250,242},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Motor",lineColor={30,75,50}),
        Text(extent={{-90,-12},{90,-46}},textString="Mixer",lineColor={30,75,50})}),
      Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));

    parameter Real output_limit=20.0;
    SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Gain roll_pos(k=0.707) annotation(Placement(transformation(origin={-130,65},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_neg(k=-0.707) annotation(Placement(transformation(origin={-130,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_pos(k=0.707) annotation(Placement(transformation(origin={-130,-5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_neg(k=-0.707) annotation(Placement(transformation(origin={-130,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_pos(k=0.707) annotation(Placement(transformation(origin={-130,-75},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_neg(k=-0.707) annotation(Placement(transformation(origin={-130,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain thrust_neg(k=-1.0) annotation(Placement(transformation(origin={-130,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.MathOperation.Sum motor1_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum motor2_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum motor3_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum motor4_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={20,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SymmetricLimiterBlock motor1_limit(limit=output_limit) annotation(Placement(transformation(origin={110,90},extent={{-10,-10},{10,10}})));
    SymmetricLimiterBlock motor2_limit(limit=output_limit) annotation(Placement(transformation(origin={110,30},extent={{-10,-10},{10,10}})));
    SymmetricLimiterBlock motor3_limit(limit=output_limit) annotation(Placement(transformation(origin={110,-30},extent={{-10,-10},{10,10}})));
    SymmetricLimiterBlock motor4_limit(limit=output_limit) annotation(Placement(transformation(origin={110,-90},extent={{-10,-10},{10,10}})));
  equation
    connect(thrust_ref,thrust_neg.u) annotation(Line(points={{-190,90},{-170,90},{-170,110},{-142,110}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_cmd,roll_pos.u) annotation(Line(points={{-190,30},{-164,30},{-164,65},{-142,65}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_cmd,roll_neg.u) annotation(Line(points={{-190,30},{-164,30},{-164,40},{-142,40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_cmd,pitch_pos.u) annotation(Line(points={{-190,-30},{-164,-30},{-164,-5},{-142,-5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_cmd,pitch_neg.u) annotation(Line(points={{-190,-30},{-142,-30}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_cmd,yaw_pos.u) annotation(Line(points={{-190,-90},{-164,-90},{-164,-75},{-142,-75}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_cmd,yaw_neg.u) annotation(Line(points={{-190,-90},{-164,-90},{-164,-100},{-142,-100}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

    connect(thrust_ref,motor1_sum.u1) annotation(Line(points={{-190,90},{0,90},{0,99},{8,99}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_pos.y,motor1_sum.u2) annotation(Line(points={{-118,65},{-10,65},{-10,93},{8,93}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_neg.y,motor1_sum.u3) annotation(Line(points={{-118,-30},{-4,-30},{-4,87},{8,87}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_neg.y,motor1_sum.u4) annotation(Line(points={{-118,-100},{2,-100},{2,81},{8,81}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

    connect(thrust_neg.y,motor2_sum.u1) annotation(Line(points={{-118,110},{-16,110},{-16,39},{8,39}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_pos.y,motor2_sum.u2) annotation(Line(points={{-118,65},{-8,65},{-8,33},{8,33}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_pos.y,motor2_sum.u3) annotation(Line(points={{-118,-5},{-8,-5},{-8,27},{8,27}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_neg.y,motor2_sum.u4) annotation(Line(points={{-118,-100},{0,-100},{0,21},{8,21}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

    connect(thrust_ref,motor3_sum.u1) annotation(Line(points={{-190,90},{-22,90},{-22,-21},{8,-21}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_neg.y,motor3_sum.u2) annotation(Line(points={{-118,40},{-14,40},{-14,-27},{8,-27}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_pos.y,motor3_sum.u3) annotation(Line(points={{-118,-5},{-10,-5},{-10,-33},{8,-33}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_neg.y,motor3_sum.u4) annotation(Line(points={{-118,-100},{-4,-100},{-4,-39},{8,-39}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

    connect(thrust_neg.y,motor4_sum.u1) annotation(Line(points={{-118,110},{-30,110},{-30,-81},{8,-81}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_neg.y,motor4_sum.u2) annotation(Line(points={{-118,40},{-22,40},{-22,-87},{8,-87}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_neg.y,motor4_sum.u3) annotation(Line(points={{-118,-30},{-14,-30},{-14,-93},{8,-93}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_neg.y,motor4_sum.u4) annotation(Line(points={{-118,-100},{8,-100},{8,-99}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));

    connect(motor1_sum.y,motor1_limit.u) annotation(Line(points={{32,90},{98,90}},color={0,0,0}));
    connect(motor2_sum.y,motor2_limit.u) annotation(Line(points={{32,30},{98,30}},color={0,0,0}));
    connect(motor3_sum.y,motor3_limit.u) annotation(Line(points={{32,-30},{98,-30}},color={0,0,0}));
    connect(motor4_sum.y,motor4_limit.u) annotation(Line(points={{32,-90},{98,-90}},color={0,0,0}));
    connect(motor1_limit.y,y) annotation(Line(points={{122,90},{190,90}},color={0,0,0}));
    connect(motor2_limit.y,y1) annotation(Line(points={{122,30},{190,30}},color={0,0,0}));
    connect(motor3_limit.y,y2) annotation(Line(points={{122,-30},{190,-30}},color={0,0,0}));
    connect(motor4_limit.y,y3) annotation(Line(points={{122,-90},{190,-90}},color={0,0,0}));
  end MotorMixerBlock;

  model KnownRotorFaultMixerBlock
    "Known rotor-1 efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={135,95,45},fillColor={255,248,232},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Fault",lineColor={95,65,25}),
        Text(extent={{-90,-12},{90,-46}},textString="Allocation",lineColor={95,65,25})}),
      Diagram(coordinateSystem(extent={{-220,-140},{220,140}},grid={2,2})));
    parameter Real output_limit=20.0;
    parameter Real rotor1_efficiency=0.85;
    parameter Real min_rotor_efficiency=0.50;
    parameter Real rotor1_allocation_blend=0.52;
    SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    MotorMixerBlock raw_mixer(output_limit=1e9) annotation(Placement(transformation(origin={-40,0},extent={{-45,-50},{45,50}})));
    SysplorerEmbeddedCoder.Sources.Constant rotor1_eta(k=rotor1_efficiency) annotation(Placement(transformation(origin={45,55},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(inherit=InheritType.constantValue,ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)))));
    EfficiencyCompensationKernelBlock rotor1_allocator(output_limit=output_limit,allocation_blend=rotor1_allocation_blend,min_rotor_efficiency=min_rotor_efficiency) annotation(Placement(transformation(origin={105,80},extent={{-30,-20},{30,20}})));
    SymmetricLimiterBlock motor2_limit(limit=output_limit) annotation(Placement(transformation(origin={105,20},extent={{-10,-10},{10,10}})));
    SymmetricLimiterBlock motor3_limit(limit=output_limit) annotation(Placement(transformation(origin={105,-40},extent={{-10,-10},{10,10}})));
    SymmetricLimiterBlock motor4_limit(limit=output_limit) annotation(Placement(transformation(origin={105,-100},extent={{-10,-10},{10,10}})));
  equation
    connect(thrust_ref,raw_mixer.thrust_ref) annotation(Line(points={{-190,90},{-120,90},{-120,32},{-86,32}},color={0,0,0}));
    connect(roll_cmd,raw_mixer.roll_cmd) annotation(Line(points={{-190,30},{-86,11}},color={0,0,0}));
    connect(pitch_cmd,raw_mixer.pitch_cmd) annotation(Line(points={{-190,-30},{-120,-30},{-120,-11},{-86,-11}},color={0,0,0}));
    connect(yaw_cmd,raw_mixer.yaw_cmd) annotation(Line(points={{-190,-90},{-120,-90},{-120,-32},{-86,-32}},color={0,0,0}));
    connect(raw_mixer.y,rotor1_allocator.raw_cmd) annotation(Line(points={{6,32},{42,32},{42,88},{74,88}},color={0,0,0}));
    connect(rotor1_eta.y,rotor1_allocator.eta_hat) annotation(Line(points={{57,55},{64,55},{64,72},{74,72}},color={0,0,0}));
    connect(raw_mixer.y1,motor2_limit.u) annotation(Line(points={{6,11},{74,11},{74,20},{93,20}},color={0,0,0}));
    connect(raw_mixer.y2,motor3_limit.u) annotation(Line(points={{6,-11},{74,-11},{74,-40},{93,-40}},color={0,0,0}));
    connect(raw_mixer.y3,motor4_limit.u) annotation(Line(points={{6,-32},{68,-32},{68,-100},{93,-100}},color={0,0,0}));
    connect(rotor1_allocator.y,y) annotation(Line(points={{136,80},{160,80},{160,90},{190,90}},color={0,0,0}));
    connect(motor2_limit.y,y1) annotation(Line(points={{117,20},{160,20},{160,30},{190,30}},color={0,0,0}));
    connect(motor3_limit.y,y2) annotation(Line(points={{117,-40},{160,-40},{160,-30},{190,-30}},color={0,0,0}));
    connect(motor4_limit.y,y3) annotation(Line(points={{117,-100},{160,-100},{160,-90},{190,-90}},color={0,0,0}));
  end KnownRotorFaultMixerBlock;

  model RotorFaultIsolationBlock
    "Online four-rotor fault isolation from lateral residual signature"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error),Right(eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={145,55,55},fillColor={255,238,238},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Fault",lineColor={100,35,35}),
        Text(extent={{-90,-12},{90,-46}},textString="Isolation",lineColor={100,35,35})}),
      Diagram(coordinateSystem(extent={{-220,-160},{220,160}},grid={2,2})));

    parameter Real position_derivative_filter_T=0.05;
    parameter Real eta_min_est=0.50;
    parameter Real eta_max_est=1.00;
    parameter Real eta_est_filter_T=5.0;
    parameter Real eta_signature_deadband=0.015;
    parameter Real eta_signature_gain=2.65;
    parameter Real fault_lock_margin=0.012;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-200,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-200,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={200,100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={200,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={200,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={200,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={200,-110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    FaultSignatureEstimatorKernelBlock signature_kernel(
      eta_min_est=eta_min_est,
      eta_max_est=eta_max_est,
      eta_signature_deadband=eta_signature_deadband,
      eta_signature_gain=eta_signature_gain,
      fault_lock_margin=fault_lock_margin) annotation(Placement(transformation(origin={0,0},extent={{-60,-70},{60,70}})));
  equation
    connect(x_error,signature_kernel.x_error) annotation(Line(points={{-190,50},{-100,50},{-100,29},{-61,29}},color={0,0,0}));
    connect(y_error,signature_kernel.y_error) annotation(Line(points={{-190,-50},{-100,-50},{-100,-29},{-61,-29}},color={0,0,0}));
    connect(signature_kernel.eta_hat1,eta_hat1) annotation(Line(points={{61,47},{150,47},{150,100},{190,100}},color={0,0,0}));
    connect(signature_kernel.eta_hat2,eta_hat2) annotation(Line(points={{61,23},{150,23},{150,50},{190,50}},color={0,0,0}));
    connect(signature_kernel.eta_hat3,eta_hat3) annotation(Line(points={{61,0},{190,0}},color={0,0,0}));
    connect(signature_kernel.eta_hat4,eta_hat4) annotation(Line(points={{61,-23},{150,-23},{150,-50},{190,-50}},color={0,0,0}));
    connect(signature_kernel.fault_index,fault_index) annotation(Line(points={{61,-53},{140,-53},{140,-110},{190,-110}},color={0,0,0}));
  end RotorFaultIsolationBlock;

  model AdaptiveFaultMixerBlock
    "Motor mixer with online rotor-efficiency allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(thrust_ref,roll_cmd,pitch_cmd,yaw_cmd,eta_hat1,eta_hat2,eta_hat3,eta_hat4),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={120,55,55},fillColor={255,240,236},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,26},{90,-8}},textString="Adaptive",lineColor={95,35,35}),
        Text(extent={{-90,-12},{90,-46}},textString="Fault Mixer",lineColor={95,35,35})}),
      Diagram(coordinateSystem(extent={{-220,-240},{220,140}},grid={2,2})));

    parameter Real output_limit=20.0;
    parameter Real allocation_blend=0.52;
    parameter Real min_rotor_efficiency=0.50;
    SysplorerEmbeddedCoder.Port.Inport thrust_ref annotation(Placement(transformation(origin={-200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_cmd annotation(Placement(transformation(origin={-200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_cmd annotation(Placement(transformation(origin={-200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_cmd annotation(Placement(transformation(origin={-200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat1 annotation(Placement(transformation(origin={-200,-135},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat2 annotation(Placement(transformation(origin={-200,-165},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat3 annotation(Placement(transformation(origin={-200,-195},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport eta_hat4 annotation(Placement(transformation(origin={-200,-225},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={200,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={200,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={200,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={200,-90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    MotorMixerBlock raw_mixer(output_limit=1e9) annotation(Placement(transformation(origin={-35,0},extent={{-45,-50},{45,50}})));
    EfficiencyCompensationKernelBlock eta1_allocator(output_limit=output_limit,allocation_blend=allocation_blend,min_rotor_efficiency=min_rotor_efficiency) annotation(Placement(transformation(origin={95,80},extent={{-30,-20},{30,20}})));
    EfficiencyCompensationKernelBlock eta2_allocator(output_limit=output_limit,allocation_blend=allocation_blend,min_rotor_efficiency=min_rotor_efficiency) annotation(Placement(transformation(origin={95,20},extent={{-30,-20},{30,20}})));
    EfficiencyCompensationKernelBlock eta3_allocator(output_limit=output_limit,allocation_blend=allocation_blend,min_rotor_efficiency=min_rotor_efficiency) annotation(Placement(transformation(origin={95,-40},extent={{-30,-20},{30,20}})));
    EfficiencyCompensationKernelBlock eta4_allocator(output_limit=output_limit,allocation_blend=allocation_blend,min_rotor_efficiency=min_rotor_efficiency) annotation(Placement(transformation(origin={95,-100},extent={{-30,-20},{30,20}})));
  equation
    connect(thrust_ref,raw_mixer.thrust_ref) annotation(Line(points={{-190,90},{-120,90},{-120,32},{-81,32}},color={0,0,0}));
    connect(roll_cmd,raw_mixer.roll_cmd) annotation(Line(points={{-190,30},{-81,11}},color={0,0,0}));
    connect(pitch_cmd,raw_mixer.pitch_cmd) annotation(Line(points={{-190,-30},{-120,-30},{-120,-11},{-81,-11}},color={0,0,0}));
    connect(yaw_cmd,raw_mixer.yaw_cmd) annotation(Line(points={{-190,-90},{-120,-90},{-120,-32},{-81,-32}},color={0,0,0}));
    connect(raw_mixer.y,eta1_allocator.raw_cmd) annotation(Line(points={{11,32},{42,32},{42,88},{64,88}},color={0,0,0}));
    connect(raw_mixer.y1,eta2_allocator.raw_cmd) annotation(Line(points={{11,11},{64,11},{64,28}},color={0,0,0}));
    connect(raw_mixer.y2,eta3_allocator.raw_cmd) annotation(Line(points={{11,-11},{42,-11},{42,-32},{64,-32}},color={0,0,0}));
    connect(raw_mixer.y3,eta4_allocator.raw_cmd) annotation(Line(points={{11,-32},{36,-32},{36,-92},{64,-92}},color={0,0,0}));
    connect(eta_hat1,eta1_allocator.eta_hat) annotation(Line(points={{-190,-135},{48,-135},{48,72},{64,72}},color={0,0,0}));
    connect(eta_hat2,eta2_allocator.eta_hat) annotation(Line(points={{-190,-165},{52,-165},{52,12},{64,12}},color={0,0,0}));
    connect(eta_hat3,eta3_allocator.eta_hat) annotation(Line(points={{-190,-195},{56,-195},{56,-48},{64,-48}},color={0,0,0}));
    connect(eta_hat4,eta4_allocator.eta_hat) annotation(Line(points={{-190,-225},{60,-225},{60,-108},{64,-108}},color={0,0,0}));
    connect(eta1_allocator.y,y) annotation(Line(points={{126,80},{160,80},{160,90},{190,90}},color={0,0,0}));
    connect(eta2_allocator.y,y1) annotation(Line(points={{126,20},{160,20},{160,30},{190,30}},color={0,0,0}));
    connect(eta3_allocator.y,y2) annotation(Line(points={{126,-40},{160,-40},{160,-30},{190,-30}},color={0,0,0}));
    connect(eta4_allocator.y,y3) annotation(Line(points={{126,-100},{160,-100},{160,-90},{190,-90}},color={0,0,0}));
  end AdaptiveFaultMixerBlock;

  model AWFF_L1ResidualControllerGraphical_Sysblock
    "Graphical L1 residual AWFF controller"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_L1ResidualControllerGraphical_Sysblock;

  model AWFF_INDIControllerGraphical_Sysblock
    "Graphical L1 residual plus INDI attitude controller"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_INDIControllerGraphical_Sysblock;

  model AWFF_L1FaultAllocationControllerGraphical_Sysblock
    "Graphical L1 residual controller with known rotor-1 fault allocation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-220},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    KnownRotorFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
  end AWFF_L1FaultAllocationControllerGraphical_Sysblock;

  model AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock
    "Graphical L1 residual controller with online four-rotor fault isolation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref),Right(y,y1,y2,y3,eta_hat1,eta_hat2,eta_hat3,eta_hat4,fault_index)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.02),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false)),Diagram(coordinateSystem(extent={{-340,-360},{320,220}},grid={2,2})));

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-320,180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-320,130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-320,80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-320,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport roll_mea annotation(Placement(transformation(origin={-320,-30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport pitch_mea annotation(Placement(transformation(origin={-320,-80},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_mea annotation(Placement(transformation(origin={-320,-130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport yaw_ref annotation(Placement(transformation(origin={-320,-180},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y1 annotation(Placement(transformation(origin={300,50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y2 annotation(Placement(transformation(origin={300,-50},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport y3 annotation(Placement(transformation(origin={300,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat1 annotation(Placement(transformation(origin={300,-205},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat2 annotation(Placement(transformation(origin={300,-235},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat3 annotation(Placement(transformation(origin={300,-265},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport eta_hat4 annotation(Placement(transformation(origin={300,-295},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport fault_index annotation(Placement(transformation(origin={300,-330},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    L1ResidualOuterLoopBlock l1_outer annotation(Placement(transformation(origin={-160,70},extent={{-50,-45},{50,45}})));
    PIDAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={0,-25},extent={{-50,-45},{50,45}})));
    AdaptiveFaultMixerBlock motor_mixer annotation(Placement(transformation(origin={165,-25},extent={{-50,-45},{50,45}})));
    RotorFaultIsolationBlock fault_isolation annotation(Placement(transformation(origin={0,-165},extent={{-45,-35},{45,35}})));
  equation
    connect(x_error,l1_outer.x_error) annotation(Line(points={{-310,180},{-240,180},{-240,111},{-211,111}},color={0,0,0}));
    connect(y_error,l1_outer.y_error) annotation(Line(points={{-310,130},{-230,130},{-230,84},{-211,84}},color={0,0,0}));
    connect(z_error,l1_outer.z_error) annotation(Line(points={{-310,80},{-230,80},{-230,56},{-211,56}},color={0,0,0}));
    connect(z_ref_rate,l1_outer.z_ref_rate) annotation(Line(points={{-310,30},{-230,30},{-230,29},{-211,29}},color={0,0,0}));
    connect(l1_outer.roll_ref,attitude_loop.roll_ref) annotation(Line(points={{-109,70},{-70,70},{-70,29},{-51,29}},color={0,0,0}));
    connect(l1_outer.pitch_ref,attitude_loop.pitch_ref) annotation(Line(points={{-109,102},{-58,102},{-58,6},{-51,6}},color={0,0,0}));
    connect(yaw_ref,attitude_loop.yaw_ref) annotation(Line(points={{-310,-180},{-78,-180},{-78,-16},{-51,-16}},color={0,0,0}));
    connect(roll_mea,attitude_loop.roll_mea) annotation(Line(points={{-310,-30},{-94,-30},{-94,-43},{-51,-43}},color={0,0,0}));
    connect(pitch_mea,attitude_loop.pitch_mea) annotation(Line(points={{-310,-80},{-102,-80},{-102,-66},{-51,-66}},color={0,0,0}));
    connect(yaw_mea,attitude_loop.yaw_mea) annotation(Line(points={{-310,-130},{-112,-130},{-112,-88},{-51,-88}},color={0,0,0}));
    connect(l1_outer.thrust_ref,motor_mixer.thrust_ref) annotation(Line(points={{-109,38},{92,38},{92,16},{114,16}},color={0,0,0}));
    connect(attitude_loop.roll_cmd,motor_mixer.roll_cmd) annotation(Line(points={{51,16},{92,16},{92,-12},{114,-12}},color={0,0,0}));
    connect(attitude_loop.pitch_cmd,motor_mixer.pitch_cmd) annotation(Line(points={{51,-25},{114,-25},{114,-39}},color={0,0,0}));
    connect(attitude_loop.yaw_cmd,motor_mixer.yaw_cmd) annotation(Line(points={{51,-66},{92,-66},{92,-66},{114,-66}},color={0,0,0}));
    connect(motor_mixer.y,y) annotation(Line(points={{216,16},{250,16},{250,150},{290,150}},color={0,0,0}));
    connect(motor_mixer.y1,y1) annotation(Line(points={{216,-12},{246,-12},{246,50},{290,50}},color={0,0,0}));
    connect(motor_mixer.y2,y2) annotation(Line(points={{216,-39},{246,-39},{246,-50},{290,-50}},color={0,0,0}));
    connect(motor_mixer.y3,y3) annotation(Line(points={{216,-66},{250,-66},{250,-150},{290,-150}},color={0,0,0}));
    connect(x_error,fault_isolation.x_error) annotation(Line(points={{-310,180},{-250,180},{-250,-154},{-46,-154}},color={0,0,0}));
    connect(y_error,fault_isolation.y_error) annotation(Line(points={{-310,130},{-260,130},{-260,-176},{-46,-176}},color={0,0,0}));
    connect(fault_isolation.eta_hat1,motor_mixer.eta_hat1) annotation(Line(points={{46,-143},{88,-143},{88,-86},{114,-86}},color={0,0,0}));
    connect(fault_isolation.eta_hat2,motor_mixer.eta_hat2) annotation(Line(points={{46,-154},{96,-154},{96,-99},{114,-99}},color={0,0,0}));
    connect(fault_isolation.eta_hat3,motor_mixer.eta_hat3) annotation(Line(points={{46,-165},{104,-165},{104,-113},{114,-113}},color={0,0,0}));
    connect(fault_isolation.eta_hat4,motor_mixer.eta_hat4) annotation(Line(points={{46,-176},{112,-176},{112,-126},{114,-126}},color={0,0,0}));
    connect(fault_isolation.eta_hat1,eta_hat1) annotation(Line(points={{46,-143},{260,-143},{260,-205},{290,-205}},color={0,0,0}));
    connect(fault_isolation.eta_hat2,eta_hat2) annotation(Line(points={{46,-154},{252,-154},{252,-235},{290,-235}},color={0,0,0}));
    connect(fault_isolation.eta_hat3,eta_hat3) annotation(Line(points={{46,-165},{244,-165},{244,-265},{290,-265}},color={0,0,0}));
    connect(fault_isolation.eta_hat4,eta_hat4) annotation(Line(points={{46,-176},{236,-176},{236,-295},{290,-295}},color={0,0,0}));
    connect(fault_isolation.fault_index,fault_index) annotation(Line(points={{46,-189},{228,-189},{228,-330},{290,-330}},color={0,0,0}));
  end AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock;

  AWFF_L1ResidualControllerGraphical_Sysblock l1_residual_overview annotation(Placement(transformation(origin={-170,80},extent={{-70,-45},{70,45}})));
  AWFF_INDIControllerGraphical_Sysblock l1_indi_overview annotation(Placement(transformation(origin={170,80},extent={{-70,-45},{70,45}})));
  AWFF_L1FaultAllocationControllerGraphical_Sysblock known_fault_allocation_overview annotation(Placement(transformation(origin={-170,-100},extent={{-70,-45},{70,45}})));
  AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock online_fault_isolation_overview annotation(Placement(transformation(origin={170,-100},extent={{-70,-45},{70,45}})));
end AWFF_InnovationGraphicalControllers;
