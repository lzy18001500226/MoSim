within MoSimQuadrotorModel.Control.Bridges;
model AdaptiveMpcEquationBridge
  "Adaptive MPC equation bridge for the P4 graphical core"
  extends MoSimQuadrotorModel.Control.Bridges.PredictiveMpcEquationBridge(
    algorithm_variant = 2);
  annotation(__MWORKS(version = "26.3.0"));
end AdaptiveMpcEquationBridge;