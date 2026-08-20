within MoSimQuadrotorModel.Control.PID;
model OfficialPidGraphicalCore "Official PID native graphical controller core"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version = "26.3.0",PortArrangement(Left(x_ref, y_ref, z_ref, x_mea, y_mea, z_mea, roll_mea, pitch_mea, yaw_mea), Right(y, y1, y2, y3)),modelType = Control,BlockSystem(blockKind = BlockKind.userModel,SampleTime(auto=true,group = "")=0.01,OutputInterval=0.01),SysblockVersion = "1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"}, "code_replacement":{"standard_c_library":"C99"}, "custom_code":{"code":{"function_declare":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "function_define":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "global_variable_declare":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "global_variable_define":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "include":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "macro":{"head":"", "item_head":"", "item_tail":"", "tail":""}, "type":{"head":"", "item_head":"", "item_tail":"", "tail":""}}, "code_protection":{"integer_division_by_zero":false, "overflow":false}}, "data_type":{"real_as_float":true}, "experiment":{"task_and_sample":{"muti_task_mode":false, "whether_to_use_prefix":false}}, "hardware_platform":{"largest_atomic_size":{"floating_point":"32", "integer":"32"}}, "identifier":{"max_length":32, "style":{"function":"camelCase", "local_variable":"camelCase", "macro":"camelCase", "mem_var":"camelCase", "type":"camelCase"}}, "interface":{"function_name":{"initialize":"Init", "step":"Step"}}, "is_expand":{"is_expand":false}, "optimization":{"array_loop_threshold":5, "logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:/Users/HP/Documents/MWORKS/Simulation"}})), Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
    Rectangle(extent = {{-100, 100}, {100, -100}}, lineColor = {0, 100, 150}, fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
    Text(origin = {0, 32}, extent = {{-90, 18}, {90, -18}}, textString = "Official PID", textColor = {0, 100, 150}),
    Text(origin = {0, 0}, extent = {{-90, 18}, {90, -18}}, textString = "SYSBLOCK CORE", textColor = {0, 100, 150}),
    Text(origin = {0, -34}, extent = {{-90, 14}, {90, -14}}, textString = "9 IN | 4 OUT", textColor = {0, 100, 150})}), experiment(Algorithm = Euler, IntegratorStep = 0.01, Interval = 0.01, StartTime = 0, StopTime = 0.02, StoreEventValue = 0));
  SysplorerEmbeddedCoder.Port.Inport x_ref 
    annotation(Placement(transformation(origin = {-560, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport y_ref 
    annotation(Placement(transformation(origin = {-560, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport z_ref 
    annotation(Placement(transformation(origin = {-560, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport x_mea 
    annotation(Placement(transformation(origin = {-560, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport y_mea 
    annotation(Placement(transformation(origin = {-560, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport z_mea 
    annotation(Placement(transformation(origin = {-560, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport roll_mea 
    annotation(Placement(transformation(origin = {-560, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport pitch_mea 
    annotation(Placement(transformation(origin = {-560, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Inport yaw_mea 
    annotation(Placement(transformation(origin = {-560, -450}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport y 
    annotation(Placement(transformation(origin = {430, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport y1 
    annotation(Placement(transformation(origin = {430, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport y2 
    annotation(Placement(transformation(origin = {430, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Port.Outport y3 
    annotation(Placement(transformation(origin = {430, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, 300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain x_p(k = 1.5) 
    annotation(Placement(transformation(origin = {-400, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_derivative_input(k = 1.0) 
    annotation(Placement(transformation(origin = {-480, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference x_derivative_difference 
    annotation(Placement(transformation(origin = {-420, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(origin = {-360, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_derivative_filtered_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(origin = {-300, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay x_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-300, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_derivative_state_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(origin = {-240, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_derivative_state_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {-180, 300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain x_derivative(k = 1.0) 
    annotation(Placement(transformation(origin = {-120, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain x_d(k = 1.0) 
    annotation(Placement(transformation(origin = {-320, 300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum x_pd(inputs = "++") 
    annotation(Placement(transformation(origin = {-240, 300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_ref_scale(k = 0.1) 
    annotation(Placement(transformation(origin = {-160, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_ref_limit(upLimit = 0.2617801047120419, lowLimit = -0.2617801047120419) 
    annotation(Placement(transformation(origin = {-80, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum y_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, 150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain y_p(k = 1.5) 
    annotation(Placement(transformation(origin = {-400, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_derivative_input(k = 1.0) 
    annotation(Placement(transformation(origin = {-480, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference y_derivative_difference 
    annotation(Placement(transformation(origin = {-420, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(origin = {-360, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_derivative_filtered_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(origin = {-300, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay y_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-300, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_derivative_state_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(origin = {-240, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum y_derivative_state_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {-180, 150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain y_derivative(k = 1.0) 
    annotation(Placement(transformation(origin = {-120, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain y_d(k = 1.0) 
    annotation(Placement(transformation(origin = {-320, 150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum y_pd(inputs = "++") 
    annotation(Placement(transformation(origin = {-240, 150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_ref_scale(k = 0.1) 
    annotation(Placement(transformation(origin = {-160, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_ref_limit(upLimit = 0.2617801047120419, lowLimit = -0.2617801047120419) 
    annotation(Placement(transformation(origin = {-80, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, 0}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain z_p(k = 8.0) 
    annotation(Placement(transformation(origin = {-400, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_integral_dt(k = 0.01) 
    annotation(Placement(transformation(origin = {-480, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_integral_accum(inputs = "++") 
    annotation(Placement(transformation(origin = {-340, 0}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discrete.UnitDelay z_integral_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-340, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_i(k = 6.0) 
    annotation(Placement(transformation(origin = {-360, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_derivative_input(k = 1.0) 
    annotation(Placement(transformation(origin = {-480, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference z_derivative_difference 
    annotation(Placement(transformation(origin = {-420, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(origin = {-360, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_derivative_filtered_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(origin = {-300, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay z_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-300, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_derivative_state_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(origin = {-240, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_derivative_state_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {-180, 0}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain z_derivative(k = 1.0) 
    annotation(Placement(transformation(origin = {-120, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain z_d(k = 4.0) 
    annotation(Placement(transformation(origin = {-320, 0}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum z_pi(inputs = "++") 
    annotation(Placement(transformation(origin = {-240, 0}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum thrust_command(inputs = "++") 
    annotation(Placement(transformation(origin = {-160, -15}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Sources.Constant yaw_reference(k = 0.0) 
    annotation(Placement(transformation(origin = {-480, -450}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, -300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_p(k = 14.142) 
    annotation(Placement(transformation(origin = {-400, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_input(k = 1.0) 
    annotation(Placement(transformation(origin = {-480, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference pitch_derivative_difference 
    annotation(Placement(transformation(origin = {-420, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(origin = {-360, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_filtered_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(origin = {-300, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pitch_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-300, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative_state_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(origin = {-240, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_derivative_state_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {-180, -300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_derivative(k = 1.0) 
    annotation(Placement(transformation(origin = {-120, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_d(k = 1.414) 
    annotation(Placement(transformation(origin = {-320, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pitch_pd(inputs = "++") 
    annotation(Placement(transformation(origin = {-240, -300}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pitch_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(origin = {-160, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pitch_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {-80, -300}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mea_sign(k = -1) 
    annotation(Placement(transformation(origin = {-500, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, -150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_p(k = 14.142) 
    annotation(Placement(transformation(origin = {-400, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_input(k = 1.0) 
    annotation(Placement(transformation(origin = {-480, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.Difference roll_derivative_difference 
    annotation(Placement(transformation(origin = {-420, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_slope(k = 100.0) 
    annotation(Placement(transformation(origin = {-360, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_filtered_increment(k = 0.631839272714496) 
    annotation(Placement(transformation(origin = {-300, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay roll_derivative_previous_state(initCond = 0.0) 
    annotation(Placement(transformation(origin = {-300, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative_state_decay(k = 0.368160727285504) 
    annotation(Placement(transformation(origin = {-240, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_derivative_state_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {-180, -150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_derivative(k = 1.0) 
    annotation(Placement(transformation(origin = {-120, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_d(k = 1.414) 
    annotation(Placement(transformation(origin = {-320, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum roll_pd(inputs = "++") 
    annotation(Placement(transformation(origin = {-240, -150}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation roll_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(origin = {-160, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain roll_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {-80, -150}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum yaw_error(inputs = "+-") 
    annotation(Placement(transformation(origin = {-480, -450}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_p(k = 5.0) 
    annotation(Placement(transformation(origin = {-400, -450}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation yaw_limit(upLimit = 7.0, lowLimit = -7.0) 
    annotation(Placement(transformation(origin = {-160, -450}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain yaw_mix(k = 0.707) 
    annotation(Placement(transformation(origin = {-80, -450}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_yaw_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, 215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_pitch_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_1_roll_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, 145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1_first(inputs = "++") 
    annotation(Placement(transformation(origin = {100, 180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_1(inputs = "++") 
    annotation(Placement(transformation(origin = {260, 180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_1_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {255, 180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_1_sign(k = 1) 
    annotation(Placement(transformation(origin = {335, 180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_yaw_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, 95}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_pitch_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_2_roll_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, 25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2_first(inputs = "++") 
    annotation(Placement(transformation(origin = {100, 60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_2(inputs = "++") 
    annotation(Placement(transformation(origin = {260, 60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_2_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {255, 60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_2_sign(k = 1) 
    annotation(Placement(transformation(origin = {335, 60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_yaw_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, -25}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_pitch_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_3_roll_gain(k = -1) 
    annotation(Placement(transformation(origin = {55, -95}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3_first(inputs = "++") 
    annotation(Placement(transformation(origin = {100, -60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_3(inputs = "++") 
    annotation(Placement(transformation(origin = {260, -60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_3_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {255, -60}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_3_sign(k = 1) 
    annotation(Placement(transformation(origin = {335, -60}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_yaw_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, -145}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_pitch_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, -180}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Gain mixer_4_roll_gain(k = 1) 
    annotation(Placement(transformation(origin = {55, -215}, extent = {{-17, -13}, {17, 13}})));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4_first(inputs = "++") 
    annotation(Placement(transformation(origin = {100, -180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum mixer_4(inputs = "++") 
    annotation(Placement(transformation(origin = {260, -180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum rotor_4_sum(inputs = "++") 
    annotation(Placement(transformation(origin = {255, -180}, extent = {{-17, -13}, {17, 13}})), __MWORKS(BlockSystem(Instance(u(u1, u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain rotor_4_sign(k = 1) 
    annotation(Placement(transformation(origin = {335, -180}, extent = {{-17, -13}, {17, 13}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(x_derivative_input.y, x_derivative_difference.u) 
    annotation(Line(points = {{-463, 225}, {-437, 225}}, color = {0, 0, 127}));
  connect(x_derivative_difference.y, x_derivative_slope.u) 
    annotation(Line(points = {{-403, 225}, {-377, 225}}, color = {0, 0, 127}));
  connect(x_derivative_slope.y, x_derivative_filtered_increment.u) 
    annotation(Line(points = {{-343, 225}, {-330, 225}, {-330, 195}, {-317, 195}}, color = {0, 0, 127}));
  connect(x_derivative_filtered_increment.y, x_derivative_state_sum.u2) 
    annotation(Line(points = {{-283, 195}, {-240, 195}, {-240, 225}, {-197, 225}}, color = {0, 0, 127}));
  connect(x_derivative_previous_state.y, x_derivative_state_decay.u) 
    annotation(Line(points = {{-283, 255}, {-257, 255}}, color = {0, 0, 127}));
  connect(x_derivative_state_decay.y, x_derivative_state_sum.u1) 
    annotation(Line(points = {{-223, 255}, {-210, 255}, {-210, 225}, {-197, 225}}, color = {0, 0, 127}));
  connect(x_derivative_state_sum.y, x_derivative_previous_state.u1) 
    annotation(Line(points = {{-197, 225}, {-240, 225}, {-240, 255}, {-283, 255}}, color = {0, 0, 127}));
  connect(x_derivative_state_sum.y, x_derivative.u) 
    annotation(Line(points = {{-163, 225}, {-137, 225}}, color = {0, 0, 127}));
  connect(x_ref, x_error.u1) 
    annotation(Line(points = {{-543, 260}, {-497, 260}}, color = {0, 0, 127}));
  connect(x_mea, x_error.u2) 
    annotation(Line(points = {{-560, 99}, {-560, 173}, {-480, 173}, {-480, 247}}, color = {0, 0, 127}));
  connect(x_error.y, x_p.u) 
    annotation(Line(points = {{-463, 260}, {-440, 260}, {-440, 295}, {-417, 295}}, color = {0, 0, 127}));
  connect(x_error.y, x_derivative_input.u) 
    annotation(Line(points = {{-480, 247}, {-480, 238}}, color = {0, 0, 127}));
  connect(x_derivative.y, x_d.u) 
    annotation(Line(points = {{-137, 225}, {-303, 225}}, color = {0, 0, 127}));
  connect(x_p.y, x_pd.u1) 
    annotation(Line(points = {{-383, 295}, {-320, 295}, {-320, 260}, {-257, 260}}, color = {0, 0, 127}));
  connect(x_d.y, x_pd.u2) 
    annotation(Line(points = {{-303, 225}, {-280, 225}, {-280, 260}, {-257, 260}}, color = {0, 0, 127}));
  connect(x_pd.y, pitch_ref_scale.u) 
    annotation(Line(points = {{-223, 260}, {-177, 260}}, color = {0, 0, 127}));
  connect(pitch_ref_scale.y, pitch_ref_limit.u) 
    annotation(Line(points = {{-143, 260}, {-97, 260}}, color = {0, 0, 127}));
  connect(y_derivative_input.y, y_derivative_difference.u) 
    annotation(Line(points = {{-463, 85}, {-437, 85}}, color = {0, 0, 127}));
  connect(y_derivative_difference.y, y_derivative_slope.u) 
    annotation(Line(points = {{-403, 85}, {-377, 85}}, color = {0, 0, 127}));
  connect(y_derivative_slope.y, y_derivative_filtered_increment.u) 
    annotation(Line(points = {{-343, 85}, {-330, 85}, {-330, 55}, {-317, 55}}, color = {0, 0, 127}));
  connect(y_derivative_filtered_increment.y, y_derivative_state_sum.u2) 
    annotation(Line(points = {{-283, 55}, {-240, 55}, {-240, 85}, {-197, 85}}, color = {0, 0, 127}));
  connect(y_derivative_previous_state.y, y_derivative_state_decay.u) 
    annotation(Line(points = {{-283, 115}, {-257, 115}}, color = {0, 0, 127}));
  connect(y_derivative_state_decay.y, y_derivative_state_sum.u1) 
    annotation(Line(points = {{-223, 115}, {-210, 115}, {-210, 85}, {-197, 85}}, color = {0, 0, 127}));
  connect(y_derivative_state_sum.y, y_derivative_previous_state.u1) 
    annotation(Line(points = {{-197, 85}, {-240, 85}, {-240, 115}, {-283, 115}}, color = {0, 0, 127}));
  connect(y_derivative_state_sum.y, y_derivative.u) 
    annotation(Line(points = {{-163, 85}, {-137, 85}}, color = {0, 0, 127}));
  connect(y_ref, y_error.u1) 
    annotation(Line(points = {{-560, 189}, {-560, 161}, {-480, 161}, {-480, 133}}, color = {0, 0, 127}));
  connect(y_mea, y_error.u2) 
    annotation(Line(points = {{-560, 41}, {-560, 74}, {-480, 74}, {-480, 107}}, color = {0, 0, 127}));
  connect(y_error.y, y_p.u) 
    annotation(Line(points = {{-463, 120}, {-440, 120}, {-440, 155}, {-417, 155}}, color = {0, 0, 127}));
  connect(y_error.y, y_derivative_input.u) 
    annotation(Line(points = {{-480, 107}, {-480, 98}}, color = {0, 0, 127}));
  connect(y_derivative.y, y_d.u) 
    annotation(Line(points = {{-137, 85}, {-303, 85}}, color = {0, 0, 127}));
  connect(y_p.y, y_pd.u1) 
    annotation(Line(points = {{-383, 155}, {-320, 155}, {-320, 120}, {-257, 120}}, color = {0, 0, 127}));
  connect(y_d.y, y_pd.u2) 
    annotation(Line(points = {{-303, 85}, {-280, 85}, {-280, 120}, {-257, 120}}, color = {0, 0, 127}));
  connect(y_pd.y, roll_ref_scale.u) 
    annotation(Line(points = {{-223, 120}, {-177, 120}}, color = {0, 0, 127}));
  connect(roll_ref_scale.y, roll_ref_limit.u) 
    annotation(Line(points = {{-143, 120}, {-97, 120}}, color = {0, 0, 127}));
  connect(z_derivative_input.y, z_derivative_difference.u) 
    annotation(Line(points = {{-463, -65}, {-437, -65}}, color = {0, 0, 127}));
  connect(z_derivative_difference.y, z_derivative_slope.u) 
    annotation(Line(points = {{-403, -65}, {-377, -65}}, color = {0, 0, 127}));
  connect(z_derivative_slope.y, z_derivative_filtered_increment.u) 
    annotation(Line(points = {{-343, -65}, {-330, -65}, {-330, -95}, {-317, -95}}, color = {0, 0, 127}));
  connect(z_derivative_filtered_increment.y, z_derivative_state_sum.u2) 
    annotation(Line(points = {{-283, -95}, {-240, -95}, {-240, -65}, {-197, -65}}, color = {0, 0, 127}));
  connect(z_derivative_previous_state.y, z_derivative_state_decay.u) 
    annotation(Line(points = {{-283, -35}, {-257, -35}}, color = {0, 0, 127}));
  connect(z_derivative_state_decay.y, z_derivative_state_sum.u1) 
    annotation(Line(points = {{-223, -35}, {-210, -35}, {-210, -65}, {-197, -65}}, color = {0, 0, 127}));
  connect(z_derivative_state_sum.y, z_derivative_previous_state.u1) 
    annotation(Line(points = {{-197, -65}, {-240, -65}, {-240, -35}, {-283, -35}}, color = {0, 0, 127}));
  connect(z_derivative_state_sum.y, z_derivative.u) 
    annotation(Line(points = {{-163, -65}, {-137, -65}}, color = {0, 0, 127}));
  connect(z_ref, z_error.u1) 
    annotation(Line(points = {{-560, 131}, {-560, 62}, {-480, 62}, {-480, -7}}, color = {0, 0, 127}));
  connect(z_mea, z_error.u2) 
    annotation(Line(points = {{-543, -30}, {-520, -30}, {-520, -20}, {-497, -20}}, color = {0, 0, 127}));
  connect(z_error.y, z_p.u) 
    annotation(Line(points = {{-463, -20}, {-440, -20}, {-440, 25}, {-417, 25}}, color = {0, 0, 127}));
  connect(z_error.y, z_integral_dt.u) 
    annotation(Line(points = {{-463, -20}, {-417, -20}}, color = {0, 0, 127}));
  connect(z_integral_dt.y, z_integral_accum.u1) 
    annotation(Line(points = {{-383, -20}, {-357, -20}}, color = {0, 0, 127}));
  connect(z_integral_state.y, z_integral_accum.u2) 
    annotation(Line(points = {{-323, -50}, {-310, -50}, {-310, -30}, {-357, -30}}, color = {0, 0, 127}));
  connect(z_integral_accum.y, z_integral_state.u1) 
    annotation(Line(points = {{-323, -20}, {-310, -20}, {-310, -50}, {-357, -50}}, color = {0, 0, 127}));
  connect(z_integral_accum.y, z_i.u) 
    annotation(Line(points = {{-323, -20}, {-300, -20}, {-300, -20}, {-337, -20}}, color = {0, 0, 127}));
  connect(z_error.y, z_derivative_input.u) 
    annotation(Line(points = {{-480, -33}, {-480, -52}}, color = {0, 0, 127}));
  connect(z_derivative.y, z_d.u) 
    annotation(Line(points = {{-137, -65}, {-303, -65}}, color = {0, 0, 127}));
  connect(z_p.y, z_pi.u1) 
    annotation(Line(points = {{-383, 25}, {-320, 25}, {-320, 0}, {-257, 0}}, color = {0, 0, 127}));
  connect(z_i.y, z_pi.u2) 
    annotation(Line(points = {{-303, -20}, {-280, -20}, {-280, 0}, {-257, 0}}, color = {0, 0, 127}));
  connect(z_pi.y, thrust_command.u1) 
    annotation(Line(points = {{-223, 0}, {-200, 0}, {-200, -15}, {-177, -15}}, color = {0, 0, 127}));
  connect(z_d.y, thrust_command.u2) 
    annotation(Line(points = {{-303, -65}, {-240, -65}, {-240, -15}, {-177, -15}}, color = {0, 0, 127}));
  connect(pitch_derivative_input.y, pitch_derivative_difference.u) 
    annotation(Line(points = {{-403, -158}, {-377, -158}}, color = {0, 0, 127}));
  connect(pitch_derivative_difference.y, pitch_derivative_slope.u) 
    annotation(Line(points = {{-343, -158}, {-317, -158}}, color = {0, 0, 127}));
  connect(pitch_derivative_slope.y, pitch_derivative_filtered_increment.u) 
    annotation(Line(points = {{-283, -158}, {-270, -158}, {-270, -188}, {-257, -188}}, color = {0, 0, 127}));
  connect(pitch_derivative_filtered_increment.y, pitch_derivative_state_sum.u2) 
    annotation(Line(points = {{-223, -188}, {-180, -188}, {-180, -158}, {-137, -158}}, color = {0, 0, 127}));
  connect(pitch_derivative_previous_state.y, pitch_derivative_state_decay.u) 
    annotation(Line(points = {{-223, -128}, {-197, -128}}, color = {0, 0, 127}));
  connect(pitch_derivative_state_decay.y, pitch_derivative_state_sum.u1) 
    annotation(Line(points = {{-163, -128}, {-150, -128}, {-150, -158}, {-137, -158}}, color = {0, 0, 127}));
  connect(pitch_derivative_state_sum.y, pitch_derivative_previous_state.u1) 
    annotation(Line(points = {{-137, -158}, {-180, -158}, {-180, -128}, {-223, -128}}, color = {0, 0, 127}));
  connect(pitch_derivative_state_sum.y, pitch_derivative.u) 
    annotation(Line(points = {{-103, -158}, {-77, -158}}, color = {0, 0, 127}));
  connect(pitch_error.y, pitch_derivative_input.u) 
    annotation(Line(points = {{-420, -143}, {-420, -145}}, color = {0, 0, 127}));
  connect(pitch_derivative.y, pitch_d.u) 
    annotation(Line(points = {{-77, -158}, {-243, -158}}, color = {0, 0, 127}));
  connect(pitch_p.y, pitch_pd.u1) 
    annotation(Line(points = {{-323, -102}, {-260, -102}, {-260, -130}, {-197, -130}}, color = {0, 0, 127}));
  connect(pitch_d.y, pitch_pd.u2) 
    annotation(Line(points = {{-243, -158}, {-220, -158}, {-220, -130}, {-197, -130}}, color = {0, 0, 127}));
  connect(pitch_error.y, pitch_p.u) 
    annotation(Line(points = {{-403, -130}, {-380, -130}, {-380, -102}, {-357, -102}}, color = {0, 0, 127}));
  connect(pitch_pd.y, pitch_limit.u) 
    annotation(Line(points = {{-163, -130}, {-117, -130}}, color = {0, 0, 127}));
  connect(pitch_limit.y, pitch_mix.u) 
    annotation(Line(points = {{-83, -130}, {-37, -130}}, color = {0, 0, 127}));
  connect(pitch_ref_limit.y, pitch_error.u1) 
    annotation(Line(points = {{-80, 247}, {-80, 65}, {-420, 65}, {-420, -117}}, color = {0, 0, 127}));
  connect(pitch_mea, pitch_error.u2) 
    annotation(Line(points = {{-543, -146}, {-490, -146}, {-490, -130}, {-437, -130}}, color = {0, 0, 127}));
  connect(roll_mea, roll_mea_sign.u) 
    annotation(Line(points = {{-560, -101}, {-560, -169}, {-500, -169}, {-500, -237}}, color = {0, 0, 127}));
  connect(roll_derivative_input.y, roll_derivative_difference.u) 
    annotation(Line(points = {{-403, -278}, {-377, -278}}, color = {0, 0, 127}));
  connect(roll_derivative_difference.y, roll_derivative_slope.u) 
    annotation(Line(points = {{-343, -278}, {-317, -278}}, color = {0, 0, 127}));
  connect(roll_derivative_slope.y, roll_derivative_filtered_increment.u) 
    annotation(Line(points = {{-283, -278}, {-270, -278}, {-270, -308}, {-257, -308}}, color = {0, 0, 127}));
  connect(roll_derivative_filtered_increment.y, roll_derivative_state_sum.u2) 
    annotation(Line(points = {{-223, -308}, {-180, -308}, {-180, -278}, {-137, -278}}, color = {0, 0, 127}));
  connect(roll_derivative_previous_state.y, roll_derivative_state_decay.u) 
    annotation(Line(points = {{-223, -248}, {-197, -248}}, color = {0, 0, 127}));
  connect(roll_derivative_state_decay.y, roll_derivative_state_sum.u1) 
    annotation(Line(points = {{-163, -248}, {-150, -248}, {-150, -278}, {-137, -278}}, color = {0, 0, 127}));
  connect(roll_derivative_state_sum.y, roll_derivative_previous_state.u1) 
    annotation(Line(points = {{-137, -278}, {-180, -278}, {-180, -248}, {-223, -248}}, color = {0, 0, 127}));
  connect(roll_derivative_state_sum.y, roll_derivative.u) 
    annotation(Line(points = {{-103, -278}, {-77, -278}}, color = {0, 0, 127}));
  connect(roll_error.y, roll_derivative_input.u) 
    annotation(Line(points = {{-420, -263}, {-420, -265}}, color = {0, 0, 127}));
  connect(roll_derivative.y, roll_d.u) 
    annotation(Line(points = {{-77, -278}, {-243, -278}}, color = {0, 0, 127}));
  connect(roll_p.y, roll_pd.u1) 
    annotation(Line(points = {{-323, -222}, {-260, -222}, {-260, -250}, {-197, -250}}, color = {0, 0, 127}));
  connect(roll_d.y, roll_pd.u2) 
    annotation(Line(points = {{-243, -278}, {-220, -278}, {-220, -250}, {-197, -250}}, color = {0, 0, 127}));
  connect(roll_error.y, roll_p.u) 
    annotation(Line(points = {{-403, -250}, {-380, -250}, {-380, -222}, {-357, -222}}, color = {0, 0, 127}));
  connect(roll_pd.y, roll_limit.u) 
    annotation(Line(points = {{-163, -250}, {-117, -250}}, color = {0, 0, 127}));
  connect(roll_limit.y, roll_mix.u) 
    annotation(Line(points = {{-83, -250}, {-37, -250}}, color = {0, 0, 127}));
  connect(roll_ref_limit.y, roll_error.u1) 
    annotation(Line(points = {{-80, 107}, {-80, -65}, {-420, -65}, {-420, -237}}, color = {0, 0, 127}));
  connect(roll_mea_sign.y, roll_error.u2) 
    annotation(Line(points = {{-483, -250}, {-437, -250}}, color = {0, 0, 127}));
  connect(yaw_error.y, yaw_p.u) 
    annotation(Line(points = {{-403, -370}, {-380, -370}, {-380, -342}, {-357, -342}}, color = {0, 0, 127}));
  connect(yaw_p.y, yaw_limit.u) 
    annotation(Line(points = {{-323, -342}, {-220, -342}, {-220, -370}, {-117, -370}}, color = {0, 0, 127}));
  connect(yaw_limit.y, yaw_mix.u) 
    annotation(Line(points = {{-83, -370}, {-37, -370}}, color = {0, 0, 127}));
  connect(yaw_reference.y, yaw_error.u1) 
    annotation(Line(points = {{-463, -370}, {-437, -370}}, color = {0, 0, 127}));
  connect(yaw_mea, yaw_error.u2) 
    annotation(Line(points = {{-560, -217}, {-560, -287}, {-420, -287}, {-420, -357}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_1_yaw_gain.u) 
    annotation(Line(points = {{-20, -357}, {-20, -77.5}, {55, -77.5}, {55, 202}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_1_pitch_gain.u) 
    annotation(Line(points = {{-20, -117}, {-20, 25}, {55, 25}, {55, 167}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_1_roll_gain.u) 
    annotation(Line(points = {{-20, -237}, {-20, -52.5}, {55, -52.5}, {55, 132}}, color = {0, 0, 127}));
  connect(mixer_1_yaw_gain.y, mixer_1_first.u1) 
    annotation(Line(points = {{72, 215}, {90, 215}, {90, 198}, {108, 198}}, color = {0, 0, 127}));
  connect(mixer_1_pitch_gain.y, mixer_1_first.u2) 
    annotation(Line(points = {{72, 180}, {90, 180}, {90, 198}, {108, 198}}, color = {0, 0, 127}));
  connect(mixer_1_first.y, mixer_1.u1) 
    annotation(Line(points = {{142, 198}, {155, 198}, {155, 180}, {168, 180}}, color = {0, 0, 127}));
  connect(mixer_1_roll_gain.y, mixer_1.u2) 
    annotation(Line(points = {{72, 145}, {120, 145}, {120, 180}, {168, 180}}, color = {0, 0, 127}));
  connect(mixer_1.y, rotor_1_sum.u1) 
    annotation(Line(points = {{202, 180}, {238, 180}}, color = {0, 0, 127}));
  connect(thrust_command.y, rotor_1_sum.u2) 
    annotation(Line(points = {{-143, -15}, {47.5, -15}, {47.5, 180}, {238, 180}}, color = {0, 0, 127}));
  connect(rotor_1_sum.y, rotor_1_sign.u) 
    annotation(Line(points = {{272, 180}, {318, 180}}, color = {0, 0, 127}));
  connect(rotor_1_sign.y, y) 
    annotation(Line(points = {{352, 180}, {413, 180}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_2_yaw_gain.u) 
    annotation(Line(points = {{-20, -357}, {-20, -137.5}, {55, -137.5}, {55, 82}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_2_pitch_gain.u) 
    annotation(Line(points = {{-20, -117}, {-20, -35}, {55, -35}, {55, 47}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_2_roll_gain.u) 
    annotation(Line(points = {{-20, -237}, {-20, -112.5}, {55, -112.5}, {55, 12}}, color = {0, 0, 127}));
  connect(mixer_2_yaw_gain.y, mixer_2_first.u1) 
    annotation(Line(points = {{72, 95}, {90, 95}, {90, 78}, {108, 78}}, color = {0, 0, 127}));
  connect(mixer_2_pitch_gain.y, mixer_2_first.u2) 
    annotation(Line(points = {{72, 60}, {90, 60}, {90, 78}, {108, 78}}, color = {0, 0, 127}));
  connect(mixer_2_first.y, mixer_2.u1) 
    annotation(Line(points = {{142, 78}, {155, 78}, {155, 60}, {168, 60}}, color = {0, 0, 127}));
  connect(mixer_2_roll_gain.y, mixer_2.u2) 
    annotation(Line(points = {{72, 25}, {120, 25}, {120, 60}, {168, 60}}, color = {0, 0, 127}));
  connect(mixer_2.y, rotor_2_sum.u1) 
    annotation(Line(points = {{202, 60}, {238, 60}}, color = {0, 0, 127}));
  connect(thrust_command.y, rotor_2_sum.u2) 
    annotation(Line(points = {{-143, -15}, {47.5, -15}, {47.5, 60}, {238, 60}}, color = {0, 0, 127}));
  connect(rotor_2_sum.y, rotor_2_sign.u) 
    annotation(Line(points = {{272, 60}, {318, 60}}, color = {0, 0, 127}));
  connect(rotor_2_sign.y, y1) 
    annotation(Line(points = {{352, 60}, {413, 60}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_3_yaw_gain.u) 
    annotation(Line(points = {{-20, -357}, {-20, -197.5}, {55, -197.5}, {55, -38}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_3_pitch_gain.u) 
    annotation(Line(points = {{-3, -130}, {17.5, -130}, {17.5, -60}, {38, -60}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_3_roll_gain.u) 
    annotation(Line(points = {{-20, -237}, {-20, -172.5}, {55, -172.5}, {55, -108}}, color = {0, 0, 127}));
  connect(mixer_3_yaw_gain.y, mixer_3_first.u1) 
    annotation(Line(points = {{72, -25}, {90, -25}, {90, -42}, {108, -42}}, color = {0, 0, 127}));
  connect(mixer_3_pitch_gain.y, mixer_3_first.u2) 
    annotation(Line(points = {{72, -60}, {90, -60}, {90, -42}, {108, -42}}, color = {0, 0, 127}));
  connect(mixer_3_first.y, mixer_3.u1) 
    annotation(Line(points = {{142, -42}, {155, -42}, {155, -60}, {168, -60}}, color = {0, 0, 127}));
  connect(mixer_3_roll_gain.y, mixer_3.u2) 
    annotation(Line(points = {{72, -95}, {120, -95}, {120, -60}, {168, -60}}, color = {0, 0, 127}));
  connect(mixer_3.y, rotor_3_sum.u1) 
    annotation(Line(points = {{202, -60}, {238, -60}}, color = {0, 0, 127}));
  connect(thrust_command.y, rotor_3_sum.u2) 
    annotation(Line(points = {{-143, -15}, {47.5, -15}, {47.5, -60}, {238, -60}}, color = {0, 0, 127}));
  connect(rotor_3_sum.y, rotor_3_sign.u) 
    annotation(Line(points = {{272, -60}, {318, -60}}, color = {0, 0, 127}));
  connect(rotor_3_sign.y, y2) 
    annotation(Line(points = {{352, -60}, {413, -60}}, color = {0, 0, 127}));
  connect(yaw_mix.y, mixer_4_yaw_gain.u) 
    annotation(Line(points = {{-20, -357}, {-20, -257.5}, {55, -257.5}, {55, -158}}, color = {0, 0, 127}));
  connect(pitch_mix.y, mixer_4_pitch_gain.u) 
    annotation(Line(points = {{-3, -130}, {17.5, -130}, {17.5, -180}, {38, -180}}, color = {0, 0, 127}));
  connect(roll_mix.y, mixer_4_roll_gain.u) 
    annotation(Line(points = {{-3, -250}, {17.5, -250}, {17.5, -215}, {38, -215}}, color = {0, 0, 127}));
  connect(mixer_4_yaw_gain.y, mixer_4_first.u1) 
    annotation(Line(points = {{72, -145}, {90, -145}, {90, -162}, {108, -162}}, color = {0, 0, 127}));
  connect(mixer_4_pitch_gain.y, mixer_4_first.u2) 
    annotation(Line(points = {{72, -180}, {90, -180}, {90, -162}, {108, -162}}, color = {0, 0, 127}));
  connect(mixer_4_first.y, mixer_4.u1) 
    annotation(Line(points = {{142, -162}, {155, -162}, {155, -180}, {168, -180}}, color = {0, 0, 127}));
  connect(mixer_4_roll_gain.y, mixer_4.u2) 
    annotation(Line(points = {{72, -215}, {120, -215}, {120, -180}, {168, -180}}, color = {0, 0, 127}));
  connect(mixer_4.y, rotor_4_sum.u1) 
    annotation(Line(points = {{202, -180}, {238, -180}}, color = {0, 0, 127}));
  connect(thrust_command.y, rotor_4_sum.u2) 
    annotation(Line(points = {{-143, -15}, {47.5, -15}, {47.5, -180}, {238, -180}}, color = {0, 0, 127}));
  connect(rotor_4_sum.y, rotor_4_sign.u) 
    annotation(Line(points = {{272, -180}, {318, -180}}, color = {0, 0, 127}));
  connect(rotor_4_sign.y, y3) 
    annotation(Line(points = {{352, -180}, {413, -180}}, color = {0, 0, 127}));
end OfficialPidGraphicalCore;