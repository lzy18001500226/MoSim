within MoSimQuadrotorModel.Experiment.Runners;
model RlGainSchedulerFormalRunner
  "Formal 100 Hz whole-aircraft runner for RlGainSchedulerAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.RlGainSchedulerAttitudeThrustAdapter);
end RlGainSchedulerFormalRunner;
