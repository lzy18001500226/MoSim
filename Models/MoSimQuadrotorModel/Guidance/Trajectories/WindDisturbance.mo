within MoSimQuadrotorModel.Guidance.Trajectories;
model WindDisturbance
  "ClimbPath reference with a persistent lateral gust contract"

  extends MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath;
  parameter Real gust_force[3](each unit = "N") = {0.25, 0, 0}
    "Persistent lateral force read by a Runner when this scenario is bound";
  parameter Real gust_start_s(unit = "s") = 0;
  parameter Real gust_duration_s(unit = "s") = 50;

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50,
      Tolerance = 0.0001, Interval = 0.01),
    __MWORKS(version = "26.3.0"));
end WindDisturbance;