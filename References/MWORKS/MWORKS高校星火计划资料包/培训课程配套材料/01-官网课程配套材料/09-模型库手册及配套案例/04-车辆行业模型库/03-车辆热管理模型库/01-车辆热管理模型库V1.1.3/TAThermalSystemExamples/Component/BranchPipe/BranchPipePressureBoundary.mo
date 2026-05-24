model BranchPipePressureBoundary "多通管道"
  parameter Modelica.Units.SI.Pressure p_in1 = 4.999999999999999e5 "输入1压力";
  parameter Modelica.Units.SI.Pressure p_in2 = 4.999999999999999e5 "输入2压力";
  TAThermalSystem.BranchPipe.TJunction junctionJoint1 annotation(Placement(transformation(origin = {1.9090909090909136, -3.0374331550802083},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  annotation(Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    grid = {2.0, 2.0}), graphics = {Bitmap(origin = {0.0, 0.0},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    fileName = "modelica://TAThermalSystem/Resource/Icons/Example.svg")}),
    Protection(access = Access.nonPackageDuplicate),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/BranchPipePressureBoundary.html"), __MWORKS(ResultViewerManager(resultViewers = {
    ResultViewer(name = "1", executeTrigger = executeTrigger.SimulationFinished, commands = {
    CreatePlot(id = 1, x_display_unit = "s", legend_layout = 7, left_title = "[kg/s]", fix_time_range_value = 0, zoom_x = (0,1), zoom_y_l = (-15,15)),
    Plot(y = ["mdot_a", "mdot_b", "mdot_c"], colors = ["4278190335", "4294901760", "4278222848"])})
    })));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT(p = p_in1) 
    annotation(Placement(transformation(origin = {-63.999999999999986, -3.0374331550802083},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 180.0)));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = p_in2) 
    annotation(Placement(transformation(origin = {1.9128683121263261, -56.00000000000001},
    extent = {{-10.0, -10.0}, {10.0, 10.0}},
    rotation = 270.0)));
  TAThermalSystem.Sources.Coolant.Coolant_tank gW50_tank(p = 100000) 
    annotation(Placement(transformation(origin = {67.81818181818181, -3.0374331550802083},
    extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Units.SI.MassFlowRate mdot_a;
  Modelica.Units.SI.MassFlowRate mdot_b;
  Modelica.Units.SI.MassFlowRate mdot_c;
equation
  mdot_a = -junctionJoint1.summarySimple.mdot_a;
  mdot_b = -junctionJoint1.summarySimple.mdot_b;
  mdot_c = -junctionJoint1.summarySimple.mdot_c;
  connect(Coolant_pT.port_a, junctionJoint1.a) 
    annotation(Line(origin = {-32.905313506055485, -1.0374331550802072},
    points = {{-21.0, -2.0}, {25.0, -2.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(junctionJoint1.b, Coolant_pT1.port_a) 
    annotation(Line(origin = {2.09468649394451, -21.03743315508021},
    points = {{0.0, 8.0}, {0.0, -25.0}},
    color = {0, 170, 255},
    thickness = 1.0));
  connect(junctionJoint1.c, gW50_tank.port_a) 
    annotation(Line(origin = {42.094686493944515, -6.0374331550802065},
    points = {{-30.0, 3.0}, {26.0, 3.0}},
    color = {0, 170, 255},
    thickness = 1.0));
end BranchPipePressureBoundary;