within MoSimQuadrotorModel.Experiment.Runners;
model NonsingularTerminalSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for NonsingularTerminalSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NonsingularTerminalSmcAttitudeThrustAdapter);
end NonsingularTerminalSmcFormalRunner;
