within MoSimQuadrotorModel.Experiment.Runners;
model PassivityBasedControlFormalRunner
  "Formal 100 Hz whole-aircraft runner for PassivityBasedControlAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.PassivityBasedControlAttitudeThrustAdapter);
end PassivityBasedControlFormalRunner;
