within MoSimQuadrotorModel.Control.Bridges;
model GainScheduledPidEquationBridge
  "Gain-scheduled PID equation bridge over the shared cascade-PID core"

  extends MoSimQuadrotorModel.Control.Bridges.PidAttitudeThrustCFunction;

  parameter Real algorithm_id = 2
    "MOSIM_PID_GAIN_SCHEDULED";

equation
  algorithm_id_in = algorithm_id;

  annotation(__MWORKS(version = "26.3.0"));
end GainScheduledPidEquationBridge;
