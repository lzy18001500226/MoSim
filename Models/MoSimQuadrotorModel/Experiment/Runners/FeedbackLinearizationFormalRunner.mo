within MoSimQuadrotorModel.Experiment.Runners;
model FeedbackLinearizationFormalRunner
  "Formal 100 Hz whole-aircraft runner for FeedbackLinearizationAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FeedbackLinearizationAttitudeThrustAdapter);
end FeedbackLinearizationFormalRunner;
