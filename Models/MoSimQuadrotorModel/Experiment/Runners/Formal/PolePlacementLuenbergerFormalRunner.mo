within MoSimQuadrotorModel.Experiment.Runners.Formal;
model PolePlacementLuenbergerFormalRunner
  "Formal 100 Hz whole-aircraft runner for PolePlacementLuenbergerAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.PolePlacementLuenbergerAttitudeThrustAdapter);
end PolePlacementLuenbergerFormalRunner;
