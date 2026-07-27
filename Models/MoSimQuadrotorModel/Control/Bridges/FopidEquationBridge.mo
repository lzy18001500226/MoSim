within MoSimQuadrotorModel.Control.Bridges;
model FopidEquationBridge
  "FOPID route through the stateful fixed-memory classic CFunction core"

  extends MoSimQuadrotorModel.Control.Bridges.ClassicAccelerationEquationBridge(
    controller_id = 4);

  annotation(__MWORKS(version = "26.3.0"));
end FopidEquationBridge;
