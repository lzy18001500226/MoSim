within MoSimQuadrotorModel.Guidance.Planning;
model Sunray150PlanningOpenBlocksSingleUavMapAudit
  "Single-UAV OpenBlocks global-map review only; not an avoidance acceptance"

  extends Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.2, Tolerance = 0.0001, Interval = 0.01));
  annotation(__MWORKS(hide=true,version="26.3.0"));
end Sunray150PlanningOpenBlocksSingleUavMapAudit;