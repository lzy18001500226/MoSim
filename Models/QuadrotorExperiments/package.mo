package QuadrotorExperiments
  "Project-local experiment models for official quadrotor comparisons"

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
  end saturate;

  package OfficialScenarios
    "官方任务与控制器闭环场景（兼容旧平铺类名的分类入口）"
    model Example1AWFF
      "阶跃爬升：AWFF Sysblock 闭环"
      extends QuadrotorExperiments.Example1AWFFSysblockClosedLoop;
    end Example1AWFF;
    model Example1INDI
      "阶跃爬升：INDI / L1 组合控制闭环"
      extends QuadrotorExperiments.Example1INDISysblockClosedLoop;
    end Example1INDI;
    model Example1L1
      "阶跃爬升：L1 残差补偿闭环"
      extends QuadrotorExperiments.Example1L1SysblockClosedLoop;
    end Example1L1;
    model Example1LinearMPC
      "阶跃爬升：线性 MPC 闭环"
      extends QuadrotorExperiments.Example1LinearMPCSysblockClosedLoop;
    end Example1LinearMPC;
    model Example1PlanarFigure8Trail
      "阶跃起飞后平面 8 字轨迹留痕审查"
      extends QuadrotorExperiments.Example1PlanarFigure8TrailSysblockClosedLoop;
    end Example1PlanarFigure8Trail;
    model Example1HelicalFigure8Trail
      "阶跃起飞后螺旋 8 字轨迹留痕审查"
      extends QuadrotorExperiments.Example1HelicalFigure8TrailSysblockClosedLoop;
    end Example1HelicalFigure8Trail;
    model Example2AWFF
      "螺旋爬升：AWFF Sysblock 闭环"
      extends QuadrotorExperiments.Example2AWFFSysblockClosedLoop;
    end Example2AWFF;
    model Example2HelixTunedAWFF
      "螺旋爬升：调参 AWFF Sysblock 闭环"
      extends QuadrotorExperiments.Example2HelixTunedAWFFSysblockClosedLoop;
    end Example2HelixTunedAWFF;
    model Example2INDI
      "螺旋爬升：INDI / L1 组合控制闭环"
      extends QuadrotorExperiments.Example2INDISysblockClosedLoop;
    end Example2INDI;
    model Example2HelixTunedINDI
      "螺旋爬升：调参 INDI / L1 组合控制闭环"
      extends QuadrotorExperiments.Example2HelixTunedINDISysblockClosedLoop;
    end Example2HelixTunedINDI;
    model Example2LinearMPC
      "螺旋爬升：线性 MPC 闭环"
      extends QuadrotorExperiments.Example2LinearMPCSysblockClosedLoop;
    end Example2LinearMPC;
    model Example3AWFF
      "8 字任务：AWFF Sysblock 闭环"
      extends QuadrotorExperiments.Example3AWFFSysblockClosedLoop;
    end Example3AWFF;
    model Example3INDI
      "8 字任务：INDI / L1 组合控制闭环"
      extends QuadrotorExperiments.Example3INDISysblockClosedLoop;
    end Example3INDI;
    model Example3L1
      "8 字任务：L1 残差补偿闭环"
      extends QuadrotorExperiments.Example3L1SysblockClosedLoop;
    end Example3L1;
    model Example3LinearMPC
      "8 字任务：线性 MPC 闭环"
      extends QuadrotorExperiments.Example3LinearMPCSysblockClosedLoop;
    end Example3LinearMPC;
  end OfficialScenarios;

  package ControllerBaselines
    "控制器基线与对比模型（兼容旧平铺类名的分类入口）"
    model AntiWindupFeedforwardCore
      "AWFF 控制器核心"
      extends QuadrotorExperiments.AntiWindupFeedforwardController;
    end AntiWindupFeedforwardCore;
    model Example1AWFFBaseline
      "阶跃爬升：AWFF 控制器基线"
      extends QuadrotorExperiments.Example1AntiWindupFeedforwardPID;
    end Example1AWFFBaseline;
    model Example2AWFFBaseline
      "螺旋爬升：AWFF 控制器基线"
      extends QuadrotorExperiments.Example2AntiWindupFeedforwardPID;
    end Example2AWFFBaseline;
    model Example2HelixTunedAWFFBaseline
      "螺旋爬升：调参 AWFF 控制器基线"
      extends QuadrotorExperiments.Example2HelixTunedAntiWindupFeedforwardPID;
    end Example2HelixTunedAWFFBaseline;
    model Example3AWFFBaseline
      "8 字任务：AWFF 控制器基线"
      extends QuadrotorExperiments.Example3AntiWindupFeedforwardPID;
    end Example3AWFFBaseline;
    model Example1ImprovedPIDBaseline
      "阶跃爬升：改进 PID 对比基线"
      extends QuadrotorExperiments.Example1ImprovedPID;
    end Example1ImprovedPIDBaseline;
    model Example1EnhancedPIDBaseline
      "阶跃爬升：增强 PID 对比基线"
      extends QuadrotorExperiments.Example1EnhancedPID;
    end Example1EnhancedPIDBaseline;
    model Example2ImprovedPIDBaseline
      "螺旋爬升：改进 PID 对比基线"
      extends QuadrotorExperiments.Example2ImprovedPID;
    end Example2ImprovedPIDBaseline;
    model Example2EnhancedPIDBaseline
      "螺旋爬升：增强 PID 对比基线"
      extends QuadrotorExperiments.Example2EnhancedPID;
    end Example2EnhancedPIDBaseline;
    model Example2HelixTunedEnhancedPIDBaseline
      "螺旋爬升：调参增强 PID 对比基线"
      extends QuadrotorExperiments.Example2HelixTunedEnhancedPID;
    end Example2HelixTunedEnhancedPIDBaseline;
    model Example3ImprovedPIDBaseline
      "8 字任务：改进 PID 对比基线"
      extends QuadrotorExperiments.Example3ImprovedPID;
    end Example3ImprovedPIDBaseline;
    model Example3EnhancedPIDBaseline
      "8 字任务：增强 PID 对比基线"
      extends QuadrotorExperiments.Example3EnhancedPID;
    end Example3EnhancedPIDBaseline;
  end ControllerBaselines;

  package RobustFaultScenarios
    "鲁棒扰动、安全与电机故障场景（兼容旧平铺类名的分类入口）"
    package PIDBaselines
      "扰动/故障下的 PID 系列对比基线"
      model Mass20PID
        "质量 +20%：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1Mass20PID;
      end Mass20PID;
      model Mass20ImprovedPID
        "质量 +20%：改进 PID 对比基线"
        extends QuadrotorExperiments.Example1Mass20ImprovedPID;
      end Mass20ImprovedPID;
      model Mass20EnhancedPID
        "质量 +20%：增强 PID 对比基线"
        extends QuadrotorExperiments.Example1Mass20EnhancedPID;
      end Mass20EnhancedPID;
      model WindGustPID
        "横向阵风：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1WindGustPID;
      end WindGustPID;
      model WindGustImprovedPID
        "横向阵风：改进 PID 对比基线"
        extends QuadrotorExperiments.Example1WindGustImprovedPID;
      end WindGustImprovedPID;
      model WindGustEnhancedPID
        "横向阵风：增强 PID 对比基线"
        extends QuadrotorExperiments.Example1WindGustEnhancedPID;
      end WindGustEnhancedPID;
      model Rotor1LossPID
        "1 号电机损失：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor1Loss15PID;
      end Rotor1LossPID;
      model Rotor1LossImprovedPID
        "1 号电机损失：改进 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor1Loss15ImprovedPID;
      end Rotor1LossImprovedPID;
      model Rotor1LossEnhancedPID
        "1 号电机损失：增强 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor1Loss15EnhancedPID;
      end Rotor1LossEnhancedPID;
      model Rotor2LossPID
        "2 号电机损失：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor2Loss15PID;
      end Rotor2LossPID;
      model Rotor3LossPID
        "3 号电机损失：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor3Loss15PID;
      end Rotor3LossPID;
      model Rotor4LossPID
        "4 号电机损失：官方 PID 对比基线"
        extends QuadrotorExperiments.Example1Rotor4Loss15PID;
      end Rotor4LossPID;
    end PIDBaselines;
    model Mass20AWFFBaseline
      "质量 +20%：AWFF 控制器基线"
      extends QuadrotorExperiments.Example1Mass20AntiWindupFeedforwardPID;
    end Mass20AWFFBaseline;
    model Mass20AWFF
      "质量 +20%：AWFF 闭环"
      extends QuadrotorExperiments.Example1Mass20AWFFSysblockClosedLoop;
    end Mass20AWFF;
    model Mass20L1
      "质量 +20%：L1 残差补偿闭环"
      extends QuadrotorExperiments.Example1Mass20L1SysblockClosedLoop;
    end Mass20L1;
    model Mass20LinearMPC
      "质量 +20%：线性 MPC 闭环"
      extends QuadrotorExperiments.Example1Mass20LinearMPCSysblockClosedLoop;
    end Mass20LinearMPC;
    model WindGustAWFF
      "横向阵风：AWFF 闭环"
      extends QuadrotorExperiments.Example1WindGustAWFFSysblockClosedLoop;
    end WindGustAWFF;
    model WindGustAWFFBaseline
      "横向阵风：AWFF 控制器基线"
      extends QuadrotorExperiments.Example1WindGustAntiWindupFeedforwardPID;
    end WindGustAWFFBaseline;
    model WindGustL1
      "横向阵风：L1 残差补偿闭环"
      extends QuadrotorExperiments.Example1WindGustL1SysblockClosedLoop;
    end WindGustL1;
    model WindGustLinearMPC
      "横向阵风：线性 MPC 闭环"
      extends QuadrotorExperiments.Example1WindGustLinearMPCSysblockClosedLoop;
    end WindGustLinearMPC;
    model SafetyQPNMPC
      "安全滤波：QP/NMPC 闭环"
      extends QuadrotorExperiments.Example1QPNMPCSafetySysblockClosedLoop;
    end SafetyQPNMPC;
    model SafetyReturnLand
      "安全滤波：返航降落闭环"
      extends QuadrotorExperiments.Example1QPNMPCSafetyReturnLandSysblockClosedLoop;
    end SafetyReturnLand;
    package RotorLoss
      "单电机损失与故障分配场景"
      model Rotor1AWFF
        "1 号电机损失：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15AWFFSysblockClosedLoop;
      end Rotor1AWFF;
      model Rotor1AWFFBaseline
        "1 号电机损失：AWFF 控制器基线"
        extends QuadrotorExperiments.Example1Rotor1Loss15AntiWindupFeedforwardPID;
      end Rotor1AWFFBaseline;
      model Rotor1L1
        "1 号电机损失：L1 闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15L1SysblockClosedLoop;
      end Rotor1L1;
      model Rotor1L1FaultAllocation
        "1 号电机损失：L1 故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;
      end Rotor1L1FaultAllocation;
      model Rotor1L1OnlineFaultAllocation
        "1 号电机损失：L1 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;
      end Rotor1L1OnlineFaultAllocation;
      model Rotor1L1MultiFaultIsolation
        "1 号电机损失：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;
      end Rotor1L1MultiFaultIsolation;
      model Rotor1LinearMPC
        "1 号电机损失：线性 MPC 闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15LinearMPCSysblockClosedLoop;
      end Rotor1LinearMPC;
      model Rotor1LinearMPCOnlineFaultAllocation
        "1 号电机损失：线性 MPC 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;
      end Rotor1LinearMPCOnlineFaultAllocation;
      model Rotor2AWFF
        "2 号电机损失：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor2Loss15AWFFSysblockClosedLoop;
      end Rotor2AWFF;
      model Rotor3AWFF
        "3 号电机损失：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor3Loss15AWFFSysblockClosedLoop;
      end Rotor3AWFF;
      model Rotor4AWFF
        "4 号电机损失：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor4Loss15AWFFSysblockClosedLoop;
      end Rotor4AWFF;
      model Rotor1WindGustAWFF
        "1 号电机损失 + 阵风：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;
      end Rotor1WindGustAWFF;
      model Rotor1WindGustAWFFFaultCompensation
        "1 号电机损失 + 阵风：AWFF 故障补偿闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;
      end Rotor1WindGustAWFFFaultCompensation;
      model Rotor1WindGustL1MultiFaultIsolation
        "1 号电机损失 + 阵风：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
      end Rotor1WindGustL1MultiFaultIsolation;
      model Rotor1WindGustLinearMPCOnlineFaultAllocation
        "1 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
      end Rotor1WindGustLinearMPCOnlineFaultAllocation;
      model Rotor2WindGustAWFF
        "2 号电机损失 + 阵风：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;
      end Rotor2WindGustAWFF;
      model Rotor2L1MultiFaultIsolation
        "2 号电机损失：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;
      end Rotor2L1MultiFaultIsolation;
      model Rotor2WindGustL1MultiFaultIsolation
        "2 号电机损失 + 阵风：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
      end Rotor2WindGustL1MultiFaultIsolation;
      model Rotor2WindGustLinearMPCOnlineFaultAllocation
        "2 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
      end Rotor2WindGustLinearMPCOnlineFaultAllocation;
      model Rotor3WindGustAWFF
        "3 号电机损失 + 阵风：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;
      end Rotor3WindGustAWFF;
      model Rotor3L1MultiFaultIsolation
        "3 号电机损失：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;
      end Rotor3L1MultiFaultIsolation;
      model Rotor3WindGustL1MultiFaultIsolation
        "3 号电机损失 + 阵风：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
      end Rotor3WindGustL1MultiFaultIsolation;
      model Rotor3WindGustLinearMPCOnlineFaultAllocation
        "3 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
      end Rotor3WindGustLinearMPCOnlineFaultAllocation;
      model Rotor4WindGustAWFF
        "4 号电机损失 + 阵风：AWFF 闭环"
        extends QuadrotorExperiments.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;
      end Rotor4WindGustAWFF;
      model Rotor4L1MultiFaultIsolation
        "4 号电机损失：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;
      end Rotor4L1MultiFaultIsolation;
      model Rotor4WindGustL1MultiFaultIsolation
        "4 号电机损失 + 阵风：L1 多故障隔离闭环"
        extends QuadrotorExperiments.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
      end Rotor4WindGustL1MultiFaultIsolation;
      model Rotor4WindGustLinearMPCOnlineFaultAllocation
        "4 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
        extends QuadrotorExperiments.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
      end Rotor4WindGustLinearMPCOnlineFaultAllocation;
    end RotorLoss;
  end RobustFaultScenarios;

  package PlanningScenarios
    "规划避障与轨迹生成场景（兼容旧平铺类名的分类入口）"
    model QuinticReference
      "五次多项式参考轨迹"
      extends QuadrotorExperiments.PlannedQuinticReference;
    end QuinticReference;
    model NavigationDisplay
      "规划/导航显示与局部地图审查支撑"
      extends QuadrotorExperiments.PlanningNavigationDisplay;
    end NavigationDisplay;
    model OpenBlocksAWFF
      "开放障碍场：AWFF 规划闭环"
      extends QuadrotorExperiments.Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop;
    end OpenBlocksAWFF;
    model OpenBlocksLinearMPC
      "开放障碍场：线性 MPC 规划闭环"
      extends QuadrotorExperiments.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop;
    end OpenBlocksLinearMPC;
    model OpenBlocksColorMapReview
      "开放障碍场：颜色地图审查"
      extends QuadrotorExperiments.Sunray150PlanningOpenBlocksColorMapReview;
    end OpenBlocksColorMapReview;
    model CorridorGateAWFF
      "走廊门控场：AWFF 规划闭环"
      extends QuadrotorExperiments.Sunray150PlanningCorridorGateAWFFSysblockClosedLoop;
    end CorridorGateAWFF;
    model CorridorGateLinearMPC
      "走廊门控场：线性 MPC 规划闭环"
      extends QuadrotorExperiments.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop;
    end CorridorGateLinearMPC;
  end PlanningScenarios;

  package SceneTraceScenarios
    "UE 场景与轨迹表驱动烟测（兼容旧平铺类名的分类入口）"
    model UEFactoryLinearMPC
      "Factory 场景：线性 MPC 烟测"
      extends QuadrotorExperiments.Sunray150UEFactoryLinearMPCSysblockSmoke;
    end UEFactoryLinearMPC;
    model UEFactoryTraceTable
      "Factory 场景：轨迹表驱动烟测"
      extends QuadrotorExperiments.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke;
    end UEFactoryTraceTable;
    model UEDerelictLinearMPC
      "Derelict 场景：线性 MPC 烟测"
      extends QuadrotorExperiments.Sunray150UEDerelictLinearMPCSysblockSmoke;
    end UEDerelictLinearMPC;
  end SceneTraceScenarios;

  package TraceIsolation
    "Factory 轨迹接入隔离烟测（保留历史证据链，不作为最终模型入口）"
    model FactoryLite
      "Factory-lite 轨迹接入烟测"
      extends QuadrotorExperiments.FactoryLiteTraceSmoke;
    end FactoryLite;
    model Iso01FullDisplay
      "隔离 01：完整显示链路烟测"
      extends QuadrotorExperiments.FactoryTraceIso01FullDisplaySmoke;
    end Iso01FullDisplay;
    model Iso02ControllerOnly
      "隔离 02：控制器独立烟测"
      extends QuadrotorExperiments.FactoryTraceIso02ControllerOnlySmoke;
    end Iso02ControllerOnly;
    model Iso03PlantHoverStack
      "隔离 03：机体悬停栈烟测"
      extends QuadrotorExperiments.FactoryTraceIso03PlantHoverStackSmoke;
    end Iso03PlantHoverStack;
    model Iso04ControllerPlantWiring
      "隔离 04：控制器-机体接线烟测"
      extends QuadrotorExperiments.FactoryTraceIso04ControllerPlantWiringSmoke;
    end Iso04ControllerPlantWiring;
    model Iso05CleanHoverSum
      "隔离 05：干净悬停合力烟测"
      extends QuadrotorExperiments.FactoryTraceIso05CleanHoverSumSmoke;
    end Iso05CleanHoverSum;
    model Iso06CleanControllerPlantWiring
      "隔离 06：干净控制器-机体接线烟测"
      extends QuadrotorExperiments.FactoryTraceIso06CleanControllerPlantWiringSmoke;
    end Iso06CleanControllerPlantWiring;
    model Iso07ControllerOpenFeedback
      "隔离 07：控制器开反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso07CleanControllerOpenFeedbackSmoke;
    end Iso07ControllerOpenFeedback;
    model Iso08PositionFeedback
      "隔离 08：位置反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso08PositionFeedbackSmoke;
    end Iso08PositionFeedback;
    model Iso09PositionAttitudeFeedback
      "隔离 09：位置与姿态反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso09PositionAttitudeFeedbackSmoke;
    end Iso09PositionAttitudeFeedback;
    model Iso10RollFeedback
      "隔离 10：滚转反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso10RollFeedbackSmoke;
    end Iso10RollFeedback;
    model Iso11PitchFeedback
      "隔离 11：俯仰反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso11PitchFeedbackSmoke;
    end Iso11PitchFeedback;
    model Iso12RollFeedbackNegated
      "隔离 12：滚转反馈取反烟测"
      extends QuadrotorExperiments.FactoryTraceIso12RollFeedbackNegatedSmoke;
    end Iso12RollFeedbackNegated;
    model Iso13PitchFeedbackNegated
      "隔离 13：俯仰反馈取反烟测"
      extends QuadrotorExperiments.FactoryTraceIso13PitchFeedbackNegatedSmoke;
    end Iso13PitchFeedbackNegated;
    model Iso14ConstantAttitudeInput
      "隔离 14：常量姿态输入烟测"
      extends QuadrotorExperiments.FactoryTraceIso14ConstantAttitudeInputSmoke;
    end Iso14ConstantAttitudeInput;
    model Iso15TableAttitudeInput
      "隔离 15：表格姿态输入烟测"
      extends QuadrotorExperiments.FactoryTraceIso15TableAttitudeInputSmoke;
    end Iso15TableAttitudeInput;
    model Iso16RealExpressionAngle
      "隔离 16：RealExpression 角度烟测"
      extends QuadrotorExperiments.FactoryTraceIso16RealExpressionAngleSmoke;
    end Iso16RealExpressionAngle;
    model Iso17SampleHoldAngle
      "隔离 17：角度采样保持烟测"
      extends QuadrotorExperiments.FactoryTraceIso17SampleHoldAngleSmoke;
    end Iso17SampleHoldAngle;
    model Iso18ProjectAttitudeEstimator
      "隔离 18：项目姿态估计器烟测"
      extends QuadrotorExperiments.FactoryTraceIso18ProjectAttitudeEstimatorSmoke;
    end Iso18ProjectAttitudeEstimator;
    model Iso19RollPitchEstimator
      "隔离 19：滚转/俯仰估计器烟测"
      extends QuadrotorExperiments.FactoryTraceIso19RollPitchEstimatorSmoke;
    end Iso19RollPitchEstimator;
    model Iso20RollPitchYawEstimator
      "隔离 20：滚转/俯仰/偏航估计器烟测"
      extends QuadrotorExperiments.FactoryTraceIso20RollPitchYawEstimatorSmoke;
    end Iso20RollPitchYawEstimator;
    model Iso21RateAlias
      "隔离 21：控制器速率别名烟测"
      extends QuadrotorExperiments.FactoryTraceIso21ControllerRateAliasSmoke;
    end Iso21RateAlias;
    model Iso22SensorDisplayReconnect
      "隔离 22：传感器显示重连烟测"
      extends QuadrotorExperiments.FactoryTraceIso22SensorDisplayReconnectSmoke;
    end Iso22SensorDisplayReconnect;
    model Iso23PositionSampleHold
      "隔离 23：位置采样保持桥接烟测"
      extends QuadrotorExperiments.FactoryTraceIso23PositionSampleHoldBridgeSmoke;
    end Iso23PositionSampleHold;
    model Iso24DirectAttitudeFeedback
      "隔离 24：直接姿态反馈烟测"
      extends QuadrotorExperiments.FactoryTraceIso24DirectAttitudeFeedbackSmoke;
    end Iso24DirectAttitudeFeedback;
    model Iso25AttitudeSampleHold
      "隔离 25：姿态采样保持桥接烟测"
      extends QuadrotorExperiments.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;
    end Iso25AttitudeSampleHold;
    model Iso26ControllerOutput
      "隔离 26：控制器输出别名烟测"
      extends QuadrotorExperiments.FactoryTraceIso26ControllerOutputAliasSmoke;
    end Iso26ControllerOutput;
    model Iso27ActuatorInput
      "隔离 27：执行器输入别名烟测"
      extends QuadrotorExperiments.FactoryTraceIso27ActuatorInputAliasSmoke;
    end Iso27ActuatorInput;
    model Iso28ActuatorToWrenchBridge
      "隔离 28：执行器输入到物理力矩桥接烟测"
      extends QuadrotorExperiments.FactoryTraceIso28ActuatorToWrenchBridgeSmoke;
    end Iso28ActuatorToWrenchBridge;
    model Iso29ExternalFrameWrenchBoundary
      "隔离 29：外部 MultiBody frame 力矩边界烟测"
      extends QuadrotorExperiments.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;
    end Iso29ExternalFrameWrenchBoundary;
    model Iso30ExternalBodyStateBoundary
      "隔离 30：外部测试体状态响应边界烟测"
      extends QuadrotorExperiments.FactoryTraceIso30ExternalBodyStateBoundarySmoke;
    end Iso30ExternalBodyStateBoundary;
  end TraceIsolation;

  package DynamicsUpgrade
    "Sunray150 动力学升级与物理力矩包装（RflySim-like 结构验证）"
    model RotorDynamicsCore
      "RflySim-like 转子动力学核心"
      extends QuadrotorExperiments.Sunray150RflyStyleRotorDynamics;
    end RotorDynamicsCore;
    model RotorHoverSmoke
      "转子动力学悬停烟测"
      extends QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke;
    end RotorHoverSmoke;
    model RotorYawStepSmoke
      "转子动力学偏航阶跃烟测"
      extends QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke;
    end RotorYawStepSmoke;
    model WrapperSurface
      "动力学包装接口：电机命令到合力/合矩"
      extends QuadrotorExperiments.Sunray150DynamicsWrapperSurface;
    end WrapperSurface;
    model WrapperHoverSmoke
      "动力学包装接口悬停烟测"
      extends QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke;
    end WrapperHoverSmoke;
    model WrapperYawStepSmoke
      "动力学包装接口偏航阶跃烟测"
      extends QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke;
    end WrapperYawStepSmoke;
    model PhysicalWrenchAdapter
      "物理力/矩施加适配器"
      extends QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter;
    end PhysicalWrenchAdapter;
    model PhysicalWrenchHoverSmoke
      "物理力/矩悬停施加烟测"
      extends QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke;
    end PhysicalWrenchHoverSmoke;
    model PhysicalWrenchYawStepSmoke
      "物理力/矩偏航施加烟测"
      extends QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke;
    end PhysicalWrenchYawStepSmoke;
  end DynamicsUpgrade;

  package SystemArchitecture
    "完整系统图形化架构与失效模式烟测（非最终性能证据）"
    model CompleteSystemGraphical
      "Sunray150 完整系统图形化架构"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock;
    end CompleteSystemGraphical;
    model GPSDropout
      "完整系统：GPS 丢失烟测"
      extends QuadrotorExperiments.Sunray150CompleteSystemGPSDropoutSysblock;
    end GPSDropout;
    model BatteryLow
      "完整系统：低电量烟测"
      extends QuadrotorExperiments.Sunray150CompleteSystemBatteryLowSysblock;
    end BatteryLow;
    model OffboardLoss
      "完整系统：Offboard 心跳丢失烟测"
      extends QuadrotorExperiments.Sunray150CompleteSystemOffboardLossSysblock;
    end OffboardLoss;
    model MissionFailure
      "完整系统：任务不可行烟测"
      extends QuadrotorExperiments.Sunray150CompleteSystemMissionFailureSysblock;
    end MissionFailure;
    model GeofenceBreach
      "完整系统：地理围栏越界烟测"
      extends QuadrotorExperiments.Sunray150CompleteSystemGeofenceBreachSysblock;
    end GeofenceBreach;
  end SystemArchitecture;

  package SystemModules
    "Sunray150 系统组成模块（架构图与接口支撑）"
    block PerceptionInterface
      "感知接口模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.PerceptionInterfaceModule;
    end PerceptionInterface;
    block FlightController
      "V6X 飞控模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.V6XFlightControllerModule;
    end FlightController;
    block MissionComputer
      "ORIN NX 任务计算机模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.ORINNXMissionComputerModule;
    end MissionComputer;
    block Supervisor
      "系统监督与模式管理模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.SystemSupervisorModule;
    end Supervisor;
    block BatteryPower
      "电池与供电模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.BatteryPowerModule;
    end BatteryPower;
    block ESCDrive
      "电调驱动模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.ESCDriveModule;
    end ESCDrive;
    block AWFFController
      "AWFF 控制器接口模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.AWFFControllerModule;
    end AWFFController;
    model MotorDrive
      "电机驱动模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.MotorDriveModule;
    end MotorDrive;
    model AirframeSensor
      "机体与传感器模块"
      extends QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock.Sunray150AirframeSensorModule;
    end AirframeSensor;
  end SystemModules;

  package SupportModels
    "支撑模型、表格引用与 echo 状态烟测"
    model TraceInline
      "内联轨迹引用"
      extends QuadrotorExperiments.TraceInlineReference;
    end TraceInline;
    model TraceTable
      "轨迹表引用"
      extends QuadrotorExperiments.TraceTableReference;
    end TraceTable;
    model TraceLookupStandalone
      "轨迹查表独立烟测"
      extends QuadrotorExperiments.TraceLookupStandaloneSmoke;
    end TraceLookupStandalone;
    model EchoMcpState
      "MWORKS MCP echo 状态烟测"
      extends QuadrotorExperiments.EchoMcpStateSmoke;
    end EchoMcpState;
  end SupportModels;

  package FormationScenarios
    "多机编队场景（后续扩展入口）"
    model TriangleFigure8LinearMPC
      "三机三角编队 8 字：线性 MPC 闭环"
      extends QuadrotorExperiments.FormationTriangleFigure8LinearMPCSysblockClosedLoop;
    end TriangleFigure8LinearMPC;
  end FormationScenarios;

  model AntiWindupFeedforwardController
    "Project-owned PID controller with conditional integration and reference feedforward"
    parameter Real kp_x = 1.65;
    parameter Real ki_x = 0.0;
    parameter Real kd_x = 1.0;
    parameter Real kp_y = 1.65;
    parameter Real ki_y = 0.0;
    parameter Real kd_y = 1.0;
    parameter Real kp_z = 8.0;
    parameter Real ki_z = 6.0;
    parameter Real kd_z = 4.0;
    parameter Real kp_roll = 14.142;
    parameter Real kd_roll = 1.70;
    parameter Real kp_pitch = 14.142;
    parameter Real kd_pitch = 1.70;
    parameter Real kp_yaw = 5.0;
    parameter Real roll_pitch_cmd_limit = 12 / 57.3;
    parameter Real attitude_cmd_limit = 6.5;
    parameter Real yaw_cmd_limit = 6.5;
    parameter Real output_limit = 20.0;
    parameter Real reference_feedforward_z = 0.35;
    parameter Real reference_filter_T = 0.20;
    parameter Real position_derivative_filter_T = 0.05;
    parameter Real altitude_derivative_filter_T = 0.08;
    parameter Real attitude_derivative_filter_T = 0.03;

    Modelica.Blocks.Interfaces.RealInput position_command[3];
    Modelica.Blocks.Interfaces.RealInput position[3];
    Modelica.Blocks.Interfaces.RealInput angle[3];
    Modelica.Blocks.Interfaces.RealOutput y;
    Modelica.Blocks.Interfaces.RealOutput y1;
    Modelica.Blocks.Interfaces.RealOutput y2;
    Modelica.Blocks.Interfaces.RealOutput y3;

    Real ex;
    Real ey;
    Real ez;
    Real e_roll;
    Real e_pitch;
    Real e_yaw;
    Real ex_filter(start = 0, fixed = true);
    Real ey_filter(start = 0, fixed = true);
    Real ez_filter(start = 0, fixed = true);
    Real e_roll_filter(start = 0, fixed = true);
    Real e_pitch_filter(start = 0, fixed = true);
    Real dex;
    Real dey;
    Real dez;
    Real d_roll;
    Real d_pitch;
    Real ix(start = 0, fixed = true);
    Real iy(start = 0, fixed = true);
    Real iz(start = 0, fixed = true);
    Real x_cmd_raw;
    Real y_cmd_raw;
    Real z_cmd_raw;
    Real x_cmd;
    Real y_cmd;
    Real z_cmd;
    Real roll_cmd_raw;
    Real pitch_cmd_raw;
    Real yaw_cmd_raw;
    Real roll_cmd;
    Real pitch_cmd;
    Real yaw_cmd;
    Real z_ref_filter(start = 0, fixed = true);
    Real z_ref_rate;
    Real common;
    Real yaw_mix;
    Real pitch_mix;
    Real roll_mix;
    Real u1_raw;
    Real u2_raw;
    Real u3_raw;
    Real u4_raw;

  equation
    ex = position_command[1] - position[1];
    ey = position_command[2] - position[2];
    ez = position_command[3] - position[3];

    der(z_ref_filter) = (position_command[3] - z_ref_filter) / reference_filter_T;
    z_ref_rate = (position_command[3] - z_ref_filter) / reference_filter_T;

    der(ex_filter) = (ex - ex_filter) / position_derivative_filter_T;
    der(ey_filter) = (ey - ey_filter) / position_derivative_filter_T;
    der(ez_filter) = (ez - ez_filter) / altitude_derivative_filter_T;
    dex = (ex - ex_filter) / position_derivative_filter_T;
    dey = (ey - ey_filter) / position_derivative_filter_T;
    dez = (ez - ez_filter) / altitude_derivative_filter_T;

    x_cmd_raw = kp_x * ex + ki_x * ix + kd_x * dex;
    y_cmd_raw = kp_y * ey + ki_y * iy + kd_y * dey;
    z_cmd_raw = kp_z * ez + ki_z * iz + kd_z * dez + reference_feedforward_z * z_ref_rate;
    x_cmd = saturate(0.1 * x_cmd_raw, roll_pitch_cmd_limit);
    y_cmd = saturate(0.1 * y_cmd_raw, roll_pitch_cmd_limit);
    z_cmd = z_cmd_raw;

    der(ix) = if abs(0.1 * x_cmd_raw) < roll_pitch_cmd_limit or ex * x_cmd_raw < 0 then ex else 0;
    der(iy) = if abs(0.1 * y_cmd_raw) < roll_pitch_cmd_limit or ey * y_cmd_raw < 0 then ey else 0;
    der(iz) = if abs(z_cmd_raw) < output_limit or ez * z_cmd_raw < 0 then ez else 0;

    e_pitch = x_cmd - angle[2];
    e_roll = y_cmd + angle[1];
    e_yaw = -angle[3];

    der(e_pitch_filter) = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
    der(e_roll_filter) = (e_roll - e_roll_filter) / attitude_derivative_filter_T;
    d_pitch = (e_pitch - e_pitch_filter) / attitude_derivative_filter_T;
    d_roll = (e_roll - e_roll_filter) / attitude_derivative_filter_T;

    pitch_cmd_raw = kp_pitch * e_pitch + kd_pitch * d_pitch;
    roll_cmd_raw = kp_roll * e_roll + kd_roll * d_roll;
    yaw_cmd_raw = kp_yaw * e_yaw;
    pitch_cmd = saturate(pitch_cmd_raw, attitude_cmd_limit);
    roll_cmd = saturate(roll_cmd_raw, attitude_cmd_limit);
    yaw_cmd = saturate(yaw_cmd_raw, yaw_cmd_limit);

    common = z_cmd;
    yaw_mix = 0.707 * yaw_cmd;
    pitch_mix = 0.707 * pitch_cmd;
    roll_mix = 0.707 * roll_cmd;

    u1_raw = common + (-yaw_mix - pitch_mix + roll_mix);
    u2_raw = -(common + (yaw_mix - pitch_mix - roll_mix));
    u3_raw = common + (-yaw_mix + pitch_mix - roll_mix);
    u4_raw = -(common + (yaw_mix + pitch_mix + roll_mix));

    y = saturate(u1_raw, output_limit);
    y1 = saturate(u2_raw, output_limit);
    y2 = saturate(u3_raw, output_limit);
    y3 = saturate(u4_raw, output_limit);
  end AntiWindupFeedforwardController;

  partial model Example1ProjectControllerBase
    "Project-owned Example1 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.ClimbPath climbePath(gain(k = 1));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1ProjectControllerBase;

  partial model Example2ProjectControllerBase
    "Project-owned Example2 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.CirclePath climbePath(ramp(height = 20), sine(f = 0.05), cosine(f = 0.05, startTime = 10, phase = 0));
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2ProjectControllerBase;

  partial model Example3ProjectControllerBase
    "Project-owned Example3 clone with controller3_2 replaced by project controller"
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
      "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
    parameter Real hover_motor_speed_cmd = 53.562090367172424
      "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
      "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
    QuadrotorModel.PathPlanning.EightPath climbePath;
    QuadrotorModel.Mechanics.QuadChassis quadChassisTest17_1;
    QuadrotorModel.Electricals.Actuator actuator1_1(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_2(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_3(dcpm(wMechanical(start = hover_motor_speed_cmd)));
    QuadrotorModel.Electricals.Actuator actuator1_4(dcpm(wMechanical(start = -hover_motor_speed_cmd)));
    QuadrotorModel.Sensors.Sensors sensors1_1;
    AntiWindupFeedforwardController controller3_2;
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor[4];
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);

  equation
    connect(actuator1_1.flange_a, quadChassisTest17_1.flange_a);
    connect(actuator1_2.flange_a, quadChassisTest17_1.flange_a1);
    connect(actuator1_3.flange_a, quadChassisTest17_1.flange_a2);
    connect(actuator1_4.flange_a, quadChassisTest17_1.flange_a3);
    connect(quadChassisTest17_1.frame_a, sensors1_1.frame_a);
    connect(controller3_2.y, motor1_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(motor1_hover_sum.y, actuator1_1.u);
    connect(controller3_2.y1, motor2_delta_scale.u);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(motor2_hover_sum.y, actuator1_2.u);
    connect(controller3_2.y2, motor3_delta_scale.u);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(motor3_hover_sum.y, actuator1_3.u);
    connect(controller3_2.y3, motor4_delta_scale.u);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor4_hover_sum.y, actuator1_4.u);
    connect(sensors1_1.AngleMea, controller3_2.angle);
    connect(sensors1_1.PosMea, controller3_2.position);
    connect(climbePath.position_command, controller3_2.position_command);
    connect(actuator1_1.flange_a, speedSensor[1].flange);
    connect(actuator1_2.flange_a, speedSensor[2].flange);
    connect(actuator1_3.flange_a, speedSensor[3].flange);
    connect(actuator1_4.flange_a, speedSensor[4].flange);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3ProjectControllerBase;

  model Example1AntiWindupFeedforwardPID
    "Example1 with project-owned anti-windup and reference-feedforward controller"
    extends Example1ProjectControllerBase;
  end Example1AntiWindupFeedforwardPID;

  model Example2AntiWindupFeedforwardPID
    "Example2 with project-owned anti-windup and reference-feedforward controller"
    extends Example2ProjectControllerBase;
  end Example2AntiWindupFeedforwardPID;

  model Example2HelixTunedAntiWindupFeedforwardPID
    "Example2 AWFF PID with helix-specific lateral command authority"
    extends Example2ProjectControllerBase(
      controller3_2(
        roll_pitch_cmd_limit = 15 / 57.3,
        attitude_cmd_limit = 7.0,
        yaw_cmd_limit = 7.0));
  end Example2HelixTunedAntiWindupFeedforwardPID;

  model Example3AntiWindupFeedforwardPID
    "Example3 with project-owned anti-windup and reference-feedforward controller"
    extends Example3ProjectControllerBase;
  end Example3AntiWindupFeedforwardPID;

  model Example1Mass20AntiWindupFeedforwardPID
    "Example1 AWFF PID with +20% central body mass perturbation"
    extends Example1ProjectControllerBase(
      quadChassisTest17_1.body(m = 1.2));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20AntiWindupFeedforwardPID;

  partial model Example1WindGustBase
    "Example1 with lateral world-frame gust force connected to the chassis body"
    extends QuadrotorModel.Examples.Example1;

    parameter Real gust_force_x_N = 0.22;
    parameter Real gust_force_y_N = -0.10;
    parameter Real gust_start_s = 15.0;
    parameter Real gust_duration_s = 4.0;
    parameter Real gust_sine_amplitude_x_N = 0.08;
    parameter Real gust_sine_amplitude_y_N = 0.04;
    parameter Real gust_sine_frequency_Hz = 1.2;

    Modelica.Mechanics.MultiBody.Forces.WorldForce gustForce(
      resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
      animation = false);

  equation
    gustForce.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then 
      gust_force_x_N + gust_sine_amplitude_x_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s)) 
      else 0;
    gustForce.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then 
      gust_force_y_N + gust_sine_amplitude_y_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s)) 
      else 0;
    gustForce.force[3] = 0;
    connect(gustForce.frame_b, quadChassisTest17_1.body.frame_b);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1WindGustBase;

  partial model Example1WindGustProjectControllerBase
    "Example1 project controller clone with lateral world-frame gust force"
    extends Example1ProjectControllerBase;

    parameter Real gust_force_x_N = 0.22;
    parameter Real gust_force_y_N = -0.10;
    parameter Real gust_start_s = 15.0;
    parameter Real gust_duration_s = 4.0;
    parameter Real gust_sine_amplitude_x_N = 0.08;
    parameter Real gust_sine_amplitude_y_N = 0.04;
    parameter Real gust_sine_frequency_Hz = 1.2;

    Modelica.Mechanics.MultiBody.Forces.WorldForce gustForce(
      resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.world,
      animation = false);

  equation
    gustForce.force[1] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then 
      gust_force_x_N + gust_sine_amplitude_x_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s)) 
      else 0;
    gustForce.force[2] = if time >= gust_start_s and time <= gust_start_s + gust_duration_s then 
      gust_force_y_N + gust_sine_amplitude_y_N * sin(2 * Modelica.Constants.pi * gust_sine_frequency_Hz * (time - gust_start_s)) 
      else 0;
    gustForce.force[3] = 0;
    connect(gustForce.frame_b, quadChassisTest17_1.body.frame_b);
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1WindGustProjectControllerBase;

  model Example1WindGustAntiWindupFeedforwardPID
    "Example1 AWFF PID with lateral gust disturbance"
    extends Example1WindGustProjectControllerBase;
  end Example1WindGustAntiWindupFeedforwardPID;

  model Example1Rotor1Loss15AntiWindupFeedforwardPID
    "Example1 AWFF PID with rotor 1 lift efficiency reduced to 85%"
    extends Example1ProjectControllerBase(
      quadChassisTest17_1.gain2(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15AntiWindupFeedforwardPID;

  model Example1ImprovedPID
    "Example1 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example1(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1ImprovedPID;

  model Example1EnhancedPID
    "Example1 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example1(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1EnhancedPID;

  model Example1Mass20PID
    "Example1 baseline PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20PID;

  model Example1Mass20ImprovedPID
    "Example1 improved PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20ImprovedPID;

  model Example1Mass20EnhancedPID
    "Example1 enhanced PID with +20% central body mass perturbation"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.body(m = 1.2),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Mass20EnhancedPID;

  model Example1WindGustPID
    "Example1 baseline PID with lateral gust disturbance"
    extends Example1WindGustBase;
  end Example1WindGustPID;

  model Example1WindGustImprovedPID
    "Example1 improved PID with lateral gust disturbance"
    extends Example1WindGustBase(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
  end Example1WindGustImprovedPID;

  model Example1WindGustEnhancedPID
    "Example1 enhanced PID with lateral gust disturbance"
    extends Example1WindGustBase(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
  end Example1WindGustEnhancedPID;

  model Example1Rotor1Loss15PID
    "Example1 baseline PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15PID;

  model Example1Rotor1Loss15ImprovedPID
    "Example1 improved PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15ImprovedPID;

  model Example1Rotor1Loss15EnhancedPID
    "Example1 enhanced PID with rotor 1 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain2(k = 0.0007266293),
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor1Loss15EnhancedPID;

  model Example1Rotor2Loss15PID
    "Example1 baseline PID with rotor 2 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain3(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor2Loss15PID;

  model Example1Rotor3Loss15PID
    "Example1 baseline PID with rotor 3 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain4(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor3Loss15PID;

  model Example1Rotor4Loss15PID
    "Example1 baseline PID with rotor 4 lift efficiency reduced to 85%"
    extends QuadrotorModel.Examples.Example1(
      quadChassisTest17_1.gain5(k = 0.0007266293));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example1Rotor4Loss15PID;

  model Example2ImprovedPID
    "Example2 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2ImprovedPID;

  model Example2EnhancedPID
    "Example2 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2EnhancedPID;

  model Example2HelixTunedEnhancedPID
    "Example2 enhanced PID with helix-specific lateral command authority"
    extends QuadrotorModel.Examples.Example2(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 15 / 57.3, uMin = -15 / 57.3),
      controller3_2.limiter2(uMax = 15 / 57.3, uMin = -15 / 57.3),
      controller3_2.limiter3(uMax = 7.0, uMin = -7.0),
      controller3_2.limiter4(uMax = 7.0, uMin = -7.0),
      controller3_2.limiter5(uMax = 7.0, uMin = -7.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Tolerance = 0.0001, Interval = 0.01));
  end Example2HelixTunedEnhancedPID;

  model Example3ImprovedPID
    "Example3 with project improved PID parameter set selected by MCP tuning"
    extends QuadrotorModel.Examples.Example3(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3ImprovedPID;

  model Example3EnhancedPID
    "Example3 with explicit derivative filtering and conservative command limits"
    extends QuadrotorModel.Examples.Example3(
      controller3_2.PID3(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID4(KP = 1.65, KI = 0, KD = 1.0, der1(T = 0.05)),
      controller3_2.PID5(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID6(KP = 14.142, KI = 0, KD = 1.70, der1(T = 0.03)),
      controller3_2.PID7(KP = 8.0, KI = 6.0, KD = 4.0, der1(T = 0.08)),
      controller3_2.limiter1(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter2(uMax = 12 / 57.3, uMin = -12 / 57.3),
      controller3_2.limiter3(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter4(uMax = 6.5, uMin = -6.5),
      controller3_2.limiter5(uMax = 6.5, uMin = -6.5));
    annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 120, Tolerance = 0.0001, Interval = 0.01));
  end Example3EnhancedPID;
model Sunray150CompleteSystemGraphical_Sysblock
  "Sunray150 complete graphical system with project AWFF Sysblock data flow"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";
  parameter Real system_degraded_nav_start_s = 1e9;
  parameter Real system_degraded_nav_end_s = 1e9;
  parameter Real system_battery_voltage_drop_per_second = 0.002;
  parameter Real system_battery_low_start_s = 1e9;
  parameter Real system_battery_low_end_s = 1e9;
  parameter Real system_offboard_loss_start_s = 1e9;
  parameter Real system_offboard_loss_end_s = 1e9;
  parameter Real system_mission_failure_start_s = 1e9;
  parameter Real system_mission_failure_end_s = 1e9;
  parameter Real system_geofence_breach_start_s = 1e9;
  parameter Real system_geofence_breach_end_s = 1e9;

  block PerceptionInterfaceModule
    "Top-level perception interface: GPS/GNSS and Mid360 local-map data"
    parameter Real gps_dropout_start_s = 1e9;
    parameter Real gps_dropout_end_s = 1e9;
    parameter Real mid360_dropout_start_s = 1e9;
    parameter Real mid360_dropout_end_s = 1e9;
    parameter Real nominal_obstacle_margin_m = 5.0;
    Modelica.Blocks.Interfaces.RealInput position_raw[3] 
      annotation (Placement(transformation(origin = {-110, 20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput gps_position[3] 
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput local_position[3] 
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_margin 
      annotation (Placement(transformation(origin = {110, -35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {110, -75}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput gps_valid
      annotation (Placement(transformation(origin = {110, -105}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput mid360_valid
      annotation (Placement(transformation(origin = {110, -130}, extent = {{-5, -5}, {5, 5}})));
  equation
    gps_position = position_raw;
    local_position = position_raw;
    gps_valid = if time >= gps_dropout_start_s and time <= gps_dropout_end_s then 0 else 1;
    mid360_valid = if time >= mid360_dropout_start_s and time <= mid360_dropout_end_s then 0 else 1;
    obstacle_margin = if mid360_valid > 0.5 then nominal_obstacle_margin_m else 0.2;
    health = 0.5 * gps_valid + 0.5 * mid360_valid;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 100, 150}, fillColor = {242, 252, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {-58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://QuadrotorModel/Resources/Images/GPS.png"),
        Bitmap(origin = {58, 18}, extent = {{-48, -48}, {48, 48}}, fileName = "modelica://QuadrotorModel/Resources/Images/MId360.png"),
        Text(origin = {0, -78}, extent = {{-100, 14}, {100, -14}}, textString = "GPS + Mid360", textColor = {0, 100, 150})}));
  end PerceptionInterfaceModule;

  block V6XFlightControllerModule
    "Top-level V6X/PX6C flight-controller interface"
    parameter Real estimator_position_T = 0.08;
    parameter Real estimator_attitude_T = 0.03;
    parameter Real estimator_motor_T = 0.05;
    Modelica.Blocks.Interfaces.RealInput gps_position[3] 
      annotation (Placement(transformation(origin = {-110, 55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput attitude_raw[3] 
      annotation (Placement(transformation(origin = {-110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4] 
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput gps_valid
      annotation (Placement(transformation(origin = {-110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3] 
      annotation (Placement(transformation(origin = {110, 55}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput attitude_est[3] 
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4] 
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality
      annotation (Placement(transformation(origin = {110, -110}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode
      annotation (Placement(transformation(origin = {110, -135}, extent = {{-5, -5}, {5, 5}})));
    Real position_est_state[3](start = {0, 0, 0}, fixed = {true, true, true});
    Real attitude_est_state[3](start = {0, 0, 0}, fixed = {true, true, true});
    Real motor_speed_est_state[4](start = {53.562090367172424, -53.562090367172424, 53.562090367172424, -53.562090367172424}, fixed = {true, true, true, true});
  equation
    for i in 1:3 loop
      der(position_est_state[i]) = if gps_valid > 0.5 then (gps_position[i] - position_est_state[i]) / estimator_position_T else 0;
      der(attitude_est_state[i]) = (attitude_raw[i] - attitude_est_state[i]) / estimator_attitude_T;
      position_est[i] = position_est_state[i];
      attitude_est[i] = attitude_est_state[i];
    end for;
    for i in 1:4 loop
      der(motor_speed_est_state[i]) = (motor_speed_raw[i] - motor_speed_est_state[i]) / estimator_motor_T;
      motor_speed_est[i] = motor_speed_est_state[i];
    end for;
    estimator_quality = if gps_valid > 0.5 then 1 else 0.45;
    estimator_mode = if gps_valid > 0.5 then 1 else 2;
    health = estimator_quality;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -54}, {96, 54}}, fileName = "modelica://QuadrotorModel/Resources/Images/V6X.png"),
        Text(origin = {0, -78}, extent = {{-95, 14}, {95, -14}}, textString = "V6X / PX6C", textColor = {100, 70, 20})}));
  end V6XFlightControllerModule;

  block ORINNXMissionComputerModule
    "Top-level ORIN NX mission computer with internal trajectory source"
    parameter Real takeoff_time_s = 3.0;
    parameter Real return_altitude_m = 1.0;
    parameter Real landing_altitude_m = 0.15;
    parameter Real obstacle_warning_margin_m = 0.6;
    parameter Real estimator_degraded_threshold = 0.6;
    parameter Real degraded_nav_start_s = 1e9;
    parameter Real degraded_nav_end_s = 1e9;
    Modelica.Blocks.Interfaces.RealInput aircraft_position[3] 
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput local_position[3] 
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput obstacle_margin 
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput estimator_quality
      annotation (Placement(transformation(origin = {-110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput reference_position[3] 
      annotation (Placement(transformation(origin = {110, 50}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput yaw_reference 
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput z_reference_rate 
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput health 
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode
      annotation (Placement(transformation(origin = {110, -110}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source
      annotation (Placement(transformation(origin = {110, -135}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status
      annotation (Placement(transformation(origin = {110, -160}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput event_code
      annotation (Placement(transformation(origin = {110, -185}, extent = {{-5, -5}, {5, 5}})));
    QuadrotorModel.PathPlanning.ClimbPath trajectory(gain(k = 1));
    Real degraded_nav_active;
    Real obstacle_avoid_active;
  equation
    degraded_nav_active = if estimator_quality < estimator_degraded_threshold then 1 else if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
    obstacle_avoid_active = if obstacle_margin < obstacle_warning_margin_m then 1 else 0;
    flight_mode = if degraded_nav_active > 0.5 then 6 else if obstacle_avoid_active > 0.5 then 4 else if time < takeoff_time_s then 3 else 5;
    active_setpoint_source = if degraded_nav_active > 0.5 then 90 else if obstacle_avoid_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 40;
    safety_status = if degraded_nav_active > 0.5 then 3 else if obstacle_avoid_active > 0.5 then 2 else 0;
    event_code = if degraded_nav_active > 0.5 then 60 else if obstacle_avoid_active > 0.5 then 40 else if time < takeoff_time_s then 30 else 50;
    reference_position[1] = if flight_mode >= 6 then 0 else trajectory.position_command[1];
    reference_position[2] = if flight_mode >= 6 then 0 else trajectory.position_command[2];
    reference_position[3] = if flight_mode >= 6 then return_altitude_m else if flight_mode >= 3 then trajectory.position_command[3] else landing_altitude_m;
    yaw_reference = 0;
    z_reference_rate = 0;
    health = min(estimator_quality, if obstacle_margin >= obstacle_warning_margin_m then 1 else 0.6);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -72}, {96, 72}}, fileName = "modelica://QuadrotorModel/Resources/Images/ORIN_NX.png"),
        Text(origin = {0, -82}, extent = {{-95, 14}, {95, -14}}, textString = "ORIN NX", textColor = {80, 80, 80})}));
  end ORINNXMissionComputerModule;

  block SystemSupervisorModule
    "System-level failsafe supervisor for exported mode/event evidence"
    parameter Real degraded_nav_start_s = 1e9;
    parameter Real degraded_nav_end_s = 1e9;
    parameter Real battery_low_start_s = 1e9;
    parameter Real battery_low_end_s = 1e9;
    parameter Real offboard_loss_start_s = 1e9;
    parameter Real offboard_loss_end_s = 1e9;
    parameter Real mission_failure_start_s = 1e9;
    parameter Real mission_failure_end_s = 1e9;
    parameter Real geofence_breach_start_s = 1e9;
    parameter Real geofence_breach_end_s = 1e9;
    parameter Real battery_low_threshold = 0.1;
    parameter Real takeoff_time_s = 3.0;
    Modelica.Blocks.Interfaces.RealInput voltage_margin
      annotation (Placement(transformation(origin = {-110, 75}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput degraded_nav_active
      annotation (Placement(transformation(origin = {110, 60}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_avoid_active
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_quality
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput estimator_mode
      annotation (Placement(transformation(origin = {110, -15}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput flight_mode
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput active_setpoint_source
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput safety_status
      annotation (Placement(transformation(origin = {110, -90}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput event_code
      annotation (Placement(transformation(origin = {110, -115}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput battery_low_active
      annotation (Placement(transformation(origin = {110, -140}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput offboard_loss_active
      annotation (Placement(transformation(origin = {110, -165}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput mission_failure_active
      annotation (Placement(transformation(origin = {110, -190}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput geofence_breach_active
      annotation (Placement(transformation(origin = {110, -215}, extent = {{-5, -5}, {5, 5}})));
  equation
    degraded_nav_active = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 1 else 0;
    battery_low_active = if voltage_margin < battery_low_threshold then 1 else if time >= battery_low_start_s and time <= battery_low_end_s then 1 else 0;
    offboard_loss_active = if time >= offboard_loss_start_s and time <= offboard_loss_end_s then 1 else 0;
    mission_failure_active = if time >= mission_failure_start_s and time <= mission_failure_end_s then 1 else 0;
    geofence_breach_active = if time >= geofence_breach_start_s and time <= geofence_breach_end_s then 1 else 0;
    obstacle_avoid_active = 0;
    estimator_quality = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 0.45 else 1;
    estimator_mode = if time >= degraded_nav_start_s and time <= degraded_nav_end_s then 2 else 1;
    flight_mode = if geofence_breach_active > 0.5 then 6 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 6 else if battery_low_active > 0.5 then 6 else if degraded_nav_active > 0.5 then 6 else if time < takeoff_time_s then 3 else 5;
    active_setpoint_source = if geofence_breach_active > 0.5 then 94 else if mission_failure_active > 0.5 then 93 else if offboard_loss_active > 0.5 then 92 else if battery_low_active > 0.5 then 91 else if degraded_nav_active > 0.5 then 90 else if time < takeoff_time_s then 30 else 40;
    safety_status = if geofence_breach_active > 0.5 then 7 else if mission_failure_active > 0.5 then 6 else if offboard_loss_active > 0.5 then 5 else if battery_low_active > 0.5 then 4 else if degraded_nav_active > 0.5 then 3 else 0;
    event_code = if geofence_breach_active > 0.5 then 64 else if mission_failure_active > 0.5 then 63 else if offboard_loss_active > 0.5 then 62 else if battery_low_active > 0.5 then 61 else if degraded_nav_active > 0.5 then 60 else if time < takeoff_time_s then 30 else 50;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {120, 0, 0}, fillColor = {255, 245, 245}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 18}, extent = {{-95, 25}, {95, -25}}, textString = "System", textColor = {120, 0, 0}),
        Text(origin = {0, -38}, extent = {{-95, 25}, {95, -25}}, textString = "Supervisor", textColor = {120, 0, 0})}));
  end SystemSupervisorModule;

  block BatteryPowerModule
    "Battery power source abstraction for system-level graphical review"
    parameter Real nominal_voltage = 16.8;
    parameter Real low_voltage = 14.0;
    parameter Real voltage_drop_per_second = 0.002;
    Modelica.Blocks.Interfaces.RealOutput bus_voltage
      annotation (Placement(transformation(origin = {110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput power_ok
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput voltage_margin
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-5, -5}, {5, 5}})));
  equation
    bus_voltage = max(low_voltage, nominal_voltage - voltage_drop_per_second * time);
    voltage_margin = max(0, (bus_voltage - low_voltage) / (nominal_voltage - low_voltage));
    power_ok = if voltage_margin > 0.05 then 1 else 0;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {250, 250, 250}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 8}, extent = {{-96, -62}, {96, 62}}, fileName = "modelica://QuadrotorModel/Resources/Images/Battery.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "Battery", textColor = {80, 80, 80})}));
  end BatteryPowerModule;

  block ESCDriveModule
    "Electronic speed controller abstraction between control allocation and motors"
    parameter Real nominal_voltage = 16.8;
    parameter Real motor_limit_abs = 80.0;
    Modelica.Blocks.Interfaces.RealInput motor_command_raw[4]
      annotation (Placement(transformation(origin = {-110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput bus_voltage
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput power_ok
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4]
      annotation (Placement(transformation(origin = {110, 35}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput esc_health[4]
      annotation (Placement(transformation(origin = {110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput saturation_ratio_est
      annotation (Placement(transformation(origin = {110, -65}, extent = {{-5, -5}, {5, 5}})));
    Real voltage_scale;
    Real saturated_count;
  equation
    voltage_scale = max(0.0, min(1.0, bus_voltage / nominal_voltage));
    saturated_count =
      (if abs(motor_command_raw[1] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[2] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[3] * voltage_scale) >= motor_limit_abs then 1 else 0) +
      (if abs(motor_command_raw[4] * voltage_scale) >= motor_limit_abs then 1 else 0);
    for i in 1:4 loop
      motor_command[i] = if power_ok > 0.5 then max(-motor_limit_abs, min(motor_limit_abs, motor_command_raw[i] * voltage_scale)) else 0;
      esc_health[i] = power_ok * voltage_scale;
    end for;
    saturation_ratio_est = saturated_count / 4;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {70, 70, 120}, fillColor = {246, 246, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 8}, extent = {{-96, -62}, {96, 62}}, fileName = "modelica://QuadrotorModel/Resources/Images/ESC.png"),
        Text(origin = {0, -78}, extent = {{-90, 14}, {90, -14}}, textString = "ESC", textColor = {70, 70, 120})}));
  end ESCDriveModule;

  block AWFFControllerModule
    "Encapsulated AWFF graphical controller, error generation, hover trim, and motor command scaling"
    parameter Real hover_motor_speed_cmd = 53.562090367172424;
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604;
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd;
    Modelica.Blocks.Interfaces.RealInput reference_position[3] 
      annotation (Placement(transformation(origin = {-110, 70}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput position_est[3] 
      annotation (Placement(transformation(origin = {-110, 25}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput attitude_est[3] 
      annotation (Placement(transformation(origin = {-110, -20}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput yaw_reference 
      annotation (Placement(transformation(origin = {-110, -60}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealInput z_reference_rate 
      annotation (Placement(transformation(origin = {-110, -90}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4] 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));

    Modelica.Blocks.Math.Feedback x_error;
    Modelica.Blocks.Math.Feedback y_error;
    Modelica.Blocks.Math.Feedback z_error;
    AWFF_FullControllerEquation_Sysblock controller;
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
  equation
    connect(reference_position[1], x_error.u1);
    connect(position_est[1], x_error.u2);
    connect(reference_position[2], y_error.u1);
    connect(position_est[2], y_error.u2);
    connect(reference_position[3], z_error.u1);
    connect(position_est[3], z_error.u2);
    connect(x_error.y, controller.x_error);
    connect(y_error.y, controller.y_error);
    connect(z_error.y, controller.z_error);
    connect(z_reference_rate, controller.z_ref_rate);
    connect(attitude_est[1], controller.roll_mea);
    connect(attitude_est[2], controller.pitch_mea);
    connect(attitude_est[3], controller.yaw_mea);
    connect(yaw_reference, controller.yaw_ref);
    connect(controller.y, motor1_delta_scale.u);
    connect(controller.y1, motor2_delta_scale.u);
    connect(controller.y2, motor3_delta_scale.u);
    connect(controller.y3, motor4_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor1_hover_sum.y, motor_command[1]);
    connect(motor2_hover_sum.y, motor_command[2]);
    connect(motor3_hover_sum.y, motor_command[3]);
    connect(motor4_hover_sum.y, motor_command[4]);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 130, 0}, fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 45}, {70, -45}}, lineColor = {0, 130, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 5}, extent = {{-65, 25}, {65, -25}}, textString = "AWFF", textColor = {0, 130, 0}),
        Text(origin = {0, -72}, extent = {{-90, 15}, {90, -15}}, textString = "controller", textColor = {0, 130, 0})}));
  end AWFFControllerModule;

  model MotorDriveModule
    "Motor actuator with speed feedback, shown as one top-level motor block"
    parameter Real initial_speed = 53.562090367172424;
    Modelica.Blocks.Interfaces.RealInput command 
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput speed 
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange 
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    QuadrotorModel.Electricals.Actuator actuator(dcpm(wMechanical(start = initial_speed)));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor;
  equation
    connect(command, actuator.u);
    connect(actuator.flange_a, flange);
    connect(actuator.flange_a, speedSensor.flange);
    connect(speedSensor.w, speed);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {130, 0, 130}, fillColor = {252, 244, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 14}, extent = {{-96, -55}, {96, 55}}, fileName = "modelica://QuadrotorModel/Resources/Images/motor.png"),
        Text(origin = {0, -80}, extent = {{-80, 14}, {80, -14}}, textString = "%name", textColor = {130, 0, 130})}));
  end MotorDriveModule;

  model Sunray150AirframeSensorModule
    "Sunray150 airframe, rotor flanges, and sensor outputs"
    Modelica.Mechanics.Rotational.Interfaces.Flange_a rotor_flange[4] 
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput position[3] 
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-5, -5}, {5, 5}})));
    Modelica.Blocks.Interfaces.RealOutput attitude[3] 
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-5, -5}, {5, 5}})));
    QuadrotorModel.Mechanics.QuadChassis chassis;
    QuadrotorModel.Sensors.Sensors sensors;
  equation
    connect(rotor_flange[1], chassis.flange_a);
    connect(rotor_flange[2], chassis.flange_a1);
    connect(rotor_flange[3], chassis.flange_a2);
    connect(rotor_flange[4], chassis.flange_a3);
    connect(chassis.frame_a, sensors.frame_a);
    connect(sensors.PosMea, position);
    connect(sensors.AngleMea, attitude);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {160, 80, 0}, fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 10}, extent = {{-96, -96}, {96, 96}}, fileName = "modelica://QuadrotorModel/Resources/Images/Sunray150.png"),
        Text(origin = {0, -86}, extent = {{-95, 14}, {95, -14}}, textString = "Sunray150", textColor = {160, 80, 0})}));
  end Sunray150AirframeSensorModule;

  PerceptionInterfaceModule perception 
    annotation (Placement(transformation(origin = {-760, -145}, extent = {{-135, -135}, {135, 135}})));
  V6XFlightControllerModule flight_controller 
    annotation (Placement(transformation(origin={-275,-230},
extent={{-125,-125},{125,125}})));
  ORINNXMissionComputerModule mission_computer 
    annotation (Placement(transformation(origin = {-760, 170}, extent = {{-130, -130}, {130, 130}})));
  SystemSupervisorModule system_supervisor(
    degraded_nav_start_s = system_degraded_nav_start_s,
    degraded_nav_end_s = system_degraded_nav_end_s,
    battery_low_start_s = system_battery_low_start_s,
    battery_low_end_s = system_battery_low_end_s,
    offboard_loss_start_s = system_offboard_loss_start_s,
    offboard_loss_end_s = system_offboard_loss_end_s,
    mission_failure_start_s = system_mission_failure_start_s,
    mission_failure_end_s = system_mission_failure_end_s,
    geofence_breach_start_s = system_geofence_breach_start_s,
    geofence_breach_end_s = system_geofence_breach_end_s)
    annotation (Placement(transformation(origin = {-455, 300}, extent = {{-70, -70}, {70, 70}})));
  BatteryPowerModule battery(voltage_drop_per_second = system_battery_voltage_drop_per_second)
    annotation (Placement(transformation(origin = {-90, -315}, extent = {{-72, -72}, {72, 72}})));
  AWFFControllerModule controller(
    hover_motor_speed_cmd = hover_motor_speed_cmd,
    legacy_hover_motor_speed_cmd = legacy_hover_motor_speed_cmd,
    motor_command_scale = motor_command_scale) 
    annotation (Placement(transformation(origin={-285,149},
extent={{-110,-110},{110,110}})));
  ESCDriveModule esc
    annotation (Placement(transformation(origin = {-20, -90}, extent = {{-80, -80}, {80, 80}})));
  MotorDriveModule motor1(initial_speed = hover_motor_speed_cmd) 
    annotation (Placement(transformation(origin = {250, 255}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor2(initial_speed = -hover_motor_speed_cmd) 
    annotation (Placement(transformation(origin = {250, 85}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor3(initial_speed = hover_motor_speed_cmd) 
    annotation (Placement(transformation(origin = {250, -85}, extent = {{-72, -72}, {72, 72}})));
  MotorDriveModule motor4(initial_speed = -hover_motor_speed_cmd) 
    annotation (Placement(transformation(origin = {250, -255}, extent = {{-72, -72}, {72, 72}})));
  Sunray150AirframeSensorModule airframe 
    annotation (Placement(transformation(origin = {630, 0}, extent = {{-150, -150}, {150, 150}})));
  Real system_degraded_nav_active;
  Real system_obstacle_avoid_active;
  Real system_estimator_quality;
  Real system_estimator_mode;
  Real system_flight_mode;
  Real system_active_setpoint_source;
  Real system_failsafe_setpoint_source;
  Real system_safety_status;
  Real system_failsafe_safety_status;
  Real system_failsafe_status_code;
  Real system_failsafe_source_code;
  Real system_event_code;
  Real system_failsafe_event_code;
  Real system_battery_voltage;
  Real system_voltage_margin;
  Real system_esc_saturation_ratio;
  Real system_battery_low_active;
  Real system_offboard_loss_active;
  Real system_mission_failure_active;
  Real system_geofence_breach_active;
  Real system_supervisor_keepalive;

equation
  system_degraded_nav_active = system_supervisor.degraded_nav_active;
  system_obstacle_avoid_active = system_supervisor.obstacle_avoid_active;
  system_estimator_quality = system_supervisor.estimator_quality;
  system_estimator_mode = system_supervisor.estimator_mode;
  system_flight_mode = system_supervisor.flight_mode;
  system_active_setpoint_source = system_supervisor.active_setpoint_source;
  system_safety_status = system_supervisor.safety_status;
  system_battery_voltage = battery.bus_voltage;
  system_voltage_margin = battery.voltage_margin;
  system_esc_saturation_ratio = esc.saturation_ratio_est;
  system_battery_low_active = system_supervisor.battery_low_active;
  system_offboard_loss_active = system_supervisor.offboard_loss_active;
  system_mission_failure_active = system_supervisor.mission_failure_active;
  system_geofence_breach_active = system_supervisor.geofence_breach_active;
  system_failsafe_safety_status = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 7 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 6 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 5 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 4 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 3 else 0;
  system_failsafe_setpoint_source = if system_failsafe_safety_status >= 3 then system_failsafe_safety_status + 87 else if time < 3.0 then 30 else 40;
  system_failsafe_event_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 64 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 63 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 62 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 61 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 60 else if time < 3.0 then 30 else 50;
  system_failsafe_status_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 7 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 6 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 5 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 4 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 3 else 0;
  system_failsafe_source_code = if time >= system_geofence_breach_start_s and time <= system_geofence_breach_end_s then 94 else if time >= system_mission_failure_start_s and time <= system_mission_failure_end_s then 93 else if time >= system_offboard_loss_start_s and time <= system_offboard_loss_end_s then 92 else if battery.voltage_margin < 0.1 or (time >= system_battery_low_start_s and time <= system_battery_low_end_s) then 91 else if time >= system_degraded_nav_start_s and time <= system_degraded_nav_end_s then 90 else if time < 3.0 then 30 else 40;
  system_event_code = system_failsafe_event_code;
  system_supervisor_keepalive = 0.001 * system_event_code + 0.001 * system_estimator_quality + 0.001 * system_battery_low_active + 0.001 * system_offboard_loss_active + 0.001 * system_mission_failure_active + 0.001 * system_geofence_breach_active;
  connect(airframe.position, perception.position_raw) 
    annotation (Line(points = {{792, 68}, {825, 68}, {825, -385}, {-950, -385}, {-950, -124}, {-909, -124}}, color = {110, 130, 145}, thickness = 0.08));
  connect(perception.gps_position, flight_controller.gps_position) 
    annotation (Line(origin={0,0},
points={{-611.5,-84.25},{-420.75,-84.25},{-420.75,-161.25},{-412.5,-161.25}},
color={110,130,145},
thickness=0.08));
  flight_controller.gps_valid = perception.gps_valid;
  connect(perception.local_position, mission_computer.local_position) 
    annotation (Line(points = {{-611, -140}, {-575, -140}, {-575, 170}, {-903, 170}}, color = {110, 130, 145}, thickness = 0.08));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin) 
    annotation (Line(points = {{-611, -182}, {-560, -182}, {-560, 122}, {-903, 122}}, color = {110, 130, 145}, thickness = 0.08));
  mission_computer.estimator_quality = flight_controller.estimator_quality;
  connect(airframe.attitude, flight_controller.attitude_raw) 
    annotation (Line(origin={0,0},
points={{795,0},{804.5,0},{804.5,-357},{-420.75,-357},{-420.75,-217.5},{-412.5,-217.5}},
color={110,130,145},
thickness=0.08));
  connect(motor1.speed, flight_controller.motor_speed_raw[1]) 
    annotation (Line(origin={0,0},
points={{329.2,222.6},{-420.75,222.6},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor2.speed, flight_controller.motor_speed_raw[2]) 
    annotation (Line(origin={0,0},
points={{329.2,52.6},{334.8,52.6},{334.8,145},{-420.75,145},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor3.speed, flight_controller.motor_speed_raw[3]) 
    annotation (Line(origin={0,0},
points={{329.2,-117.4},{334.8,-117.4},{334.8,-357},{-420.75,-357},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(motor4.speed, flight_controller.motor_speed_raw[4]) 
    annotation (Line(origin={0,0},
points={{329.2,-287.4},{334.8,-287.4},{334.8,-357},{-420.75,-357},{-420.75,-286.25},{-412.5,-286.25}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.position_est, mission_computer.aircraft_position) 
    annotation (Line(origin={0,0},
points={{-137.5,-161.25},{33.4584,-161.25},{33.4584,302},{-911.5,302},{-911.5,222},{-903,222}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.reference_position, controller.reference_position) 
    annotation (Line(origin={0,0},
points={{-617,235},{-413.5,235},{-413.5,226},{-406,226}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.position_est, controller.position_est) 
    annotation (Line(origin={0,0},
points={{-137.5,-161.25},{33.4584,-161.25},{33.4584,261},{-413.5,261},{-413.5,176.5},{-406,176.5}},
color={110,130,145},
thickness=0.08));
  connect(flight_controller.attitude_est, controller.attitude_est) 
    annotation (Line(origin={0,0},
points={{-137.5,-217.5},{33.4584,-217.5},{33.4584,261},{-413.5,261},{-413.5,127},{-406,127}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.yaw_reference, controller.yaw_reference) 
    annotation (Line(origin={0,0},
points={{-617,176.5},{-413.5,176.5},{-413.5,83},{-406,83}},
color={110,130,145},
thickness=0.08));
  connect(mission_computer.z_reference_rate, controller.z_reference_rate) 
    annotation (Line(origin={0,0},
points={{-617,118},{-413.5,118},{-413.5,50},{-406,50}},
color={110,130,145},
thickness=0.08));
  connect(controller.motor_command, esc.motor_command_raw)
    annotation (Line(points = {{-164, 149}, {-120, 149}, {-120, -54}, {-108, -54}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.bus_voltage, esc.bus_voltage)
    annotation (Line(points = {{-11, -286}, {-120, -286}, {-120, -90}, {-108, -90}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.power_ok, esc.power_ok)
    annotation (Line(points = {{-11, -315}, {-130, -315}, {-130, -126}, {-108, -126}}, color = {110, 130, 145}, thickness = 0.08));
  connect(battery.voltage_margin, system_supervisor.voltage_margin)
    annotation (Line(points = {{-11, -344}, {20, -344}, {20, 352}, {-532, 352}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[1], motor1.command)
    annotation (Line(points = {{68, -62}, {95, -62}, {95, 255}, {171, 255}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[2], motor2.command)
    annotation (Line(points = {{68, -62}, {132, -62}, {132, 85}, {171, 85}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[3], motor3.command)
    annotation (Line(points = {{68, -62}, {132, -62}, {132, -85}, {171, -85}}, color = {110, 130, 145}, thickness = 0.08));
  connect(esc.motor_command[4], motor4.command)
    annotation (Line(points = {{68, -62}, {95, -62}, {95, -255}, {171, -255}}, color = {110, 130, 145}, thickness = 0.08));
  connect(motor1.flange, airframe.rotor_flange[1]) 
    annotation (Line(points = {{330, 288}, {430, 288}, {430, 60}, {465, 60}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor2.flange, airframe.rotor_flange[2]) 
    annotation (Line(points = {{330, 118}, {440, 118}, {440, 72}, {465, 72}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor3.flange, airframe.rotor_flange[3]) 
    annotation (Line(points = {{330, -52}, {440, -52}, {440, 84}, {465, 84}}, color = {115, 115, 115}, thickness = 0.1));
  connect(motor4.flange, airframe.rotor_flange[4]) 
    annotation (Line(points = {{330, -222}, {430, -222}, {430, 96}, {465, 96}}, color = {115, 115, 115}, thickness = 0.1));

  annotation(
    Diagram(coordinateSystem(extent={{-980,-430},{850,380}},
grid={5,5}),graphics = {Rectangle(origin={-760,10},
lineColor={0,0,127},
pattern=LinePattern.Dash,
extent={{-180,320},{180,-355}}), Text(origin={-760,355},
lineColor={0,0,127},
extent={{-150,14},{150,-14}},
textString="mission and perception",
textColor={0,0,127}), Rectangle(origin={-430,-145},
lineColor={100,70,20},
pattern=LinePattern.Dash,
extent={{-150,130},{150,-130}}), Text(origin={-270,-70},
lineColor={100,70,20},
extent={{-125,14},{125,-14}},
textString="flight controller",
textColor={100,70,20}), Rectangle(origin={-120,40},
lineColor={0,130,0},
pattern=LinePattern.Dash,
extent={{-145,150},{145,-150}}), Text(origin={-285,231},
lineColor={0,130,0},
extent={{-115,14},{115,-14}},
textString="control law",
textColor={0,130,0}), Rectangle(origin={-55,-205},
lineColor={70,70,120},
pattern=LinePattern.Dash,
extent={{-125,175},{125,-190}}), Text(origin={-55,-395},
lineColor={70,70,120},
extent={{-105,14},{105,-14}},
textString="power and ESC",
textColor={70,70,120}), Rectangle(origin={250,0},
lineColor={130,0,130},
pattern=LinePattern.Dash,
extent={{-100,340},{100,-340}}), Text(origin={250,360},
lineColor={130,0,130},
extent={{-95,14},{95,-14}},
textString="motor drives",
textColor={130,0,130}), Rectangle(origin={630,0},
lineColor={160,80,0},
pattern=LinePattern.Dash,
extent={{-180,185},{180,-185}}), Text(origin={630,210},
lineColor={160,80,0},
extent={{-130,14},{130,-14}},
textString="Sunray150 airframe",
textColor={160,80,0})}),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemGraphical_Sysblock;

model Sunray150CompleteSystemGPSDropoutSysblock
  "Complete Sunray150 system smoke case with GPS dropout triggering degraded navigation mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_degraded_nav_start_s = 0.35,
    system_degraded_nav_end_s = 0.85,
    perception(gps_dropout_start_s = 0.35, gps_dropout_end_s = 0.85),
    mission_computer(estimator_degraded_threshold = 0.6, degraded_nav_start_s = 0.35, degraded_nav_end_s = 0.85));
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemGPSDropoutSysblock;

model Sunray150CompleteSystemBatteryLowSysblock
  "Complete Sunray150 system smoke case with battery low triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_battery_voltage_drop_per_second = 8.0);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemBatteryLowSysblock;

model Sunray150CompleteSystemOffboardLossSysblock
  "Complete Sunray150 system smoke case with offboard heartbeat loss triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_offboard_loss_start_s = 0.35,
    system_offboard_loss_end_s = 0.85);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemOffboardLossSysblock;

model Sunray150CompleteSystemMissionFailureSysblock
  "Complete Sunray150 system smoke case with infeasible mission triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_mission_failure_start_s = 0.35,
    system_mission_failure_end_s = 0.85);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemMissionFailureSysblock;

model Sunray150CompleteSystemGeofenceBreachSysblock
  "Complete Sunray150 system smoke case with geofence breach triggering return mode"
  extends Sunray150CompleteSystemGraphical_Sysblock(
    system_geofence_breach_start_s = 0.35,
    system_geofence_breach_end_s = 0.85);
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemGeofenceBreachSysblock;

model Sunray150RflyStyleRotorDynamics
  "Experimental Sunray150 rotor dynamics core: command lag, thrust, yaw reaction torque, and rotor-center moment"
  parameter Real mass_kg = 1.0
    "source=SDF_migration; not a measured Sunray150 takeoff mass";
  parameter Real lift_coefficient = 0.000854858
    "source=SDF_migration; Sunray motorConstant scaled by rotorVelocitySlowdownSim^2 for MWORKS visual rotor speed";
  parameter Real moment_constant = 0.06
    "source=SDF_migration; Gazebo/Sunray yaw moment ratio seed, not ULog identified";
  parameter Real time_constant_up = 0.0125
    "source=SDF_migration; Sunray SDF motor plugin timeConstantUp";
  parameter Real time_constant_down = 0.025
    "source=SDF_migration; Sunray SDF motor plugin timeConstantDown";
  parameter Real hover_motor_speed_cmd = sqrt(mass_kg * 9.81 / (4 * lift_coefficient))
    "MWORKS visual rotor hover speed seed; physical Sunray rotor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real rotor_center[4, 3] = [
    0.053745, -0.053740, -0.014052;
    0.053746,  0.053759, -0.014052;
   -0.053761,  0.053760, -0.014052;
   -0.053761, -0.053739, -0.014052]
    "source=user-reviewed DAE screw-pair fit, mapped to MWORKS Dronefixed1..4 order";
  parameter Real spin_command_sign[4] = {1, -1, 1, -1}
    "Existing MWORKS actuator command sign convention; requires PX4 motor-order validation before allocation claims";
  parameter Real yaw_direction[4] = {1, -1, 1, -1}
    "source=Sunray SDF turningDirection mapped to MWORKS Dronefixed1..4 order; positive is an experimental convention";
  Real motor_command[4](each unit = "rad/s")
    "Signed visual rotor speed command";
  Real omega[4](start = {hover_motor_speed_cmd, -hover_motor_speed_cmd, hover_motor_speed_cmd, -hover_motor_speed_cmd}, each unit = "rad/s")
    "Lagged signed visual rotor speed";
  Real motor_tau[4](each unit = "s");
  Real thrust[4](each unit = "N")
    "Per-rotor thrust Ct * omega^2";
  Real yaw_reaction_moment[4](each unit = "N.m")
    "Per-rotor reaction yaw moment Cm * thrust";
  Real rotor_arm_moment[4, 3](each unit = "N.m")
    "Per-rotor moment from r_cross_F plus yaw reaction moment";
  Real total_thrust(unit = "N");
  Real total_moment_body[3](each unit = "N.m");
  Real hover_thrust_error(unit = "N");
equation
  for i in 1:4 loop
    motor_tau[i] = if abs(motor_command[i]) > abs(omega[i]) then time_constant_up else time_constant_down;
    der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i];
    thrust[i] = lift_coefficient * omega[i] * omega[i];
    yaw_reaction_moment[i] = yaw_direction[i] * moment_constant * thrust[i];
    rotor_arm_moment[i, 1] = rotor_center[i, 2] * thrust[i];
    rotor_arm_moment[i, 2] = -rotor_center[i, 1] * thrust[i];
    rotor_arm_moment[i, 3] = yaw_reaction_moment[i];
  end for;
  total_thrust = sum(thrust);
  total_moment_body[1] = sum({rotor_arm_moment[i, 1] for i in 1:4});
  total_moment_body[2] = sum({rotor_arm_moment[i, 2] for i in 1:4});
  total_moment_body[3] = sum({rotor_arm_moment[i, 3] for i in 1:4});
  hover_thrust_error = total_thrust - mass_kg * 9.81;
end Sunray150RflyStyleRotorDynamics;

model Sunray150DynamicsUpgradeHoverSmoke
  "Hover smoke for the experimental Sunray150 rotor dynamics upgrade"
  Sunray150RflyStyleRotorDynamics dynamics;
equation
  dynamics.motor_command = {
    dynamics.spin_command_sign[1] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[2] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[3] * dynamics.hover_motor_speed_cmd,
    dynamics.spin_command_sign[4] * dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150DynamicsUpgradeHoverSmoke;

model Sunray150DynamicsUpgradeYawStepSmoke
  "Yaw-step smoke for the experimental Sunray150 rotor dynamics upgrade"
  parameter Real yaw_delta_omega2 = 300
    "Small differential omega^2 command preserving approximate total thrust";
  Real yaw_step;
  Real rotor_speed_mag[4](each unit = "rad/s");
  Sunray150RflyStyleRotorDynamics dynamics;
equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_mag[i] = sqrt(dynamics.hover_motor_speed_cmd * dynamics.hover_motor_speed_cmd + dynamics.yaw_direction[i] * yaw_step);
    dynamics.motor_command[i] = dynamics.spin_command_sign[i] * rotor_speed_mag[i];
  end for;
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150DynamicsUpgradeYawStepSmoke;

model Sunray150DynamicsWrapperSurface
  "Project-owned wrapper surface for the Sunray150 Rfly-style rotor dynamics core"
  parameter Real expected_yaw_direction[4] = {1, -1, 1, -1}
    "MWORKS wrapper yaw direction convention validated only as a source-labeled smoke gate";
  parameter Real expected_rotor_center[4, 3] = [
    0.053745, -0.053740, -0.014052;
    0.053746,  0.053759, -0.014052;
   -0.053761,  0.053760, -0.014052;
   -0.053761, -0.053739, -0.014052]
    "source=user-reviewed DAE screw-pair fit, in MWORKS Dronefixed1..4 order";
  Sunray150RflyStyleRotorDynamics dynamics;
  Real motor_command[4](each unit = "rad/s")
    "Signed MWORKS visual rotor speed command surface";
  Real commanded_thrust[4](each unit = "N")
    "Algebraic command-side Ct*omega_cmd^2 thrust for sign/order checks";
  Real commanded_yaw_reaction_moment[4](each unit = "N.m")
    "Command-side yaw reaction moment for sign/order checks";
  Real commanded_rotor_arm_moment[4, 3](each unit = "N.m")
    "Command-side rotor-center moment from r_cross_F plus yaw reaction moment";
  Real total_thrust(unit = "N")
    "Lagged dynamic wrapper total thrust";
  Real total_moment_body[3](each unit = "N.m")
    "Lagged dynamic wrapper body moment";
  Real commanded_total_thrust(unit = "N")
    "Command-side total thrust";
  Real commanded_total_moment_body[3](each unit = "N.m")
    "Command-side body moment";
  Real hover_thrust_error(unit = "N");
  Real commanded_hover_thrust_error(unit = "N");
  Real yaw_moment_gate(unit = "N.m");
  Real commanded_yaw_moment_gate(unit = "N.m");
  Real motor_order_gate_error;
  Real yaw_direction_gate_error;
equation
  dynamics.motor_command = motor_command;

  for i in 1:4 loop
    commanded_thrust[i] = dynamics.lift_coefficient * motor_command[i] * motor_command[i];
    commanded_yaw_reaction_moment[i] = dynamics.yaw_direction[i] * dynamics.moment_constant * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 1] = dynamics.rotor_center[i, 2] * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 2] = -dynamics.rotor_center[i, 1] * commanded_thrust[i];
    commanded_rotor_arm_moment[i, 3] = commanded_yaw_reaction_moment[i];
  end for;

  total_thrust = dynamics.total_thrust;
  total_moment_body = dynamics.total_moment_body;
  hover_thrust_error = dynamics.hover_thrust_error;
  commanded_total_thrust = sum(commanded_thrust);
  commanded_total_moment_body[1] = sum({commanded_rotor_arm_moment[i, 1] for i in 1:4});
  commanded_total_moment_body[2] = sum({commanded_rotor_arm_moment[i, 2] for i in 1:4});
  commanded_total_moment_body[3] = sum({commanded_rotor_arm_moment[i, 3] for i in 1:4});
  commanded_hover_thrust_error = commanded_total_thrust - dynamics.mass_kg * 9.81;
  yaw_moment_gate = total_moment_body[3];
  commanded_yaw_moment_gate = commanded_total_moment_body[3];
  motor_order_gate_error = sum({abs(dynamics.rotor_center[i, j] - expected_rotor_center[i, j]) for i in 1:4, j in 1:3});
  yaw_direction_gate_error = sum({abs(dynamics.yaw_direction[i] - expected_yaw_direction[i]) for i in 1:4});
end Sunray150DynamicsWrapperSurface;

model Sunray150DynamicsWrapperHoverSmoke
  "Hover smoke for the project-owned Sunray150 dynamics wrapper surface"
  Sunray150DynamicsWrapperSurface wrapper;
equation
  wrapper.motor_command = {
    wrapper.dynamics.spin_command_sign[1] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[2] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[3] * wrapper.dynamics.hover_motor_speed_cmd,
    wrapper.dynamics.spin_command_sign[4] * wrapper.dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150DynamicsWrapperHoverSmoke;

model Sunray150DynamicsWrapperYawStepSmoke
  "Yaw-step smoke for the project-owned Sunray150 dynamics wrapper surface"
  parameter Real yaw_delta_omega2 = 300
    "Small differential omega^2 command preserving approximate total thrust";
  Real yaw_step;
  Real rotor_speed_mag[4](each unit = "rad/s");
  Sunray150DynamicsWrapperSurface wrapper;
equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_mag[i] = sqrt(wrapper.dynamics.hover_motor_speed_cmd * wrapper.dynamics.hover_motor_speed_cmd + wrapper.dynamics.yaw_direction[i] * yaw_step);
    wrapper.motor_command[i] = wrapper.dynamics.spin_command_sign[i] * rotor_speed_mag[i];
  end for;
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150DynamicsWrapperYawStepSmoke;

model Sunray150PhysicalWrenchFrameAdapter
  "Apply the project-owned Sunray150 wrapper force and torque to a MultiBody frame"
  inner Modelica.Mechanics.MultiBody.World world(
    animateWorld = false,
    animateGravity = false,
    n = {0, 0, -1},
    gravityType = Modelica.Mechanics.MultiBody.Types.GravityTypes.UniformGravity,
    g = 9.81);
  Sunray150DynamicsWrapperSurface wrapper;
  Modelica.Mechanics.MultiBody.Parts.Body body(
    animation = false,
    r_CM = {0, 0, 0},
    m = wrapper.dynamics.mass_kg,
    I_11 = 0.0085,
    I_22 = 0.0085,
    I_33 = 0.012,
    I_21 = 0,
    I_31 = 0,
    I_32 = 0,
    r_0(start = {0, 0, 0}, fixed = {true, true, true}),
    v_0(start = {0, 0, 0}, fixed = {true, true, true}),
    angles_fixed = true,
    angles_start = {0, 0, 0},
    w_0_fixed = true,
    w_0_start = {0, 0, 0},
    enforceStates = true);
  Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque forceAndTorque(
    resolveInFrame = Modelica.Mechanics.MultiBody.Types.ResolveInFrameB.frame_b,
    animation = false);
  Real applied_force_body[3](each unit = "N");
  Real applied_torque_body[3](each unit = "N.m");
  Real applied_force_z_body(unit = "N");
  Real applied_yaw_torque_body(unit = "N.m");
  Real force_application_error(unit = "N");
  Real torque_application_error(unit = "N.m");
  Real hover_weight_balance_error(unit = "N");
  Real wrapper_total_thrust(unit = "N");
  Real wrapper_yaw_moment(unit = "N.m");
  Real motor_order_gate_error;
  Real yaw_direction_gate_error;
equation
  applied_force_body = {0, 0, wrapper.total_thrust};
  applied_torque_body = wrapper.total_moment_body;
  forceAndTorque.force = applied_force_body;
  forceAndTorque.torque = applied_torque_body;
  connect(forceAndTorque.frame_b, body.frame_a);

  applied_force_z_body = applied_force_body[3];
  applied_yaw_torque_body = applied_torque_body[3];
  wrapper_total_thrust = wrapper.total_thrust;
  wrapper_yaw_moment = wrapper.total_moment_body[3];
  force_application_error = abs(body.frame_a.f[3] - applied_force_z_body);
  torque_application_error = abs(body.frame_a.t[3] - applied_yaw_torque_body);
  hover_weight_balance_error = wrapper.total_thrust - wrapper.dynamics.mass_kg * world.g;
  motor_order_gate_error = wrapper.motor_order_gate_error;
  yaw_direction_gate_error = wrapper.yaw_direction_gate_error;
end Sunray150PhysicalWrenchFrameAdapter;

model Sunray150PhysicalWrenchHoverSmoke
  "Hover smoke for the project-owned physical wrench frame adapter"
  Sunray150PhysicalWrenchFrameAdapter adapter;
equation
  adapter.wrapper.motor_command = {
    adapter.wrapper.dynamics.spin_command_sign[1] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[2] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[3] * adapter.wrapper.dynamics.hover_motor_speed_cmd,
    adapter.wrapper.dynamics.spin_command_sign[4] * adapter.wrapper.dynamics.hover_motor_speed_cmd};
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150PhysicalWrenchHoverSmoke;

model Sunray150PhysicalWrenchYawStepSmoke
  "Yaw-step smoke for the project-owned physical wrench frame adapter"
  parameter Real yaw_delta_omega2 = 300
    "Small differential omega^2 command preserving approximate total thrust";
  Real yaw_step;
  Real rotor_speed_mag[4](each unit = "rad/s");
  Sunray150PhysicalWrenchFrameAdapter adapter;
equation
  yaw_step = if time >= 0.05 then yaw_delta_omega2 else 0;
  for i in 1:4 loop
    rotor_speed_mag[i] = sqrt(adapter.wrapper.dynamics.hover_motor_speed_cmd * adapter.wrapper.dynamics.hover_motor_speed_cmd + adapter.wrapper.dynamics.yaw_direction[i] * yaw_step);
    adapter.wrapper.motor_command[i] = adapter.wrapper.dynamics.spin_command_sign[i] * rotor_speed_mag[i];
  end for;
  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end Sunray150PhysicalWrenchYawStepSmoke;

model FactoryTraceIso30ExternalBodyStateBoundarySmoke
  "External-body state response boundary smoke after Iso29"
  extends FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;

  parameter Real external_body_initial_z(unit = "m") = 0;
  parameter Real external_body_initial_vz(unit = "m/s") = 0;
  parameter Real external_body_initial_yaw_rate(unit = "rad/s") = 0;
  Real external_body_z(unit = "m");
  Real external_body_vz(unit = "m/s");
  Real external_body_yaw_rate(unit = "rad/s");
  Real external_body_z_delta(unit = "m");
  Real external_body_vz_delta(unit = "m/s");
  Real external_body_yaw_rate_delta(unit = "rad/s");
  Real external_body_vertical_response_gate;
  Real external_body_yaw_response_gate;
  Real external_body_state_boundary_gate_error;

equation
  external_body_z = external_test_body.r_0[3];
  external_body_vz = der(external_test_body.r_0[3]);
  external_body_yaw_rate = external_test_body.w_a[3];
  external_body_z_delta = external_body_z - external_body_initial_z;
  external_body_vz_delta = external_body_vz - external_body_initial_vz;
  external_body_yaw_rate_delta = external_body_yaw_rate - external_body_initial_yaw_rate;
  external_body_vertical_response_gate =
    if time >= 0.2 then abs(external_body_z_delta) + abs(external_body_vz_delta) else 0;
  external_body_yaw_response_gate =
    if time >= 0.2 then abs(external_body_yaw_rate_delta) else 0;
  external_body_state_boundary_gate_error =
    external_boundary_gate_error +
    (if time >= 0.2 and external_body_vertical_response_gate <= 1e-9 then 1 else 0);

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 0.25, Tolerance = 0.0001, Interval = 0.001));
end FactoryTraceIso30ExternalBodyStateBoundarySmoke;

end QuadrotorExperiments;
