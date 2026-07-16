model MoSim_PID_Unified_Graphical_Fixture "Fixed-input graphical PID fixture"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",PortArrangement(Right(command, outer_command, unsaturated_command, integral_state, scheduled_gain)),modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.02,IntegratorStep=0.02,StartTime=0,StopTime=0.2,StoreEventValue=0));
  SysplorerEmbeddedCoder.Sources.Constant setpoint_source(k=0.5)
    annotation (Placement(transformation(origin = {-220, 160}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant measurement_source(k=0.1)
    annotation (Placement(transformation(origin = {-220, 122}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant inner_measurement_source(k=0.05)
    annotation (Placement(transformation(origin = {-220, 84}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant feedforward_source(k=0.3)
    annotation (Placement(transformation(origin = {-220, 46}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant schedule_source(k=0.0)
    annotation (Placement(transformation(origin = {-220, 8}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant fuzzy_error_source(k=0.0)
    annotation (Placement(transformation(origin = {-220, -30}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant neural_residual_source(k=0.0)
    annotation (Placement(transformation(origin = {-220, -68}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant cascade_mode_source(k=0.0)
    annotation (Placement(transformation(origin = {-220, -106}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Sources.Constant enable_source(k=1.0)
    annotation (Placement(transformation(origin = {-220, -144}, extent = {{-14, -12}, {14, 12}})));
  MoSim_PID_Unified_Graphical_Sysblock controller
    annotation (Placement(transformation(origin = {0, 0}, extent = {{-14, -12}, {14, 12}})),__MWORKS(SECInstance=true,PortLabels(labelType="PortName")));
  SysplorerEmbeddedCoder.Port.Outport command
    annotation (Placement(transformation(origin = {220, 120}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport outer_command
    annotation (Placement(transformation(origin = {220, 68}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport unsaturated_command
    annotation (Placement(transformation(origin = {220, 16}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport integral_state
    annotation (Placement(transformation(origin = {220, -36}, extent = {{-14, -12}, {14, 12}})));
  SysplorerEmbeddedCoder.Port.Outport scheduled_gain
    annotation (Placement(transformation(origin = {220, -88}, extent = {{-14, -12}, {14, 12}})));
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
  connect(setpoint_source.y, controller.setpoint)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(measurement_source.y, controller.measurement)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(inner_measurement_source.y, controller.inner_measurement)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(feedforward_source.y, controller.feedforward)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(schedule_source.y, controller.schedule)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(fuzzy_error_source.y, controller.fuzzy_error)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(neural_residual_source.y, controller.neural_residual)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(cascade_mode_source.y, controller.cascade_mode)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(enable_source.y, controller.enable)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(controller.command, command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(controller.outer_command, outer_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(controller.unsaturated_command, unsaturated_command)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(controller.integral_state, integral_state)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));
  connect(controller.scheduled_gain, scheduled_gain)
    annotation(Line(origin = {0.0, 0.0}, points = {{0, 0}, {0, 0}}));

end MoSim_PID_Unified_Graphical_Fixture;
