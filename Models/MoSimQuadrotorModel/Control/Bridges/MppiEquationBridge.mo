within MoSimQuadrotorModel.Control.Bridges;
model MppiEquationBridge
  "Seven-sample MPPI equation bridge for the P4 graphical core"
  extends MoSimQuadrotorModel.Control.Bridges.PredictiveMpcEquationBridge(
    algorithm_variant = 6);
  annotation(__MWORKS(version = "26.3.0"));
end MppiEquationBridge;
