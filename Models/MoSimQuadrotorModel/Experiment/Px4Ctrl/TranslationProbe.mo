within MoSimQuadrotorModel.Experiment.Px4Ctrl;
model TranslationProbe
  "Minimal scalar Modelica probe for the current Sysplorer translation service"

  Real elapsed_s;

equation
  elapsed_s = time;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.1,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end TranslationProbe;