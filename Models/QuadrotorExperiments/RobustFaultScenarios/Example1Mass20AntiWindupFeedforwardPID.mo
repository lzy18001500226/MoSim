within QuadrotorExperiments.RobustFaultScenarios;
model Example1Mass20AntiWindupFeedforwardPID
  "Example1 AWFF PID with +20% central body mass perturbation"
  extends Example1ProjectControllerBase(
    quadChassisTest17_1.body(m = 1.2));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true));
end Example1Mass20AntiWindupFeedforwardPID;
