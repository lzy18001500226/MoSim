within MoSimQuadrotorModel.Control.Implementations.PidFamily;
model MoSim_PID_CASCADE_PID_GRAPHICAL_MIL "Exact fixed-input graphical MIL for cascade_pid"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(command, outer_command, unsaturated_command, integral, scheduled_gain)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Sources.Constant setpoint_source(k=0.5) 
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
  SysplorerEmbeddedCoder.MathOperation.Sum outer_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-330, 280}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant outer_gain_bias(k=1.0) 
    annotation (Placement(transformation(origin = {-330, 470}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_schedule_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, 520}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction outer_fuzzy_tanh(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {-330, 565}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_fuzzy_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, 565}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_neural_limit(upLimit=0.0,lowLimit=-0.0) 
    annotation (Placement(transformation(origin = {-330, 615}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_neural_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, 615}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_gain_sum_a(inputs="++") 
    annotation (Placement(transformation(origin = {-175, 505}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_gain_sum_b(inputs="++") 
    annotation (Placement(transformation(origin = {-100, 535}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_gain_sum_c(inputs="++") 
    annotation (Placement(transformation(origin = {-25, 565}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_gain_limit(upLimit=4.0,lowLimit=0.25) 
    annotation (Placement(transformation(origin = {50, 565}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product outer_gain_error(inputs="**") 
    annotation (Placement(transformation(origin = {-245, 325}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_p_term(k=1.2) 
    annotation (Placement(transformation(origin = {-165, 325}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay outer_previous_error(initCond=0.4) 
    annotation (Placement(transformation(origin = {-255, 215}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_error_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {-175, 235}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_derivative_rate(k=100.0) 
    annotation (Placement(transformation(origin = {-100, 235}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay outer_filter_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {-100, 155}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_filter_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {-25, 215}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_filter_alpha(k=0.16666666666666666) 
    annotation (Placement(transformation(origin = {50, 215}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_filter_update(inputs="++") 
    annotation (Placement(transformation(origin = {125, 190}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product outer_gain_derivative(inputs="**") 
    annotation (Placement(transformation(origin = {200, 210}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_d_term(k=0.1) 
    annotation (Placement(transformation(origin = {275, 210}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay outer_integral_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {-245, 90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product outer_integral_drive(inputs="**") 
    annotation (Placement(transformation(origin = {-165, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_integral_dt(k=0.01) 
    annotation (Placement(transformation(origin = {-90, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_integral_pre(inputs="++") 
    annotation (Placement(transformation(origin = {-15, 90}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_pre_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {60, 90}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_i_term(k=0.8) 
    annotation (Placement(transformation(origin = {135, 100}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_feedforward(k=0.0) 
    annotation (Placement(transformation(origin = {135, 385}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_pi_sum(inputs="++") 
    annotation (Placement(transformation(origin = {215, 305}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_pid_sum(inputs="++") 
    annotation (Placement(transformation(origin = {290, 280}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_unsaturated(inputs="++") 
    annotation (Placement(transformation(origin = {365, 310}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_command_limit(upLimit=1.0,lowLimit=-1.0) 
    annotation (Placement(transformation(origin = {440, 310}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_saturation_error(inputs="+-") 
    annotation (Placement(transformation(origin = {365, 160}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain outer_aw_correction(k=0.004) 
    annotation (Placement(transformation(origin = {440, 160}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum outer_integral_final(inputs="++") 
    annotation (Placement(transformation(origin = {515, 115}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_final_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {590, 115}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_error(inputs="+-") 
    annotation (Placement(transformation(origin = {-330, -300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Sources.Constant inner_gain_bias(k=1.0) 
    annotation (Placement(transformation(origin = {-330, -110}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_schedule_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, -60}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction inner_fuzzy_tanh(operatorType=SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh) 
    annotation (Placement(transformation(origin = {-330, -15}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_fuzzy_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, -15}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_neural_limit(upLimit=0.0,lowLimit=-0.0) 
    annotation (Placement(transformation(origin = {-330, 35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_neural_term(k=0.0) 
    annotation (Placement(transformation(origin = {-255, 35}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_gain_sum_a(inputs="++") 
    annotation (Placement(transformation(origin = {-175, -75}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_gain_sum_b(inputs="++") 
    annotation (Placement(transformation(origin = {-100, -45}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_gain_sum_c(inputs="++") 
    annotation (Placement(transformation(origin = {-25, -15}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_gain_limit(upLimit=4.0,lowLimit=0.25) 
    annotation (Placement(transformation(origin = {50, -15}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product inner_gain_error(inputs="**") 
    annotation (Placement(transformation(origin = {-245, -255}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_p_term(k=1.5) 
    annotation (Placement(transformation(origin = {-165, -255}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay inner_previous_error(initCond=0.4332) 
    annotation (Placement(transformation(origin = {-255, -365}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_error_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {-175, -345}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_derivative_rate(k=100.0) 
    annotation (Placement(transformation(origin = {-100, -345}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay inner_filter_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {-100, -425}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_filter_delta(inputs="+-") 
    annotation (Placement(transformation(origin = {-25, -365}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_filter_alpha(k=0.25) 
    annotation (Placement(transformation(origin = {50, -365}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_filter_update(inputs="++") 
    annotation (Placement(transformation(origin = {125, -390}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Product inner_gain_derivative(inputs="**") 
    annotation (Placement(transformation(origin = {200, -370}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_d_term(k=0.05) 
    annotation (Placement(transformation(origin = {275, -370}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.Discrete.UnitDelay inner_integral_state(initCond=0.0) 
    annotation (Placement(transformation(origin = {-245, -490}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Product inner_integral_drive(inputs="**") 
    annotation (Placement(transformation(origin = {-165, -465}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_integral_dt(k=0.01) 
    annotation (Placement(transformation(origin = {-90, -465}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_integral_pre(inputs="++") 
    annotation (Placement(transformation(origin = {-15, -490}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_integral_pre_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {60, -490}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_i_term(k=0.4) 
    annotation (Placement(transformation(origin = {135, -480}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_feedforward(k=0.0) 
    annotation (Placement(transformation(origin = {135, -195}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_pi_sum(inputs="++") 
    annotation (Placement(transformation(origin = {215, -275}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_pid_sum(inputs="++") 
    annotation (Placement(transformation(origin = {290, -300}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_unsaturated(inputs="++") 
    annotation (Placement(transformation(origin = {365, -270}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_command_limit(upLimit=1.0,lowLimit=-1.0) 
    annotation (Placement(transformation(origin = {440, -270}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_saturation_error(inputs="+-") 
    annotation (Placement(transformation(origin = {365, -420}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.MathOperation.Gain inner_aw_correction(k=0.004) 
    annotation (Placement(transformation(origin = {440, -420}, extent = {{-14, -11}, {14, 11}})));
  SysplorerEmbeddedCoder.MathOperation.Sum inner_integral_final(inputs="++") 
    annotation (Placement(transformation(origin = {515, -465}, extent = {{-14, -11}, {14, 11}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
  SysplorerEmbeddedCoder.Discontinuities.Saturation inner_integral_final_limit(upLimit=0.5,lowLimit=-0.5) 
    annotation (Placement(transformation(origin = {590, -465}, extent = {{-14, -11}, {14, 11}})));
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
  connect(setpoint_source.y, outer_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(measurement_source.y, outer_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(schedule_source.y, outer_schedule_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_error_source.y, outer_fuzzy_tanh.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_fuzzy_tanh.y1, outer_fuzzy_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_residual_source.y, outer_neural_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_neural_limit.y, outer_neural_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_bias.y, outer_gain_sum_a.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_schedule_term.y, outer_gain_sum_a.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_sum_a.y, outer_gain_sum_b.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_fuzzy_term.y, outer_gain_sum_b.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_sum_b.y, outer_gain_sum_c.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_neural_term.y, outer_gain_sum_c.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_sum_c.y, outer_gain_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_limit.y, outer_gain_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error.y, outer_gain_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_error.y, outer_p_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error.y, outer_previous_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error.y, outer_error_delta.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_previous_error.y, outer_error_delta.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error_delta.y, outer_derivative_rate.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_derivative_rate.y, outer_filter_delta.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_state.y, outer_filter_delta.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_delta.y, outer_filter_alpha.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_state.y, outer_filter_update.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_alpha.y, outer_filter_update.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_update.y, outer_filter_state.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_limit.y, outer_gain_derivative.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_filter_update.y, outer_gain_derivative.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_derivative.y, outer_d_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_gain_limit.y, outer_integral_drive.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_error.y, outer_integral_drive.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_drive.y, outer_integral_dt.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_state.y, outer_integral_pre.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_dt.y, outer_integral_pre.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_pre.y, outer_integral_pre_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_pre_limit.y, outer_i_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward_source.y, outer_feedforward.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_p_term.y, outer_pi_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_i_term.y, outer_pi_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_pi_sum.y, outer_pid_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_d_term.y, outer_pid_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_pid_sum.y, outer_unsaturated.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_feedforward.y, outer_unsaturated.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_unsaturated.y, outer_command_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_command_limit.y, outer_saturation_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_unsaturated.y, outer_saturation_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_saturation_error.y, outer_aw_correction.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_pre_limit.y, outer_integral_final.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_aw_correction.y, outer_integral_final.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_final.y, outer_integral_final_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_integral_final_limit.y, outer_integral_state.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_command_limit.y, inner_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_measurement_source.y, inner_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(schedule_source.y, inner_schedule_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_error_source.y, inner_fuzzy_tanh.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_fuzzy_tanh.y1, inner_fuzzy_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_residual_source.y, inner_neural_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_neural_limit.y, inner_neural_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_bias.y, inner_gain_sum_a.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_schedule_term.y, inner_gain_sum_a.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_sum_a.y, inner_gain_sum_b.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_fuzzy_term.y, inner_gain_sum_b.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_sum_b.y, inner_gain_sum_c.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_neural_term.y, inner_gain_sum_c.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_sum_c.y, inner_gain_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_limit.y, inner_gain_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error.y, inner_gain_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_error.y, inner_p_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error.y, inner_previous_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error.y, inner_error_delta.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_previous_error.y, inner_error_delta.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error_delta.y, inner_derivative_rate.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_derivative_rate.y, inner_filter_delta.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_state.y, inner_filter_delta.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_delta.y, inner_filter_alpha.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_state.y, inner_filter_update.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_alpha.y, inner_filter_update.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_update.y, inner_filter_state.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_limit.y, inner_gain_derivative.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_filter_update.y, inner_gain_derivative.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_derivative.y, inner_d_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_gain_limit.y, inner_integral_drive.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_error.y, inner_integral_drive.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_drive.y, inner_integral_dt.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_state.y, inner_integral_pre.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_dt.y, inner_integral_pre.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_pre.y, inner_integral_pre_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_pre_limit.y, inner_i_term.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward_source.y, inner_feedforward.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_p_term.y, inner_pi_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_i_term.y, inner_pi_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_pi_sum.y, inner_pid_sum.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_d_term.y, inner_pid_sum.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_pid_sum.y, inner_unsaturated.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_feedforward.y, inner_unsaturated.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_unsaturated.y, inner_command_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_command_limit.y, inner_saturation_error.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_unsaturated.y, inner_saturation_error.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_saturation_error.y, inner_aw_correction.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_pre_limit.y, inner_integral_final.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_aw_correction.y, inner_integral_final.u2) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_final.y, inner_integral_final_limit.u) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_final_limit.y, inner_integral_state.u1) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_command_limit.y, command) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(outer_command_limit.y, outer_command) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_command_limit.y, unsaturated_command) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_integral_final_limit.y, integral) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(one_source.y, scheduled_gain) 
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  end MoSim_PID_CASCADE_PID_GRAPHICAL_MIL;