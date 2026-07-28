within MoSimQuadrotorModel.Experiment.Runners;
model PolePlacementLuenbergerFormalRunner
  "Formal 100 Hz whole-aircraft runner for PolePlacementLuenbergerAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.PolePlacementLuenbergerAttitudeThrustAdapter);
end PolePlacementLuenbergerFormalRunner;
