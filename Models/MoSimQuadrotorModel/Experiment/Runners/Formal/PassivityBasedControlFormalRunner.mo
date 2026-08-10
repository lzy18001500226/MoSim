within MoSimQuadrotorModel.Experiment.Runners.Formal;
model PassivityBasedControlFormalRunner
  "Formal 100 Hz whole-aircraft runner for PassivityBasedControlAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.PassivityBasedControlAttitudeThrustAdapter);
end PassivityBasedControlFormalRunner;