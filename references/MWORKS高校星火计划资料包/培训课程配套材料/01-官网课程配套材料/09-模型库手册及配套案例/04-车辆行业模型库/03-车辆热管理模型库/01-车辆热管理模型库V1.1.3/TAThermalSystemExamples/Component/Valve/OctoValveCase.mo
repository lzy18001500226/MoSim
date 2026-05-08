model OctoValveCase "八通阀案例"
 extends TAThermalSystem.Utilities.Icons.BasicIcons.Example;

  TAThermalSystem.Valves.HydraulicValve.DirectionalValves.DV8P4W mPValve8P4W 
    annotation (Placement(transformation(origin = {0.49999999999999556, 0.5000000000000018},
      extent = {{-19.499999999999996, -19.5}, {19.500000000000004, 19.5}})));



  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT1(p = 1.2e5) 
    annotation (Placement(transformation(origin = {-48.0, 14.500000000000014},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT2(p = 1.2e5) 
    annotation (Placement(transformation(origin = {-48.0, 48.50000000000003},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));



  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT4(p = 1.2e5) 
    annotation (Placement(transformation(origin = {-48.0, -53.50000000000003},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT5(p = 1.2e5) 
    annotation (Placement(transformation(origin = {-48.0, -19.499999999999993},
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Ramp ramp(offset = -1, height = 2, startTime = 1) 
    annotation (Placement(transformation(origin = {-92.0, 0.5},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT3 
    annotation (Placement(transformation(origin = {42.0, 14.500000000000014},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT6 
    annotation (Placement(transformation(origin = {42.0, 48.50000000000003},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT7 
    annotation (Placement(transformation(origin = {42.0, -53.50000000000003},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TAThermalSystem.Sources.Coolant.Coolant_pT Coolant_pT8 
    annotation (Placement(transformation(origin = {42.0, -19.499999999999993},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));

  annotation (Protection(access=Access.nonPackageDuplicate),
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 10, Tolerance = 0.0001),
    Documentation(link = "modelica://TAThermalSystem/Resource/Doc/OctoValveCase.html"),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title="[kg/s]", fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.4, 0.4)),
Plot(y=["mPValve8P4W.mdotA", "mPValve8P4W.mdotB", "mPValve8P4W.mdotC", "mPValve8P4W.mdotD", "mPValve8P4W.mdotW", "mPValve8P4W.mdotX", "mPValve8P4W.mdotY", "mPValve8P4W.mdotZ"], colors=["4278190335", "4294901760", "4278222848", "4294902015", "4278190080", "4294951205", "4288684272", "4286589482"])})
})));
equation
  connect(Coolant_pT2.port_a, mPValve8P4W.B) 
    annotation (Line(origin = {-19.000000000000004, 39.5},
      points = {{-19.0, 9.0}, {15.0, 9.0}, {15.0, -20.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(Coolant_pT1.port_a, mPValve8P4W.A) 
    annotation (Line(origin = {-23.000000000000004, 22.500000000000004},
      points = {{-15.0, -8.0}, {-15.0, -3.0}, {9.0, -3.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(ramp.y, mPValve8P4W.spool_position) 
    annotation (Line(origin = {-40.0, 17.500000000000004},
      points = {{-41.0, -17.0}, {19.0, -17.0}},
      color = {0, 0, 127}));
  connect(Coolant_pT6.port_a, mPValve8P4W.C) 
    annotation (Line(origin = {20.0, 39.5},
      points = {{12.0, 9.0}, {-15.0, 9.0}, {-15.0, -20.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(mPValve8P4W.D, Coolant_pT3.port_a) 
    annotation (Line(origin = {22.999999999999996, 22.500000000000004},
      points = {{-8.0, -3.0}, {11.0, -3.0}, {11.0, -8.0}, {9.0, -8.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(mPValve8P4W.W, Coolant_pT5.port_a) 
    annotation (Line(origin = {-23.000000000000004, -9.499999999999996},
      points = {{9.0, -10.0}, {-15.0, -10.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(Coolant_pT4.port_a, mPValve8P4W.X) 
    annotation (Line(origin = {-19.000000000000004, -26.499999999999996},
      points = {{-19.0, -27.0}, {15.0, -27.0}, {15.0, 7.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(Coolant_pT7.port_a, mPValve8P4W.Y) 
    annotation (Line(origin = {20.0, -26.499999999999996},
      points = {{12.0, -27.0}, {-15.0, -27.0}, {-15.0, 7.0}},
      color = {0, 170, 255},
      thickness = 1.0));
  connect(Coolant_pT8.port_a, mPValve8P4W.Z) 
    annotation (Line(origin = {22.999999999999996, -9.499999999999996},
      points = {{9.0, -10.0}, {-8.0, -10.0}},
      color = {0, 170, 255},
      thickness = 1.0));
end OctoValveCase;