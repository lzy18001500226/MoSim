within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model AwffSingleUavGraphicalRunner
  "Strict graphical single-UAV AWFF closed loop"

  extends MoSimQuadrotorModel.Experiment.Runners.Golden.AdapterSingleUavGoldenRunner(
    redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AWFFGraphicalRotorAdapter);
end AwffSingleUavGraphicalRunner;