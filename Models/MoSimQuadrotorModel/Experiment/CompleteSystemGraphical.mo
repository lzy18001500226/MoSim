within MoSimQuadrotorModel.Experiment;
model CompleteSystemGraphical
  "Direct review entry for the px4ctrl Sunray150 graphical system architecture"

  extends MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical;

  annotation(
    Diagram(
      coordinateSystem(extent = {{-580, -300}, {560, 240}}, grid = {5, 5}),
      graphics = {
        Text(origin = {-10, 220}, extent = {{-300, 14}, {300, -14}},
          textString = "Sunray150 / px4ctrl complete architecture",
          fontSize = 24, textColor = {45, 45, 45})}),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(hide=false,version="26.3.0"));
end CompleteSystemGraphical;