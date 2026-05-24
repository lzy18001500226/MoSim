model ChainDriveWithGuideSprockert "带有张紧轮的链条传动系统"

  inner Modelica.Mechanics.MultiBody.World world 
    annotation(Placement(transformation(origin = {-78, 80}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Sprocket sprocket(phi0_a = 4.87927736346039, phi0_b = 1.5707963267949, rhol = 0.1, d = 1000, Dr = 0.05, numberOfTeeth = 30) annotation(Placement(transformation(origin = {-66, 42.0648}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Sprocket sprocket1(phi0_a = 1.5707963267949, phi0_b = -1.73768470987059, rhol = 0.1, d = 1000, Dr = 0.05, numberOfTeeth = 30) annotation(Placement(transformation(origin = {72, 42.0648}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.SprocketConstriant fixed1(r = {-0.5, 1, 0}) 
    annotation(Placement(transformation(origin = {-70.6, 14.0648}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  TYDriveline3D.ChainDrive.SprocketConstriant fixed2(r = {0.5, 1, 0}) 
    annotation(Placement(transformation(origin = {67.4, 14.0648}, 
    extent = {{-10, -10}, {10, 10}}, 
    rotation = 90)));
  Modelica.Mechanics.Rotational.Sources.Speed speed(phi(fixed = false), 
    exact = false) 
    annotation(Placement(transformation(origin = {67.4, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Ramp ramp(startTime = 0.1, 
    height = -10, 
    duration = 1.9) 
    annotation(Placement(transformation(origin = {32, -2}, 
    extent = {{-10, -10}, {10, 10}})));
  Modelica.Mechanics.Rotational.Sources.Torque torque 
    annotation(Placement(transformation(origin = {-46, -2}, 
    extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Sine sine annotation(Placement(transformation(origin = {-7, -2}, 
    extent = {{10, -10}, {-10, 10}})));
  TYDriveline3D.ChainDrive.Sprocket sprocket2(
    rhol = 0.1, d = 10000, phi0_b = 1.4039079437192, phi0_a = 1.73768470987059, Dr = 0.05, numberOfTeeth = 15) annotation(Placement(transformation(origin = {-6, -46.0649}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.SprocketConstriant fixedC(r = {0, 0.4, 0}, SupportType = .TYDriveline3D.Utilities.Type.SprocketTypes.Translation, n = {0, 1, 0}, s_rel0 = 0.8, animation = false, s_rel = 0.3) 
    annotation(Placement(transformation(origin = {-28.5, -70.9676}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Chain chain1(pitch = 0.23, noM = 2, d = 10000) 
    annotation(Placement(transformation(origin = {-63.3, -46.0649}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.ChainMass chainMass(r_0(start = {0, 1.24, 0}, fixed = true), animation = false) 
    annotation(Placement(transformation(origin = {3, 42.0648}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Chain chain(usePreload = true, pitch = 0.25, noM = 2, diameter = 0.05, d = 10000) 
    annotation(Placement(transformation(origin = {-31.5, 42.0648}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Chain chain2(usePreload = false, pitch = 0.25, noM = 2, diameter = 0.05, d = 10000) 
    annotation(Placement(transformation(origin = {37.5, 42.0648}, 
    extent = {{-10, -10}, {10, 10}})));
  TYDriveline3D.ChainDrive.Chain chain5(pitch = 0.23, noM = 2, d = 10000) 
    annotation(Placement(transformation(origin = {51.3, -46.0649}, 
    extent = {{-10, -10}, {10, 10}})));
equation
  connect(speed.flange, sprocket1.flange_a) 
    annotation(Line(origin = {53.7, 9.8702}, 
    points = {{23.7, -11.8702}, {36, -11.8702}, {36, 22.1946}, {25.7, 22.1946}}, 
    color = {0, 0, 0}));
  connect(ramp.y, speed.w_ref) 
    annotation(Line(origin = {1, -2}, 
    points = {{42, 0}, {54.4, 0}}, 
    color = {0, 0, 127}));
  connect(torque.flange, sprocket.flange_a) 
    annotation(Line(origin = {-57, 15}, 
    points = {{1, -17}, {1, 17.0648}, {-1.6, 17.0648}}, 
    color = {0, 0, 0}));
  connect(sine.y, torque.tau) 
    annotation(Line(origin = {-25, -5}, 
    points = {{7, 3}, {-9, 3}}, 
    color = {0, 0, 127}));
  connect(fixed1.frame_b, sprocket.frame_c) 
    annotation(Line(origin = {-68.5, 28.0324}, 
    points = {{-2.1, -3.9676}, {-2.1, 4.0324}, {2.5, 4.0324}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixed2.frame_b, sprocket1.frame_c) 
    annotation(Line(origin = {69.5, 28.0324}, 
    points = {{-2.1, -3.9676}, {-2.1, 4.0324}, {2.5, 4.0324}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(fixedC.frame_b, sprocket2.frame_c) 
    annotation(Line(origin = {-36.5, -85.9676}, 
    points = {{18, 15}, {30.5, 15}, {30.5, 29.9027}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain1.frame_b, sprocket2.frame_a) 
    annotation(Line(origin = {-52.5, -51.9676}, 
    points = {{-0.8, 5.9027}, {36.5, 5.9027}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain1.chainPort_b, sprocket2.chainPort_a) 
    annotation(Line(origin = {-52.5, -45.9676}, 
    points = {{-0.8, 5.9027}, {36.5, 5.9027}}, 
    color = {0, 0, 0}));
  connect(chain1.frame_a, sprocket.frame_a) 
    annotation(Line(origin = {-96.5, -6.9676}, 
    points = {{23.2, -39.0973}, {0.5, -39.0973}, {0.5, 49.0324}, {20.5, 49.0324}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain1.chainPort_a, sprocket.chainPort_a) 
    annotation(Line(origin = {-94.5, -0.9676}, 
    points = {{21.2, -39.0973}, {4.5, -39.0973}, {4.5, 49.0324}, {18.5, 49.0324}}, 
    color = {0, 0, 0}));
  connect(sprocket.frame_b, chain.frame_a) 
    annotation(Line(origin = {-48.5, 42.5486}, 
    points = {{-7.5, -0.4838}, {7, -0.4838}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(sprocket.chainPort_b, chain.chainPort_a) 
    annotation(Line(origin = {-48.5, 48.5486}, 
    points = {{-7.5, -0.4838}, {7, -0.4838}}, 
    color = {0, 0, 0}));
  connect(chain.chainPort_b, chainMass.chainPort_a) 
    annotation(Line(origin = {-14.5, 48.5486}, 
    points = {{-7, -0.4838}, {7.5, -0.4838}, {7.5, -0.2838}}, 
    color = {0, 0, 0}));
  connect(chain.frame_b, chainMass.frame_a) 
    annotation(Line(origin = {-9.5, 42.5486}, 
    points = {{-12, -0.4838}, {12.5, -0.4838}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chainMass.chainPort_b, chain2.chainPort_a) 
    annotation(Line(origin = {20.5, 48.5486}, 
    points = {{-7.5, -0.4838}, {7, -0.4838}}, 
    color = {0, 0, 0}));
  connect(sprocket1.chainPort_a, chain2.chainPort_b) 
    annotation(Line(origin = {54.5, 48.5486}, 
    points = {{7.5, -0.4838}, {-7, -0.4838}}, 
    color = {0, 0, 0}));
  connect(sprocket1.frame_a, chain2.frame_b) 
    annotation(Line(origin = {54.5, 42.5486}, 
    points = {{7.5, -0.4838}, {-7, -0.4838}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain2.frame_a, chainMass.frame_a) 
    annotation(Line(origin = {15.5, 42.5486}, 
    points = {{12, -0.4838}, {-12.5, -0.4838}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain5.chainPort_a, sprocket2.chainPort_b) 
    annotation(Line(origin = {22.5, -48.4514}, 
    points = {{18.8, 8.3865}, {-18.5, 8.3865}}, 
    color = {0, 0, 0}));
  connect(chain5.frame_a, sprocket2.frame_b) 
    annotation(Line(origin = {22.5, -54.4514}, 
    points = {{18.8, 8.3865}, {-18.5, 8.3865}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain5.frame_b, sprocket1.frame_b) 
    annotation(Line(origin = {94.5, -10.4514}, 
    points = {{-33.2, -35.6135}, {5.5, -35.6135}, {5.5, 52.5162}, {-12.5, 52.5162}}, 
    color = {95, 95, 95}, 
    thickness = 0.5));
  connect(chain5.chainPort_b, sprocket1.chainPort_b) 
    annotation(Line(origin = {88.5, -4.4514}, 
    points = {{-27.2, -35.6135}, {7.5, -35.6135}, {7.5, 52.5162}, {-6.5, 52.5162}}, 
    color = {0, 0, 0}));

  annotation(Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Rectangle(origin = {0, 6}, 
    lineColor = {255, 255, 255}, 
    fillColor = {255, 255, 255}, 
    fillPattern = FillPattern.Solid, 
    extent = {{-126, 92}, {126, -92}})}), Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, 
    grid = {2, 2}), graphics = {Polygon(origin = {-3.55271e-15, 27}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64, 1}, {0, 37}, {64, 1}, {0, -37}}), Line(origin = {3.55271e-15, -18}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5), Line(origin = {1.06581e-14, -46}, 
    points = {{-62, 18}, {0, -18}, {62, 18}}, 
    color = {96, 96, 96}, 
    thickness = 5)}), experiment(Algorithm = Dassl, InlineIntegrator = false, InlineStepSize = false, Interval = 0.001, StartTime = 0, StopTime = 3, Tolerance = 1e-06), __MWORKS(ContinueSimConfig(SaveContinueFile = "false", SaveBeforeStop = "false", NumberBeforeStop = 1, FixedContinueInterval = "false", ContinueIntervalLength = 0.75, ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, left_title_type=2, left_title="[rad/s]", bottom_title_type=2, right_title_type=2, fix_time_range_value=0, zoom_x=(0, 3), zoom_y_l=(-15, 25)), 
Plot(y=["sprocket.om", "sprocket1.om", "sprocket2.om"], colors=["4278190335", "4294901760", "4278222848"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 3), zoom_y_l=(-3000, 4000)), 
Plot(y=["chain.sds[1].Fi", "chain1.sds[1].Fi", "chain5.sds[1].Fi"], colors=["4278190335", "4294901760", "4278222848"])})
})), 
    Documentation(link = "modelica://TYDriveline3D/Resources/html/Example/ChainDrive/ChainDriveWithGuideSprockert.html"),Protection(access=Access.nonPackageDuplicate));

end ChainDriveWithGuideSprockert;