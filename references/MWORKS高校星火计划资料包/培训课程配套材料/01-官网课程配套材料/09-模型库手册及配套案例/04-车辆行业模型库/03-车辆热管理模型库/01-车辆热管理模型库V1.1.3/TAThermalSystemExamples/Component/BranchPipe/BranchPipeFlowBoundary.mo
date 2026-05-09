model BranchPipeFlowBoundary "多通管道"
  parameter Modelica.Units.SI.MassFlowRate m_flow1 = 0.3 "输入流量1";
  parameter Modelica.Units.SI.MassFlowRate m_flow2 = 0.3 "输入流量2";
  TAThermalSystem.BranchPipe.TJunction junctionJoint(
    fromDp = false, dpModuleA(dp(displayUnit = "Pa", start = 1)), coolingCV(p0 = 7.999999999999999e5)) annotation (Placement(transformation(origin = {-4.440892098500626e-16, 2.0},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access=Access.nonPackageDuplicate),
    Documentation(link="modelica://TAThermalSystem/Resource/Doc/BranchPipeFlowBoundary.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[bar]", fix_time_range_value=0, zoom_x=(0, 1), zoom_y_l=(4.5e-05, 8.5e-05)),
Plot(y=["pa", "pc", "pb"], colors=["4278190335", "4294901760", "4278222848"])})
})));
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT(mflow = m_flow1,
    T_source = 293.15) 
    annotation (Placement(transformation(origin = {-63.59358288770054, 0.9732620320855574},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_tank gW50_tank1(p = 4.999999999999999e5, T = 293.15) 
    annotation (Placement(transformation(origin = {63.59358288770052, 0.9732620320855574},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Units.SI.Pressure pa;
  Modelica.Units.SI.Pressure pb;
  Modelica.Units.SI.Pressure pc;
  TAThermalSystem.Sources.Coolant.Coolant_mT Coolant_mT1(mflow = m_flow2,
    T_source = 293.15) 
    annotation (Placement(transformation(origin = {0.21838972991821182, -53.425316211362045},
      extent = {{-10.0, -10.0}, {10.0, 10.0}},
      rotation = 90.0)));
equation
  pa = junctionJoint.summarySimple.pa / 1e5;
  pb = junctionJoint.summarySimple.pb / 1e5;
  pc = junctionJoint.summarySimple.pc / 1e5;

  connect(Coolant_mT.port_b, junctionJoint.a) 
    annotation (Line(origin = {-31.593582887700535, 1.9732620320855574},
      points = {{-22.0, -1.0}, {22.0, -1.0}, {22.0, 0.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(junctionJoint.c, gW50_tank1.port_a) 
    annotation (Line(origin = {37.406417112299465, 1.9732620320855574},
      points = {{-27.0, 0.0}, {26.0, 0.0}, {26.0, -1.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(Coolant_mT1.port_b, junctionJoint.b) 
    annotation (Line(origin = {-4.0, -28.0},
      points = {{4.0, -15.0}, {4.0, 20.0}},
      color = {0, 170, 255},
      thickness = 1.0));
end BranchPipeFlowBoundary;