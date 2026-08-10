within MoSimQuadrotorModel.Experiment.Runners.Formal;
model TerminalSmcFormalRunner
  "Formal 100 Hz whole-aircraft runner for TerminalSmcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.TerminalSmcAttitudeThrustAdapter);
end TerminalSmcFormalRunner;