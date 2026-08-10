within MoSimQuadrotorModel.Experiment.Runners.Formal;
model RlGainSchedulerFormalRunner
  "Formal 100 Hz whole-aircraft runner for RlGainSchedulerAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.RlGainSchedulerAttitudeThrustAdapter);
end RlGainSchedulerFormalRunner;