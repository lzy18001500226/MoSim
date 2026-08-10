within MoSimQuadrotorModel.Control.Bridges;
model ExplicitGainScheduledMpcEquationBridge
  "Explicit gain-scheduled MPC equation bridge for the P4 graphical core"
  extends MoSimQuadrotorModel.Control.Bridges.PredictiveMpcEquationBridge(
    algorithm_variant = 4);
  annotation(__MWORKS(version = "26.3.0"));
end ExplicitGainScheduledMpcEquationBridge;