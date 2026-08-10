within MoSimQuadrotorModel.Control.Bridges;
model IlqrEquationBridge
  "Five-iteration iLQR equation bridge for the P4 graphical core"
  extends MoSimQuadrotorModel.Control.Bridges.PredictiveMpcEquationBridge(
    algorithm_variant = 5);
  annotation(__MWORKS(version = "26.3.0"));
end IlqrEquationBridge;