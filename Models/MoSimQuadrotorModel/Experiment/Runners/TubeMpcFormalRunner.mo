within MoSimQuadrotorModel.Experiment.Runners;
model TubeMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for TubeMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.TubeMpcAttitudeThrustAdapter);
end TubeMpcFormalRunner;
