within MoSimQuadrotorModel.Experiment.Runners.Formal;
model NeuralPidFormalRunner
  "Formal 100 Hz whole-aircraft runner for NeuralPidAttitudeThrustAdapter"

  extends MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.NeuralPidAttitudeThrustAdapter);
end NeuralPidFormalRunner;