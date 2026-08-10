within MoSimQuadrotorModel.Control.Bridges;
model RlGainSchedulerEquationBridge
  "Frozen RL gain-scheduler bridge over the bounded learning cascade-PID core"

  extends MoSimQuadrotorModel.Control.Bridges.TrainedNeuralResidualCFunction;

  parameter Real controller_mode = 2
    "MOSIM_LEARNING_RL_GAIN_SCHEDULER";

equation
  mode_in = controller_mode;

  annotation(__MWORKS(version = "26.3.0"));
end RlGainSchedulerEquationBridge;