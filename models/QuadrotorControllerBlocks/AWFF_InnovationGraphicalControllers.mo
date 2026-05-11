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

    Real x_error_filter(start=0,fixed=true);
    Real y_error_filter(start=0,fixed=true);
    Real z_error_filter(start=0,fixed=true);
    Real z_integral(start=0,fixed=true);
    Real d_hat_x(start=0,fixed=true);
    Real d_hat_y(start=0,fixed=true);
    Real d_hat_z(start=0,fixed=true);
    Real x_error_rate;
    Real y_error_rate;
    Real z_error_rate;
    Real comp_x;
    Real comp_y;
    Real comp_z;
    Real pitch_ref_raw;
    Real roll_ref_raw;
    Real thrust_ref_raw;

  equation
    x_error_filter = x_error;
    y_error_filter = y_error;
    x_error_rate = l1_model_decay * x_error;
    y_error_rate = l1_model_decay * y_error;
    d_hat_x = l1_gain_xy * (x_error_rate + l1_model_decay * x_error);
    d_hat_y = l1_gain_xy * (y_error_rate + l1_model_decay * y_error);
    comp_x = min(max(d_hat_x,-l1_comp_limit_xy),l1_comp_limit_xy);
    comp_y = min(max(d_hat_y,-l1_comp_limit_xy),l1_comp_limit_xy);
    pitch_ref_raw = 0.1 * (kp_x * x_error + kd_x * x_error_rate + comp_x);
    roll_ref_raw = 0.1 * (kp_y * y_error + kd_y * y_error_rate + comp_y);
    z_error_filter = z_error;
    z_error_rate = l1_model_decay * z_error;
    d_hat_z = l1_gain_z * (z_error_rate + l1_model_decay * z_error);
    comp_z = min(max(d_hat_z,-l1_comp_limit_z),l1_comp_limit_z);
    thrust_ref_raw = kp_z * z_error + ki_z * z_integral + kd_z * z_error_rate + kff_z * z_ref_rate + comp_z;
    pitch_ref = min(max(pitch_ref_raw,-roll_pitch_cmd_limit),roll_pitch_cmd_limit);
    roll_ref = min(max(roll_ref_raw,-roll_pitch_cmd_limit),roll_pitch_cmd_limit);
    thrust_ref = min(max(thrust_ref_raw,-output_limit),output_limit);
    z_integral = 0;
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

    Real roll_error;
    Real pitch_error;
    Real yaw_error;
    Real roll_error_filter(start=0,fixed=true);
    Real pitch_error_filter(start=0,fixed=true);
    Real roll_cmd_raw;
    Real pitch_cmd_raw;
    Real yaw_cmd_raw;

  equation
    roll_error = roll_ref + roll_mea;
    pitch_error = pitch_ref - pitch_mea;
    yaw_error = yaw_ref - yaw_mea;
    roll_error_filter = 0;
    pitch_error_filter = 0;
    roll_cmd_raw = kp_roll * roll_error + kd_roll * (roll_error - roll_error_filter) / attitude_derivative_filter_T;
    pitch_cmd_raw = kp_pitch * pitch_error + kd_pitch * (pitch_error - pitch_error_filter) / attitude_derivative_filter_T;
    yaw_cmd_raw = kp_yaw * yaw_error;
    roll_cmd = min(max(roll_cmd_raw,-attitude_cmd_limit),attitude_cmd_limit);
    pitch_cmd = min(max(pitch_cmd_raw,-attitude_cmd_limit),attitude_cmd_limit);
    yaw_cmd = min(max(yaw_cmd_raw,-yaw_cmd_limit),yaw_cmd_limit);
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
    Real roll_error;
    Real pitch_error;
    Real yaw_error;
    Real roll_error_filter(start=0,fixed=true);
    Real pitch_error_filter(start=0,fixed=true);
    Real roll_cmd_raw;
    Real pitch_cmd_raw;
    Real yaw_cmd_raw;
    Real roll_mea_filter(start=0,fixed=true);
    Real pitch_mea_filter(start=0,fixed=true);
    Real yaw_mea_filter(start=0,fixed=true);
    Real roll_rate_filter(start=0,fixed=true);
    Real pitch_rate_filter(start=0,fixed=true);
    Real yaw_rate_filter(start=0,fixed=true);
    Real roll_rate;
    Real pitch_rate;
    Real yaw_rate;
    Real roll_inc;
    Real pitch_inc;
    Real yaw_inc;
  equation
    roll_error = roll_ref + roll_mea;
    pitch_error = pitch_ref - pitch_mea;
    yaw_error = yaw_ref - yaw_mea;
    roll_error_filter = 0;
    pitch_error_filter = 0;
    roll_cmd_raw = kp_roll * roll_error + kd_roll * (roll_error - roll_error_filter) / attitude_rate_filter_T;
    pitch_cmd_raw = kp_pitch * pitch_error + kd_pitch * (pitch_error - pitch_error_filter) / attitude_rate_filter_T;
    yaw_cmd_raw = kp_yaw * yaw_error;
    roll_mea_filter = roll_mea;
    pitch_mea_filter = pitch_mea;
    yaw_mea_filter = yaw_mea;
    roll_rate = 0;
    pitch_rate = 0;
    yaw_rate = 0;
    roll_rate_filter = 0;
    pitch_rate_filter = 0;
    yaw_rate_filter = 0;
    roll_inc = min(max(indi_roll_gain * (roll_cmd_raw - (roll_rate - roll_rate_filter) / angular_accel_filter_T),-indi_increment_limit),indi_increment_limit);
    pitch_inc = min(max(indi_pitch_gain * (pitch_cmd_raw - (pitch_rate - pitch_rate_filter) / angular_accel_filter_T),-indi_increment_limit),indi_increment_limit);
    yaw_inc = min(max(indi_yaw_gain * (yaw_cmd_raw - (yaw_rate - yaw_rate_filter) / angular_accel_filter_T),-indi_increment_limit),indi_increment_limit);
    roll_cmd = min(max(attitude_feedback_blend * roll_cmd_raw + roll_inc,-attitude_cmd_limit),attitude_cmd_limit);
    pitch_cmd = min(max(attitude_feedback_blend * pitch_cmd_raw + pitch_inc,-attitude_cmd_limit),attitude_cmd_limit);
    yaw_cmd = min(max(attitude_feedback_blend * yaw_cmd_raw + yaw_inc,-yaw_cmd_limit),yaw_cmd_limit);
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
    Real yaw_mix;
    Real pitch_mix;
    Real roll_mix;
    Real u1_raw;
    Real u2_raw;
    Real u3_raw;
    Real u4_raw;
  equation
    yaw_mix = 0.707 * yaw_cmd;
    pitch_mix = 0.707 * pitch_cmd;
    roll_mix = 0.707 * roll_cmd;
    u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix);
    u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix));
    u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix);
    u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix));
    y = min(max(u1_raw,-output_limit),output_limit);
    y1 = min(max(u2_raw,-output_limit),output_limit);
    y2 = min(max(u3_raw,-output_limit),output_limit);
    y3 = min(max(u4_raw,-output_limit),output_limit);
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
    Real yaw_mix;
    Real pitch_mix;
    Real roll_mix;
    Real u1_raw;
    Real u2_raw;
    Real u3_raw;
    Real u4_raw;
  equation
    yaw_mix = 0.707 * yaw_cmd;
    pitch_mix = 0.707 * pitch_cmd;
    roll_mix = 0.707 * roll_cmd;
    u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix);
    u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix));
    u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix);
    u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix));
    y = min(max(u1_raw * (1 + rotor1_allocation_blend * (1 / max(rotor1_efficiency,min_rotor_efficiency) - 1)),-output_limit),output_limit);
    y1 = min(max(u2_raw,-output_limit),output_limit);
    y2 = min(max(u3_raw,-output_limit),output_limit);
    y3 = min(max(u4_raw,-output_limit),output_limit);
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
    Real yaw_mix;
    Real pitch_mix;
    Real roll_mix;
    Real u1_raw;
    Real u2_raw;
    Real u3_raw;
    Real u4_raw;
    Real eta1_safe;
    Real eta2_safe;
    Real eta3_safe;
    Real eta4_safe;
  equation
    yaw_mix = 0.707 * yaw_cmd;
    pitch_mix = 0.707 * pitch_cmd;
    roll_mix = 0.707 * roll_cmd;
    u1_raw = thrust_ref + (-yaw_mix - pitch_mix + roll_mix);
    u2_raw = -(thrust_ref + (yaw_mix - pitch_mix - roll_mix));
    u3_raw = thrust_ref + (-yaw_mix + pitch_mix - roll_mix);
    u4_raw = -(thrust_ref + (yaw_mix + pitch_mix + roll_mix));
    eta1_safe = max(eta_hat1,min_rotor_efficiency);
    eta2_safe = max(eta_hat2,min_rotor_efficiency);
    eta3_safe = max(eta_hat3,min_rotor_efficiency);
    eta4_safe = max(eta_hat4,min_rotor_efficiency);
    y = min(max(u1_raw * (1 + allocation_blend * (1 / eta1_safe - 1)),-output_limit),output_limit);
    y1 = min(max(u2_raw * (1 + allocation_blend * (1 / eta2_safe - 1)),-output_limit),output_limit);
    y2 = min(max(u3_raw * (1 + allocation_blend * (1 / eta3_safe - 1)),-output_limit),output_limit);
    y3 = min(max(u4_raw * (1 + allocation_blend * (1 / eta4_safe - 1)),-output_limit),output_limit);
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
