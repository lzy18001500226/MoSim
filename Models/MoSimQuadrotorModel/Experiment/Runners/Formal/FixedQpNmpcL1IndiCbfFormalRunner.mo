within MoSimQuadrotorModel.Experiment.Runners.Formal;
model FixedQpNmpcL1IndiCbfFormalRunner
  "Formal whole-aircraft runner for the fixed QP NMPC L1 INDI CBF chain"

  extends MoSimQuadrotorModel.Experiment.Templates.IntegratedChains.FixedQpNmpcL1IndiCbf;

  Real position_ref[3];
  Real position[3];
  Real position_error_norm;

equation
  position_ref = climbePath.position_command;
  position = sensors1_1.PosMea;
  position_error_norm = sqrt((position_ref[1] - position[1]) ^ 2
    + (position_ref[2] - position[2]) ^ 2 + (position_ref[3] - position[3]) ^ 2);

  annotation(__MWORKS(hide = false, version = "26.3.0"));
end FixedQpNmpcL1IndiCbfFormalRunner;
