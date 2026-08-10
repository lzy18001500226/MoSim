within MoSimQuadrotorModel.Control.Bridges;
model MracEquationBridge
  "MRAC route through the classic acceleration bridge"

  extends MoSimQuadrotorModel.Control.Bridges.ClassicAccelerationEquationBridge(
    controller_id = 2);

  annotation(__MWORKS(version = "26.3.0"));
end MracEquationBridge;