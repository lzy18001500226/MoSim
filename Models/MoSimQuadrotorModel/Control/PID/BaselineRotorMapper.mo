within MoSimQuadrotorModel.Control.PID;
model BaselineRotorMapper "Shared graphical baseline rotor mapper — common yaw mixing and saturation chain for OfficialPid and Px4Ctrl baselines"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version = "26.3.0",PortArrangement(Left(amplitude_1, amplitude_2, amplitude_3, amplitude_4), Right(rotor_command_1, rotor_command_2, rotor_command_3, rotor_command_4)),modelType = Control,BlockSystem(blockKind = BlockKind.userModel,SampleTime(auto=true,group = "")=0.01,OutputInterval=0.01),SysblockVersion = "1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"}, "code_replacement":{"standard_c_library":"C99"}, "custom_code":{"code":{"function_declare":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "function_define":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "global_variable_declare":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "global_variable_define":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "include":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "macro":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "type":{"head":"", "item_head":"", "item_tail":"", "tail":""}}, "code_protection":{"integer_division_by_zero":false, "overflow":false}}, "data_type":{"real_as_float":true}, "experiment":{"task_and_sample":{"muti_task_mode":false, "whether_to_use_prefix":false}}, "hardware_platform":{"largest_atomic_size":{"floating_point":"32", "integer":"32"}}, "identifier":{"max_length":32, "style":{"function":"camelCase", "local_variable":"camelCase", "macro":"camelCase", "mem_var":"camelCase", "type":"camelCase"}}, "interface":{"function_name":{"initialize":"Init", "step":"Step"}}, "is_expand":{"is_expand":false}, "optimization":{"array_loop_threshold":5, "logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:/Users/HP/Documents/MWORKS/Simulation"}})), Icon(coordinateSystem(preserveAspectRatio = false)), experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01, StartTime = 0, StopTime = 0.02, StoreEventValue = 0));
  SysplorerEmbeddedCoder.Port.Inport amplitude_1 
    annotation(Placement(transformation(extent = {{-257, 377}, {-223, 403}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_2 
    annotation(Placement(transformation(extent = {{-257, 325}, {-223, 351}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_3 
    annotation(Placement(transformation(extent = {{-257, 273}, {-223, 299}})));
  SysplorerEmbeddedCoder.Port.Inport amplitude_4 
    annotation(Placement(transformation(extent = {{-257, 221}, {-223, 247}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_1 
    annotation(Placement(transformation(extent = {{223, 65}, {257, 91}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_2 
    annotation(Placement(transformation(extent = {{223, 13}, {257, 39}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_3 
    annotation(Placement(transformation(extent = {{223, -39}, {257, -13}})));
  SysplorerEmbeddedCoder.Port.Outport rotor_command_4 
    annotation(Placement(transformation(extent = {{223, -91}, {257, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_1(k = -0.25) 
    annotation(Placement(transformation(extent = {{-209, 65}, {-175, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_2(k = 0.25) 
    annotation(Placement(transformation(extent = {{-209, 13}, {-175, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_3(k = -0.25) 
    annotation(Placement(transformation(extent = {{-209, -39}, {-175, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_projection_4(k = 0.25) 
    annotation(Placement(transformation(extent = {{-209, -91}, {-175, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_sum(inputs = "++++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-161, -13}, {-127, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2, u3, u4)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2"), label(text = "+", instance = "u3"), label(text = "+", instance = "u4")))));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_1(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-113, 169}, {-79, 195}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_1(k = -0.26666666666666666) 
    annotation(Placement(transformation(extent = {{-113, 117}, {-79, 143}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_1(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-65, 65}, {-31, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_1(k = 4.632854053414571) 
    annotation(Placement(transformation(extent = {{-17, 65}, {17, 91}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_1(k = 64.7923778389665) 
    annotation(Placement(transformation(extent = {{-257, 169}, {-223, 195}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_1(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{31, 65}, {65, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_1(k = 1) 
    annotation(Placement(transformation(extent = {{175, 65}, {209, 91}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_2(inputs = "+-", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-113, 65}, {-79, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "-", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_2(k = 0.26666666666666666) 
    annotation(Placement(transformation(extent = {{-113, 13}, {-79, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_2(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-65, 13}, {-31, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_2(k = 4.632854053414571) 
    annotation(Placement(transformation(extent = {{-17, 13}, {17, 39}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_2(k = 64.7923778389665) 
    annotation(Placement(transformation(extent = {{-257, 117}, {-223, 143}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_2(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{31, 13}, {65, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_2(k = -1) 
    annotation(Placement(transformation(extent = {{175, 13}, {209, 39}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_3(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-113, -39}, {-79, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_3(k = -0.26666666666666666) 
    annotation(Placement(transformation(extent = {{-113, -91}, {-79, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_3(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-65, -39}, {-31, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_3(k = 4.632854053414571) 
    annotation(Placement(transformation(extent = {{-17, -39}, {17, -13}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_3(k = 64.7923778389665) 
    annotation(Placement(transformation(extent = {{-257, 65}, {-223, 91}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_3(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{31, -39}, {65, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_3(k = 1) 
    annotation(Placement(transformation(extent = {{175, -39}, {209, -13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum non_yaw_4(inputs = "+-", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-113, -143}, {-79, -117}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "-", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_authority_4(k = 0.26666666666666666) 
    annotation(Placement(transformation(extent = {{-113, -195}, {-79, -169}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mapped_4(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{-65, -91}, {-31, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain command_scale_4(k = 4.632854053414571) 
    annotation(Placement(transformation(extent = {{-17, -91}, {17, -65}})));
  SysplorerEmbeddedCoder.Sources.Constant hover_4(k = 64.7923778389665) 
    annotation(Placement(transformation(extent = {{-257, 13}, {-223, 39}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Sum hover_plus_4(inputs = "++", isSaturate = false) 
    annotation(Placement(transformation(extent = {{31, -91}, {65, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap)), PortLabels(labelType = "CustomType", labels(label(text = "+", instance = "u1"), label(text = "+", instance = "u2")))));
  SysplorerEmbeddedCoder.MathOperation.Gain spin_sign_4(k = -1) 
    annotation(Placement(transformation(extent = {{175, -91}, {209, -65}})));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_1(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{79, 65}, {113, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_1(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{127, 65}, {161, 91}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_1(k = 110) 
    annotation(Placement(transformation(extent = {{-257, -39}, {-223, -13}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_1(k = 0) 
    annotation(Placement(transformation(extent = {{-257, -247}, {-223, -221}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_2(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{79, 13}, {113, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_2(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{127, 13}, {161, 39}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_2(k = 110) 
    annotation(Placement(transformation(extent = {{-257, -91}, {-223, -65}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_2(k = 0) 
    annotation(Placement(transformation(extent = {{-257, -299}, {-223, -273}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_3(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{79, -39}, {113, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_3(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{127, -39}, {161, -13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_3(k = 110) 
    annotation(Placement(transformation(extent = {{-257, -143}, {-223, -117}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_3(k = 0) 
    annotation(Placement(transformation(extent = {{-257, -351}, {-223, -325}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_ceiling_4(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{79, -91}, {113, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.MathOperation.Maxmin command_floor_4(maxMinType = SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max, portNumber = 2, isSaturate = false) 
    annotation(Placement(transformation(extent = {{127, -91}, {161, -65}})), __MWORKS(BlockSystem(Instance(u(u1, u2)), Type(overflowKind = SysplorerEmbeddedCoder.Types.OverflowKind.wrap))));
  SysplorerEmbeddedCoder.Sources.Constant command_upper_limit_4(k = 110) 
    annotation(Placement(transformation(extent = {{-257, -195}, {-223, -169}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  SysplorerEmbeddedCoder.Sources.Constant command_lower_limit_4(k = 0) 
    annotation(Placement(transformation(extent = {{-257, -403}, {-223, -377}})), __MWORKS(BlockSystem(SampleTime(auto = true) = -1)));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(amplitude_1, yaw_projection_1.u) 
    annotation(Line(points = {{-223, 390}, {-216, 390}, {-216, 78}, {-209, 78}}, color = {0, 0, 127}));
  connect(yaw_projection_1.y, yaw_sum.u1) 
    annotation(Line(points = {{-175, 78}, {-168, 78}, {-168, 0}, {-161, 0}}, color = {0, 0, 127}));
  connect(amplitude_2, yaw_projection_2.u) 
    annotation(Line(points = {{-223, 338}, {-216, 338}, {-216, 26}, {-209, 26}}, color = {0, 0, 127}));
  connect(yaw_projection_2.y, yaw_sum.u2) 
    annotation(Line(points = {{-175, 26}, {-168, 26}, {-168, 0}, {-161, 0}}, color = {0, 0, 127}));
  connect(amplitude_3, yaw_projection_3.u) 
    annotation(Line(points = {{-223, 286}, {-216, 286}, {-216, -26}, {-209, -26}}, color = {0, 0, 127}));
  connect(yaw_projection_3.y, yaw_sum.u3) 
    annotation(Line(points = {{-175, -26}, {-168, -26}, {-168, 0}, {-161, 0}}, color = {0, 0, 127}));
  connect(amplitude_4, yaw_projection_4.u) 
    annotation(Line(points = {{-223, 234}, {-216, 234}, {-216, -78}, {-209, -78}}, color = {0, 0, 127}));
  connect(yaw_projection_4.y, yaw_sum.u4) 
    annotation(Line(points = {{-175, -78}, {-168, -78}, {-168, 0}, {-161, 0}}, color = {0, 0, 127}));
  connect(amplitude_1, non_yaw_1.u1) 
    annotation(Line(origin={0,0},
points={{-220.954,389.986},{-168,389.986},{-168,188.5},{-114.8,188.5}},
color={0,0,127}));
  connect(yaw_sum.y, non_yaw_1.u2) 
    annotation(Line(origin={0,0},
points={{-125.2,0},{-120,0},{-120,50},{-168,50},{-168,175.5},{-114.8,175.5}},
color={0,0,127}));
  connect(yaw_sum.y, yaw_authority_1.u) 
    annotation(Line(origin={0,0},
points={{-125.2,0},{-120,0},{-120,50},{-168,50},{-168,130},{-114.8,130}},
color={0,0,127}));
  connect(non_yaw_1.y, mapped_1.u1) 
    annotation(Line(points = {{-79, 182}, {-72, 182}, {-72, 78}, {-65, 78}}, color = {0, 0, 127}));
  connect(yaw_authority_1.y, mapped_1.u2) 
    annotation(Line(points = {{-79, 130}, {-72, 130}, {-72, 78}, {-65, 78}}, color = {0, 0, 127}));
  connect(mapped_1.y, command_scale_1.u) 
    annotation(Line(points = {{-31, 78}, {-17, 78}}, color = {0, 0, 127}));
  connect(command_scale_1.y, hover_plus_1.u1) 
    annotation(Line(origin = {0, 0},
    points = {{18.8, 78}, {24, 78}, {24, 84.5}, {29.2, 84.5}},
    color = {0, 0, 127}));
  connect(hover_1.y, hover_plus_1.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,182},{-168,182},{-168,50},{24,50},{24,71.5},{29.2,71.5}},
color={0,0,127}));
  connect(spin_sign_1.y, rotor_command_1) 
    annotation(Line(points = {{209, 78}, {223, 78}}, color = {0, 0, 127}));
  connect(amplitude_2, non_yaw_2.u1) 
    annotation(Line(points = {{-223, 338}, {-168, 338}, {-168, 78}, {-113, 78}}, color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_2.u2) 
    annotation(Line(origin={0,0},
points={{-125.2,0},{-120,0},{-120,71.5},{-114.8,71.5}},
color={0,0,127}));
  connect(yaw_sum.y, yaw_authority_2.u) 
    annotation(Line(points = {{-127, 0}, {-120, 0}, {-120, 26}, {-113, 26}}, color = {0, 0, 127}));
  connect(non_yaw_2.y, mapped_2.u1) 
    annotation(Line(points = {{-79, 78}, {-72, 78}, {-72, 26}, {-65, 26}}, color = {0, 0, 127}));
  connect(yaw_authority_2.y, mapped_2.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-77.2, 26}, {-72, 26}, {-72, 19.5}, {-66.8, 19.5}},
    color = {0, 0, 127}));
  connect(mapped_2.y, command_scale_2.u) 
    annotation(Line(points = {{-31, 26}, {-17, 26}}, color = {0, 0, 127}));
  connect(command_scale_2.y, hover_plus_2.u1) 
    annotation(Line(origin = {0, 0},
    points = {{18.8, 26}, {24, 26}, {24, 32.5}, {29.2, 32.5}},
    color = {0, 0, 127}));
  connect(hover_2.y, hover_plus_2.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,130},{-168,130},{-168,50},{24,50},{24,19.5},{29.2,19.5}},
color={0,0,127}));
  connect(spin_sign_2.y, rotor_command_2) 
    annotation(Line(points = {{209, 26}, {223, 26}}, color = {0, 0, 127}));
  connect(amplitude_3, non_yaw_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-220.954, 285.986}, {-168, 285.986}, {-168, -54}, {-120, -54}, {-120, -19.5}, {-114.8, -19.5}},
    color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_3.u2) 
    annotation(Line(points = {{-127, 0}, {-120, 0}, {-120, -26}, {-113, -26}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_3.u) 
    annotation(Line(points = {{-127, 0}, {-120, 0}, {-120, -78}, {-113, -78}}, color = {0, 0, 127}));
  connect(non_yaw_3.y, mapped_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-77.2, -26}, {-72, -26}, {-72, -19.5}, {-66.8, -19.5}},
    color = {0, 0, 127}));
  connect(yaw_authority_3.y, mapped_3.u2) 
    annotation(Line(points = {{-79, -78}, {-72, -78}, {-72, -26}, {-65, -26}}, color = {0, 0, 127}));
  connect(mapped_3.y, command_scale_3.u) 
    annotation(Line(points = {{-31, -26}, {-17, -26}}, color = {0, 0, 127}));
  connect(command_scale_3.y, hover_plus_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{18.8, -26}, {24, -26}, {24, -19.5}, {29.2, -19.5}},
    color = {0, 0, 127}));
  connect(hover_3.y, hover_plus_3.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,78},{-168,78},{-168,-54},{24,-54},{24,-32.5},{29.2,-32.5}},
color={0,0,127}));
  connect(spin_sign_3.y, rotor_command_3) 
    annotation(Line(points = {{209, -26}, {223, -26}}, color = {0, 0, 127}));
  connect(amplitude_4, non_yaw_4.u1) 
    annotation(Line(origin = {0, 0},
    points = {{-220.954, 233.986}, {-168, 233.986}, {-168, -123.5}, {-114.8, -123.5}},
    color = {0, 0, 127}));
  connect(yaw_sum.y, non_yaw_4.u2) 
    annotation(Line(points = {{-127, 0}, {-120, 0}, {-120, -130}, {-113, -130}}, color = {0, 0, 127}));
  connect(yaw_sum.y, yaw_authority_4.u) 
    annotation(Line(origin={0,0},
points={{-125.2,0},{-120,0},{-120,-182},{-114.8,-182}},
color={0,0,127}));
  connect(non_yaw_4.y, mapped_4.u1) 
    annotation(Line(points = {{-79, -130}, {-72, -130}, {-72, -78}, {-65, -78}}, color = {0, 0, 127}));
  connect(yaw_authority_4.y, mapped_4.u2) 
    annotation(Line(points = {{-79, -182}, {-72, -182}, {-72, -78}, {-65, -78}}, color = {0, 0, 127}));
  connect(mapped_4.y, command_scale_4.u) 
    annotation(Line(points = {{-31, -78}, {-17, -78}}, color = {0, 0, 127}));
  connect(command_scale_4.y, hover_plus_4.u1) 
    annotation(Line(origin = {0, 0},
    points = {{18.8, -78}, {24, -78}, {24, -71.5}, {29.2, -71.5}},
    color = {0, 0, 127}));
  connect(hover_4.y, hover_plus_4.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,26},{-216,26},{-216,-54},{24,-54},{24,-84.5},{29.2,-84.5}},
color={0,0,127}));
  connect(spin_sign_4.y, rotor_command_4) 
    annotation(Line(points = {{209, -78}, {223, -78}}, color = {0, 0, 127}));
  connect(hover_plus_1.y, command_ceiling_1.u1) 
    annotation(Line(origin = {0, 0},
    points = {{66.8, 78}, {72, 78}, {72, 84.5}, {77.2, 84.5}},
    color = {0, 0, 127}));
  connect(command_upper_limit_1.y, command_ceiling_1.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,-26},{-216,-26},{-216,-54},{-168,-54},{-168,50},{72,50},{72,71.5},{77.2,71.5}},
color={0,0,127}));
  connect(command_ceiling_1.y, command_floor_1.u1) 
    annotation(Line(origin = {0, 0},
    points = {{114.8, 78}, {120, 78}, {120, 84.5}, {125.2, 84.5}},
    color = {0, 0, 127}));
  connect(command_lower_limit_1.y, command_floor_1.u2) 
    annotation(Line(origin={0,0},
points={{-221.2,-234},{-168,-234},{-168,50},{120,50},{120,71.5},{125.2,71.5}},
color={0,0,127}));
  connect(command_floor_1.y, spin_sign_1.u) 
    annotation(Line(points = {{161, 78}, {175, 78}}, color = {0, 0, 127}));
  connect(hover_plus_2.y, command_ceiling_2.u1) 
    annotation(Line(origin = {0, 0},
    points = {{66.8, 26}, {72, 26}, {72, 32.5}, {77.2, 32.5}},
    color = {0, 0, 127}));
  connect(command_upper_limit_2.y, command_ceiling_2.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -78}, {-216, -78}, {-216, -54}, {-72, -54}, {-72, 50}, {72, 50}, {72, 19.5}, {77.2, 19.5}},
    color = {0, 0, 127}), __MWORKS(BlockSystem(NamedSignal)));
  connect(command_ceiling_2.y, command_floor_2.u1) 
    annotation(Line(origin = {0, 0},
    points = {{114.8, 26}, {120, 26}, {120, 32.5}, {125.2, 32.5}},
    color = {0, 0, 127}));
  connect(command_lower_limit_2.y, command_floor_2.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -286}, {-72, -286}, {-72, 50}, {120, 50}, {120, 19.5}, {125.2, 19.5}},
    color = {0, 0, 127}));
  connect(command_floor_2.y, spin_sign_2.u) 
    annotation(Line(points = {{161, 26}, {175, 26}}, color = {0, 0, 127}));
  connect(hover_plus_3.y, command_ceiling_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{66.8, -26}, {72, -26}, {72, -19.5}, {77.2, -19.5}},
    color = {0, 0, 127}));
  connect(command_upper_limit_3.y, command_ceiling_3.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -130}, {-216, -130}, {-216, -54}, {72, -54}, {72, -32.5}, {77.2, -32.5}},
    color = {0, 0, 127}));
  connect(command_ceiling_3.y, command_floor_3.u1) 
    annotation(Line(origin = {0, 0},
    points = {{114.8, -26}, {120, -26}, {120, -19.5}, {125.2, -19.5}},
    color = {0, 0, 127}));
  connect(command_lower_limit_3.y, command_floor_3.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -338}, {-72, -338}, {-72, -54}, {120, -54}, {120, -32.5}, {125.2, -32.5}},
    color = {0, 0, 127}));
  connect(command_floor_3.y, spin_sign_3.u) 
    annotation(Line(points = {{161, -26}, {175, -26}}, color = {0, 0, 127}));
  connect(hover_plus_4.y, command_ceiling_4.u1) 
    annotation(Line(origin = {0, 0},
    points = {{66.8, -78}, {72, -78}, {72, -71.5}, {77.2, -71.5}},
    color = {0, 0, 127}));
  connect(command_upper_limit_4.y, command_ceiling_4.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -182}, {-216, -182}, {-216, -54}, {72, -54}, {72, -84.5}, {77.2, -84.5}},
    color = {0, 0, 127}));
  connect(command_ceiling_4.y, command_floor_4.u1) 
    annotation(Line(origin = {0, 0},
    points = {{114.8, -78}, {120, -78}, {120, -71.5}, {125.2, -71.5}},
    color = {0, 0, 127}));
  connect(command_lower_limit_4.y, command_floor_4.u2) 
    annotation(Line(origin = {0, 0},
    points = {{-221.2, -390}, {-72, -390}, {-72, -54}, {120, -54}, {120, -84.5}, {125.2, -84.5}},
    color = {0, 0, 127}));
  connect(command_floor_4.y, spin_sign_4.u) 
    annotation(Line(points = {{161, -78}, {175, -78}}, color = {0, 0, 127}));
end BaselineRotorMapper;