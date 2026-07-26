within MoSimQuadrotorModel.Vehicle;
package Electricals "电气系统"
  extends Modelica.Icons.Package;
  annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
    preserveAspectRatio = false,
    grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0},
    lineColor = {128, 128, 128},
    extent = {{-100.0, -100.0}, {100.0, 100.0}},
    radius = 25.0), Rectangle(origin = {20.3125, 82.8571},
    extent = {{-45.3125, -57.8571}, {4.6875, -27.8571}}), Line(origin = {8.0, 48.0},
    points = {{32.0, -58.0}, {72.0, -58.0}}), Line(origin = {9.0, 54.0},
    points = {{31.0, -49.0}, {71.0, -49.0}}), Line(origin = {-2.0, 55.0},
    points = {{-83.0, -50.0}, {-33.0, -50.0}}), Line(origin = {-3.0, 45.0},
    points = {{-72.0, -55.0}, {-42.0, -55.0}}), Line(origin = {1.0, 50.0},
    points = {{-61.0, -45.0}, {-61.0, -10.0}, {-26.0, -10.0}}), Line(origin = {7.0, 50.0},
    points = {{18.0, -10.0}, {53.0, -10.0}, {53.0, -45.0}}), Line(origin = {6.2593, 48.0},
    points = {{53.7407, -58.0}, {53.7407, -93.0}, {-66.2593, -93.0}, {-66.2593, -58.0}})}));
  model Actuator "电机模型"
    replaceable parameter Modelica.Electrical.Machines.Examples.ControlledDCDrives.Utilities.DriveDataDCPM driveData constrainedby ControlledDCDrives.Utilities.DriveDataDCPM
      annotation (Placement(transformation(origin = {-78.0, 38.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor annotation (
      Placement(transformation(origin = {82.00000000000003, -53.99999999999999},
        extent = {{-10.0, -10.0}, {10.0, 10.0}},
        rotation = 270.0)));
    Modelica.Electrical.Machines.BasicMachines.DCMachines.DC_PermanentMagnet dcpm(
      TaOperational = driveData.motorData.TaNominal,
      VaNominal = driveData.motorData.VaNominal,
      IaNominal = driveData.motorData.IaNominal,
      wNominal = driveData.motorData.wNominal,
      TaNominal = driveData.motorData.TaNominal,
      Ra = driveData.motorData.Ra,
      TaRef = driveData.motorData.TaRef,
      La = driveData.motorData.La,
      Jr = driveData.motorData.Jr,
      frictionParameters = driveData.motorData.frictionParameters,
      phiMechanical(fixed = true),
      wMechanical(fixed = true),
      coreParameters = driveData.motorData.coreParameters,
      strayLoadParameters = driveData.motorData.strayLoadParameters,
      brushParameters = driveData.motorData.brushParameters,
      ia(fixed = true),
      Js = driveData.motorData.Js,
      alpha20a = driveData.motorData.alpha20a)
      annotation (Placement(transformation(origin = {62.0, -24.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Electrical.Machines.Examples.ControlledDCDrives.Utilities.DcdcInverter armatureInverter(
      fS = driveData.fS,
      Td = driveData.Td,
      Tmf = driveData.Tmf,
      VMax = driveData.VaMax)
      annotation (Placement(transformation(origin = {62.0, 6.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Electrical.Machines.Examples.ControlledDCDrives.Utilities.Battery source(
      INominal = driveData.motorData.IaNominal, V0 = driveData.VBat)
      annotation (Placement(transformation(origin = {62.0, 48.0},
        extent = {{10.0, -10.0}, {-10.0, 10.0}},
        rotation = 180.0)));
    Modelica.Electrical.Machines.Examples.ControlledDCDrives.Utilities.LimitedPI currentController(
      constantLimits = false,
      k = driveData.kpI,
      Ti = driveData.TiI,
      KFF = driveData.kPhi,
      initType = Modelica.Blocks.Types.Init.InitialOutput,
      useFF = true)
      annotation (Placement(transformation(origin = {-8.0, 6.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Blocks.Math.Gain tau2i(k = 1 / driveData.kPhi) annotation (Placement(transformation(origin = {-38.0, 6.0},
      extent = {{10.0, -10.0}, {-10.0, 10.0}},
      rotation = 180.0)));
    Modelica.Electrical.Machines.Examples.ControlledDCDrives.Utilities.LimitedPI speedController(
      initType = Modelica.Blocks.Types.Init.InitialOutput,
      k = driveData.kpw,
      Ti = driveData.Tiw,
      constantLimits = true,
      yMax = driveData.tauMax)
      annotation (Placement(transformation(origin = {-78.0, 6.0},
        extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    Modelica.Mechanics.Rotational.Interfaces.Flange_a flange_a
      annotation (Placement(transformation(origin = {120.0, -24.0},
        extent = {{-2.0, -2.0}, {2.0, 2.0}}),
        iconTransformation(origin = {99.30272050638656, 2.0655011867162516},
          extent = {{-10.0, -10.0}, {10.0, 10.0}})));
    annotation (Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      grid = {2.0, 2.0}), graphics = {Rectangle(origin = {-0.21868787276341806, 0.44532803180914016},
      lineColor = {200, 200, 200},
      fillColor = {248, 248, 248},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-100.0, -100.0}, {100.0, 100.0}},
      radius = 25.0), Rectangle(origin = {-24.71292246520875, 1.959443339960238},
      lineColor = {82, 0, 2},
      fillColor = {252, 37, 57},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-65.0, -50.0}, {65.0, 50.0}},
      radius = 10.0), Polygon(origin = {-24.71292246520875, -58.04055666003976},
      fillColor = {64, 64, 64},
      fillPattern = FillPattern.Solid,
      points = {{-65.0, -30.0}, {-55.0, -30.0}, {-25.0, 40.0}, {25.0, 40.0}, {55.0, -30.0}, {65.0, -30.0}, {65.0, -40.0}, {-65.0, -40.0}, {-65.0, -30.0}}), Rectangle(origin = {70.28707753479125, 1.959443339960238},
      lineColor = {64, 64, 64},
      fillColor = {255, 255, 255},
      fillPattern = FillPattern.HorizontalCylinder,
      extent = {{-30.0, -10.0}, {30.0, 10.0}})}),
      Diagram(coordinateSystem(extent = {{-120.0, -100.0}, {120.0, 100.0}},
        grid = {2.0, 2.0})));
    Modelica.Blocks.Interfaces.RealInput u
      annotation (Placement(transformation(origin = {-119.688, 5.68798},
        extent = {{-4.31202, -4.31202}, {4.31202, 4.31202}}),
        iconTransformation(origin = {-118.37598000000001, 3.0000000000000036},
          extent = {{-16.999999999999986, -17.000000000000004}, {17.000000000000014, 16.999999999999996}})));
  equation
    connect(speedSensor.flange, dcpm.flange)
      annotation (Line(origin = {77.0, -34.0},
        points = {{5.0, -10.0}, {5.0, 10.0}, {-5.0, 10.0}}));
    connect(armatureInverter.pin_nMot, dcpm.pin_an)
      annotation (Line(origin = {56.0, -9.0},
        points = {{0.0, 5.0}, {0.0, -5.0}},
        color = {0, 0, 255}));
    connect(armatureInverter.pin_pMot, dcpm.pin_ap)
      annotation (Line(origin = {68.0, -9.0},
        points = {{0.0, 5.0}, {0.0, -5.0}},
        color = {0, 0, 255}));
    connect(armatureInverter.vDC, currentController.yMaxVar)
      annotation (Line(origin = {27.5, 12.0},
        points = {{24.0, 0.0}, {-24.0, 0.0}},
        color = {0, 0, 127}));
    connect(armatureInverter.vRef, currentController.y)
      annotation (Line(origin = {26.5, 6.0},
        points = {{24.0, 0.0}, {-24.0, 0.0}},
        color = {0, 0, 127}));
    connect(armatureInverter.iMot, currentController.u_m)
      annotation (Line(origin = {18.5, -7.0},
        points = {{33.0, 7.0}, {3.0, 7.0}, {3.0, -25.0}, {-33.0, -25.0}, {-33.0, 1.0}},
        color = {0, 0, 127}));
    connect(speedSensor.w, currentController.feedForward)
      annotation (Line(origin = {37.0, -40.0},
        points = {{45.0, -25.0}, {45.0, -34.0}, {-45.0, -34.0}, {-45.0, 34.0}},
        color = {0, 0, 127}));
    connect(tau2i.y, currentController.u)
      annotation (Line(origin = {-23.5, 6.0},
        points = {{-4.0, 0.0}, {4.0, 0.0}},
        color = {0, 0, 127}));
    connect(source.pin_n, armatureInverter.pin_nBat)
      annotation (Line(origin = {56.0, 51.0},
        points = {{0.0, -13.0}, {0.0, -35.0}},
        color = {0, 0, 255}));
    connect(source.pin_p, armatureInverter.pin_pBat)
      annotation (Line(origin = {68.0, 51.0},
        points = {{0.0, -13.0}, {0.0, -35.0}},
        color = {0, 0, 255}));
    connect(speedSensor.w, speedController.u_m)
      annotation (Line(origin = {-1.0, -40.0},
        points = {{83.0, -25.0}, {83.0, -34.0}, {-83.0, -34.0}, {-83.0, 34.0}},
        color = {0, 0, 127}));
    connect(speedController.y, tau2i.u)
      annotation (Line(origin = {-58.5, 6.0},
        points = {{-9.0, 0.0}, {9.0, 0.0}},
        color = {0, 0, 127}));

    connect(dcpm.flange, flange_a)
      annotation (Line(origin = {82.0, -39.0},
        points = {{-10.0, 15.0}, {38.0, 15.0}},
        color = {0, 0, 0}));
    connect(u, speedController.u)
      annotation (Line(origin = {-109.0, 5.0},
        points = {{-11.0, 1.0}, {19.0, 1.0}},
        color = {0, 0, 127}));
  end Actuator;
end Electricals;
