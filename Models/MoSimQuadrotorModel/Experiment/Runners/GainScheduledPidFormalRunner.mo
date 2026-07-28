within MoSimQuadrotorModel.Experiment.Runners;
model GainScheduledPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for GainScheduledPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.GainScheduledPidAttitudeThrustAdapter);
end GainScheduledPidFormalRunner;
