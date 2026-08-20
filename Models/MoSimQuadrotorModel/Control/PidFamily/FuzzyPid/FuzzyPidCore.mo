within MoSimQuadrotorModel.Control.PidFamily.FuzzyPid;
model FuzzyPidCore "Exact fixed-input graphical MIL for fuzzy_pid"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(command, outer_command, unsaturated_command, integral, scheduled_gain)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  SysplorerEmbeddedCoder.Sources.Constant setpoint_source(k=0.5) 
    annotation (Placement(transformation(origin = {-620, 120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant measurement_source(k=0.1) 
    annotation (Placement(transformation(origin = {-620, 60}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant inner_measurement_source(k=0.05) 
    annotation (Placement(transformation(origin = {-620, 0}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant feedforward_source(k=0.3) 
    annotation (Placement(transformation(origin = {-620, -80}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant schedule_source(k=0.5) 
    annotation (Placement(transformation(origin = {-620, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_error_source(k=0.4) 
    annotation (Placement(transformation(origin = {-620, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant neural_residual_source(k=0.1) 
    annotation (Placement(transformation(origin = {-620, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant zero_source(k=0.0) 
    annotation (Placement(transformation(origin = {900, 40}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Sources.Constant one_source(k=1.0) 
    annotation (Placement(transformation(origin = {900, 420}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-450, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant pid_gain_bias(k=1.0) 
    annotation (Placement(transformation(origin = {-450, 420}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_schedule_term(k=0.0) 
    annotation (Placement(transformation(origin = {-480, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction pid_fuzzy_tanh(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {-480, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_fuzzy_term(k=0.3) 
    annotation (Placement(transformation(origin = {-330, 300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_neural_limit(upLimit=0.0,lowLimit=-0.0) 
    annotation (Placement(transformation(origin = {-480, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_neural_term(k=0.0) 
    annotation (Placement(transformation(origin = {-330, 240}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_a(inputs="++") 
    annotation (Placement(transformation(origin = {-300, 360}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_b(inputs="++") 
    annotation (Placement(transformation(origin = {-150, 360}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_gain_sum_c(inputs="++") 
    annotation (Placement(transformation(origin = {0, 360}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_gain_limit(upLimit=4.0,lowLimit=0.25) 
    annotation (Placement(transformation(origin = {150, 360}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product pid_gain_error(inputs="**") 
    annotation (Placement(transformation(origin = {-250, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_p_term(k=1.2) 
    annotation (Placement(transformation(origin = {-100, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_previous_error(initCond=0.4) 
    annotation (Placement(transformation(origin = {-350, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_error_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {-220, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_derivative_rate(k=100.0) 
    annotation (Placement(transformation(origin = {-90, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_filter_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {180, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_filter_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {60, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_filter_alpha(k=0.16666666666666666) 
    annotation (Placement(transformation(origin = {210, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_filter_update(inputs="++") 
    annotation (Placement(transformation(origin = {330, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product pid_gain_derivative(inputs="**") 
    annotation (Placement(transformation(origin = {430, -20}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_d_term(k=0.1) 
    annotation (Placement(transformation(origin = {530, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay pid_integral_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {-300, -320}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product pid_integral_drive(inputs="**") 
    annotation (Placement(transformation(origin = {-250, -220}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_integral_dt(k=0.01) 
    annotation (Placement(transformation(origin = {-100, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_integral_pre(inputs="++") 
    annotation (Placement(transformation(origin = {50, -220}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_integral_pre_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {200, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_i_term(k=0.8) 
    annotation (Placement(transformation(origin = {330, -220}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_feedforward(k=0.0) 
    annotation (Placement(transformation(origin = {460, 180}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_pi_sum(inputs="++") 
    annotation (Placement(transformation(origin = {430, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_pid_sum(inputs="++") 
    annotation (Placement(transformation(origin = {580, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_unsaturated(inputs="++") 
    annotation (Placement(transformation(origin = {700, 100}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_command_limit(upLimit=1.0,lowLimit=-1.0) 
    annotation (Placement(transformation(origin = {820, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_saturation_error(inputs="+-") 
    annotation (Placement(transformation(origin = {820, -120}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain pid_aw_correction(k=0.004) 
    annotation (Placement(transformation(origin = {930, -120}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum pid_integral_final(inputs="++") 
    annotation (Placement(transformation(origin = {700, -300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation pid_integral_final_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {830, -300}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport command 
    annotation (Placement(transformation(origin = {1100, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport outer_command 
    annotation (Placement(transformation(origin = {1100, 40}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport unsaturated_command 
    annotation (Placement(transformation(origin = {1100, -20}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport integral 
    annotation (Placement(transformation(origin = {1100, -100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain 
    annotation (Placement(transformation(origin = {1100, 360}, extent = {{-14, -11}, {14, 11}})));
equation
  connect(setpoint_source.y, pid_error.u1) 
    annotation(Line(points = {{-606, 120}, {-535, 120}, {-535, 100}, {-464, 100}}, color = {0, 0, 127}));
  connect(measurement_source.y, pid_error.u2) 
    annotation(Line(points = {{-606, 60}, {-535, 60}, {-535, 100}, {-464, 100}}, color = {0, 0, 127}));
  connect(schedule_source.y, pid_schedule_term.u) 
    annotation(Line(points = {{-606, 360}, {-494, 360}}, color = {0, 0, 127}));
  connect(fuzzy_error_source.y, pid_fuzzy_tanh.u1) 
    annotation(Line(points = {{-606, 300}, {-494, 300}}, color = {0, 0, 127}));
  connect(pid_fuzzy_tanh.y1, pid_fuzzy_term.u) 
    annotation(Line(points = {{-466, 300}, {-344, 300}}, color = {0, 0, 127}));
  connect(neural_residual_source.y, pid_neural_limit.u) 
    annotation(Line(points = {{-606, 240}, {-494, 240}}, color = {0, 0, 127}));
  connect(pid_neural_limit.y, pid_neural_term.u) 
    annotation(Line(points = {{-466, 240}, {-344, 240}}, color = {0, 0, 127}));
  connect(pid_gain_bias.y, pid_gain_sum_a.u1) 
    annotation(Line(points = {{-436, 420}, {-375, 420}, {-375, 360}, {-314, 360}}, color = {0, 0, 127}));
  connect(pid_schedule_term.y, pid_gain_sum_a.u2) 
    annotation(Line(points = {{-466, 360}, {-314, 360}}, color = {0, 0, 127}));
  connect(pid_gain_sum_a.y, pid_gain_sum_b.u1) 
    annotation(Line(points = {{-286, 360}, {-164, 360}}, color = {0, 0, 127}));
  connect(pid_fuzzy_term.y, pid_gain_sum_b.u2) 
    annotation(Line(points = {{-316, 300}, {-240, 300}, {-240, 360}, {-164, 360}}, color = {0, 0, 127}));
  connect(pid_gain_sum_b.y, pid_gain_sum_c.u1) 
    annotation(Line(points = {{-136, 360}, {-14, 360}}, color = {0, 0, 127}));
  connect(pid_neural_term.y, pid_gain_sum_c.u2) 
    annotation(Line(points = {{-316, 240}, {-165, 240}, {-165, 360}, {-14, 360}}, color = {0, 0, 127}));
  connect(pid_gain_sum_c.y, pid_gain_limit.u) 
    annotation(Line(points = {{14, 360}, {136, 360}}, color = {0, 0, 127}));
  connect(pid_gain_limit.y, pid_gain_error.u1) 
    annotation(Line(points = {{136, 360}, {-50, 360}, {-50, 100}, {-236, 100}}, color = {0, 0, 127}));
  connect(pid_error.y, pid_gain_error.u2) 
    annotation(Line(points = {{-436, 100}, {-264, 100}}, color = {0, 0, 127}));
  connect(pid_gain_error.y, pid_p_term.u) 
    annotation(Line(points = {{-236, 100}, {-114, 100}}, color = {0, 0, 127}));
  connect(pid_error.y, pid_previous_error.u1) 
    annotation(Line(points = {{-450, 89}, {-450, 40}, {-350, 40}, {-350, -9}}, color = {0, 0, 127}));
  connect(pid_error.y, pid_error_delta.u1) 
    annotation(Line(points = {{-436, 100}, {-335, 100}, {-335, -20}, {-234, -20}}, color = {0, 0, 127}));
  connect(pid_previous_error.y, pid_error_delta.u2) 
    annotation(Line(points = {{-336, -20}, {-234, -20}}, color = {0, 0, 127}));
  connect(pid_error_delta.y, pid_derivative_rate.u) 
    annotation(Line(points = {{-206, -20}, {-104, -20}}, color = {0, 0, 127}));
  connect(pid_derivative_rate.y, pid_filter_delta.u1) 
    annotation(Line(points = {{-76, -20}, {46, -20}}, color = {0, 0, 127}));
  connect(pid_filter_state.y, pid_filter_delta.u2) 
    annotation(Line(points = {{166, -110}, {120, -110}, {120, -20}, {74, -20}}, color = {0, 0, 127}));
  connect(pid_filter_delta.y, pid_filter_alpha.u) 
    annotation(Line(points = {{74, -20}, {196, -20}}, color = {0, 0, 127}));
  connect(pid_filter_state.y, pid_filter_update.u1) 
    annotation(Line(points = {{194, -110}, {255, -110}, {255, -20}, {316, -20}}, color = {0, 0, 127}));
  connect(pid_filter_alpha.y, pid_filter_update.u2) 
    annotation(Line(points = {{224, -20}, {316, -20}}, color = {0, 0, 127}));
  connect(pid_filter_update.y, pid_filter_state.u1) 
    annotation(Line(points = {{316, -20}, {255, -20}, {255, -110}, {194, -110}}, color = {0, 0, 127}));
  connect(pid_gain_limit.y, pid_gain_derivative.u1) 
    annotation(Line(points = {{150, 349}, {150, 170}, {430, 170}, {430, -9}}, color = {0, 0, 127}));
  connect(pid_filter_update.y, pid_gain_derivative.u2) 
    annotation(Line(points = {{344, -20}, {416, -20}}, color = {0, 0, 127}));
  connect(pid_gain_derivative.y, pid_d_term.u) 
    annotation(Line(points = {{444, -20}, {516, -20}}, color = {0, 0, 127}));
  connect(pid_gain_limit.y, pid_integral_drive.u1) 
    annotation(Line(points = {{150, 349}, {150, 70}, {-250, 70}, {-250, -209}}, color = {0, 0, 127}));
  connect(pid_error.y, pid_integral_drive.u2) 
    annotation(Line(points = {{-450, 89}, {-450, -60}, {-250, -60}, {-250, -209}}, color = {0, 0, 127}));
  connect(pid_integral_drive.y, pid_integral_dt.u) 
    annotation(Line(points = {{-236, -220}, {-114, -220}}, color = {0, 0, 127}));
  connect(pid_integral_state.y, pid_integral_pre.u1) 
    annotation(Line(points = {{-286, -320}, {-125, -320}, {-125, -220}, {36, -220}}, color = {0, 0, 127}));
  connect(pid_integral_dt.y, pid_integral_pre.u2) 
    annotation(Line(points = {{-86, -220}, {36, -220}}, color = {0, 0, 127}));
  connect(pid_integral_pre.y, pid_integral_pre_limit.u) 
    annotation(Line(points = {{64, -220}, {186, -220}}, color = {0, 0, 127}));
  connect(pid_integral_pre_limit.y, pid_i_term.u) 
    annotation(Line(points = {{214, -220}, {316, -220}}, color = {0, 0, 127}));
  connect(feedforward_source.y, pid_feedforward.u) 
    annotation(Line(points = {{-606, -80}, {-80, -80}, {-80, 180}, {446, 180}}, color = {0, 0, 127}));
  connect(pid_p_term.y, pid_pi_sum.u1) 
    annotation(Line(points = {{-86, 100}, {416, 100}}, color = {0, 0, 127}));
  connect(pid_i_term.y, pid_pi_sum.u2) 
    annotation(Line(points = {{330, -209}, {330, -60}, {430, -60}, {430, 89}}, color = {0, 0, 127}));
  connect(pid_pi_sum.y, pid_pid_sum.u1) 
    annotation(Line(points = {{444, 100}, {566, 100}}, color = {0, 0, 127}));
  connect(pid_d_term.y, pid_pid_sum.u2) 
    annotation(Line(points = {{530, -9}, {530, 40}, {580, 40}, {580, 89}}, color = {0, 0, 127}));
  connect(pid_pid_sum.y, pid_unsaturated.u1) 
    annotation(Line(points = {{594, 100}, {686, 100}}, color = {0, 0, 127}));
  connect(pid_feedforward.y, pid_unsaturated.u2) 
    annotation(Line(points = {{474, 180}, {580, 180}, {580, 100}, {686, 100}}, color = {0, 0, 127}));
  connect(pid_unsaturated.y, pid_command_limit.u) 
    annotation(Line(points = {{714, 100}, {806, 100}}, color = {0, 0, 127}));
  connect(pid_command_limit.y, pid_saturation_error.u1) 
    annotation(Line(points = {{820, 89}, {820, -109}}, color = {0, 0, 127}));
  connect(pid_unsaturated.y, pid_saturation_error.u2) 
    annotation(Line(points = {{700, 89}, {700, -10}, {820, -10}, {820, -109}}, color = {0, 0, 127}));
  connect(pid_saturation_error.y, pid_aw_correction.u) 
    annotation(Line(points = {{834, -120}, {916, -120}}, color = {0, 0, 127}));
  connect(pid_integral_pre_limit.y, pid_integral_final.u1) 
    annotation(Line(points = {{214, -220}, {450, -220}, {450, -300}, {686, -300}}, color = {0, 0, 127}));
  connect(pid_aw_correction.y, pid_integral_final.u2) 
    annotation(Line(points = {{916, -120}, {815, -120}, {815, -300}, {714, -300}}, color = {0, 0, 127}));
  connect(pid_integral_final.y, pid_integral_final_limit.u) 
    annotation(Line(points = {{714, -300}, {816, -300}}, color = {0, 0, 127}));
  connect(pid_integral_final_limit.y, pid_integral_state.u1) 
    annotation(Line(points = {{816, -300}, {265, -300}, {265, -320}, {-286, -320}}, color = {0, 0, 127}));
  connect(pid_command_limit.y, command) 
    annotation(Line(points = {{834, 100}, {1086, 100}}, color = {0, 0, 127}));
  connect(zero_source.y, outer_command) 
    annotation(Line(points = {{914, 40}, {1086, 40}}, color = {0, 0, 127}));
  connect(pid_unsaturated.y, unsaturated_command) 
    annotation(Line(points = {{714, 100}, {900, 100}, {900, -20}, {1086, -20}}, color = {0, 0, 127}));
  connect(pid_integral_final_limit.y, integral) 
    annotation(Line(points = {{844, -300}, {965, -300}, {965, -100}, {1086, -100}}, color = {0, 0, 127}));
  connect(pid_gain_limit.y, scheduled_gain) 
    annotation(Line(points = {{164, 360}, {1086, 360}}, color = {0, 0, 127}));

end FuzzyPidCore;
