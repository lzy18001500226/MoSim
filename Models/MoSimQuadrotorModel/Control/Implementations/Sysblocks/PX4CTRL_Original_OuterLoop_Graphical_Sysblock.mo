within MoSimQuadrotorModel.Control.Implementations.Sysblocks;
model PX4CTRL_Original_OuterLoop_Graphical_Sysblock "Visible graphical implementation of the original px4ctrl position/velocity outer loop. It emits Euler attitude and collective thrust commands for the shared MWORKS inner loop; it is not a ROS/C++ deployment-equivalence claim."
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(ref_px, px, ref_vx, vx, ref_ax, ref_py, py, ref_vy, vy, ref_ay, ref_pz, pz, ref_vz, vz, ref_az, yaw_mea, ref_yaw), Right(desired_acc_x, desired_acc_y, desired_acc_z, roll_cmd, pitch_cmd, yaw_cmd, collective_thrust_n, normalized_thrust)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"64","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\px4ctrl_codegen_sil_v1\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.5,StoreEventValue=0),Diagram(coordinateSystem(extent={{-900
,-560},{760,590}},grid={2,2})));
  SysplorerEmbeddedCoder.Port.Inport ref_px 
    annotation (Placement(transformation(origin = {-192, 442}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport px 
    annotation (Placement(transformation(origin = {-192, 494}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vx 
    annotation (Placement(transformation(origin = {-192, 390}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vx 
    annotation (Placement(transformation(origin = {-192, 338}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_ax 
    annotation (Placement(transformation(origin = {-192, -390}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_py 
    annotation (Placement(transformation(origin = {-192, 234}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport py 
    annotation (Placement(transformation(origin = {-192, 286}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vy 
    annotation (Placement(transformation(origin = {-192, 182}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vy 
    annotation (Placement(transformation(origin = {-192, 130}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_ay 
    annotation (Placement(transformation(origin = {-192, -442}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_pz 
    annotation (Placement(transformation(origin = {-192, 26}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport pz 
    annotation (Placement(transformation(origin = {-192, 78}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_vz 
    annotation (Placement(transformation(origin = {-192, -26}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport vz 
    annotation (Placement(transformation(origin = {-192, -78}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_az 
    annotation (Placement(transformation(origin = {-192, -494}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation (Placement(transformation(origin = {-192, -286}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Inport ref_yaw 
    annotation (Placement(transformation(origin = {-192, -182}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Gain Kp_x(k=1.5) 
    annotation (Placement(transformation(origin = {-96, 182}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain Kv_x(k=1.5) 
    annotation (Placement(transformation(origin = {-96, 130}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain Kp_y(k=1.5) 
    annotation (Placement(transformation(origin = {-96, 78}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain Kv_y(k=1.5) 
    annotation (Placement(transformation(origin = {-96, 26}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain Kp_z(k=1.5) 
    annotation (Placement(transformation(origin = {-96, -26}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain Kv_z(k=1.5) 
    annotation (Placement(transformation(origin = {-96, -78}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant gravity_mps2(k=9.80665) 
    annotation (Placement(transformation(origin = {-192, -234}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant mass_kg(k=1.0) 
    annotation (Placement(transformation(origin = {-192, -130}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_fraction(k=0.37) 
    annotation (Placement(transformation(origin = {-192, -338}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_x 
    annotation (Placement(transformation(origin = {48, -104}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_y 
    annotation (Placement(transformation(origin = {48, -156}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport desired_acc_z 
    annotation (Placement(transformation(origin = {96, -78}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction sin_yaw(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.sin) 
    annotation (Placement(transformation(origin = {-144, -208}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction cos_yaw(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.cos) 
    annotation (Placement(transformation(origin = {-144, -156}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_command_identity(k=1.0) 
    annotation (Placement(transformation(origin = {-144, -104}, extent = {{-17, -11}, {17, 11}})));
  SysplorerEmbeddedCoder.Port.Outport roll_cmd 
    annotation (Placement(transformation(origin = {192, 0}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport pitch_cmd 
    annotation (Placement(transformation(origin = {192, 52}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport yaw_cmd 
    annotation (Placement(transformation(origin = {-96, -182}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport collective_thrust_n 
    annotation (Placement(transformation(origin = {192, -52}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.Port.Outport normalized_thrust 
    annotation (Placement(transformation(origin = {144, -78}, extent = {{-17, -11}, {17, 11}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1,SampleTime(auto=false)=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_x(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 208},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_y(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 156},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_y(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 104},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_z(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum velocity_error_z(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product ax_times_sin_yaw(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={48, 52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product ay_times_cos_yaw(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={48, 0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product ax_times_cos_yaw(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={48, 156},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product ay_times_sin_yaw(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={48, 104},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_numerator(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={96, 26},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product roll_divide_gravity(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={144, 26},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_numerator(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={96, 78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product pitch_divide_gravity(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={144, 78},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product gravity_over_hover(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={-144, -260},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product normalized_thrust_divide(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={96, -26},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product mass_times_gravity(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={-144, -52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product full_collective_thrust(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={-96, -130},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Product collective_thrust_multiply(isSaturate=false,inputs="**") 
    annotation (Placement(transformation(origin={144, -26},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="*",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_acc_x_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-48, 52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acc_x_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={0, 52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_acc_y_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-48, 0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acc_y_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={0, 0},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum feedback_acc_z_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={-48, -52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acc_z_reference_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={0, -52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum desired_acc_z_sum(isSaturate=false,inputs="++") annotation(Placement(transformation(origin={48, -52},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum position_error_x(isSaturate=false,inputs="+-") annotation(Placement(transformation(origin={-144, 260},extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1,u2),y(Type(ref="double"),Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(yaw_mea, sin_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -286}, {-168, -286}, {-168, -208}, {-162, -208}}));
  connect(yaw_mea, cos_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -286}, {-168, -286}, {-168, -156}, {-162, -156}}));
  connect(ref_yaw, yaw_command_identity.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -182}, {-168, -182}, {-168, -104}, {-162, -104}}));
  connect(yaw_command_identity.y, yaw_cmd) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -104}, {-120, -104}, {-120, -182}, {-114, -182}}));
  connect(ref_vx, velocity_error_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 390}, {-168, 390}, {-168, 208}, {-162, 208}}));
  connect(vx, velocity_error_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 338}, {-168, 338}, {-168, 208}, {-162, 208}}));
  connect(velocity_error_x.y, Kv_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 208}, {-120, 208}, {-120, 130}, {-114, 130}}));
  connect(ref_py, position_error_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 234}, {-168, 234}, {-168, 156}, {-162, 156}}));
  connect(py, position_error_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 286}, {-168, 286}, {-168, 156}, {-162, 156}}));
  connect(position_error_y.y, Kp_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 156}, {-120, 156}, {-120, 78}, {-114, 78}}));
  connect(ref_vy, velocity_error_y.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 182}, {-168, 182}, {-168, 104}, {-162, 104}}));
  connect(vy, velocity_error_y.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 130}, {-168, 130}, {-168, 104}, {-162, 104}}));
  connect(velocity_error_y.y, Kv_y.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 104}, {-120, 104}, {-120, 26}, {-114, 26}}));
  connect(ref_pz, position_error_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 26}, {-168, 26}, {-168, 52}, {-162, 52}}));
  connect(pz, position_error_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 78}, {-168, 78}, {-168, 52}, {-162, 52}}));
  connect(position_error_z.y, Kp_z.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 52}, {-120, 52}, {-120, -26}, {-114, -26}}));
  connect(ref_vz, velocity_error_z.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -26}, {-168, -26}, {-168, 0}, {-162, 0}}));
  connect(vz, velocity_error_z.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -78}, {-168, -78}, {-168, 0}, {-162, 0}}));
  connect(velocity_error_z.y, Kv_z.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 0}, {-120, 0}, {-120, -78}, {-114, -78}}));
  connect(sin_yaw.y1, ax_times_sin_yaw.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -208}, {-48, -208}, {-48, 52}, {30, 52}}));
  connect(cos_yaw.y1, ay_times_cos_yaw.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -156}, {-48, -156}, {-48, 0}, {30, 0}}));
  connect(ax_times_sin_yaw.y, roll_numerator.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, 52}, {72, 52}, {72, 26}, {78, 26}}));
  connect(ay_times_cos_yaw.y, roll_numerator.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, 0}, {72, 0}, {72, 26}, {78, 26}}));
  connect(roll_numerator.y, roll_divide_gravity.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{114, 26}, {126, 26}}));
  connect(gravity_mps2.y, roll_divide_gravity.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -234}, {-24, -234}, {-24, 26}, {126, 26}}));
  connect(roll_divide_gravity.y, roll_cmd) 
    annotation(Line(origin = {0.0, 0.0}, points = {{162, 26}, {168, 26}, {168, 0}, {174, 0}}));
  connect(cos_yaw.y1, ax_times_cos_yaw.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -156}, {-48, -156}, {-48, 156}, {30, 156}}));
  connect(sin_yaw.y1, ay_times_sin_yaw.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -208}, {-48, -208}, {-48, 104}, {30, 104}}));
  connect(ax_times_cos_yaw.y, pitch_numerator.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, 156}, {72, 156}, {72, 78}, {78, 78}}));
  connect(ay_times_sin_yaw.y, pitch_numerator.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, 104}, {72, 104}, {72, 78}, {78, 78}}));
  connect(pitch_numerator.y, pitch_divide_gravity.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{114, 78}, {126, 78}}));
  connect(gravity_mps2.y, pitch_divide_gravity.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -234}, {-24, -234}, {-24, 78}, {126, 78}}));
  connect(pitch_divide_gravity.y, pitch_cmd) 
    annotation(Line(origin = {0.0, 0.0}, points = {{162, 78}, {168, 78}, {168, 52}, {174, 52}}));
  connect(gravity_mps2.y, gravity_over_hover.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -234}, {-168, -234}, {-168, -260}, {-162, -260}}));
  connect(hover_fraction.y, gravity_over_hover.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -338}, {-168, -338}, {-168, -260}, {-162, -260}}));
  connect(gravity_over_hover.y, normalized_thrust_divide.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -260}, {-24, -260}, {-24, -26}, {78, -26}}));
  connect(normalized_thrust_divide.y, normalized_thrust) 
    annotation(Line(origin = {0.0, 0.0}, points = {{114, -26}, {120, -26}, {120, -78}, {126, -78}}));
  connect(mass_kg.y, mass_times_gravity.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -130}, {-168, -130}, {-168, -52}, {-162, -52}}));
  connect(gravity_mps2.y, mass_times_gravity.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -234}, {-168, -234}, {-168, -52}, {-162, -52}}));
  connect(mass_times_gravity.y, full_collective_thrust.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, -52}, {-120, -52}, {-120, -130}, {-114, -130}}));
  connect(hover_fraction.y, full_collective_thrust.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -338}, {-144, -338}, {-144, -130}, {-114, -130}}));
  connect(normalized_thrust_divide.y, collective_thrust_multiply.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{114, -26}, {126, -26}}));
  connect(full_collective_thrust.y, collective_thrust_multiply.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, -130}, {24, -130}, {24, -26}, {126, -26}}));
  connect(collective_thrust_multiply.y, collective_thrust_n) 
    annotation(Line(origin = {0.0, 0.0}, points = {{162, -26}, {168, -26}, {168, -52}, {174, -52}}));
  connect(Kp_x.y, feedback_acc_x_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, 182}, {-72, 182}, {-72, 52}, {-66, 52}}));
  connect(Kv_x.y, feedback_acc_x_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, 130}, {-72, 130}, {-72, 52}, {-66, 52}}));
  connect(feedback_acc_x_sum.y, desired_acc_x_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-30, 52}, {-18, 52}}));
  connect(ref_ax, desired_acc_x_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -390}, {-96, -390}, {-96, 52}, {-18, 52}}));
  connect(desired_acc_x_sum.y, desired_acc_x) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 52}, {24, 52}, {24, -104}, {30, -104}}));
  connect(desired_acc_x_sum.y, ax_times_sin_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 52}, {30, 52}}));
  connect(desired_acc_x_sum.y, ax_times_cos_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 52}, {24, 52}, {24, 156}, {30, 156}}));
  connect(Kp_y.y, feedback_acc_y_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, 78}, {-72, 78}, {-72, 0}, {-66, 0}}));
  connect(Kv_y.y, feedback_acc_y_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, 26}, {-72, 26}, {-72, 0}, {-66, 0}}));
  connect(feedback_acc_y_sum.y, desired_acc_y_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-30, 0}, {-18, 0}}));
  connect(ref_ay, desired_acc_y_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -442}, {-96, -442}, {-96, 0}, {-18, 0}}));
  connect(desired_acc_y_sum.y, desired_acc_y) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 0}, {24, 0}, {24, -156}, {30, -156}}));
  connect(desired_acc_y_sum.y, ay_times_cos_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 0}, {30, 0}}));
  connect(desired_acc_y_sum.y, ay_times_sin_yaw.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, 0}, {24, 0}, {24, 104}, {30, 104}}));
  connect(Kp_z.y, feedback_acc_z_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, -26}, {-72, -26}, {-72, -52}, {-66, -52}}));
  connect(Kv_z.y, feedback_acc_z_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-78, -78}, {-72, -78}, {-72, -52}, {-66, -52}}));
  connect(feedback_acc_z_sum.y, desired_acc_z_reference_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-30, -52}, {-18, -52}}));
  connect(ref_az, desired_acc_z_reference_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -494}, {-96, -494}, {-96, -52}, {-18, -52}}));
  connect(desired_acc_z_reference_sum.y, desired_acc_z_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{18, -52}, {30, -52}}));
  connect(gravity_mps2.y, desired_acc_z_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, -234}, {-72, -234}, {-72, -52}, {30, -52}}));
  connect(desired_acc_z_sum.y, desired_acc_z) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, -52}, {72, -52}, {72, -78}, {78, -78}}));
  connect(desired_acc_z_sum.y, normalized_thrust_divide.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{66, -52}, {72, -52}, {72, -26}, {78, -26}}));
  connect(ref_px, position_error_x.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 442}, {-168, 442}, {-168, 260}, {-162, 260}}));
  connect(px, position_error_x.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-174, 494}, {-168, 494}, {-168, 260}, {-162, 260}}));
  connect(position_error_x.y, Kp_x.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{-126, 260}, {-120, 260}, {-120, 182}, {-114, 182}}));
  end PX4CTRL_Original_OuterLoop_Graphical_Sysblock;