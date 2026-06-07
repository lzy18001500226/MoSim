within MoSimQuadrotorModel;
package Controllers
  "控制器基线与对比（改进PID、AWFF、L1、INDI、MPC等迁移入口）"

  extends QuadrotorExperiments.ControllerBaselines;

  package AWFFPidBlocks
    "AWFF PID 基线分解、混控与完整控制器正式入口"
    extends QuadrotorControllerBlocks.AWFFPidBlocks;
    annotation(__MWORKS(hide=false));
  end AWFFPidBlocks;

  package InnovationControllers
    "INDI、L1 残差与创新控制器正式入口"
    extends QuadrotorControllerBlocks.InnovationControllers;
    annotation(__MWORKS(hide=false));
  end InnovationControllers;

  package FaultAllocationControllers
    "故障补偿、在线故障分配与多故障隔离正式入口"
    extends QuadrotorControllerBlocks.FaultAllocationControllers;
    annotation(__MWORKS(hide=false));
  end FaultAllocationControllers;

  package LinearMPCControllers
    "标称线性 MPC 外环控制器正式入口"
    extends QuadrotorControllerBlocks.LinearMPCControllers;
    annotation(__MWORKS(hide=false));
  end LinearMPCControllers;

  package SafetyControllers
    "QP/NMPC 安全滤波与返航降落控制正式入口"
    extends QuadrotorControllerBlocks.SafetyControllers;
    annotation(__MWORKS(hide=false));
  end SafetyControllers;

  package DemosAndSIL
    "演示、代码生成与 SIL 验证正式入口"
    extends QuadrotorControllerBlocks.DemosAndSIL;
    annotation(__MWORKS(hide=false));
  end DemosAndSIL;

  package CompatibilityAndLegacy
    "控制器库兼容与废弃候选保留入口"
    extends QuadrotorControllerBlocks.CompatibilityAndLegacy;
    annotation(__MWORKS(hide=false));
  end CompatibilityAndLegacy;
end Controllers;
