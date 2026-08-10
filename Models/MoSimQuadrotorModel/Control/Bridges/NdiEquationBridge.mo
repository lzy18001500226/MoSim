within MoSimQuadrotorModel.Control.Bridges;
model NdiEquationBridge
  "Nonlinear dynamic inversion route through the classic acceleration bridge"

  extends MoSimQuadrotorModel.Control.Bridges.ClassicAccelerationEquationBridge(
    controller_id = 3);

  annotation(__MWORKS(version = "26.3.0"));
end NdiEquationBridge;