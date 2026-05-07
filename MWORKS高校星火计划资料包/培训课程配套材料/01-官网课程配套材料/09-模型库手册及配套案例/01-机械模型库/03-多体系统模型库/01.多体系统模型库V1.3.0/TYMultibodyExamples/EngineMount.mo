model EngineMount "发动机悬置"
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
    grid = {2.0, 2.0}), graphics = {Polygon(origin = {-7.105427357601002e-15, 33.0}, 
    lineColor = {96, 96, 96}, 
    fillColor = {96, 96, 96}, 
    fillPattern = FillPattern.Solid, 
    points = {{-64.0, 1.0}, {0.0, 37.0}, {64.0, 1.0}, {0.0, -37.0}}), Line(origin = {0.0, -12.0}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0), Line(origin = {7.105427357601002e-15, -39.99999999999999}, 
    points = {{-62.0, 18.0}, {0.0, -18.0}, {62.0, 18.0}}, 
    color = {96, 96, 96}, 
    thickness = 5.0)}), 
    Protection(access = Access.nonPackageDuplicate),Documentation(link = "modelica://TYMultibody/Resources/html/EngineMount.html"),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Line(origin={-19,1}, 
points={{-175,109},{-175,-109},{175,-107},{175,109},{-175,109}}, 
color={255,255,255})}),experiment(Algorithm=Dassl,Interval=0.001,StartTime=0,StopTime=10,Tolerance=1e-06),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=0.03,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="1", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=2, x_display_unit="s", legend_layout=1, left_title="[m]", right_title_type=2, fix_time_range_value=0, zoom_x=(0, 10), zoom_y_l=(-0.26015, -0.25985)), 
Plot(y=["EngineBody.r_OG_0[1]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(1, 2), zoom_x=(0, 10), zoom_y_l=(0.0396, 0.0406)), 
Plot(y=["EngineBody.r_OG_0[2]"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[N.m]", fix_time_range_value=0, sub_plot=(2, 2), zoom_x=(0, 10), zoom_y_l=(85, 115)), 
Plot(y=["Ty.y"], colors=["4278190335"]), 
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, left_title="[m]", fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 10), zoom_y_l=(0.212, 0.222)), 
Plot(y=["EngineBody.r_OG_0[3]"], colors=["4278190335"])})
})));
  TYMultibody.Forces.TranslationalMount Mount_LH 
    annotation (Placement(transformation(origin = {-115.93527458417626, 46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Fixed fixed_RH(
                        r = {-290e-3, 500e-3, 450e-3}, 
    ShowFrame = true


                    ) 
    annotation (Placement(transformation(origin = {108.0, 74.99999999999996}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Forces.TranslationalMount Mount_RH 
    annotation (Placement(transformation(origin = {62.0, 74.99999999999994}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Forces.TranslationalMount Mount_TR 
    annotation (Placement(transformation(origin = {4.999999999999987, -51.000000000000014}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation(
                                           r = {-50e-3, -20e-3, -50e-3}


                                                                       ) 
    annotation (Placement(transformation(origin = {-18.0, 10.000000000000002}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}}, 
      rotation = -90.0)));
  TYMultibody.Joints.Fixed fixed_TR(
                        r = {-50e-3, -20e-3, -50e-3}, 
    ShowFrame = true


                    ) 
    annotation (Placement(transformation(origin = {42.999999999999986, -51.000000000000014}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper LH_KX(
                                                                 c = 250e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {-159.8705491683525, -1.9999999999999825}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper LH_KY(
                                                                 c = 90e3, d = 100, 
    s_rel(fixed 
       = false)


               ) 
    annotation (Placement(transformation(origin = {-121.93527458417627, -1.9999999999999825}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper LH_KZ(
                                                                 c = 250e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {-84.0, -1.9999999999999831}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper TR_KX(
                                                                 c = 280e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {-46.87054916835251, -83.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper TR_KY(
                                                                 c = 20e3, d = 100


                                                                                  ) 
    annotation (Placement(transformation(origin = {-12.935274584176238, -83.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper TR_KZ(
                                                                 c = 20e3, d = 100


                                                                                  ) 
    annotation (Placement(transformation(origin = {20.99999999999999, -83.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper RH_KX(
                                                                 c = 180e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {62.0, 31.999999999999993}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper RH_KY(
                                                                 c = 180e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {94.0, 34.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Modelica.Mechanics.Translational.Components.SpringDamper RH_KZ(
                                                                 c = 300e3, d = 100


                                                                                   ) 
    annotation (Placement(transformation(origin = {120.0, 34.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Joints.Fixed fixed_LH(
                        r = {-240e-3, -380e-3, 350e-3}, 
    ShowFrame = true


                    ) 
    annotation (Placement(transformation(origin = {-159.8705491683525, 46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation1(
                                            r = {-290e-3, 500e-3, 450e-3}


                                                                         ) 
    annotation (Placement(transformation(origin = {23.999999999999982, 74.99999999999996}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation2(
                                            r = {-270e-3, 150e-3, 150e-3}


                                                                         ) 
    annotation (Placement(transformation(origin = {40.0, -10.0}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  TYMultibody.Forces.GlobalTorque globalTorque(
                                   useVariableTorque = true, 
    Nm_to_m = 500


                 ) annotation (Placement(transformation(origin = {80.0, -10.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression Tx 
    annotation (Placement(transformation(origin = {120.0, -6.0}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression Tz 
    annotation (Placement(transformation(origin = {120.0, -51.000000000000014}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  Modelica.Blocks.Sources.RealExpression Ty(
                                            y = 100 + 10 * sin(2 * Modelica.Constants.pi *time)


                                                                             ) 
    annotation (Placement(transformation(origin = {120.0, -28.500000000000014}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Bodies.RigidTranslation rigidTranslation3(
                                            r = {-240e-3, -380e-3, 350e-3}


                                                                          ) 
    annotation (Placement(transformation(origin = {-55.46763729208814, 46.00000000000001}, 
      extent = {{10.0, -10.0}, {-10.0, 10.0}})));
  TYMultibody.Bodies.Body EngineBody(
                         r_AG_a = {-260e-3, 40e-3, 220e-3}, m = 200, Ixx = 14, Iyy = 7, Izz = 12, Ixy = -0.6, Ixz = 0.5, Iyz = 3, shapeType = "box", r_shape = {-440e-3, 50e-3, 300e-3}, length = 350e-3, width = 800e-3, height = 500e-3, 
    r_OA_0(fixed 
       = true), 
    angles_fixed = true


                       ) annotation (Placement(transformation(origin = {4.999999999999989, 46.00000000000001}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  inner TYMultibody.World world(
                    n = {0, 0, -1}


                                  ) 
    annotation (Placement(transformation(origin = {-84.0, 85.99999999999997}, 
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
equation
  connect(Mount_RH.frame_b, fixed_RH.frame_b) 
    annotation (Line(origin = {86.99999999999999, 46.99999999999997}, 
      points = {{-15.0, 28.0}, {15.0, 28.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation.frame_b, Mount_TR.frame_a) 
    annotation (Line(origin = {1.9999999999999876, -5.000000000000028}, 
      points = {{-20.0, 5.0}, {-20.0, -46.0}, {-7.0, -46.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(Mount_TR.frame_b, fixed_TR.frame_b) 
    annotation (Line(origin = {44.999999999999986, -11.000000000000028}, 
      points = {{-30.0, -40.0}, {-8.0, -40.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(LH_KX.flange_b, Mount_LH.flange_xa) 
    annotation (Line(origin = {-131.93527458417626, 17.000000000000018}, 
      points = {{-18.0, -19.0}, {-14.0, -19.0}, {-14.0, -4.0}, {10.0, -4.0}, {10.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(LH_KX.flange_a, Mount_LH.flange_xb) 
    annotation (Line(origin = {-143.93527458417626, 17.000000000000018}, 
      points = {{-26.0, -19.0}, {-30.0, -19.0}, {-30.0, 0.0}, {18.0, 0.0}, {18.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(LH_KY.flange_b, Mount_LH.flange_ya) 
    annotation (Line(origin = {-110.93527458417627, 17.000000000000018}, 
      points = {{-1.0, -19.0}, {0.0, -19.0}, {0.0, -5.0}, {-3.0, -5.0}, {-3.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(LH_KY.flange_a, Mount_LH.flange_yb) 
    annotation (Line(origin = {-122.93527458417626, 17.000000000000018}, 
      points = {{-9.0, -19.0}, {-20.0, -19.0}, {-20.0, -6.0}, {5.0, -6.0}, {5.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(LH_KZ.flange_a, Mount_LH.flange_zb) 
    annotation (Line(origin = {-101.93527458417626, 17.000000000000018}, 
      points = {{8.0, -19.0}, {2.0, -19.0}, {2.0, -2.0}, {-8.0, -2.0}, {-8.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(LH_KZ.flange_b, Mount_LH.flange_za) 
    annotation (Line(origin = {-89.93527458417626, 17.000000000000018}, 
      points = {{16.0, -19.0}, {24.0, -19.0}, {24.0, 2.0}, {-16.0, 2.0}, {-16.0, 19.0}}, 
      color = {0, 127, 0}));
  connect(TR_KX.flange_b, Mount_TR.flange_xa) 
    annotation (Line(origin = {-19.000000000000014, -72.0}, 
      points = {{-18.0, -11.0}, {-18.0, 8.0}, {18.0, 8.0}, {18.0, 11.0}}, 
      color = {0, 127, 0}));
  connect(TR_KX.flange_a, Mount_TR.flange_xb) 
    annotation (Line(origin = {-31.000000000000014, -72.0}, 
      points = {{-26.0, -11.0}, {-26.0, 10.0}, {26.0, 10.0}, {26.0, 11.0}}, 
      color = {0, 127, 0}));
  connect(TR_KY.flange_b, Mount_TR.flange_ya) 
    annotation (Line(origin = {1.9999999999999911, -72.0}, 
      points = {{-5.0, -11.0}, {-5.0, 2.0}, {5.0, 2.0}, {5.0, 11.0}}, 
      color = {0, 127, 0}));
  connect(TR_KY.flange_a, Mount_TR.flange_yb) 
    annotation (Line(origin = {-10.000000000000012, -72.0}, 
      points = {{-13.0, -11.0}, {-18.0, -11.0}, {-18.0, 6.0}, {13.0, 6.0}, {13.0, 11.0}}, 
      color = {0, 127, 0}));
  connect(TR_KZ.flange_a, Mount_TR.flange_zb) 
    annotation (Line(origin = {10.999999999999991, -72.0}, 
      points = {{0.0, -11.0}, {0.0, 11.0}}, 
      color = {0, 127, 0}));
  connect(Mount_TR.flange_za, TR_KZ.flange_b) 
    annotation (Line(origin = {22.999999999999993, -72.0}, 
      points = {{-8.0, 11.0}, {-8.0, 6.0}, {12.0, 6.0}, {12.0, -11.0}, {8.0, -11.0}}, 
      color = {96, 96, 96}));
  connect(RH_KX.flange_a, Mount_RH.flange_xb) 
    annotation (Line(origin = {55.999999999999986, 27.999999999999975}, 
      points = {{-4.0, 4.0}, {-18.0, 4.0}, {-18.0, 18.0}, {-4.0, 18.0}, {-4.0, 37.0}}, 
      color = {0, 127, 0}));
  connect(RH_KX.flange_b, Mount_RH.flange_xa) 
    annotation (Line(origin = {67.99999999999999, 42.99999999999999}, 
      points = {{4.0, -11.0}, {4.0, 2.0}, {-12.0, 2.0}, {-12.0, 22.0}}, 
      color = {0, 127, 0}));
  connect(RH_KY.flange_a, Mount_RH.flange_yb) 
    annotation (Line(origin = {84.99999999999999, 42.99999999999999}, 
      points = {{-1.0, -9.0}, {-6.0, -9.0}, {-6.0, 4.0}, {-25.0, 4.0}, {-25.0, 22.0}}, 
      color = {0, 127, 0}));
  connect(Mount_RH.flange_ya, RH_KY.flange_b) 
    annotation (Line(origin = {87.99999999999999, 42.99999999999999}, 
      points = {{-24.0, 22.0}, {17.0, 22.0}, {17.0, -9.0}, {16.0, -9.0}}, 
      color = {96, 96, 96}));
  connect(RH_KZ.flange_a, Mount_RH.flange_zb) 
    annotation (Line(origin = {92.99999999999999, 42.99999999999999}, 
      points = {{17.0, -9.0}, {17.0, 6.0}, {-25.0, 6.0}, {-25.0, 22.0}}, 
      color = {0, 127, 0}));
  connect(RH_KZ.flange_b, Mount_RH.flange_za) 
    annotation (Line(origin = {104.99999999999999, 42.99999999999999}, 
      points = {{25.0, -9.0}, {25.0, 8.0}, {-33.0, 8.0}, {-33.0, 22.0}}, 
      color = {0, 127, 0}));
  connect(fixed_LH.frame_b, Mount_LH.frame_a) 
    annotation (Line(origin = {-149.93527458417626, 46.000000000000014}, 
      points = {{-4.0, 0.0}, {24.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation1.frame_b, Mount_RH.frame_a) 
    annotation (Line(origin = {42.999999999999986, 74.99999999999997}, 
      points = {{-9.0, 0.0}, {9.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(globalTorque.frame_b, rigidTranslation2.frame_b) 
    annotation (Line(origin = {60.0, -10.0}, 
      points = {{10.0, 0.0}, {-10.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(globalTorque.Tx_in, Tx.y) 
    annotation (Line(origin = {100.0, -6.0}, 
      points = {{-10.0, 0.0}, {9.0, 0.0}}, 
      color = {0, 0, 127}));
  connect(Tz.y, globalTorque.Tz_in) 
    annotation (Line(origin = {100.0, -23.0}, 
      points = {{9.0, -28.0}, {-4.0, -28.0}, {-4.0, 9.0}, {-10.0, 9.0}}, 
      color = {0, 0, 127}));
  connect(Ty.y, globalTorque.Ty_in) 
    annotation (Line(origin = {100.0, -19.0}, 
      points = {{9.0, -10.0}, {4.0, -10.0}, {4.0, 9.0}, {-10.0, 9.0}}, 
      color = {0, 0, 127}));
  connect(rigidTranslation.frame_a, EngineBody.frame_a) 
    annotation (Line(origin = {-11.0, 33.0}, 
      points = {{-7.0, -13.0}, {-7.0, 13.0}, {6.0, 13.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation1.frame_a, EngineBody.frame_a) 
    annotation (Line(origin = {5.0, 61.0}, 
      points = {{9.0, 14.0}, {-24.0, 14.0}, {-24.0, -15.0}, {-10.0, -15.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation2.frame_a, EngineBody.frame_a) 
    annotation (Line(origin = {13.0, 18.0}, 
      points = {{17.0, -28.0}, {-4.0, -28.0}, {-4.0, 10.0}, {-18.0, 10.0}, {-18.0, 28.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation3.frame_a, EngineBody.frame_a) 
    annotation (Line(origin = {-25.0, 46.0}, 
      points = {{-20.0, 0.0}, {20.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
  connect(rigidTranslation3.frame_b, Mount_LH.frame_b) 
    annotation (Line(origin = {-86.0, 46.0}, 
      points = {{21.0, 0.0}, {-20.0, 0.0}}, 
      color = {95, 95, 95}, 
      thickness = 0.5));
end EngineMount;