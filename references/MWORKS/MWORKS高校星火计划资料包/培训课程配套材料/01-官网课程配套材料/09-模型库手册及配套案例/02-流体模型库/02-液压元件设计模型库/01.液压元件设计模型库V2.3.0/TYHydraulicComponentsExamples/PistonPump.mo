model PistonPump "斜盘式轴向柱塞泵-5柱塞"
  annotation (Diagram(coordinateSystem(extent = {{-200.0, -200.0}, {200.0, 200.0}}, 
    grid = {2.0, 2.0})), 
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
      grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
      lineColor = {0, 0, 255}, 
      fillColor = {0, 0, 255}, 
      fillPattern = FillPattern.Solid, 
      points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 0, 255}, 
      thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
      points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
      color = {0, 0, 255}, 
      thickness = 5.0)}), 
    experiment(Algorithm = Dassl, NumberOfIntervals = 500, StartTime = 0, StopTime = 0.1, Tolerance = 0.0001), 
    Documentation(link = "modelica://TYHydraulicComponents/Resources/HTML/PistonPump.html"),Protection(access=Access.nonPackageDuplicate),__MWORKS(ResultViewerManager(resultViewers={
ResultViewer(name="仿真结果", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=7, left_title_type=2, left_title="流量[l/min]", bottom_title_type=2, bottom_title="时间/s", fix_time_range_value=0, zoom_x=(0, 0.1), zoom_y_l=(-10, 70)), 
Plot(y=["volume_1.port_A.q"], colors=["4278190335"])})
})));
  Modelica.Mechanics.Rotational.Sources.Speed speed 
    annotation (Placement(transformation(origin = {153.08619221029758, 13.07014073205222}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.Constant const1(k = 400) 
    annotation (Placement(transformation(origin = {184.39781263497125, 13.33767591506527}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYHydraulicComponents.Sources.Tank tank9(
    p_load = 0, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-106.0, -182.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Sources.Tank tank10(
    p_load = 0, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-161.32300952868695, 102.84829388173168}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.PistonPump.SwashPlate swashPlate(
    diameter = 0.1) annotation (Placement(transformation(origin = {56.0, 133.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool(
    reverse = false, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, InterfaceSwitchA = true, InterfaceSwitchB = true) annotation (Placement(transformation(origin = {16.0, 153.99999999999997}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston(
    reverse = false, 
    dr = 0, ds = 0.015, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-18.0, 153.99999999999997}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.PistonPump.ValvePlate valuePlate(
    diameter_orifice = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-72.0, 133.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volume(
    n_ports = 1, V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-23.0, 174.99999999999997}, 
      extent = {{-9.000000000000002, 9.0}, {9.000000000000002, -9.0}})));
  TYHydraulicComponents.Sources.Tank tank(
    p_load = 100000, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {21.0, 170.99999999999997}, 
      extent = {{-9.0, 9.0}, {9.0, -9.0}})));
  TYHydraulicComponents.PistonPump.SwashPlate swashPlate1(
    theta_0 = 1.25663706143592, 
    diameter = 0.1) annotation (Placement(transformation(origin = {56.0, 72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool1(reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {16.0, 91.99999999999999}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston1(
    ds = 0.015, dr = 0, 
    reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-18.0, 91.99999999999999}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.PistonPump.ValvePlate valuePlate1(
    diameter_orifice = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-72.0, 72.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volume1(
    n_ports = 1, V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-23.0, 112.99999999999994}, 
      extent = {{-9.000000000000002, 9.0}, {9.000000000000002, -9.0}})));
  TYHydraulicComponents.Sources.Tank tank1(
    p_load = 100000, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {21.0, 110.99999999999999}, 
      extent = {{-9.0, 9.0}, {9.0, -9.0}})));
  TYHydraulicComponents.PistonPump.SwashPlate swashPlate2(
    theta_0 = 2.51327412287183, 
    diameter = 0.1) annotation (Placement(transformation(origin = {56.0, 12.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool2(reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {16.0, 32.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston2(
    ds = 0.015, dr = 0, 
    reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-18.0, 32.0}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.PistonPump.ValvePlate valuePlate2(
    diameter_orifice = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-72.0, 12.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volume2(
    n_ports = 1, V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-23.0, 52.99999999999997}, 
      extent = {{-9.000000000000002, 9.0}, {9.000000000000002, -9.0}})));
  TYHydraulicComponents.Sources.Tank tank2(
    p_load = 100000, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {21.0, 48.999999999999986}, 
      extent = {{-9.0, 9.0}, {9.0, -9.0}})));
  TYHydraulicComponents.PistonPump.SwashPlate swashPlate3(
    theta_0 = 3.76991118430775, 
    diameter = 0.1) annotation (Placement(transformation(origin = {56.0, -54.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool3(reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {16.0, -34.000000000000014}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston3(
    ds = 0.015, dr = 0, 
    reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-18.0, -34.000000000000014}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.PistonPump.ValvePlate valuePlate3(
    diameter_orifice = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-72.0, -54.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volume3(
    n_ports = 1, V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-22.999999999999993, -13.000000000000028}, 
      extent = {{-9.000000000000002, 9.0}, {9.000000000000002, -9.0}})));
  TYHydraulicComponents.Sources.Tank tank3(
    p_load = 100000, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {22.03669724770642, -13.0}, 
      extent = {{-9.0, 9.0}, {9.0, -9.0}})));
  TYHydraulicComponents.PistonPump.SwashPlate swashPlate4(
    theta_0 = 5.02654824574367, 
    diameter = 0.1) annotation (Placement(transformation(origin = {56.0, -124.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.DiaphragmLeakageSealings.ViscousFrictionAndLeakage viscousFrictionAndLeakageSpool4(reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced, InterfaceSwitchA = true, InterfaceSwitchB = true) 
    annotation (Placement(transformation(origin = {16.0, -104.00000000000003}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.Pistons.FixedBodyPiston fixedBodyPiston4(
    ds = 0.015, dr = 0, 
    reverse = false, 
    redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) 
    annotation (Placement(transformation(origin = {-18.0, -104.00000000000003}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
  TYHydraulicComponents.PistonPump.ValvePlate valuePlate4(
    diameter_orifice = 0.01, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-72.0, -124.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.VolumeV volume4(
    n_ports = 1, V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-23.000000000000014, -83.00000000000003}, 
      extent = {{-9.000000000000002, 9.0}, {9.000000000000002, -9.0}})));
  TYHydraulicComponents.Sources.Tank tank4(
    p_load = 100000, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {22.03669724770642, -83.0}, 
      extent = {{-9.0, 9.0}, {9.0, -9.0}})));
  TYHydraulicComponents.Auxiliaries.Volume2ports volume_2(
    V0 = 1e-6, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-106.03010752688172, -158.00000000000003}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYHydraulicComponents.Auxiliaries.Volume2ports volume_1(
    V0 = 1e-9, redeclare model Medium = TYOilMedia.HydraulicOil.Partial.Advanced) annotation (Placement(transformation(origin = {-146.28613364926662, 141.67620445497553}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}}, 
      rotation = 90.0)));
  Modelica.Mechanics.Rotational.Components.Fixed fixed9(phi0 = 0.174532925199433) 
    annotation (Placement(transformation(origin = {54.0, 173.99999999999997}, 
      extent = {{-10.0, 10.0}, {10.0, -10.0}})));
equation
  connect(speed.w_ref, const1.y) 
    annotation (Line(origin = {121.0, -120.00000000000003}, 
      points = {{44.08619221029758, 133.07014073205224}, {52.397812634971245, 133.07014073205224}, {52.397812634971245, 133.3376759150653}}, 
      color = {0, 0, 127}));
  connect(valuePlate.rotorangle, swashPlate.angle) 
    annotation (Line(origin = {-14.0, 127.0}, 
      points = {{-49.30909090909091, 0.39999999999997726}, {60.0, 0.39999999999997726}, {60.0, -1.0000000000000284}, {60.2, -1.0000000000000284}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston.flange_b, viscousFrictionAndLeakageSpool.flange_a) 
    annotation (Line(origin = {-1.0, 154.0}, 
      points = {{-6.7829565217391, -2.842170943040401e-14}, {6.9102608695651995, -2.842170943040401e-14}}, 
      color = {0, 127, 0}));
  connect(volume.port_A, valuePlate.port_Inter) 
    annotation (Line(origin = {-49.0, 162.0}, 
      points = {{26.0, 19.299999999999983}, {-7.0, 19.299999999999983}, {-7.0, -23.00000000000003}, {-14.0, -23.00000000000003}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool.flange_b, swashPlate.flange_a) 
    annotation (Line(origin = {36.0, 144.0}, 
      points = {{-9.782956521739102, 9.999999999999972}, {10.0, 9.999999999999972}, {10.0, -9.80000000000004}}, 
      color = {0, 127, 0}));
  connect(valuePlate1.rotorangle, swashPlate1.angle) 
    annotation (Line(origin = {-14.0, 64.99999999999999}, 
      points = {{-49.30909090909091, 0.4000000000000199}, {60.0, 0.4000000000000199}, {60.0, -0.9999999999999858}, {60.2, -0.9999999999999858}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston1.flange_b, viscousFrictionAndLeakageSpool1.flange_a) 
    annotation (Line(origin = {-1.0, 91.99999999999999}, 
      points = {{-6.7829565217391, 0.0}, {6.9102608695651995, 0.0}}, 
      color = {0, 127, 0}));
  connect(volume1.port_A, valuePlate1.port_Inter) 
    annotation (Line(origin = {-49.0, 99.99999999999999}, 
      points = {{26.0, 19.299999999999955}, {-7.0, 19.299999999999955}, {-7.0, -22.999999999999986}, {-14.0, -22.999999999999986}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool1.flange_b, swashPlate1.flange_a) 
    annotation (Line(origin = {36.0, 81.99999999999999}, 
      points = {{-9.782956521739102, 10.0}, {0.0, 10.0}, {0.0, -9.799999999999983}, {10.0, -9.799999999999983}}, 
      color = {0, 127, 0}));
  connect(valuePlate2.rotorangle, swashPlate2.angle) 
    annotation (Line(origin = {-14.0, 4.999999999999986}, 
      points = {{-49.30909090909091, 0.4000000000000137}, {60.0, 0.4000000000000137}, {60.0, -0.9999999999999858}, {60.2, -0.9999999999999858}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston2.flange_b, viscousFrictionAndLeakageSpool2.flange_a) 
    annotation (Line(origin = {-1.0, 31.999999999999986}, 
      points = {{-6.7829565217391, 1.4210854715202004e-14}, {6.9102608695651995, 1.4210854715202004e-14}}, 
      color = {0, 127, 0}));
  connect(volume2.port_A, valuePlate2.port_Inter) 
    annotation (Line(origin = {-49.0, 39.999999999999986}, 
      points = {{26.0, 19.299999999999983}, {-7.0, 19.299999999999983}, {-7.0, -22.999999999999986}, {-14.0, -22.999999999999986}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool2.flange_b, swashPlate2.flange_a) 
    annotation (Line(origin = {36.0, 21.999999999999986}, 
      points = {{-9.782956521739102, 10.000000000000014}, {0.0, 10.000000000000014}, {0.0, -9.799999999999986}, {10.0, -9.799999999999986}}, 
      color = {0, 127, 0}));
  connect(valuePlate3.rotorangle, swashPlate3.angle) 
    annotation (Line(origin = {-14.0, -61.000000000000014}, 
      points = {{-49.30909090909091, 0.3999999999999986}, {60.0, 0.3999999999999986}, {60.0, -1.0}, {60.2, -1.0}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston3.flange_b, viscousFrictionAndLeakageSpool3.flange_a) 
    annotation (Line(origin = {-1.0, -34.000000000000014}, 
      points = {{-6.7829565217391, 0.0}, {6.9102608695651995, 0.0}}, 
      color = {0, 127, 0}));
  connect(volume3.port_A, valuePlate3.port_Inter) 
    annotation (Line(origin = {-49.0, -26.000000000000014}, 
      points = {{26.000000000000007, 19.299999999999986}, {-9.0, 19.299999999999986}, {-9.0, -23.0}, {-14.0, -23.0}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool3.flange_b, swashPlate3.flange_a) 
    annotation (Line(origin = {36.0, -44.000000000000014}, 
      points = {{-9.782956521739102, 10.0}, {0.0, 10.0}, {0.0, -9.799999999999997}, {10.0, -9.799999999999997}}, 
      color = {0, 127, 0}));
  connect(valuePlate4.rotorangle, swashPlate4.angle) 
    annotation (Line(origin = {-14.0, -131.00000000000003}, 
      points = {{-49.30909090909091, 0.4000000000000057}, {60.0, 0.4000000000000057}, {60.0, -1.0}, {60.2, -1.0}}, 
      color = {0, 0, 127}));
  connect(fixedBodyPiston4.flange_b, viscousFrictionAndLeakageSpool4.flange_a) 
    annotation (Line(origin = {-1.0, -104.00000000000003}, 
      points = {{-6.7829565217391, 0.0}, {6.9102608695651995, 0.0}}, 
      color = {0, 127, 0}));
  connect(volume4.port_A, valuePlate4.port_Inter) 
    annotation (Line(origin = {-49.0, -96.00000000000003}, 
      points = {{25.999999999999986, 19.299999999999997}, {-7.0, 19.299999999999997}, {-7.0, -23.0}, {-14.0, -23.0}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool4.flange_b, swashPlate4.flange_a) 
    annotation (Line(origin = {36.0, -114.00000000000003}, 
      points = {{-9.782956521739102, 10.0}, {-3.0, 10.0}, {-3.0, -9.799999999999997}, {10.0, -9.799999999999997}}, 
      color = {0, 127, 0}));
  connect(swashPlate4.swash_a, swashPlate3.swash_b) 
    annotation (Line(origin = {54.0, -89.00000000000001}, 
      points = {{0.0, -26.000000000000014}, {0.0, 26.0}}));
  connect(swashPlate3.swash_a, swashPlate2.swash_b) 
    annotation (Line(origin = {54.0, -21.000000000000014}, 
      points = {{0.0, -24.0}, {0.0, 24.000000000000014}}));
  connect(swashPlate2.swash_a, swashPlate1.swash_b) 
    annotation (Line(origin = {55.0, 41.999999999999986}, 
      points = {{-1.0, -20.999999999999986}, {-1.0, 21.000000000000014}}));
  connect(swashPlate1.swash_a, swashPlate.swash_b) 
    annotation (Line(origin = {55.0, 102.99999999999999}, 
      points = {{-1.0, -21.999999999999986}, {-1.0, 21.999999999999986}}));
  connect(fixed9.flange, swashPlate.swash_a) 
    annotation (Line(origin = {54.0, 159.0}, 
      points = {{0.0, 14.999999999999972}, {0.0, -16.00000000000003}}));
  connect(tank.port_A, viscousFrictionAndLeakageSpool.port_B) 
    annotation (Line(origin = {21.0, 171.0}, 
      points = {{-0.02709677419354861, -0.05032258064520079}, {-0.016478263573873164, -7.104637582570575}}, 
      color = {0, 127, 255}));
  connect(tank1.port_A, viscousFrictionAndLeakageSpool1.port_B) 
    annotation (Line(origin = {21.0, 109.0}, 
      points = {{-0.02709677419354861, 1.9496774193548276}, {-0.016478263573873164, -7.104637582570561}}, 
      color = {0, 127, 255}));
  connect(tank2.port_A, viscousFrictionAndLeakageSpool2.port_B) 
    annotation (Line(origin = {21.0, 49.0}, 
      points = {{-0.02709677419354861, -0.050322580645172366}, {-0.016478263573873164, -7.104637582570547}}, 
      color = {0, 127, 255}));
  connect(tank3.port_A, viscousFrictionAndLeakageSpool3.port_B) 
    annotation (Line(origin = {22.0, -17.0}, 
      points = {{0.009600473512872298, 3.94967741935484}, {0.009600473512872298, -7.104637582570561}, {-1.0164782635738732, -7.104637582570561}}, 
      color = {0, 127, 255}));
  connect(tank4.port_A, viscousFrictionAndLeakageSpool4.port_B) 
    annotation (Line(origin = {22.0, -87.0}, 
      points = {{0.009600473512872298, 3.949677419354842}, {0.009600473512872298, -7.104637582570575}, {-1.0164782635738732, -7.104637582570575}}, 
      color = {0, 127, 255}));
  connect(volume3.portV_B[1], fixedBodyPiston3.portV_A) 
    annotation (Line(origin = {-23.0, -21.0}, 
      points = {{7.105427357601002e-15, 1.6999999999999709}, {0.0, -3.000000000000014}}, 
      color = {0, 127, 255}));
  connect(volume4.portV_B[1], fixedBodyPiston4.portV_A) 
    annotation (Line(origin = {-23.0, -91.0}, 
      points = {{-1.4210854715202004e-14, 1.6999999999999744}, {0.0, -3.0000000000000284}}, 
      color = {0, 127, 255}));
  connect(volume2.portV_B[1], fixedBodyPiston2.portV_A) 
    annotation (Line(origin = {-23.0, 45.0}, 
      points = {{0.0, 1.6999999999999744}, {0.0, -3.0}}, 
      color = {0, 127, 255}));
  connect(volume1.portV_B[1], fixedBodyPiston1.portV_A) 
    annotation (Line(origin = {-23.0, 105.0}, 
      points = {{0.0, 1.699999999999946}, {0.0, -3.000000000000014}}, 
      color = {0, 127, 255}));
  connect(volume.portV_B[1], fixedBodyPiston.portV_A) 
    annotation (Line(origin = {-23.0, 167.0}, 
      points = {{0.0, 1.6999999999999602}, {0.0, -3.0000000000000284}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool1.port_A, volume1.port_A) 
    annotation (Line(origin = {-6.0, 110.0}, 
      points = {{17.036904600550965, -8.089279889807173}, {17.036904600550965, 9.0}, {-17.0, 9.0}, {-17.0, 9.29999999999994}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool2.port_A, volume2.port_A) 
    annotation (Line(origin = {-6.0, 50.0}, 
      points = {{17.036904600550965, -8.089279889807159}, {17.036904600550965, 9.0}, {-17.0, 9.0}, {-17.0, 9.299999999999969}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool3.port_A, volume3.port_A) 
    annotation (Line(origin = {-6.0, -16.0}, 
      points = {{17.036904600550965, -8.089279889807173}, {17.036904600550965, 9.0}, {-16.999999999999993, 9.0}, {-16.999999999999993, 9.299999999999972}}, 
      color = {0, 127, 255}));
  connect(swashPlate.rotor, speed.flange) 
    annotation (Line(origin = {126.0, 66.0}, 
      points = {{-60.0, 67.99999999999997}, {-1.0, 67.99999999999997}, {-1.0, -54.0}, {17.086192210297583, -54.0}, {17.086192210297583, -52.929859267947776}}, 
      color = {0, 0, 0}));
  connect(swashPlate1.rotor, speed.flange) 
    annotation (Line(origin = {126.0, 35.0}, 
      points = {{-60.0, 37.0}, {-1.0, 37.0}, {-1.0, -23.0}, {17.086192210297583, -23.0}, {17.086192210297583, -21.92985926794778}}, 
      color = {0, 0, 0}));
  connect(swashPlate2.rotor, speed.flange) 
    annotation (Line(origin = {126.0, 5.0}, 
      points = {{-60.0, 7.0}, {17.086192210297583, 7.0}, {17.086192210297583, 8.07014073205222}}, 
      color = {0, 0, 0}));
  connect(swashPlate3.rotor, speed.flange) 
    annotation (Line(origin = {126.0, -28.0}, 
      points = {{-60.0, -26.000000000000014}, {-1.0, -26.000000000000014}, {-1.0, 40.0}, {17.086192210297583, 40.0}, {17.086192210297583, 41.070140732052224}}, 
      color = {0, 0, 0}));
  connect(swashPlate4.rotor, speed.flange) 
    annotation (Line(origin = {126.0, -63.0}, 
      points = {{-60.0, -61.00000000000003}, {-1.0, -61.00000000000003}, {-1.0, 75.0}, {17.086192210297583, 75.0}, {17.086192210297583, 76.07014073205222}}, 
      color = {0, 0, 0}));
  connect(valuePlate1.port_Out, valuePlate.port_Out) 
    annotation (Line(origin = {-99.0, 111.0}, 
      points = {{18.0, -32.0}, {-18.0, -32.0}, {-18.0, 31.0}, {18.0, 31.0}, {18.0, 29.99999999999997}}, 
      color = {0, 127, 255}));
  connect(valuePlate2.port_Out, valuePlate.port_Out) 
    annotation (Line(origin = {-99.0, 81.0}, 
      points = {{18.0, -62.0}, {-18.0, -62.0}, {-18.0, 61.0}, {18.0, 61.0}, {18.0, 59.99999999999997}}, 
      color = {0, 127, 255}));
  connect(valuePlate3.port_Out, valuePlate.port_Out) 
    annotation (Line(origin = {-99.0, 48.0}, 
      points = {{18.0, -95.00000000000001}, {-18.0, -95.00000000000001}, {-18.0, 94.0}, {18.0, 94.0}, {18.0, 92.99999999999997}}, 
      color = {0, 127, 255}));
  connect(valuePlate4.port_Out, valuePlate.port_Out) 
    annotation (Line(origin = {-99.0, 13.0}, 
      points = {{18.0, -130.00000000000003}, {-18.0, -130.00000000000003}, {-18.0, 129.0}, {18.0, 129.0}, {18.0, 127.99999999999997}}, 
      color = {0, 127, 255}));
  connect(volume_2.port_B, valuePlate4.port_In) 
    annotation (Line(origin = {-93.0, -141.0}, 
      points = {{-13.030107526881721, -10.000000000000028}, {-13.030107526881721, 19.99999999999997}, {12.0, 19.99999999999997}}, 
      color = {0, 127, 255}));
  connect(valuePlate3.port_In, valuePlate4.port_In) 
    annotation (Line(origin = {-93.0, -86.0}, 
      points = {{12.0, 34.999999999999986}, {-13.0, 34.999999999999986}, {-13.0, -35.00000000000003}, {12.0, -35.00000000000003}}, 
      color = {0, 127, 255}));
  connect(valuePlate2.port_In, valuePlate4.port_In) 
    annotation (Line(origin = {-93.0, -53.0}, 
      points = {{12.0, 68.0}, {-13.0, 68.0}, {-13.0, -68.00000000000003}, {12.0, -68.00000000000003}}, 
      color = {0, 127, 255}));
  connect(valuePlate1.port_In, valuePlate4.port_In) 
    annotation (Line(origin = {-93.0, -23.0}, 
      points = {{12.0, 98.0}, {-13.0, 98.0}, {-13.0, -98.00000000000003}, {12.0, -98.00000000000003}}, 
      color = {0, 127, 255}));
  connect(valuePlate.port_In, valuePlate4.port_In) 
    annotation (Line(origin = {-93.0, 8.0}, 
      points = {{12.0, 128.99999999999997}, {-13.0, 128.99999999999997}, {-13.0, -129.00000000000003}, {12.0, -129.00000000000003}}, 
      color = {0, 127, 255}));
  connect(volume_1.port_A, valuePlate.port_Out) 
    annotation (Line(origin = {-116.0, 142.0}, 
      points = {{-23.286133649266617, -0.32379554502446695}, {35.0, -0.32379554502446695}, {35.0, -1.0000000000000284}}, 
      color = {0, 127, 255}));
  connect(volume_1.port_B, tank10.port_A) 
    annotation (Line(origin = {-94.0, 170.0}, 
      points = {{-59.28613364926662, -28.323795545024467}, {-67.0, -28.323795545024467}, {-67.0, -67.0957921397737}, {-67.35311705556867, -67.0957921397737}}, 
      color = {0, 127, 255}));
  connect(volume_2.port_A, tank9.port_A) 
    annotation (Line(origin = {-60.0, -186.0}, 
      points = {{-46.03010752688172, 20.99999999999997}, {-46.03010752688172, 4.05591397849463}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool.port_A, volume.port_A) 
    annotation (Line(origin = {-6.0, 173.0}, 
      points = {{17.036904600550965, -9.089279889807187}, {17.036904600550965, 8.299999999999983}, {-17.0, 8.299999999999983}}, 
      color = {0, 127, 255}));
  connect(viscousFrictionAndLeakageSpool4.port_A, volume4.port_A) 
    annotation (Line(origin = {-6.0, -85.0}, 
      points = {{17.036904600550965, -9.089279889807187}, {17.036904600550965, 8.299999999999969}, {-17.000000000000014, 8.299999999999969}}, 
      color = {0, 127, 255}));
end PistonPump;