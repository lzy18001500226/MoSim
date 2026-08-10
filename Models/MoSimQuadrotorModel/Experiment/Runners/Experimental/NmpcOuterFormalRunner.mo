within MoSimQuadrotorModel.Experiment.Runners.Experimental;
model NmpcOuterFormalRunner
  "Isolated 100 Hz whole-aircraft runner for the external-input graphical NMPC probe"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NmpcOuterAttitudeThrustAdapter);
end NmpcOuterFormalRunner;