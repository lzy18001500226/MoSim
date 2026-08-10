within MoSimQuadrotorModel.Experiment.Runners.Formal;
model GainScheduledPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for GainScheduledPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.GainScheduledPidAttitudeThrustAdapter);
end GainScheduledPidFormalRunner;