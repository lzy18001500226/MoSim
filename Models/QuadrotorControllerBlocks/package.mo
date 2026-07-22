package QuadrotorControllerBlocks
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "四旋翼控制器模块库分类入口（静态 package shell；保留平铺类兼容路径）"

  package AWFFPidBlocks
    "AWFF PID 基线分解、混控与完整控制器入口"
    model PositionOuterLoop
      "AWFF 位置外环 Sysblock"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_PositionOuterLoop_Sysblock;
    end PositionOuterLoop;
    model AttitudeInnerLoop
      "AWFF 姿态内环 Sysblock"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_AttitudeInnerLoop_Sysblock;
    end AttitudeInnerLoop;
    model MotorMixer
      "四旋翼电机混控 Sysblock"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_MotorMixer_Sysblock;
    end MotorMixer;
    model FullControllerGraphical
      "AWFF 分层完整图形控制器"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullController_Sysblock;
    end FullControllerGraphical;
    model FullControllerEquation
      "AWFF 完整控制器方程桥接"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullControllerEquation_Sysblock;
    end FullControllerEquation;
    model FullControllerFlatGraphical
      "AWFF 扁平图形化完整控制器"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullControllerFlatGraphical_Sysblock;
    end FullControllerFlatGraphical;
    annotation(__MWORKS(version="26.3.0"));
  end AWFFPidBlocks;

  package InnovationControllers
    "INDI、L1 残差与创新控制器入口"
    model INDIEquation
      "INDI-like 组合控制器方程入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_INDIControllerEquation_Sysblock;
    end INDIEquation;
    model L1ResidualEquation
      "L1-inspired 残差补偿控制器入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_L1ResidualControllerEquation_Sysblock;
    end L1ResidualEquation;
    model InnovationGraphicalOverview
      "创新控制器图形化总览入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_InnovationGraphicalControllers;
    end InnovationGraphicalOverview;
    annotation(__MWORKS(version="26.3.0"));
  end InnovationControllers;

  package FaultAllocationControllers
    "故障补偿、在线故障分配与多故障隔离入口"
    model FaultCompensationEquation
      "已知故障补偿方程入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FaultCompensationControllerEquation_Sysblock;
    end FaultCompensationEquation;
    model L1FaultAllocationEquation
      "L1 已知故障分配入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_L1FaultAllocationControllerEquation_Sysblock;
    end L1FaultAllocationEquation;
    model L1OnlineFaultAllocationEquation
      "L1 在线故障分配入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock;
    end L1OnlineFaultAllocationEquation;
    model L1MultiFaultIsolationEquation
      "L1 多故障隔离入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_L1MultiFaultIsolationControllerEquation_Sysblock;
    end L1MultiFaultIsolationEquation;
    model LinearMPCOnlineFaultAllocation
      "线性 MPC 在线故障分配入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_LinearMPCOnlineFaultAllocationController_Sysblock;
    end LinearMPCOnlineFaultAllocation;
    model LinearMPCMultiFaultAllocation
      "线性 MPC 多故障分配入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_LinearMPCMultiFaultAllocationController_Sysblock;
    end LinearMPCMultiFaultAllocation;
    annotation(__MWORKS(version="26.3.0"));
  end FaultAllocationControllers;

  package LinearMPCControllers
    "标称线性 MPC 外环控制器入口"
    model OuterLoopEquation
      "标称线性 MPC-style 外环方程入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock;
    end OuterLoopEquation;
    annotation(__MWORKS(version="26.3.0"));
  end LinearMPCControllers;

  package SafetyControllers
    "QP/NMPC 安全滤波与返航降落控制入口"
    model QPNMPCSafety
      "QP/NMPC-style 安全控制器入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_QPNMPCSafetyController_Sysblock;
    end QPNMPCSafety;
    annotation(__MWORKS(version="26.3.0"));
  end SafetyControllers;

  package DemosAndSIL
    "演示、代码生成与 SIL 验证入口"
    model PIDDemo
      "AWFF PID 高度环演示入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_PID_Sysblock_Demo;
    end PIDDemo;
    model PIDDemoSILConstant
      "AWFF PID 常量输入 SIL 演示入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_PID_Sysblock_Demo_SIL_Constant;
    end PIDDemoSILConstant;
    model PX4CTRLCoreAttitudeThrustEquationBridge
      "px4ctrl ATTITUDE_THRUST Golden Slice G6 方程桥接入口"
      extends MoSimQuadrotorModel.Controllers.Sysblocks.PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock;
    end PX4CTRLCoreAttitudeThrustEquationBridge;
    annotation(__MWORKS(version="26.3.0"));
  end DemosAndSIL;

  package CompatibilityAndLegacy
    "兼容与废弃候选保留区；本轮不放入主动模型"
    annotation(__MWORKS(version="26.3.0"));
  end CompatibilityAndLegacy;
  annotation(__MWORKS(version="26.3.0"));
  annotation(__MWORKS(hide=true));
end QuadrotorControllerBlocks;