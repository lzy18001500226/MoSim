within MoSimQuadrotorModel.Control.Implementations;
package Sysblocks
  "四旋翼控制器模块库分类入口（按功能分组）"

  package AWFFPidBlocks
    "AWFF PID 基线分解、混控与完整控制器入口"
    model PositionOuterLoop
      "AWFF 位置外环 Sysblock"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_PositionOuterLoop_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end PositionOuterLoop;
    model AttitudeInnerLoop
      "AWFF 姿态内环 Sysblock"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_AttitudeInnerLoop_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end AttitudeInnerLoop;
    model MotorMixer
      "四旋翼电机混控 Sysblock"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_MotorMixer_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end MotorMixer;
    model FullControllerGraphical
      "AWFF 分层完整图形控制器"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_FullController_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end FullControllerGraphical;
    model FullControllerEquation
      "AWFF 完整控制器方程桥接"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_FullControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end FullControllerEquation;
    model FullControllerFlatGraphical
      "AWFF 扁平图形化完整控制器"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_FullControllerFlatGraphical_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end FullControllerFlatGraphical;
    annotation(__MWORKS(version="26.3.0"));
  end AWFFPidBlocks;

  package InnovationControllers
    "INDI、L1 残差与创新控制器入口"
    model INDIEquation
      "INDI-like 组合控制器方程入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_INDIControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end INDIEquation;
    model L1ResidualEquation
      "L1-inspired 残差补偿控制器入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_L1ResidualControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end L1ResidualEquation;
    model InnovationGraphicalOverview
      "创新控制器图形化总览入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_InnovationGraphicalControllers;
      annotation(__MWORKS(version="26.3.0"));
    end InnovationGraphicalOverview;
    annotation(__MWORKS(version="26.3.0"));
  end InnovationControllers;

  package FaultAllocationControllers
    "故障补偿、在线故障分配与多故障隔离入口"
    model FaultCompensationEquation
      "已知故障补偿方程入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_FaultCompensationControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end FaultCompensationEquation;
    model L1FaultAllocationEquation
      "L1 已知故障分配入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_L1FaultAllocationControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end L1FaultAllocationEquation;
    model L1OnlineFaultAllocationEquation
      "L1 在线故障分配入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_L1OnlineFaultAllocationControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end L1OnlineFaultAllocationEquation;
    model L1MultiFaultIsolationEquation
      "L1 多故障隔离入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_L1MultiFaultIsolationControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end L1MultiFaultIsolationEquation;
    model LinearMPCOnlineFaultAllocation
      "线性 MPC 在线故障分配入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCOnlineFaultAllocationController_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end LinearMPCOnlineFaultAllocation;
    model LinearMPCMultiFaultAllocation
      "线性 MPC 多故障分配入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCMultiFaultAllocationController_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end LinearMPCMultiFaultAllocation;
    annotation(__MWORKS(version="26.3.0"));
  end FaultAllocationControllers;

  package LinearMPCControllers
    "标称线性 MPC 外环控制器入口"
    model OuterLoopEquation
      "标称线性 MPC-style 外环方程入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_LinearMPCOuterLoopControllerEquation_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end OuterLoopEquation;
    annotation(__MWORKS(version="26.3.0"));
  end LinearMPCControllers;

  package SafetyControllers
    "QP/NMPC 安全滤波与返航降落控制入口"
    model QPNMPCSafety
      "QP/NMPC-style 安全控制器入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_QPNMPCSafetyController_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end QPNMPCSafety;
    annotation(__MWORKS(version="26.3.0"));
  end SafetyControllers;

  package DemosAndSIL
    "演示、代码生成与 SIL 验证入口"
    model PIDDemo
      "AWFF PID 高度环演示入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_PID_Sysblock_Demo;
      annotation(__MWORKS(version="26.3.0"));
    end PIDDemo;
    model PIDDemoSILConstant
      "AWFF PID 常量输入 SIL 演示入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.AWFF_PID_Sysblock_Demo_SIL_Constant;
      annotation(__MWORKS(version="26.3.0"));
    end PIDDemoSILConstant;
    model PX4CTRLCoreAttitudeThrustEquationBridge
      "px4ctrl ATTITUDE_THRUST Golden Slice G6 方程桥接入口"
      extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock;
      annotation(__MWORKS(version="26.3.0"));
    end PX4CTRLCoreAttitudeThrustEquationBridge;
    annotation(__MWORKS(version="26.3.0"));
  end DemosAndSIL;

  annotation(__MWORKS(version="26.3.0"));
end Sysblocks;
