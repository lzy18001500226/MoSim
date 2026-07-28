within MoSimQuadrotorModel.Experiment.Runners.Formal;
model NonsingularTerminalSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for NonsingularTerminalSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NonsingularTerminalSmcAttitudeThrustAdapter);
end NonsingularTerminalSmcFormalRunner;
