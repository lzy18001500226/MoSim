within MoSimQuadrotorModel.Experiment.Runners.Experimental;
model SmcBoundaryLayerFormalRunner
  "Isolated 100 Hz whole-aircraft runner for the external-input graphical SMC probe"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.SmcBoundaryLayerAttitudeThrustAdapter);
end SmcBoundaryLayerFormalRunner;