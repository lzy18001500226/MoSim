within MoSimQuadrotorModel.Experiment.Runners.Formal;
model TubeMpcFormalRunner
  "Formal 100 Hz whole-aircraft runner for TubeMpcAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.TubeMpcAttitudeThrustAdapter);
end TubeMpcFormalRunner;