within MoSimQuadrotorModel.Control.Bridges;
model H2StateFeedbackEquationBridge
  "H2 state-feedback route through the classic acceleration bridge"

  extends MoSimQuadrotorModel.Control.Bridges.ClassicAccelerationEquationBridge(
    controller_id = 5);

  annotation(__MWORKS(version = "26.3.0"));
end H2StateFeedbackEquationBridge;
