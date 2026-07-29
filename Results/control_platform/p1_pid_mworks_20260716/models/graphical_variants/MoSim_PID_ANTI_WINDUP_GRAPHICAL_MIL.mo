model MoSim_PID_ANTI_WINDUP_GRAPHICAL_MIL "Exact fixed-input graphical MIL for anti_windup"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(command, outer_command, unsaturated_command, integral, scheduled_gain)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Sources.Constant setpoint_source(k=2.0)
    annotation (Placement(transformation(origin = {-510, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant measurement_source(k=0.1)
    annotation (Placement(transformation(origin = {-510, 225}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant inner_measurement_source(k=0.05)
    annotation (Placement(transformation(origin = {-510, 150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant feedforward_source(k=0.3)
    annotation (Placement(transformation(origin = {-510, 75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant schedule_source(k=0.5)
    annotation (Placement(transformation(origin = {-510, 0}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_error_source(k=0.4)
    annotation (Placement(transformation(origin = {-510, -75}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant neural_residual_source(k=0.1)
    annotation (Placement(transformation(origin = {-510, -150}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant zero_source(k=0.0)
    annotation (Placement(transformation(origin = {520, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant one_source(k=1.0)
    annotation (Placement(transformation(origin = {520, 250}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_error(inputs="+-")
    annotation (Placement(transformation(origin = {-330, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant pid_gain_bias(k=1.0)
    annotation (Placement(transformation(origin = {-330, 190}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_schedule_term(k=0.0)
    annotation (Placement(transformation(origin = {-255, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction pid_fuzzy_tanh(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh)
    annotation (Placement(transformation(origin = {-330, 285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_fuzzy_term(k=0.0)
    annotation (Placement(transformation(origin = {-255, 285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_neural_limit(upLimit=0.0,lowLimit=-0.0)
    annotation (Placement(transformation(origin = {-330, 335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_neural_term(k=0.0)
    annotation (Placement(transformation(origin = {-255, 335}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_a(inputs="++")
    annotation (Placement(transformation(origin = {-175, 225}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_b(inputs="++")
    annotation (Placement(transformation(origin = {-100, 255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_c(inputs="++")
    annotation (Placement(transformation(origin = {-25, 285}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_gain_limit(upLimit=4.0,lowLimit=0.25)
    annotation (Placement(transformation(origin = {50, 285}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product pid_gain_error(inputs="**")
    annotation (Placement(transformation(origin = {-245, 45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_p_term(k=1.2)
    annotation (Placement(transformation(origin = {-165, 45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_previous_error(initCond=1.9)
    annotation (Placement(transformation(origin = {-255, -65}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_error_delta(inputs="+-")
    annotation (Placement(transformation(origin = {-175, -45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_derivative_rate(k=100.0)
    annotation (Placement(transformation(origin = {-100, -45}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_filter_state(initCond=0.0)
    annotation (Placement(transformation(origin = {-100, -125}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_filter_delta(inputs="+-")
    annotation (Placement(transformation(origin = {-25, -65}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_filter_alpha(k=0.16666666666666666)
    annotation (Placement(transformation(origin = {50, -65}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_filter_update(inputs="++")
    annotation (Placement(transformation(origin = {125, -90}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product pid_gain_derivative(inputs="**")
    annotation (Placement(transformation(origin = {200, -70}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_d_term(k=0.1)
    annotation (Placement(transformation(origin = {275, -70}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_integral_state(initCond=0.0)
    annotation (Placement(transformation(origin = {-245, -190}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product pid_integral_drive(inputs="**")
    annotation (Placement(transformation(origin = {-165, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_integral_dt(k=0.01)
    annotation (Placement(transformation(origin = {-90, -165}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_integral_pre(inputs="++")
    annotation (Placement(transformation(origin = {-15, -190}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_integral_pre_limit(upLimit=0.5,lowLimit=-0.5)
    annotation (Placement(transformation(origin = {60, -190}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_i_term(k=0.8)
    annotation (Placement(transformation(origin = {135, -180}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_feedforward(k=0.0)
    annotation (Placement(transformation(origin = {135, 105}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_pi_sum(inputs="++")
    annotation (Placement(transformation(origin = {215, 25}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_pid_sum(inputs="++")
    annotation (Placement(transformation(origin = {290, 0}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_unsaturated(inputs="++")
    annotation (Placement(transformation(origin = {365, 30}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_command_limit(upLimit=1.0,lowLimit=-1.0)
    annotation (Placement(transformation(origin = {440, 30}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_saturation_error(inputs="+-")
    annotation (Placement(transformation(origin = {365, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_aw_correction(k=0.01)
    annotation (Placement(transformation(origin = {440, -120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_integral_final(inputs="++")
    annotation (Placement(transformation(origin = {515, -165}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_integral_final_limit(upLimit=0.5,lowLimit=-0.5)
    annotation (Placement(transformation(origin = {590, -165}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport command
    annotation (Placement(transformation(origin = {700, 130}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport outer_command
    annotation (Placement(transformation(origin = {700, 60}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport unsaturated_command
    annotation (Placement(transformation(origin = {700, -10}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport integral
    annotation (Placement(transformation(origin = {700, -80}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain
    annotation (Placement(transformation(origin = {700, -150}, extent = {{-14, -11}, {14, 11}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(setpoint_source.y, pid_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(measurement_source.y, pid_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(schedule_source.y, pid_schedule_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_error_source.y, pid_fuzzy_tanh.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_fuzzy_tanh.y1, pid_fuzzy_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_residual_source.y, pid_neural_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_neural_limit.y, pid_neural_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_bias.y, pid_gain_sum_a.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_schedule_term.y, pid_gain_sum_a.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_sum_a.y, pid_gain_sum_b.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_fuzzy_term.y, pid_gain_sum_b.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_sum_b.y, pid_gain_sum_c.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_neural_term.y, pid_gain_sum_c.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_sum_c.y, pid_gain_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_limit.y, pid_gain_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_error.y, pid_gain_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_error.y, pid_p_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_error.y, pid_previous_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_error.y, pid_error_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_previous_error.y, pid_error_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_error_delta.y, pid_derivative_rate.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_derivative_rate.y, pid_filter_delta.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_state.y, pid_filter_delta.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_delta.y, pid_filter_alpha.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_state.y, pid_filter_update.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_alpha.y, pid_filter_update.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_update.y, pid_filter_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_limit.y, pid_gain_derivative.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_filter_update.y, pid_gain_derivative.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_derivative.y, pid_d_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_limit.y, pid_integral_drive.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_error.y, pid_integral_drive.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_drive.y, pid_integral_dt.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_state.y, pid_integral_pre.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_dt.y, pid_integral_pre.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_pre.y, pid_integral_pre_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_pre_limit.y, pid_i_term.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward_source.y, pid_feedforward.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_p_term.y, pid_pi_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_i_term.y, pid_pi_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_pi_sum.y, pid_pid_sum.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_d_term.y, pid_pid_sum.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_pid_sum.y, pid_unsaturated.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_feedforward.y, pid_unsaturated.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_unsaturated.y, pid_command_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_command_limit.y, pid_saturation_error.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_unsaturated.y, pid_saturation_error.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_saturation_error.y, pid_aw_correction.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_pre_limit.y, pid_integral_final.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_aw_correction.y, pid_integral_final.u2)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_final.y, pid_integral_final_limit.u)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_final_limit.y, pid_integral_state.u1)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_command_limit.y, command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(zero_source.y, outer_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_unsaturated.y, unsaturated_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_integral_final_limit.y, integral)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(pid_gain_limit.y, scheduled_gain)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_PID_ANTI_WINDUP_GRAPHICAL_MIL;