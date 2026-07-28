within MoSimQuadrotorModel.Experiment.Runners;
model H2StateFeedbackFormalRunner
  "Formal 100 Hz whole-aircraft runner for H2StateFeedbackAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.H2StateFeedbackAttitudeThrustAdapter);
end H2StateFeedbackFormalRunner;
