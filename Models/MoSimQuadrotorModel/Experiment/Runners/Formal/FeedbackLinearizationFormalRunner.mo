within MoSimQuadrotorModel.Experiment.Runners.Formal;
model FeedbackLinearizationFormalRunner
  "Formal 100 Hz whole-aircraft runner for FeedbackLinearizationAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.FeedbackLinearizationAttitudeThrustAdapter);
end FeedbackLinearizationFormalRunner;
