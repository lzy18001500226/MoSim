within MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi;
model LinearMpcL1IndiGraphicalController "AWFF Linear MPC INDI controller - standalone graphical Sysblock"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref), Right(y,y1,y2,y3)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
    Icon(coordinateSystem(preserveAspectRatio=false)),
    experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=1,StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-320,-220},{280,220}},grid={2,2})));


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

  LinearMPCOuterLoopBlock position_loop annotation(Placement(transformation(origin={-145,85},extent={{-45,-45},{45,45}})));
  INDIAttitudeInnerLoopBlock attitude_loop annotation(Placement(transformation(origin={5,-35},extent={{-45,-45},{45,45}})));
  MotorMixerBlock motor_mixer annotation(Placement(transformation(origin={155,-35},extent={{-45,-45},{45,45}})));

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace),version="26.3.0"));
  end ModelWorkspace;

  model LinearMPCOuterLoopBlock
    "Graphical finite-horizon linear MPC-style outer loop with L1 residual compensation"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,PortArrangement(Left(x_error,y_error,z_error,z_ref_rate),Right(pitch_ref,roll_ref,thrust_ref)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(preserveAspectRatio=false),graphics={
        Rectangle(extent={{-100,-100},{100,100}},lineColor={35,95,145},fillColor={236,246,255},fillPattern=FillPattern.Solid,radius=8),
        Text(extent={{-90,28},{90,-6}},textString="Linear MPC",lineColor={20,55,95}),
        Text(extent={{-90,-12},{90,-46}},textString="Outer Loop",lineColor={20,55,95})}),
      Diagram(coordinateSystem(extent={{-320,-260},{320,240}},grid={2,2})));

    parameter Real mpc_dt=0.05;
    parameter Real mpc_horizon_steps=20;
    parameter Real mpc_kp_xy=1.65;
    parameter Real mpc_kd_xy=1.00;
    parameter Real mpc_terminal_gain_xy=0.04;
    parameter Real mpc_kp_z=8.0;
    parameter Real mpc_ki_z=6.0;
    parameter Real mpc_kd_z=4.0;
    parameter Real mpc_terminal_gain_z=0.03;
    parameter Real kff_z=0.35;
    parameter Real mpc_acc_limit_xy=2.5;
    parameter Real mpc_thrust_limit=20.0;
    parameter Real roll_pitch_cmd_limit=12/57.3;
    parameter Real position_derivative_filter_T=0.05;
    parameter Real altitude_derivative_filter_T=0.08;
    parameter Real l1_model_decay=1.25;
    parameter Real l1_filter_T=0.20;
    parameter Real l1_gain_xy=0.32;
    parameter Real l1_gain_z=0.35;
    parameter Real l1_comp_limit_xy=2.0;
    parameter Real l1_comp_limit_z=2.0;

    SysplorerEmbeddedCoder.Port.Inport x_error annotation(Placement(transformation(origin={-300,170},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport y_error annotation(Placement(transformation(origin={-300,60},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_error annotation(Placement(transformation(origin={-300,-70},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Inport z_ref_rate annotation(Placement(transformation(origin={-300,-210},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport pitch_ref annotation(Placement(transformation(origin={300,150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport roll_ref annotation(Placement(transformation(origin={300,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Port.Outport thrust_ref annotation(Placement(transformation(origin={300,-140},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(group="D1")=0.01)));

    SysplorerEmbeddedCoder.Discrete.UnitDelay x_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,195},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum x_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_rate_gain(k=1/position_derivative_filter_T) annotation(Placement(transformation(origin={-155,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,205},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,145},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-12,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator x_l1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,155},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation x_comp_sat(upLimit=l1_comp_limit_xy,lowLimit=-l1_comp_limit_xy) annotation(Placement(transformation(origin={80,155},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kp_gain(k=mpc_kp_xy) annotation(Placement(transformation(origin={-108,230},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_kd_gain(k=mpc_kd_xy) annotation(Placement(transformation(origin={-108,178},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain x_terminal_gain(k=mpc_terminal_gain_xy) annotation(Placement(transformation(origin={-12,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum x_acc_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={132,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation x_acc_sat(upLimit=mpc_acc_limit_xy,lowLimit=-mpc_acc_limit_xy) annotation(Placement(transformation(origin={176,190},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_scale(k=0.1) annotation(Placement(transformation(origin={220,190},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={260,190},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.Discrete.UnitDelay y_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,82},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum y_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_rate_gain(k=1/position_derivative_filter_T) annotation(Placement(transformation(origin={-155,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,90},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,30},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_l1_gain(k=l1_gain_xy) annotation(Placement(transformation(origin={-12,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator y_l1_filter(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation y_comp_sat(upLimit=l1_comp_limit_xy,lowLimit=-l1_comp_limit_xy) annotation(Placement(transformation(origin={80,40},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kp_gain(k=mpc_kp_xy) annotation(Placement(transformation(origin={-108,118},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_kd_gain(k=mpc_kd_xy) annotation(Placement(transformation(origin={-108,62},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain y_terminal_gain(k=mpc_terminal_gain_xy) annotation(Placement(transformation(origin={-12,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum y_acc_sum(isSaturate=false,inputs="++++") annotation(Placement(transformation(origin={132,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation y_acc_sat(upLimit=mpc_acc_limit_xy,lowLimit=-mpc_acc_limit_xy) annotation(Placement(transformation(origin={176,78},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Gain roll_scale(k=0.1) annotation(Placement(transformation(origin={220,78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_sat(upLimit=roll_pitch_cmd_limit,lowLimit=-roll_pitch_cmd_limit) annotation(Placement(transformation(origin={260,78},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.Discrete.UnitDelay z_error_delay(initCond=0) annotation(Placement(transformation(origin={-238,-48},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.MathOperation.Sum z_rate_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-198,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_rate_gain(k=1/altitude_derivative_filter_T) annotation(Placement(transformation(origin={-155,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_horizon_gain(k=mpc_dt*mpc_horizon_steps) annotation(Placement(transformation(origin={-108,-38},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_terminal_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,-52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_decay_gain(k=l1_model_decay) annotation(Placement(transformation(origin={-108,-105},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum z_residual_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-60,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_l1_gain(k=l1_gain_z) annotation(Placement(transformation(origin={-12,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_l1_filter_mpc(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01/l1_filter_T,initCond=0) annotation(Placement(transformation(origin={34,-95},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.Discontinuities.Saturation z_comp_sat(upLimit=l1_comp_limit_z,lowLimit=-l1_comp_limit_z) annotation(Placement(transformation(origin={80,-95},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator z_integrator(externalResetType=SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator.ExternalResetType.None,gain=0.01,initCond=0) annotation(Placement(transformation(origin={-108,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(u1(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),gain(Type(ref="double"),Dimension=1),initCond(Type(ref="double"),Dimension=1)))));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kp_gain(k=mpc_kp_z) annotation(Placement(transformation(origin={-12,-22},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ki_gain(k=mpc_ki_z) annotation(Placement(transformation(origin={-12,-150},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_kd_gain(k=mpc_kd_z) annotation(Placement(transformation(origin={-12,-68},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_terminal_gain(k=mpc_terminal_gain_z) annotation(Placement(transformation(origin={34,-52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain z_ff_gain(k=kff_z) annotation(Placement(transformation(origin={-12,-210},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum thrust_sum(isSaturate=false,inputs="++++++") annotation(Placement(transformation(origin={140,-112},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1),u4(Type(ref="double"),Dimension=1),u5(Type(ref="double"),Dimension=1),u6(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discontinuities.Saturation thrust_sat(upLimit=mpc_thrust_limit,lowLimit=-mpc_thrust_limit) annotation(Placement(transformation(origin={220,-112},extent={{-10,-10},{10,10}})));
  equation
    connect(x_error,x_error_delay.u1) annotation(Line(points={{-290,170},{-268,170},{-268,195},{-250,195}},color={0,0,0}));
    connect(x_error,x_rate_sum.u1) annotation(Line(points={{-290,170},{-220,170},{-220,184},{-210,184}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error_delay.y,x_rate_sum.u2) annotation(Line(points={{-226,195},{-218,195},{-218,172},{-210,172}},color={0,0,0}));
    connect(x_rate_sum.y,x_rate_gain.u) annotation(Line(points={{-186,178},{-167,178}},color={0,0,0}));
    connect(x_rate_gain.y,x_horizon_gain.u) annotation(Line(points={{-143,178},{-132,178},{-132,205},{-120,205}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(x_error,x_terminal_sum.u1) annotation(Line(points={{-290,170},{-82,170},{-82,196},{-72,196}},color={0,0,0}));
    connect(x_horizon_gain.y,x_terminal_sum.u2) annotation(Line(points={{-96,205},{-78,205},{-78,184},{-72,184}},color={0,0,0}));
    connect(x_error,x_decay_gain.u) annotation(Line(points={{-290,170},{-132,170},{-132,145},{-120,145}},color={0,0,0}));
    connect(x_rate_gain.y,x_residual_sum.u1) annotation(Line(points={{-143,178},{-88,178},{-88,161},{-72,161}},color={0,0,0}));
    connect(x_decay_gain.y,x_residual_sum.u2) annotation(Line(points={{-96,145},{-82,145},{-82,149},{-72,149}},color={0,0,0}));
    connect(x_residual_sum.y,x_l1_gain.u) annotation(Line(points={{-48,155},{-24,155}},color={0,0,0}));
    connect(x_l1_gain.y,x_l1_filter.u1) annotation(Line(points={{0,155},{22,155}},color={0,0,0}));
    connect(x_l1_filter.y,x_comp_sat.u) annotation(Line(points={{46,155},{68,155}},color={0,0,0}));
    connect(x_error,x_kp_gain.u) annotation(Line(points={{-290,170},{-138,170},{-138,230},{-120,230}},color={0,0,0}));
    connect(x_rate_gain.y,x_kd_gain.u) annotation(Line(points={{-143,178},{-120,178}},color={0,0,0}));
    connect(x_terminal_sum.y,x_terminal_gain.u) annotation(Line(points={{-48,190},{-24,190}},color={0,0,0}));
    connect(x_kp_gain.y,x_acc_sum.u1) annotation(Line(points={{-96,230},{112,230},{112,205},{120,205}},color={0,0,0}));
    connect(x_kd_gain.y,x_acc_sum.u2) annotation(Line(points={{-96,178},{112,178},{112,195},{120,195}},color={0,0,0}));
    connect(x_terminal_gain.y,x_acc_sum.u3) annotation(Line(points={{0,190},{120,190}},color={0,0,0}));
    connect(x_comp_sat.y,x_acc_sum.u4) annotation(Line(points={{92,155},{112,155},{112,176},{120,176}},color={0,0,0}));
    connect(x_acc_sum.y,x_acc_sat.u) annotation(Line(points={{144,190},{164,190}},color={0,0,0}));
    connect(x_acc_sat.y,pitch_scale.u) annotation(Line(points={{188,190},{208,190}},color={0,0,0}));
    connect(pitch_scale.y,pitch_ref_sat.u) annotation(Line(points={{232,190},{248,190}},color={0,0,0}));
    connect(pitch_ref_sat.y,pitch_ref) annotation(Line(points={{272,190},{286,190},{286,150},{290,150}},color={0,0,0}));

    connect(y_error,y_error_delay.u1) annotation(Line(points={{-290,60},{-268,60},{-268,82},{-250,82}},color={0,0,0}));
    connect(y_error,y_rate_sum.u1) annotation(Line(points={{-290,60},{-220,60},{-220,68},{-210,68}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error_delay.y,y_rate_sum.u2) annotation(Line(points={{-226,82},{-218,82},{-218,56},{-210,56}},color={0,0,0}));
    connect(y_rate_sum.y,y_rate_gain.u) annotation(Line(points={{-186,62},{-167,62}},color={0,0,0}));
    connect(y_rate_gain.y,y_horizon_gain.u) annotation(Line(points={{-143,62},{-132,62},{-132,90},{-120,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(y_error,y_terminal_sum.u1) annotation(Line(points={{-290,60},{-84,60},{-84,84},{-72,84}},color={0,0,0}));
    connect(y_horizon_gain.y,y_terminal_sum.u2) annotation(Line(points={{-96,90},{-78,90},{-78,72},{-72,72}},color={0,0,0}));
    connect(y_error,y_decay_gain.u) annotation(Line(points={{-290,60},{-132,60},{-132,30},{-120,30}},color={0,0,0}));
    connect(y_rate_gain.y,y_residual_sum.u1) annotation(Line(points={{-143,62},{-88,62},{-88,46},{-72,46}},color={0,0,0}));
    connect(y_decay_gain.y,y_residual_sum.u2) annotation(Line(points={{-96,30},{-82,30},{-82,34},{-72,34}},color={0,0,0}));
    connect(y_residual_sum.y,y_l1_gain.u) annotation(Line(points={{-48,40},{-24,40}},color={0,0,0}));
    connect(y_l1_gain.y,y_l1_filter.u1) annotation(Line(points={{0,40},{22,40}},color={0,0,0}));
    connect(y_l1_filter.y,y_comp_sat.u) annotation(Line(points={{46,40},{68,40}},color={0,0,0}));
    connect(y_error,y_kp_gain.u) annotation(Line(points={{-290,60},{-138,60},{-138,118},{-120,118}},color={0,0,0}));
    connect(y_rate_gain.y,y_kd_gain.u) annotation(Line(points={{-143,62},{-120,62}},color={0,0,0}));
    connect(y_terminal_sum.y,y_terminal_gain.u) annotation(Line(points={{-48,78},{-24,78}},color={0,0,0}));
    connect(y_kp_gain.y,y_acc_sum.u1) annotation(Line(points={{-96,118},{112,118},{112,93},{120,93}},color={0,0,0}));
    connect(y_kd_gain.y,y_acc_sum.u2) annotation(Line(points={{-96,62},{112,62},{112,83},{120,83}},color={0,0,0}));
    connect(y_terminal_gain.y,y_acc_sum.u3) annotation(Line(points={{0,78},{120,78}},color={0,0,0}));
    connect(y_comp_sat.y,y_acc_sum.u4) annotation(Line(points={{92,40},{112,40},{112,64},{120,64}},color={0,0,0}));
    connect(y_acc_sum.y,y_acc_sat.u) annotation(Line(points={{144,78},{164,78}},color={0,0,0}));
    connect(y_acc_sat.y,roll_scale.u) annotation(Line(points={{188,78},{208,78}},color={0,0,0}));
    connect(roll_scale.y,roll_ref_sat.u) annotation(Line(points={{232,78},{248,78}},color={0,0,0}));
    connect(roll_ref_sat.y,roll_ref) annotation(Line(points={{272,78},{286,78},{286,40},{290,40}},color={0,0,0}));

    connect(z_error,z_error_delay.u1) annotation(Line(points={{-290,-70},{-268,-70},{-268,-48},{-250,-48}},color={0,0,0}));
    connect(z_error,z_rate_sum.u1) annotation(Line(points={{-290,-70},{-220,-70},{-220,-62},{-210,-62}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error_delay.y,z_rate_sum.u2) annotation(Line(points={{-226,-48},{-218,-48},{-218,-74},{-210,-74}},color={0,0,0}));
    connect(z_rate_sum.y,z_rate_gain.u) annotation(Line(points={{-186,-68},{-167,-68}},color={0,0,0}));
    connect(z_rate_gain.y,z_horizon_gain.u) annotation(Line(points={{-143,-68},{-132,-68},{-132,-38},{-120,-38}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(z_error,z_terminal_sum.u1) annotation(Line(points={{-290,-70},{-82,-70},{-82,-46},{-72,-46}},color={0,0,0}));
    connect(z_horizon_gain.y,z_terminal_sum.u2) annotation(Line(points={{-96,-38},{-78,-38},{-78,-58},{-72,-58}},color={0,0,0}));
    connect(z_error,z_decay_gain.u) annotation(Line(points={{-290,-70},{-132,-70},{-132,-105},{-120,-105}},color={0,0,0}));
    connect(z_rate_gain.y,z_residual_sum.u1) annotation(Line(points={{-143,-68},{-88,-68},{-88,-89},{-72,-89}},color={0,0,0}));
    connect(z_decay_gain.y,z_residual_sum.u2) annotation(Line(points={{-96,-105},{-82,-105},{-82,-101},{-72,-101}},color={0,0,0}));
    connect(z_residual_sum.y,z_l1_gain.u) annotation(Line(points={{-48,-95},{-24,-95}},color={0,0,0}));
    connect(z_l1_gain.y,z_l1_filter_mpc.u1) annotation(Line(points={{0,-95},{22,-95}},color={0,0,0}));
    connect(z_l1_filter_mpc.y,z_comp_sat.u) annotation(Line(points={{46,-95},{68,-95}},color={0,0,0}));
    connect(z_error,z_integrator.u1) annotation(Line(points={{-290,-70},{-138,-70},{-138,-150},{-120,-150}},color={0,0,0}));
    connect(z_error,z_kp_gain.u) annotation(Line(points={{-290,-70},{-44,-70},{-44,-22},{-24,-22}},color={0,0,0}));
    connect(z_integrator.y,z_ki_gain.u) annotation(Line(points={{-96,-150},{-24,-150}},color={0,0,0}));
    connect(z_rate_gain.y,z_kd_gain.u) annotation(Line(points={{-143,-68},{-24,-68}},color={0,0,0}));
    connect(z_terminal_sum.y,z_terminal_gain.u) annotation(Line(points={{-48,-52},{22,-52}},color={0,0,0}));
    connect(z_ref_rate,z_ff_gain.u) annotation(Line(points={{-290,-210},{-24,-210}},color={0,0,0}));
    connect(z_kp_gain.y,thrust_sum.u1) annotation(Line(points={{0,-22},{112,-22},{112,-97},{128,-97}},color={0,0,0}));
    connect(z_ki_gain.y,thrust_sum.u2) annotation(Line(points={{0,-150},{112,-150},{112,-103},{128,-103}},color={0,0,0}));
    connect(z_kd_gain.y,thrust_sum.u3) annotation(Line(points={{0,-68},{108,-68},{108,-109},{128,-109}},color={0,0,0}));
    connect(z_terminal_gain.y,thrust_sum.u4) annotation(Line(points={{46,-52},{104,-52},{104,-115},{128,-115}},color={0,0,0}));
    connect(z_ff_gain.y,thrust_sum.u5) annotation(Line(points={{0,-210},{112,-210},{112,-121},{128,-121}},color={0,0,0}));
    connect(z_comp_sat.y,thrust_sum.u6) annotation(Line(points={{92,-95},{116,-95},{116,-127},{128,-127}},color={0,0,0}));
    connect(thrust_sum.y,thrust_sat.u) annotation(Line(points={{152,-112},{208,-112}},color={0,0,0}));
    connect(thrust_sat.y,thrust_ref) annotation(Line(points={{232,-112},{270,-112},{270,-140},{290,-140}},color={0,0,0}));
  end LinearMPCOuterLoopBlock;  model INDIAttitudeInnerLoopBlock
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
    SysplorerEmbeddedCoder.MathOperation.Sum roll_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={135,110},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.UnitDelay roll_cmd_delay(initCond=0) annotation(Placement(transformation(origin={88,70},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation roll_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={165,110},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum pitch_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kp_gain(k=kp_pitch) annotation(Placement(transformation(origin={-70,40},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_kd_over_rate_gain(k=kd_pitch / attitude_rate_filter_T) annotation(Placement(transformation(origin={-70,0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_raw_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-5,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={50,35},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain pitch_indi_gain_block(k=indi_pitch_gain) annotation(Placement(transformation(origin={50,5},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum pitch_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={135,20},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_cmd_delay(initCond=0) annotation(Placement(transformation(origin={88,-20},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_cmd_sat(upLimit=attitude_cmd_limit,lowLimit=-attitude_cmd_limit) annotation(Placement(transformation(origin={165,20},extent={{-10,-10},{10,10}})));

    SysplorerEmbeddedCoder.MathOperation.Sum yaw_error_sum(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-135,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_kp_gain(k=kp_yaw) annotation(Placement(transformation(origin={-70,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_feedback_gain(k=attitude_feedback_blend) annotation(Placement(transformation(origin={5,-85},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Gain yaw_indi_gain_block(k=indi_yaw_gain) annotation(Placement(transformation(origin={5,-115},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double"),Dimension=1),y(Type(ref="double"),Dimension=1),k(Type(ref="double"),Dimension=1)),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.MathOperation.Sum yaw_indi_sum(isSaturate=false,inputs="+++") annotation(Placement(transformation(origin={110,-100},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double"),Dimension=1),u2(Type(ref="double"),Dimension=1),u3(Type(ref="double"),Dimension=1)),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01)));
    SysplorerEmbeddedCoder.Discrete.UnitDelay yaw_cmd_delay(initCond=0) annotation(Placement(transformation(origin={62,-140},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_cmd_sat(upLimit=yaw_cmd_limit,lowLimit=-yaw_cmd_limit) annotation(Placement(transformation(origin={145,-100},extent={{-10,-10},{10,10}})));
  equation
    connect(roll_ref,roll_error_sum.u1) annotation(Line(points={{-190,120},{-160,120},{-160,116},{-147,116}},color={0,0,0}));
    connect(roll_mea,roll_error_sum.u2) annotation(Line(points={{-190,-40},{-170,-40},{-170,104},{-147,104}},color={0,0,0}));
    connect(roll_error_sum.y,roll_kp_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,130},{-82,130}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_error_sum.y,roll_kd_over_rate_gain.u) annotation(Line(points={{-123,110},{-100,110},{-100,90},{-82,90}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_kp_gain.y,roll_raw_sum.u1) annotation(Line(points={{-58,130},{-26,130},{-26,116},{-17,116}},color={0,0,0}));
    connect(roll_kd_over_rate_gain.y,roll_raw_sum.u2) annotation(Line(points={{-58,90},{-26,90},{-26,104},{-17,104}},color={0,0,0}));
    connect(roll_raw_sum.y,roll_feedback_gain.u) annotation(Line(points={{7,110},{24,110},{24,125},{38,125}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_raw_sum.y,roll_indi_gain_block.u) annotation(Line(points={{7,110},{24,110},{24,95},{38,95}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(roll_feedback_gain.y,roll_indi_sum.u1) annotation(Line(points={{62,125},{116,125},{116,116},{123,116}},color={0,0,0}));
    connect(roll_indi_gain_block.y,roll_indi_sum.u2) annotation(Line(points={{62,95},{116,95},{116,104},{123,104}},color={0,0,0}));
    connect(roll_cmd_delay.y,roll_indi_sum.u3) annotation(Line(points={{100,70},{116,70},{116,104},{123,104}},color={0,0,0}));

    connect(pitch_ref,pitch_error_sum.u1) annotation(Line(points={{-190,70},{-160,70},{-160,26},{-147,26}},color={0,0,0}));
    connect(pitch_mea,pitch_error_sum.u2) annotation(Line(points={{-190,-90},{-170,-90},{-170,14},{-147,14}},color={0,0,0}));
    connect(pitch_error_sum.y,pitch_kp_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,40},{-82,40}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_error_sum.y,pitch_kd_over_rate_gain.u) annotation(Line(points={{-123,20},{-100,20},{-100,0},{-82,0}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_kp_gain.y,pitch_raw_sum.u1) annotation(Line(points={{-58,40},{-26,40},{-26,26},{-17,26}},color={0,0,0}));
    connect(pitch_kd_over_rate_gain.y,pitch_raw_sum.u2) annotation(Line(points={{-58,0},{-26,0},{-26,14},{-17,14}},color={0,0,0}));
    connect(pitch_raw_sum.y,pitch_feedback_gain.u) annotation(Line(points={{7,20},{24,20},{24,35},{38,35}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_raw_sum.y,pitch_indi_gain_block.u) annotation(Line(points={{7,20},{24,20},{24,5},{38,5}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(pitch_feedback_gain.y,pitch_indi_sum.u1) annotation(Line(points={{62,35},{116,35},{116,26},{123,26}},color={0,0,0}));
    connect(pitch_indi_gain_block.y,pitch_indi_sum.u2) annotation(Line(points={{62,5},{116,5},{116,14},{123,14}},color={0,0,0}));
    connect(pitch_cmd_delay.y,pitch_indi_sum.u3) annotation(Line(points={{100,-20},{116,-20},{116,14},{123,14}},color={0,0,0}));

    connect(yaw_ref,yaw_error_sum.u1) annotation(Line(points={{-190,20},{-160,20},{-160,-94},{-147,-94}},color={0,0,0}));
    connect(yaw_mea,yaw_error_sum.u2) annotation(Line(points={{-190,-140},{-170,-140},{-170,-106},{-147,-106}},color={0,0,0}));
    connect(yaw_error_sum.y,yaw_kp_gain.u) annotation(Line(points={{-123,-100},{-82,-100}},color={0,0,0}));
    connect(yaw_kp_gain.y,yaw_feedback_gain.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-85},{-7,-85}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_kp_gain.y,yaw_indi_gain_block.u) annotation(Line(points={{-58,-100},{-30,-100},{-30,-115},{-7,-115}},color={0,0,0}),__MWORKS(BlockSystem(NamedSignal)));
    connect(yaw_feedback_gain.y,yaw_indi_sum.u1) annotation(Line(points={{17,-85},{86,-85},{86,-94},{98,-94}},color={0,0,0}));
    connect(yaw_indi_gain_block.y,yaw_indi_sum.u2) annotation(Line(points={{17,-115},{86,-115},{86,-106},{98,-106}},color={0,0,0}));
    connect(yaw_cmd_delay.y,yaw_indi_sum.u3) annotation(Line(points={{74,-140},{86,-140},{86,-106},{98,-106}},color={0,0,0}));
    connect(roll_indi_sum.y,roll_cmd_sat.u) annotation(Line(points={{147,110},{153,110}},color={0,0,0}));
    connect(pitch_indi_sum.y,pitch_cmd_sat.u) annotation(Line(points={{147,20},{153,20}},color={0,0,0}));
    connect(yaw_indi_sum.y,yaw_cmd_sat.u) annotation(Line(points={{122,-100},{133,-100}},color={0,0,0}));
    connect(roll_cmd_sat.y,roll_cmd) annotation(Line(points={{177,110},{180,110},{180,90},{190,90}},color={0,0,0}));
    connect(pitch_cmd_sat.y,pitch_cmd) annotation(Line(points={{177,20},{180,20},{180,0},{190,0}},color={0,0,0}));
    connect(yaw_cmd_sat.y,yaw_cmd) annotation(Line(points={{157,-100},{180,-100},{180,-90},{190,-90}},color={0,0,0}));
    connect(roll_cmd_sat.y,roll_cmd_delay.u1) annotation(Line(points={{177,110},{184,110},{184,70},{100,70}},color={0,0,0}));
    connect(pitch_cmd_sat.y,pitch_cmd_delay.u1) annotation(Line(points={{177,20},{184,20},{184,-20},{100,-20}},color={0,0,0}));
    connect(yaw_cmd_sat.y,yaw_cmd_delay.u1) annotation(Line(points={{157,-100},{170,-100},{170,-140},{74,-140}},color={0,0,0}));
  end INDIAttitudeInnerLoopBlock;  model MotorMixerBlock
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
    SysplorerEmbeddedCoder.Discontinuities.Saturation motor1_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,90},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation motor2_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,30},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation motor3_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,-30},extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Discontinuities.Saturation motor4_sat(upLimit=output_limit,lowLimit=-output_limit) annotation(Placement(transformation(origin={95,-90},extent={{-10,-10},{10,10}})));
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
    connect(motor1_sum.y,motor1_sat.u) annotation(Line(points={{32,90},{83,90}},color={0,0,0}));
    connect(motor2_sum.y,motor2_sat.u) annotation(Line(points={{32,30},{83,30}},color={0,0,0}));
    connect(motor3_sum.y,motor3_sat.u) annotation(Line(points={{32,-30},{83,-30}},color={0,0,0}));
    connect(motor4_sum.y,motor4_sat.u) annotation(Line(points={{32,-90},{83,-90}},color={0,0,0}));
    connect(motor1_sat.y,y) annotation(Line(points={{107,90},{190,90}},color={0,0,0}));
    connect(motor2_sat.y,y1) annotation(Line(points={{107,30},{190,30}},color={0,0,0}));
    connect(motor3_sat.y,y2) annotation(Line(points={{107,-30},{190,-30}},color={0,0,0}));
    connect(motor4_sat.y,y3) annotation(Line(points={{107,-90},{190,-90}},color={0,0,0}));
  end MotorMixerBlock;
equation
  connect(x_error, position_loop.x_error) 
    annotation(Line(points={{-290,180},{-230,180},{-230,119},{-191,119}},color={0,0,0}));
  connect(y_error, position_loop.y_error) 
    annotation(Line(points={{-290,130},{-220,130},{-220,96},{-191,96}},color={0,0,0}));
  connect(z_error, position_loop.z_error) 
    annotation(Line(points={{-290,80},{-218,80},{-218,74},{-191,74}},color={0,0,0}));
  connect(z_ref_rate, position_loop.z_ref_rate) 
    annotation(Line(points={{-290,30},{-220,30},{-220,51},{-191,51}},color={0,0,0}));

  connect(position_loop.roll_ref, attitude_loop.roll_ref) 
    annotation(Line(points={{-98,85},{-70,85},{-70,1},{-42,1}},color={0,0,0}));
  connect(position_loop.pitch_ref, attitude_loop.pitch_ref) 
    annotation(Line(points={{-98,112},{-58,112},{-58,-21},{-42,-21}},color={0,0,0}));
  connect(yaw_ref, attitude_loop.yaw_ref) 
    annotation(Line(points={{-290,-180},{-72,-180},{-72,-43},{-42,-43}},color={0,0,0}));
  connect(roll_mea, attitude_loop.roll_mea) 
    annotation(Line(points={{-290,-30},{-110,-30},{-110,-66},{-42,-66}},color={0,0,0}));
  connect(pitch_mea, attitude_loop.pitch_mea) 
    annotation(Line(points={{-290,-80},{-120,-80},{-120,-88},{-42,-88}},color={0,0,0}));
  connect(yaw_mea, attitude_loop.yaw_mea) 
    annotation(Line(points={{-290,-130},{-130,-130},{-130,-106},{-42,-106}},color={0,0,0}));

  connect(position_loop.thrust_ref, motor_mixer.thrust_ref) 
    annotation(Line(points={{-98,58},{86,58},{86,-1},{108,-1}},color={0,0,0}));
  connect(attitude_loop.roll_cmd, motor_mixer.roll_cmd) 
    annotation(Line(points={{52,-8},{86,-8},{86,-24},{108,-24}},color={0,0,0}));
  connect(attitude_loop.pitch_cmd, motor_mixer.pitch_cmd) 
    annotation(Line(points={{52,-35},{108,-35},{108,-46}},color={0,0,0}));
  connect(attitude_loop.yaw_cmd, motor_mixer.yaw_cmd) 
    annotation(Line(points={{52,-62},{86,-62},{86,-69},{108,-69}},color={0,0,0}));

  connect(motor_mixer.y, y) 
    annotation(Line(points={{202,-8},{230,-8},{230,150},{240,150}},color={0,0,0}));
  connect(motor_mixer.y1, y1) 
    annotation(Line(points={{202,-35},{230,-35},{230,50},{240,50}},color={0,0,0}));
  connect(motor_mixer.y2, y2) 
    annotation(Line(points={{202,-62},{230,-62},{230,-50},{240,-50}},color={0,0,0}));
  connect(motor_mixer.y3, y3) 
    annotation(Line(points={{202,-89},{230,-89},{230,-150},{240,-150}},color={0,0,0}));
end LinearMpcL1IndiGraphicalController;