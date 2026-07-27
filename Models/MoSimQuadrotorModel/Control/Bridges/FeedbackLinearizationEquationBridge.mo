within MoSimQuadrotorModel.Control.Bridges;
model FeedbackLinearizationEquationBridge
  "Feedback-linearization P2 law with the shared acceleration-to-attitude map"

  // The readable P2 graphical core has the same P/D acceleration law and
  // gravity/attitude conversion as the selected LQR graphical core.
  extends MoSimQuadrotorModel.Control.Bridges.LqrBaselineEquationBridge;

  annotation(__MWORKS(version = "26.3.0"));
end FeedbackLinearizationEquationBridge;
