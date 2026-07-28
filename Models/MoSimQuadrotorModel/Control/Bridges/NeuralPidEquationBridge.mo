within MoSimQuadrotorModel.Control.Bridges;
model NeuralPidEquationBridge
  "Bounded neural-residual PID equation bridge over the shared cascade-PID core"

  extends MoSimQuadrotorModel.Control.Bridges.PidAttitudeThrustCFunction;

  parameter Real algorithm_id = 4
    "MOSIM_PID_NEURAL";

equation
  algorithm_id_in = algorithm_id;

  annotation(__MWORKS(version = "26.3.0"));
end NeuralPidEquationBridge;
