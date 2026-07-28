within MoSimQuadrotorModel.Experiment.Runners;
model TerminalSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for TerminalSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.TerminalSmcAttitudeThrustAdapter);
end TerminalSmcFormalRunner;
