within MoSimQuadrotorModel.Control.Bridges;
model PolePlacementLuenbergerEquationBridge
  "Pole-placement and Luenberger-observer route through the classic bridge"

  extends MoSimQuadrotorModel.Control.Bridges.ClassicAccelerationEquationBridge(
    controller_id = 1);

  annotation(__MWORKS(version = "26.3.0"));
end PolePlacementLuenbergerEquationBridge;
