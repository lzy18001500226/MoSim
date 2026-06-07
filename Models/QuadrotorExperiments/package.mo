package QuadrotorExperiments
  "旧实验池与兼容入口（正式归档/对比入口已迁移到MoSimQuadrotorModel，保留旧平铺类名用于历史脚本和证据）"

  extends Modelica.Icons.Package;
  annotation(uses(
    Modelica(version = "4.0.0.TY.1"),
    QuadrotorModel));

  function saturate
    input Real u;
    input Real limit;
    output Real y;
  algorithm
    y := if u > limit then limit else if u < -limit then -limit else u;
    annotation(__MWORKS(hide=true));
  end saturate;

  // Deprecated compatibility aliases. Real definitions live under category subpackages.
  model AntiWindupFeedforwardController
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.AntiWindupFeedforwardController instead"
    extends QuadrotorExperiments.ControllerBaselines.AntiWindupFeedforwardController;
    annotation(__MWORKS(hide=true));
  end AntiWindupFeedforwardController;

  model EchoMcpStateSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.SupportModels.EchoMcpStateSmoke instead"
    extends QuadrotorExperiments.SupportModels.EchoMcpStateSmoke;
    annotation(__MWORKS(hide=true));
  end EchoMcpStateSmoke;

  model Example1AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1AWFFSysblockClosedLoop;

  model Example1AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example1AntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example1AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1AntiWindupFeedforwardPID;

  model Example1EnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example1EnhancedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example1EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1EnhancedPID;

  model Example1HelicalFigure8TrailSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1HelicalFigure8TrailSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1HelicalFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1HelicalFigure8TrailSysblockClosedLoop;

  model Example1INDISysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1INDISysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1INDISysblockClosedLoop;

  model Example1ImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example1ImprovedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example1ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1ImprovedPID;

  model Example1L1SysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1L1SysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1L1SysblockClosedLoop;

  model Example1LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1LinearMPCSysblockClosedLoop;

  model Example1Mass20AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1Mass20AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1Mass20AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20AWFFSysblockClosedLoop;

  model Example1Mass20AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1Mass20AntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1Mass20AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20AntiWindupFeedforwardPID;

  model Example1Mass20EnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20EnhancedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20EnhancedPID;

  model Example1Mass20ImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20ImprovedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20ImprovedPID;

  model Example1Mass20L1SysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1Mass20L1SysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1Mass20L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20L1SysblockClosedLoop;

  model Example1Mass20LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1Mass20LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1Mass20LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Mass20LinearMPCSysblockClosedLoop;

  model Example1Mass20PID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20PID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Mass20PID;
    annotation(__MWORKS(hide=true));
  end Example1Mass20PID;

  model Example1PlanarFigure8TrailSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example1PlanarFigure8TrailSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example1PlanarFigure8TrailSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1PlanarFigure8TrailSysblockClosedLoop;

  model Example1QPNMPCSafetyReturnLandSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1QPNMPCSafetyReturnLandSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1QPNMPCSafetyReturnLandSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1QPNMPCSafetyReturnLandSysblockClosedLoop;

  model Example1QPNMPCSafetySysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1QPNMPCSafetySysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1QPNMPCSafetySysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1QPNMPCSafetySysblockClosedLoop;

  model Example1Rotor1Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15AWFFSysblockClosedLoop;

  model Example1Rotor1Loss15AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15AntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15AntiWindupFeedforwardPID;

  model Example1Rotor1Loss15EnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15EnhancedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15EnhancedPID;

  model Example1Rotor1Loss15ImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15ImprovedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15ImprovedPID;

  model Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15L1SysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1SysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15L1SysblockClosedLoop;

  model Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor1Loss15LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15LinearMPCSysblockClosedLoop;

  model Example1Rotor1Loss15PID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15PID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor1Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15PID;

  model Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor2Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15AWFFSysblockClosedLoop;

  model Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor2Loss15PID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor2Loss15PID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor2Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15PID;

  model Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor3Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15AWFFSysblockClosedLoop;

  model Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor3Loss15PID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor3Loss15PID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor3Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15PID;

  model Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1Rotor4Loss15AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15AWFFSysblockClosedLoop;

  model Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor4Loss15PID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor4Loss15PID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1Rotor4Loss15PID;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15PID;

  model Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;

  model Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;

  model Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;

  model Example1WindGustAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1WindGustAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustAWFFSysblockClosedLoop;

  model Example1WindGustAntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1WindGustAntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1WindGustAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustAntiWindupFeedforwardPID;

  model Example1WindGustEnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustEnhancedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustEnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustEnhancedPID;

  model Example1WindGustImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustImprovedPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustImprovedPID;

  model Example1WindGustL1SysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1WindGustL1SysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1WindGustL1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustL1SysblockClosedLoop;

  model Example1WindGustLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.Example1WindGustLinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.RobustFaultScenarios.Example1WindGustLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example1WindGustLinearMPCSysblockClosedLoop;

  model Example1WindGustPID
    "Deprecated compatibility alias; use QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustPID instead"
    extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Example1WindGustPID;
    annotation(__MWORKS(hide=true));
  end Example1WindGustPID;

  model Example2AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example2AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example2AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2AWFFSysblockClosedLoop;

  model Example2AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example2AntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example2AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2AntiWindupFeedforwardPID;

  model Example2EnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example2EnhancedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example2EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2EnhancedPID;

  model Example2HelixTunedAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example2HelixTunedAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example2HelixTunedAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAWFFSysblockClosedLoop;

  model Example2HelixTunedAntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example2HelixTunedAntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example2HelixTunedAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedAntiWindupFeedforwardPID;

  model Example2HelixTunedEnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example2HelixTunedEnhancedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example2HelixTunedEnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedEnhancedPID;

  model Example2HelixTunedINDISysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example2HelixTunedINDISysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example2HelixTunedINDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2HelixTunedINDISysblockClosedLoop;

  model Example2INDISysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example2INDISysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example2INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2INDISysblockClosedLoop;

  model Example2ImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example2ImprovedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example2ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example2ImprovedPID;

  model Example2LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example2LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example2LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example2LinearMPCSysblockClosedLoop;

  model Example3AWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example3AWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example3AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3AWFFSysblockClosedLoop;

  model Example3AntiWindupFeedforwardPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example3AntiWindupFeedforwardPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example3AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Example3AntiWindupFeedforwardPID;

  model Example3EnhancedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example3EnhancedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example3EnhancedPID;
    annotation(__MWORKS(hide=true));
  end Example3EnhancedPID;

  model Example3INDISysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example3INDISysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example3INDISysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3INDISysblockClosedLoop;

  model Example3ImprovedPID
    "Deprecated compatibility alias; use QuadrotorExperiments.ControllerBaselines.Example3ImprovedPID instead"
    extends QuadrotorExperiments.ControllerBaselines.Example3ImprovedPID;
    annotation(__MWORKS(hide=true));
  end Example3ImprovedPID;

  model Example3L1SysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example3L1SysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example3L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3L1SysblockClosedLoop;

  model Example3LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.OfficialScenarios.Example3LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.OfficialScenarios.Example3LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Example3LinearMPCSysblockClosedLoop;

  model FactoryLiteTraceSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryLiteTraceSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryLiteTraceSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryLiteTraceSmoke;

  model FactoryTraceIso01FullDisplaySmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso01FullDisplaySmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso01FullDisplaySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso01FullDisplaySmoke;

  model FactoryTraceIso02ControllerOnlySmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso02ControllerOnlySmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso02ControllerOnlySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso02ControllerOnlySmoke;

  model FactoryTraceIso03PlantHoverStackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso03PlantHoverStackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso03PlantHoverStackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso03PlantHoverStackSmoke;

  model FactoryTraceIso04ControllerPlantWiringSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso04ControllerPlantWiringSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso04ControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso04ControllerPlantWiringSmoke;

  model FactoryTraceIso05CleanHoverSumSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso05CleanHoverSumSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso05CleanHoverSumSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso05CleanHoverSumSmoke;

  model FactoryTraceIso06CleanControllerPlantWiringSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso06CleanControllerPlantWiringSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso06CleanControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso06CleanControllerPlantWiringSmoke;

  model FactoryTraceIso07CleanControllerOpenFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso07CleanControllerOpenFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso07CleanControllerOpenFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso07CleanControllerOpenFeedbackSmoke;

  model FactoryTraceIso08PositionFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso08PositionFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso08PositionFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso08PositionFeedbackSmoke;

  model FactoryTraceIso09PositionAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso09PositionAttitudeFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso09PositionAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso09PositionAttitudeFeedbackSmoke;

  model FactoryTraceIso10RollFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso10RollFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso10RollFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso10RollFeedbackSmoke;

  model FactoryTraceIso11PitchFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso11PitchFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso11PitchFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso11PitchFeedbackSmoke;

  model FactoryTraceIso12RollFeedbackNegatedSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso12RollFeedbackNegatedSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso12RollFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso12RollFeedbackNegatedSmoke;

  model FactoryTraceIso13PitchFeedbackNegatedSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso13PitchFeedbackNegatedSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso13PitchFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso13PitchFeedbackNegatedSmoke;

  model FactoryTraceIso14ConstantAttitudeInputSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso14ConstantAttitudeInputSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso14ConstantAttitudeInputSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso14ConstantAttitudeInputSmoke;

  model FactoryTraceIso15TableAttitudeInputSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso15TableAttitudeInputSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso15TableAttitudeInputSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso15TableAttitudeInputSmoke;

  model FactoryTraceIso16RealExpressionAngleSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso16RealExpressionAngleSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso16RealExpressionAngleSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso16RealExpressionAngleSmoke;

  model FactoryTraceIso17SampleHoldAngleSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso17SampleHoldAngleSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso17SampleHoldAngleSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso17SampleHoldAngleSmoke;

  model FactoryTraceIso18ProjectAttitudeEstimatorSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso18ProjectAttitudeEstimatorSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso18ProjectAttitudeEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso18ProjectAttitudeEstimatorSmoke;

  model FactoryTraceIso19RollPitchEstimatorSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso19RollPitchEstimatorSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso19RollPitchEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso19RollPitchEstimatorSmoke;

  model FactoryTraceIso20RollPitchYawEstimatorSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso20RollPitchYawEstimatorSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso20RollPitchYawEstimatorSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso20RollPitchYawEstimatorSmoke;

  model FactoryTraceIso21ControllerRateAliasSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso21ControllerRateAliasSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso21ControllerRateAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso21ControllerRateAliasSmoke;

  model FactoryTraceIso22SensorDisplayReconnectSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso22SensorDisplayReconnectSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso22SensorDisplayReconnectSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso22SensorDisplayReconnectSmoke;

  model FactoryTraceIso23PositionSampleHoldBridgeSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso23PositionSampleHoldBridgeSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso23PositionSampleHoldBridgeSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso23PositionSampleHoldBridgeSmoke;

  model FactoryTraceIso24DirectAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso24DirectAttitudeFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso24DirectAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso24DirectAttitudeFeedbackSmoke;

  model FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;

  model FactoryTraceIso26ControllerOutputAliasSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso26ControllerOutputAliasSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso26ControllerOutputAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso26ControllerOutputAliasSmoke;

  model FactoryTraceIso27ActuatorInputAliasSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso27ActuatorInputAliasSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso27ActuatorInputAliasSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso27ActuatorInputAliasSmoke;

  model FactoryTraceIso28ActuatorToWrenchBridgeSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso28ActuatorToWrenchBridgeSmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso28ActuatorToWrenchBridgeSmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso28ActuatorToWrenchBridgeSmoke;

  model FactoryTraceIso29ExternalFrameWrenchBoundarySmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;

  model FactoryTraceIso30ExternalBodyStateBoundarySmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.TraceIsolation.FactoryTraceIso30ExternalBodyStateBoundarySmoke instead"
    extends QuadrotorExperiments.TraceIsolation.FactoryTraceIso30ExternalBodyStateBoundarySmoke;
    annotation(__MWORKS(hide=true));
  end FactoryTraceIso30ExternalBodyStateBoundarySmoke;

  model FormationTriangleFigure8LinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.FormationScenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.FormationScenarios.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end FormationTriangleFigure8LinearMPCSysblockClosedLoop;

  block PlannedQuinticReference
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.PlannedQuinticReference instead"
    extends QuadrotorExperiments.PlanningScenarios.PlannedQuinticReference;
    annotation(__MWORKS(hide=true));
  end PlannedQuinticReference;

  model PlanningNavigationDisplay
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay instead"
    extends QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay;
    annotation(__MWORKS(hide=true));
  end PlanningNavigationDisplay;

  model Sunray150CompleteSystemBatteryLowSysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemBatteryLowSysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemBatteryLowSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemBatteryLowSysblock;

  model Sunray150CompleteSystemGPSDropoutSysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGPSDropoutSysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGPSDropoutSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGPSDropoutSysblock;

  model Sunray150CompleteSystemGeofenceBreachSysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGeofenceBreachSysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGeofenceBreachSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGeofenceBreachSysblock;

  model Sunray150CompleteSystemGraphical_Sysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemGraphical_Sysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemGraphical_Sysblock;

  model Sunray150CompleteSystemMissionFailureSysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemMissionFailureSysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemMissionFailureSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemMissionFailureSysblock;

  model Sunray150CompleteSystemOffboardLossSysblock
    "Deprecated compatibility alias; use QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemOffboardLossSysblock instead"
    extends QuadrotorExperiments.SystemArchitecture.Sunray150CompleteSystemOffboardLossSysblock;
    annotation(__MWORKS(hide=true));
  end Sunray150CompleteSystemOffboardLossSysblock;

  model Sunray150DynamicsUpgradeHoverSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeHoverSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeHoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsUpgradeHoverSmoke;

  model Sunray150DynamicsUpgradeYawStepSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeYawStepSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsUpgradeYawStepSmoke;

  model Sunray150DynamicsWrapperHoverSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperHoverSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperHoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperHoverSmoke;

  model Sunray150DynamicsWrapperSurface
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperSurface instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperSurface;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperSurface;

  model Sunray150DynamicsWrapperYawStepSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperYawStepSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150DynamicsWrapperYawStepSmoke;

  model Sunray150PhysicalWrenchFrameAdapter
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchFrameAdapter instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchFrameAdapter;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchFrameAdapter;

  model Sunray150PhysicalWrenchHoverSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchHoverSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchHoverSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchHoverSmoke;

  model Sunray150PhysicalWrenchYawStepSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchYawStepSmoke instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150PhysicalWrenchYawStepSmoke;

  model Sunray150PlanningCorridorGateAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;

  model Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;

  model Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop instead"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;

  model Sunray150PlanningOpenBlocksColorMapReview
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview instead"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksColorMapReview;

  model Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop
    "Deprecated compatibility alias; use QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop instead"
    extends QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;

  model Sunray150RflyStyleRotorDynamics
    "Deprecated compatibility alias; use QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics instead"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics;
    annotation(__MWORKS(hide=true));
  end Sunray150RflyStyleRotorDynamics;

  model Sunray150UEDerelictLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.SceneTraceScenarios.Sunray150UEDerelictLinearMPCSysblockSmoke instead"
    extends QuadrotorExperiments.SceneTraceScenarios.Sunray150UEDerelictLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEDerelictLinearMPCSysblockSmoke;

  model Sunray150UEFactoryLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.SceneTraceScenarios.Sunray150UEFactoryLinearMPCSysblockSmoke instead"
    extends QuadrotorExperiments.SceneTraceScenarios.Sunray150UEFactoryLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEFactoryLinearMPCSysblockSmoke;

  model Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.SceneTraceScenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke instead"
    extends QuadrotorExperiments.SceneTraceScenarios.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;
    annotation(__MWORKS(hide=true));
  end Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;

  block TraceInlineReference
    "Deprecated compatibility alias; use QuadrotorExperiments.SupportModels.TraceInlineReference instead"
    extends QuadrotorExperiments.SupportModels.TraceInlineReference;
    annotation(__MWORKS(hide=true));
  end TraceInlineReference;

  model TraceLookupStandaloneSmoke
    "Deprecated compatibility alias; use QuadrotorExperiments.SupportModels.TraceLookupStandaloneSmoke instead"
    extends QuadrotorExperiments.SupportModels.TraceLookupStandaloneSmoke;
    annotation(__MWORKS(hide=true));
  end TraceLookupStandaloneSmoke;

  block TraceTableReference
    "Deprecated compatibility alias; use QuadrotorExperiments.SupportModels.TraceTableReference instead"
    extends QuadrotorExperiments.SupportModels.TraceTableReference;
    annotation(__MWORKS(hide=true));
  end TraceTableReference;

end QuadrotorExperiments;
