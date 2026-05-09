within ;
model SimpleCar

  parameter Real R = 0.34;
  annotation (uses(Modelica(version = "2.2.2"), Utilities, ObsoleteModelica3), Diagram(Rectangle(extent = [-98, 72; 
    -20, 32], style(
      color = 3, 
      rgbcolor = {0, 0, 255}, 
      pattern = 3)), Text(
      extent = [-84, 82; -48, 72], 
      style(color = 3, rgbcolor = {0, 0, 255}), 
      string = "Engine")), 
    Commands(
      editCall(ensureTranslated = true) = 
      Design.Calibration.calibrate(Design.Internal.Records.ModelCalibrationSetup(Model = 
      "Design.Calibration.Examples.SimpleCar", 
      tunerParameters = fill(Design.Internal.Records.TunerParameter(), 0), 
      freeStartValues = fill(Design.Internal.Records.FreeStartValues(), 0), 
      calibrationData = 
      Design.Calibration.Internal.Dynamic_common(
      Design.Internal.Records.DynamicCommonCalibrationCases(experimentNames = {
      Design.Calibration.Examples.Utilities.GetPathToExamples() + "Acceleration measurements.csv"}, task = 
      {2}, parameterNames = {"carBody.v", "gearBox.i"}, parameterValues = [68.4 / 
      3.6, 2.34]), resultCouplings = {Design.Internal.Records.DynamicCalibrationResultCoupling(variable = "carBody.der(v)", data = "acc")}), 
      optimizer = Design.Internal.Records.CalibrationOptimizer(), integrator = 
      Design.Internal.Records.CalibrationIntegrator(startTime = 3.8, stopTime = 6))) "Validation of original model", 
      editCall(ensureTranslated = true) = Design.Calibration.calibrate(Design.Internal.Records.ModelCalibrationSetup(
      Model = "Design.Calibration.Examples.SimpleCar", 
      tunerParameters = {Design.Internal.Records.TunerParameter(name = 
      "gearBox.lossTable[1, 2]", Value = 1), Design.Internal.Records.TunerParameter(
      name = "engineTorque.tau_0", Value = 320)}, 
      calibrationData = Design.Calibration.Internal.Dynamic_common(
      Design.Internal.Records.DynamicCommonCalibrationCases(
      experimentNames = {
      Design.Calibration.Examples.Utilities.GetPathToExamples() + "Acceleration measurements.csv", 
      Design.Calibration.Examples.Utilities.GetPathToExamples() + "Acceleration measurements.csv"}, 
      task = {1, 2}, 
      startTime = {3.8, 2}, 
      stopTime = {6.0, 3}, 
      parameterNames = {"carBody.v", "gearBox.i"}, 
      parameterValues = [68.4 / 3.6, 2.34; 39.9 / 3.6, 4.17]), 
      resultCouplings = {Design.Internal.Records.DynamicCalibrationResultCoupling(variable = 
      "carBody.der(v)", data = "acc")}), 
      integrator = Design.Internal.Records.CalibrationIntegrator(stopTime = 6.2), 
      optimizer = Design.Internal.Records.CalibrationOptimizer())) "Calibration with validation"), 
    Protection(access = Access.nonPackageText));

  Modelica.Mechanics.Rotational.Inertia engineInertia(J = 0.4, w(fixed = false))
    annotation (extent = [-50, 40; -30, 60]);
  Modelica.Mechanics.Rotational.Inertia cardanInertia(J = 0.01)
    "Inertia of cardan and gearbox" annotation (extent = [26, 40; 46, 60]);
  Modelica.Mechanics.Rotational.Inertia wheelInertias(J = 4)
    annotation (extent = [-8, 2; 12, 22]);
  Modelica.Mechanics.Rotational.IdealGear finalDriveGear(ratio = 3.46)
    annotation (extent = [66, 40; 86, 60]);
  Modelica.Mechanics.Rotational.IdealGearR2T wheel(ratio = 1 / R)
    annotation (extent = [28, 22; 48, 2]);
  Modelica.Mechanics.Translational.SlidingMass carBody(m = 1810, v(start = 19))
    annotation (extent = [68, 2; 88, 22]);
  Modelica.Mechanics.Rotational.LossyGear gearBox(lossTable = [0, 1, 1, 0, 
    0], i = 4.17)
    annotation (extent = [-10, 40; 10, 60]);
  Utilities.Engine engineTorque(
    tau_max = 450, 
    w_max = 7200 * Modelica.Constants.pi / 60, 
    tau_0 = 320)
    annotation (extent = [-90, 40; -70, 60]);
equation 
  connect(cardanInertia.flange_b, finalDriveGear.flange_a)
    annotation (points = [46, 50; 66, 50], style(color = 0, rgbcolor = {0, 0, 0}));
  connect(finalDriveGear.flange_b, wheelInertias.flange_a) annotation (points = [86, 
    50; 92, 50; 92, 32; -16, 32; -16, 12; -8, 12], 
    style(color = 0, rgbcolor = {0, 0, 0}));
  connect(wheelInertias.flange_b, wheel.flange_a)
    annotation (points = [12, 12; 28, 12], style(color = 0, rgbcolor = {0, 0, 0}));
  connect(wheel.flange_b, carBody.flange_a)
    annotation (points = [48, 12; 68, 12], 
      style(color = 58, rgbcolor = {0, 127, 0}));
  connect(gearBox.flange_b, cardanInertia.flange_a) annotation (points = [10, 50; 
    26, 50], style(color = 0, rgbcolor = {0, 0, 0}));
  connect(engineInertia.flange_b, gearBox.flange_a)
    annotation (points = [-30, 50; -10, 50], style(color = 0, rgbcolor = {0, 0, 0}));
  connect(engineTorque.flange, engineInertia.flange_a)
    annotation (points = [-70, 50; -50, 50], style(color = 0, rgbcolor = {0, 0, 0}));
end SimpleCar;