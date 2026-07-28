within MoSimQuadrotorModel.Experiment.Runners;
model NeuralPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for NeuralPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NeuralPidAttitudeThrustAdapter);
end NeuralPidFormalRunner;
