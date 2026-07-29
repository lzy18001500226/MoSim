model MoSim_PID_Unified_Graphical_Sysblock "Unified PID family graphical counterpart"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Left(setpoint, measurement, inner_measurement, feedforward, schedule, fuzzy_error, neural_residual, cascade_mode, enable), Right(command, outer_command, unsaturated_command, integral_state, scheduled_gain)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0",CodeGeneration(Config = {"code_placement":{"mode":"Compact"},"code_replacement":{"standard_c_library":"C99"},"custom_code":{"code":{"function_declare":{"head":"","item_head":"","item_tail":"","tail":""},"function_define":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_declare":{"head":"","item_head":"","item_tail":"","tail":""},"global_variable_define":{"head":"","item_head":"","item_tail":"","tail":""},"include":{"head":"","item_head":"","item_tail":"","tail":""},"macro":{"head":"","item_head":"","item_tail":"","tail":""},"type":{"head":"","item_head":"","item_tail":"","tail":""}},"code_protection":{"integer_division_by_zero":false,"overflow":false}},"data_type":{"real_as_float":false},"experiment":{"task_and_sample":{"muti_task_mode":false,"whether_to_use_prefix":false}},"hardware_platform":{"largest_atomic_size":{"floating_point":"32","integer":"32"}},"identifier":{"max_length":32,"style":{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}},"interface":{"function_name":{"initialize":"Init","step":"Step"}},"is_expand":{"is_expand":false},"optimization":{"array_loop_threshold":5,"logical_operator":"logical"}}, Sim_seting = {"sim_seting":{"output":"C:\\Users\\HP\\Desktop\\MoSim\\Results\\control_platform\\p1_pid_mworks_20260716\\generated_c"}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Port.Inport setpoint
    annotation (Placement(transformation(origin = {-310, 180}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport measurement
    annotation (Placement(transformation(origin = {-310, 130}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport inner_measurement
    annotation (Placement(transformation(origin = {-310, 80}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport feedforward
    annotation (Placement(transformation(origin = {-310, 10}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport schedule
    annotation (Placement(transformation(origin = {-310, -50}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport fuzzy_error
    annotation (Placement(transformation(origin = {-310, -110}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport neural_residual
    annotation (Placement(transformation(origin = {-310, -170}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport cascade_mode
    annotation (Placement(transformation(origin = {-310, -230}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Inport enable
    annotation (Placement(transformation(origin = {-310, -280}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport command
    annotation (Placement(transformation(origin = {350, 120}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport outer_command
    annotation (Placement(transformation(origin = {350, 55}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport unsaturated_command
    annotation (Placement(transformation(origin = {350, -10}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport integral_state
    annotation (Placement(transformation(origin = {350, -75}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain
    annotation (Placement(transformation(origin = {350, -140}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant gain_bias(k=1.0)
    annotation (Placement(transformation(origin = {-235, -215}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain schedule_gain(k=0.4)
    annotation (Placement(transformation(origin = {-235, -50}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain fuzzy_gain(k=0.3)
    annotation (Placement(transformation(origin = {-235, -110}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation neural_limit(upLimit=0.25,lowLimit=-0.25)
    annotation (Placement(transformation(origin = {-235, -170}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain neural_gain(k=0.2)
    annotation (Placement(transformation(origin = {-170, -170}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum gain_sum_schedule(inputs="++")
    annotation (Placement(transformation(origin = {-155, -70}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum gain_sum_fuzzy(inputs="++")
    annotation (Placement(transformation(origin = {-100, -95}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum gain_sum(inputs="++")
    "Gain scheduling + fuzzy + bounded neural residual" annotation (Placement(transformation(origin = {-45, -120}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation gain_limit(upLimit=4.0,lowLimit=0.25)
    annotation (Placement(transformation(origin = {-35, -100}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum error_sum(inputs="+-")
    annotation (Placement(transformation(origin = {-225, 155}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product effective_error(inputs="**")
    annotation (Placement(transformation(origin = {-155, 155}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain kp_gain(k=1.2)
    annotation (Placement(transformation(origin = {-85, 205}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ki_drive(k=1.0)
    annotation (Placement(transformation(origin = {-85, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discrete.Difference derivative
    annotation (Placement(transformation(origin = {-85, 85}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain kd_gain(k=5.0)
    annotation (Placement(transformation(origin = {-15, 85}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum integrator_drive(inputs="++")
    annotation (Placement(transformation(origin = {-15, 145}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain integral_dt(k=0.02)
    annotation (Placement(transformation(origin = {25, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum integral_update(inputs="++")
    annotation (Placement(transformation(origin = {55, 145}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation integral_limit(upLimit=0.5,lowLimit=-0.5)
    annotation (Placement(transformation(origin = {85, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay integrator(initCond=0.0)
    "Bounded discrete integral state at Ts=0.02 s" annotation (Placement(transformation(origin = {115, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain ki_gain(k=0.8)
    annotation (Placement(transformation(origin = {145, 145}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Gain feedforward_gain(k=0.5)
    annotation (Placement(transformation(origin = {-15, 10}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_sum_pi(inputs="++")
    annotation (Placement(transformation(origin = {135, 175}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_sum_pid(inputs="++")
    annotation (Placement(transformation(origin = {175, 145}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_sum(inputs="++")
    annotation (Placement(transformation(origin = {210, 115}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation output_limit(upLimit=1.0,lowLimit=-1.0)
    annotation (Placement(transformation(origin = {235, 125}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum saturation_error(inputs="+-")
    "Tracking anti-windup error: saturated - unsaturated" annotation (Placement(transformation(origin = {235, 25}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain anti_windup_gain(k=0.4)
    annotation (Placement(transformation(origin = {165, 25}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_error(inputs="+-")
    "Cascade outer-loop error" annotation (Placement(transformation(origin = {-155, 270}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_gain(k=1.2)
    annotation (Placement(transformation(origin = {-85, 270}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_limit(upLimit=1.0,lowLimit=-1.0)
    annotation (Placement(transformation(origin = {-15, 270}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_error(inputs="+-")
    "Cascade inner-loop error" annotation (Placement(transformation(origin = {55, 250}, extent = {{-14, -12}, {14, 12}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_gain(k=1.5)
    annotation (Placement(transformation(origin = {125, 250}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_limit(upLimit=1.0,lowLimit=-1.0)
    annotation (Placement(transformation(origin = {190, 250}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch cascade_switch(threshold=0.5)
    "Select cascade or single-loop PID" annotation (Placement(transformation(origin = {270, 200}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant zero_source(k=0.0)
    annotation (Placement(transformation(origin = {235, -45}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.SignalRouting.Switch enable_switch(threshold=0.5)
    annotation (Placement(transformation(origin = {305, 120}, extent = {{-14, -12}, {14, 12}})));
  equation
  connect(schedule, schedule_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_error, fuzzy_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_residual, neural_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_limit.y, neural_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_bias.y, gain_sum_schedule.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(schedule_gain.y, gain_sum_schedule.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_sum_schedule.y, gain_sum_fuzzy.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_gain.y, gain_sum_fuzzy.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_sum_fuzzy.y, gain_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_gain.y, gain_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_sum.y, gain_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_limit.y, scheduled_gain)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(setpoint, error_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(measurement, error_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(error_sum.y, effective_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(gain_limit.y, effective_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(effective_error.y, kp_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(effective_error.y, ki_drive.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(error_sum.y, derivative.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(derivative.y, kd_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ki_drive.y, integrator_drive.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(anti_windup_gain.y, integrator_drive.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integrator_drive.y, integral_dt.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integral_dt.y, integral_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integrator.y, integral_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integral_update.y, integral_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integral_limit.y, integrator.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integrator.y, ki_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward, feedforward_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(kp_gain.y, pid_sum_pi.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(ki_gain.y, pid_sum_pi.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_sum_pi.y, pid_sum_pid.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(kd_gain.y, pid_sum_pid.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_sum_pid.y, pid_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward_gain.y, pid_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_sum.y, output_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(output_limit.y, saturation_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_sum.y, saturation_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(saturation_error.y, anti_windup_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_sum.y, unsaturated_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(integrator.y, integral_state)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(setpoint, outer_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(measurement, outer_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error.y, outer_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain.y, outer_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_limit.y, inner_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_measurement, inner_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error.y, inner_gain.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain.y, inner_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_limit.y, outer_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_limit.y, cascade_switch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(cascade_mode, cascade_switch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(output_limit.y, cascade_switch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(cascade_switch.y, enable_switch.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable, enable_switch.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero_source.y, enable_switch.u3)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_switch.y, command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  end MoSim_PID_Unified_Graphical_Sysblock;