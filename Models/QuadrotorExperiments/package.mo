package QuadrotorExperiments
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "旧实验池与兼容入口（正式归档/对比入口已迁移到MoSimQuadrotorModel，保留旧平铺类名用于历史脚本和证据）"

  extends Modelica.Icons.Package;
  annotation(uses(
    Modelica(version = "4.0.0.TY.1"),
    QuadrotorModel));

  function saturate
    "Deprecated compatibility alias; canonical implementation is MoSimQuadrotorModel.saturate"
    extends MoSimQuadrotorModel.saturate;
    annotation(__MWORKS(hide=true));
  end saturate;
// Deprecated compatibility aliases. Real definitions live under category subpackages.
  model AntiWindupFeedforwardController
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.AntiWindupFeedforwardController instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.AntiWindupFeedforwardController;
    annotation(__MWORKS(hide=true));
  end AntiWindupFeedforwardController;

  model EchoMcpStateSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Support.Models.EchoMcpStateSmoke instead"
    extends MoSimQuadrotorModel.Support.Models.EchoMcpStateSmoke;
    annotation(__MWORKS(hide=true));
  end EchoMcpStateSmoke;

  model Example1AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1AWFFSysblockClosedLoop;

  model Example1AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example1AntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1AntiWindupFeedforwardPID;

  model Example1EnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example1EnhancedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1EnhancedPID;

  model Example1HelicalFigure8TrailSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1HelicalFigure8TrailSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1HelicalFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1HelicalFigure8TrailSysblockClosedLoop;

  model Example1INDISysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1INDISysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1INDISysblockClosedLoop;

  model Example1ImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example1ImprovedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example1ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1ImprovedPID;

  model Example1L1SysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1L1SysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1L1SysblockClosedLoop;

  model Example1LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1LinearMPCSysblockClosedLoop;

  model Example1Mass20AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20AWFFSysblockClosedLoop;

  model Example1Mass20AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20AntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20AntiWindupFeedforwardPID;

  model Example1Mass20EnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20EnhancedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20EnhancedPID;

  model Example1Mass20ImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20ImprovedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20ImprovedPID;

  model Example1Mass20L1SysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20L1SysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20L1SysblockClosedLoop;

  model Example1Mass20LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1Mass20LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20LinearMPCSysblockClosedLoop;

  model Example1Mass20PID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20PID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20PID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20PID;

  model Example1PlanarFigure8TrailSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example1PlanarFigure8TrailSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example1PlanarFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1PlanarFigure8TrailSysblockClosedLoop;

  model Example1QPNMPCSafetyReturnLandSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1QPNMPCSafetyReturnLandSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1QPNMPCSafetyReturnLandSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1QPNMPCSafetyReturnLandSysblockClosedLoop;

  model Example1QPNMPCSafetySysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1QPNMPCSafetySysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1QPNMPCSafetySysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1QPNMPCSafetySysblockClosedLoop;

  model Example1Rotor1Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15AWFFSysblockClosedLoop;

  model Example1Rotor1Loss15AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15AntiWindupFeedforwardPID;

  model Example1Rotor1Loss15EnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15EnhancedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15EnhancedPID;

  model Example1Rotor1Loss15ImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15ImprovedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15ImprovedPID;

  model Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15L1SysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1SysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1SysblockClosedLoop;

  model Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15LinearMPCSysblockClosedLoop;

  model Example1Rotor1Loss15PID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15PID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15PID;

  model Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor2Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15AWFFSysblockClosedLoop;

  model Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor2Loss15PID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor2Loss15PID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor2Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15PID;

  model Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor3Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15AWFFSysblockClosedLoop;

  model Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor3Loss15PID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor3Loss15PID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor3Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15PID;

  model Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor4Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15AWFFSysblockClosedLoop;

  model Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor4Loss15PID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor4Loss15PID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor4Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15PID;

  model Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustAWFFSysblockClosedLoop;

  model Example1WindGustAntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustAntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustAntiWindupFeedforwardPID;

  model Example1WindGustEnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustEnhancedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustEnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustEnhancedPID;

  model Example1WindGustImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustImprovedPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustImprovedPID;

  model Example1WindGustL1SysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustL1SysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustL1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustL1SysblockClosedLoop;

  model Example1WindGustLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustLinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.Example1WindGustLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustLinearMPCSysblockClosedLoop;

  model Example1WindGustPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustPID instead"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustPID;

  model Example2AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example2AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example2AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2AWFFSysblockClosedLoop;

  model Example2AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example2AntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2AntiWindupFeedforwardPID;

  model Example2EnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example2EnhancedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2EnhancedPID;

  model Example2HelixTunedAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example2HelixTunedAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example2HelixTunedAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAWFFSysblockClosedLoop;

  model Example2HelixTunedAntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedAntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAntiWindupFeedforwardPID;

  model Example2HelixTunedEnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedEnhancedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2HelixTunedEnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedEnhancedPID;

  model Example2HelixTunedINDISysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example2HelixTunedINDISysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example2HelixTunedINDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedINDISysblockClosedLoop;

  model Example2INDISysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example2INDISysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example2INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2INDISysblockClosedLoop;

  model Example2ImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example2ImprovedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example2ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example2ImprovedPID;

  model Example2LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example2LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example2LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2LinearMPCSysblockClosedLoop;

  model Example3AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example3AWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example3AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3AWFFSysblockClosedLoop;

  model Example3AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example3AntiWindupFeedforwardPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example3AntiWindupFeedforwardPID;

  model Example3EnhancedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example3EnhancedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example3EnhancedPID;

  model Example3INDISysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example3INDISysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example3INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3INDISysblockClosedLoop;

  model Example3ImprovedPID
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Controllers.Baselines.Example3ImprovedPID instead"
    extends MoSimQuadrotorModel.Controllers.Baselines.Example3ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example3ImprovedPID;

  model Example3L1SysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example3L1SysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example3L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3L1SysblockClosedLoop;

  model Example3LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Missions.Official.Example3LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Missions.Official.Example3LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3LinearMPCSysblockClosedLoop;

  model FactoryLiteTraceSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryLiteTraceSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryLiteTraceSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryLiteTraceSmoke;

  model FactoryTraceIso01FullDisplaySmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso01FullDisplaySmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso01FullDisplaySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso01FullDisplaySmoke;

  model FactoryTraceIso02ControllerOnlySmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso02ControllerOnlySmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso02ControllerOnlySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso02ControllerOnlySmoke;

  model FactoryTraceIso03PlantHoverStackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso03PlantHoverStackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso03PlantHoverStackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso03PlantHoverStackSmoke;

  model FactoryTraceIso04ControllerPlantWiringSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso04ControllerPlantWiringSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso04ControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso04ControllerPlantWiringSmoke;

  model FactoryTraceIso05CleanHoverSumSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso05CleanHoverSumSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso05CleanHoverSumSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso05CleanHoverSumSmoke;

  model FactoryTraceIso06CleanControllerPlantWiringSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso06CleanControllerPlantWiringSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso06CleanControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso06CleanControllerPlantWiringSmoke;

  model FactoryTraceIso07CleanControllerOpenFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso07CleanControllerOpenFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso07CleanControllerOpenFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso07CleanControllerOpenFeedbackSmoke;

  model FactoryTraceIso08PositionFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso08PositionFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso08PositionFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso08PositionFeedbackSmoke;

  model FactoryTraceIso09PositionAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso09PositionAttitudeFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso09PositionAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso09PositionAttitudeFeedbackSmoke;

  model FactoryTraceIso10RollFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso10RollFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso10RollFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso10RollFeedbackSmoke;

  model FactoryTraceIso11PitchFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso11PitchFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso11PitchFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso11PitchFeedbackSmoke;

  model FactoryTraceIso12RollFeedbackNegatedSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso12RollFeedbackNegatedSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso12RollFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso12RollFeedbackNegatedSmoke;

  model FactoryTraceIso13PitchFeedbackNegatedSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso13PitchFeedbackNegatedSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso13PitchFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso13PitchFeedbackNegatedSmoke;

  model FactoryTraceIso14ConstantAttitudeInputSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso14ConstantAttitudeInputSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso14ConstantAttitudeInputSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso14ConstantAttitudeInputSmoke;

  model FactoryTraceIso15TableAttitudeInputSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso15TableAttitudeInputSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso15TableAttitudeInputSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso15TableAttitudeInputSmoke;

  model FactoryTraceIso16RealExpressionAngleSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso16RealExpressionAngleSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso16RealExpressionAngleSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso16RealExpressionAngleSmoke;

  model FactoryTraceIso17SampleHoldAngleSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso17SampleHoldAngleSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso17SampleHoldAngleSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso17SampleHoldAngleSmoke;

  model FactoryTraceIso18ProjectAttitudeEstimatorSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso18ProjectAttitudeEstimatorSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso18ProjectAttitudeEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso18ProjectAttitudeEstimatorSmoke;

  model FactoryTraceIso19RollPitchEstimatorSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso19RollPitchEstimatorSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso19RollPitchEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso19RollPitchEstimatorSmoke;

  model FactoryTraceIso20RollPitchYawEstimatorSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso20RollPitchYawEstimatorSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso20RollPitchYawEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso20RollPitchYawEstimatorSmoke;

  model FactoryTraceIso21ControllerRateAliasSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso21ControllerRateAliasSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso21ControllerRateAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso21ControllerRateAliasSmoke;

  model FactoryTraceIso22SensorDisplayReconnectSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso22SensorDisplayReconnectSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso22SensorDisplayReconnectSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso22SensorDisplayReconnectSmoke;

  model FactoryTraceIso23PositionSampleHoldBridgeSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso23PositionSampleHoldBridgeSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso23PositionSampleHoldBridgeSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso23PositionSampleHoldBridgeSmoke;

  model FactoryTraceIso24DirectAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso24DirectAttitudeFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso24DirectAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso24DirectAttitudeFeedbackSmoke;

  model FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;

  model FactoryTraceIso26ControllerOutputAliasSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso26ControllerOutputAliasSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso26ControllerOutputAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso26ControllerOutputAliasSmoke;

  model FactoryTraceIso27ActuatorInputAliasSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso27ActuatorInputAliasSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso27ActuatorInputAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso27ActuatorInputAliasSmoke;

  model FactoryTraceIso28ActuatorToWrenchBridgeSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso28ActuatorToWrenchBridgeSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso28ActuatorToWrenchBridgeSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso28ActuatorToWrenchBridgeSmoke;

  model FactoryTraceIso29ExternalFrameWrenchBoundarySmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;

  model FactoryTraceIso30ExternalBodyStateBoundarySmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso30ExternalBodyStateBoundarySmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso30ExternalBodyStateBoundarySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso30ExternalBodyStateBoundarySmoke;

  model FormationTriangleFigure8LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Formation.Scenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Formation.Scenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end FormationTriangleFigure8LinearMPCSysblockClosedLoop;

  block PlannedQuinticReference
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.PlannedQuinticReference instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.PlannedQuinticReference;
    annotation(__MWORKS(hide=true));
  end PlannedQuinticReference;

  model PlanningNavigationDisplay
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.PlanningNavigationDisplay instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.PlanningNavigationDisplay;
    annotation(__MWORKS(hide=true));
  end PlanningNavigationDisplay;

  model Sunray150CompleteSystemBatteryLowSysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemBatteryLowSysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemBatteryLowSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemBatteryLowSysblock;

  model Sunray150CompleteSystemGPSDropoutSysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGPSDropoutSysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGPSDropoutSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGPSDropoutSysblock;

  model Sunray150CompleteSystemGeofenceBreachSysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGeofenceBreachSysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGeofenceBreachSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGeofenceBreachSysblock;

  model Sunray150CompleteSystemGraphical_Sysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGraphical_Sysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemGraphical_Sysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGraphical_Sysblock;

  model Sunray150CompleteSystemMissionFailureSysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemMissionFailureSysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemMissionFailureSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemMissionFailureSysblock;

  model Sunray150CompleteSystemOffboardLossSysblock
    "Deprecated compatibility alias; use MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemOffboardLossSysblock instead"
    extends MoSimQuadrotorModel.System.Architecture.Sunray150CompleteSystemOffboardLossSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemOffboardLossSysblock;

  model Sunray150DynamicsUpgradeHoverSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.HoverSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.HoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsUpgradeHoverSmoke;

  model Sunray150DynamicsUpgradeYawStepSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.YawStepSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.YawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsUpgradeYawStepSmoke;

  model Sunray150DynamicsWrapperHoverSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperHoverSmoke;

  model Sunray150DynamicsWrapperSurface
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.WrapperSurface instead"
    extends MoSimQuadrotorModel.Dynamics.WrapperSurface;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperSurface;

  model Sunray150DynamicsWrapperYawStepSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperYawStepSmoke;

  model Sunray150PhysicalWrenchFrameAdapter
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter instead"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchFrameAdapter;

  model Sunray150PhysicalWrenchHoverSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchHoverSmoke;

  model Sunray150PhysicalWrenchYawStepSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke instead"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchYawStepSmoke;

  model Sunray150PlanningCorridorGateAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;

  model Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;

  model Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;

  model Sunray150PlanningOpenBlocksColorMapReview
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksColorMapReview instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksColorMapReview;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksColorMapReview;

  model Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop instead"
    extends MoSimQuadrotorModel.Planning.Scenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;

  model Sunray150RflyStyleRotorDynamics
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Dynamics.RotorActuatorCore instead"
    extends MoSimQuadrotorModel.Dynamics.RotorActuatorCore;
    annotation(__MWORKS(hide=true));
  end Sunray150RflyStyleRotorDynamics;

  model Sunray150UEDerelictLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEDerelictLinearMPCSysblockSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEDerelictLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEDerelictLinearMPCSysblockSmoke;

  model Sunray150UEFactoryLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryLinearMPCSysblockSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEFactoryLinearMPCSysblockSmoke;

  model Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke instead"
    extends MoSimQuadrotorModel.SceneTrace.Scenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;

  block TraceInlineReference
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Support.Models.TraceInlineReference instead"
    extends MoSimQuadrotorModel.Support.Models.TraceInlineReference;
    annotation(__MWORKS(hide=true));
  end TraceInlineReference;

  model TraceLookupStandaloneSmoke
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Support.Models.TraceLookupStandaloneSmoke instead"
    extends MoSimQuadrotorModel.Support.Models.TraceLookupStandaloneSmoke;
    annotation(__MWORKS(hide=true));
  end TraceLookupStandaloneSmoke;

  block TraceTableReference
    "Deprecated compatibility alias; use MoSimQuadrotorModel.Support.Models.TraceTableReference instead"
    extends MoSimQuadrotorModel.Support.Models.TraceTableReference;
    annotation(__MWORKS(hide=true));
  end TraceTableReference;
  annotation(__MWORKS(hide=true));

end QuadrotorExperiments;