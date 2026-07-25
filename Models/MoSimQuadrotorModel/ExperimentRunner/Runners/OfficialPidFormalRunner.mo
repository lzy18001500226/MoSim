within MoSimQuadrotorModel.ExperimentRunner.Runners;
model OfficialPidFormalRunner
  "Formal whole-aircraft A/B baseline for the embedded Plant Official PID"

  extends MoSimQuadrotorModel.ExperimentRunner.Runners.RotorCommandRunner(
    redeclare model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.OfficialPIDRotorAdapter);

  annotation(__MWORKS(version="26.3.0"));
end OfficialPidFormalRunner;
