within MoSimQuadrotorModel.Control.Bridges;
model PassivityBasedControlEquationBridge
  "Passivity-based P2 law with its readable storage-function output"

  // The command path is identical to the P2 feedback-linearization graphical
  // core; the distinct passivity contribution is its storage calculation.
  extends MoSimQuadrotorModel.Control.Bridges.LqrBaselineEquationBridge;

  output Real storage_function_out;

protected
  Real storage_function;
equation
  storage_function = 0.335 * (velocity_error_x_out ^ 2
    + velocity_error_y_out ^ 2 + velocity_error_z_out ^ 2)
    + 0.8 * (position_error_x_out ^ 2 + position_error_y_out ^ 2)
    + 1.1 * position_error_z_out ^ 2;
  storage_function_out = storage_function;

  annotation(__MWORKS(version = "26.3.0"));
end PassivityBasedControlEquationBridge;
