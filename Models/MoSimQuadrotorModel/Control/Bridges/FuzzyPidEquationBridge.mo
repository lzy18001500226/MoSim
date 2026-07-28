within MoSimQuadrotorModel.Control.Bridges;
model FuzzyPidEquationBridge
  "Bounded fuzzy-scheduled PID equation bridge over the shared cascade-PID core"

  extends MoSimQuadrotorModel.Control.Bridges.PidAttitudeThrustCFunction;

  parameter Real algorithm_id = 3
    "MOSIM_PID_FUZZY";

equation
  algorithm_id_in = algorithm_id;

  annotation(__MWORKS(version = "26.3.0"));
end FuzzyPidEquationBridge;
