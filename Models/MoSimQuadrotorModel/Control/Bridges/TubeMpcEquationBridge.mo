within MoSimQuadrotorModel.Control.Bridges;
model TubeMpcEquationBridge
  "Tube MPC equation bridge for the P4 graphical core"
  extends MoSimQuadrotorModel.Control.Bridges.PredictiveMpcEquationBridge(
    algorithm_variant = 3);
  annotation(__MWORKS(version = "26.3.0"));
end TubeMpcEquationBridge;