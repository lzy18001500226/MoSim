within MoSimQuadrotorModel;
package Robustness
  "鲁棒性、故障、安全与扰动场景（质量、风、电机损失、返航降落）"

  extends Modelica.Icons.Package;

  package PIDBaselines
    "扰动/故障下的 PID 系列对比基线"
    extends Modelica.Icons.Package;

    model Mass20PID
      "质量 +20%：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Mass20PID;
      annotation(__MWORKS(hide=false));
    end Mass20PID;

    model Mass20ImprovedPID
      "质量 +20%：改进 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Mass20ImprovedPID;
      annotation(__MWORKS(hide=false));
    end Mass20ImprovedPID;

    model Mass20EnhancedPID
      "质量 +20%：增强 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Mass20EnhancedPID;
      annotation(__MWORKS(hide=false));
    end Mass20EnhancedPID;

    model WindGustPID
      "横向阵风：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.WindGustPID;
      annotation(__MWORKS(hide=false));
    end WindGustPID;

    model WindGustImprovedPID
      "横向阵风：改进 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.WindGustImprovedPID;
      annotation(__MWORKS(hide=false));
    end WindGustImprovedPID;

    model WindGustEnhancedPID
      "横向阵风：增强 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.WindGustEnhancedPID;
      annotation(__MWORKS(hide=false));
    end WindGustEnhancedPID;

    model Rotor1LossPID
      "1 号电机损失：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor1LossPID;
      annotation(__MWORKS(hide=false));
    end Rotor1LossPID;

    model Rotor1LossImprovedPID
      "1 号电机损失：改进 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor1LossImprovedPID;
      annotation(__MWORKS(hide=false));
    end Rotor1LossImprovedPID;

    model Rotor1LossEnhancedPID
      "1 号电机损失：增强 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor1LossEnhancedPID;
      annotation(__MWORKS(hide=false));
    end Rotor1LossEnhancedPID;

    model Rotor2LossPID
      "2 号电机损失：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor2LossPID;
      annotation(__MWORKS(hide=false));
    end Rotor2LossPID;

    model Rotor3LossPID
      "3 号电机损失：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor3LossPID;
      annotation(__MWORKS(hide=false));
    end Rotor3LossPID;

    model Rotor4LossPID
      "4 号电机损失：官方 PID 对比基线"
      extends QuadrotorExperiments.RobustFaultScenarios.PIDBaselines.Rotor4LossPID;
      annotation(__MWORKS(hide=false));
    end Rotor4LossPID;
  end PIDBaselines;

  package RotorLoss
    "单电机损失与故障分配场景"
    extends Modelica.Icons.Package;

    model Rotor1AWFF
      "1 号电机损失：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1AWFF;
      annotation(__MWORKS(hide=false));
    end Rotor1AWFF;

    model Rotor1AWFFBaseline
      "1 号电机损失：AWFF 控制器基线"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1AWFFBaseline;
      annotation(__MWORKS(hide=false));
    end Rotor1AWFFBaseline;

    model Rotor1L1
      "1 号电机损失：L1 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1;
      annotation(__MWORKS(hide=false));
    end Rotor1L1;

    model Rotor1L1FaultAllocation
      "1 号电机损失：L1 故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1FaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor1L1FaultAllocation;

    model Rotor1L1OnlineFaultAllocation
      "1 号电机损失：L1 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1OnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor1L1OnlineFaultAllocation;

    model Rotor1L1MultiFaultIsolation
      "1 号电机损失：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1L1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor1L1MultiFaultIsolation;

    model Rotor1LinearMPC
      "1 号电机损失：线性 MPC 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1LinearMPC;
      annotation(__MWORKS(hide=false));
    end Rotor1LinearMPC;

    model Rotor1LinearMPCOnlineFaultAllocation
      "1 号电机损失：线性 MPC 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1LinearMPCOnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor1LinearMPCOnlineFaultAllocation;

    model Rotor2AWFF
      "2 号电机损失：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2AWFF;
      annotation(__MWORKS(hide=false));
    end Rotor2AWFF;

    model Rotor3AWFF
      "3 号电机损失：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3AWFF;
      annotation(__MWORKS(hide=false));
    end Rotor3AWFF;

    model Rotor4AWFF
      "4 号电机损失：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4AWFF;
      annotation(__MWORKS(hide=false));
    end Rotor4AWFF;

    model Rotor1WindGustAWFF
      "1 号电机损失 + 阵风：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustAWFF;
      annotation(__MWORKS(hide=false));
    end Rotor1WindGustAWFF;

    model Rotor1WindGustAWFFFaultCompensation
      "1 号电机损失 + 阵风：AWFF 故障补偿闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustAWFFFaultCompensation;
      annotation(__MWORKS(hide=false));
    end Rotor1WindGustAWFFFaultCompensation;

    model Rotor1WindGustL1MultiFaultIsolation
      "1 号电机损失 + 阵风：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustL1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor1WindGustL1MultiFaultIsolation;

    model Rotor1WindGustLinearMPCOnlineFaultAllocation
      "1 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor1WindGustLinearMPCOnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor1WindGustLinearMPCOnlineFaultAllocation;

    model Rotor2WindGustAWFF
      "2 号电机损失 + 阵风：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustAWFF;
      annotation(__MWORKS(hide=false));
    end Rotor2WindGustAWFF;

    model Rotor2L1MultiFaultIsolation
      "2 号电机损失：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2L1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor2L1MultiFaultIsolation;

    model Rotor2WindGustL1MultiFaultIsolation
      "2 号电机损失 + 阵风：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustL1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor2WindGustL1MultiFaultIsolation;

    model Rotor2WindGustLinearMPCOnlineFaultAllocation
      "2 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor2WindGustLinearMPCOnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor2WindGustLinearMPCOnlineFaultAllocation;

    model Rotor3WindGustAWFF
      "3 号电机损失 + 阵风：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustAWFF;
      annotation(__MWORKS(hide=false));
    end Rotor3WindGustAWFF;

    model Rotor3L1MultiFaultIsolation
      "3 号电机损失：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3L1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor3L1MultiFaultIsolation;

    model Rotor3WindGustL1MultiFaultIsolation
      "3 号电机损失 + 阵风：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustL1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor3WindGustL1MultiFaultIsolation;

    model Rotor3WindGustLinearMPCOnlineFaultAllocation
      "3 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor3WindGustLinearMPCOnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor3WindGustLinearMPCOnlineFaultAllocation;

    model Rotor4WindGustAWFF
      "4 号电机损失 + 阵风：AWFF 闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustAWFF;
      annotation(__MWORKS(hide=false));
    end Rotor4WindGustAWFF;

    model Rotor4L1MultiFaultIsolation
      "4 号电机损失：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4L1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor4L1MultiFaultIsolation;

    model Rotor4WindGustL1MultiFaultIsolation
      "4 号电机损失 + 阵风：L1 多故障隔离闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustL1MultiFaultIsolation;
      annotation(__MWORKS(hide=false));
    end Rotor4WindGustL1MultiFaultIsolation;

    model Rotor4WindGustLinearMPCOnlineFaultAllocation
      "4 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
      extends QuadrotorExperiments.RobustFaultScenarios.RotorLoss.Rotor4WindGustLinearMPCOnlineFaultAllocation;
      annotation(__MWORKS(hide=false));
    end Rotor4WindGustLinearMPCOnlineFaultAllocation;
  end RotorLoss;

  model Mass20AWFFBaseline
    "质量 +20%：AWFF 控制器基线"
    extends QuadrotorExperiments.RobustFaultScenarios.Mass20AWFFBaseline;
    annotation(__MWORKS(hide=false));
  end Mass20AWFFBaseline;

  model Mass20AWFF
    "质量 +20%：AWFF 闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.Mass20AWFF;
    annotation(__MWORKS(hide=false));
  end Mass20AWFF;

  model Mass20L1
    "质量 +20%：L1 残差补偿闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.Mass20L1;
    annotation(__MWORKS(hide=false));
  end Mass20L1;

  model Mass20LinearMPC
    "质量 +20%：线性 MPC 闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.Mass20LinearMPC;
    annotation(__MWORKS(hide=false));
  end Mass20LinearMPC;

  model WindGustAWFF
    "横向阵风：AWFF 闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.WindGustAWFF;
    annotation(__MWORKS(hide=false));
  end WindGustAWFF;

  model WindGustAWFFBaseline
    "横向阵风：AWFF 控制器基线"
    extends QuadrotorExperiments.RobustFaultScenarios.WindGustAWFFBaseline;
    annotation(__MWORKS(hide=false));
  end WindGustAWFFBaseline;

  model WindGustL1
    "横向阵风：L1 残差补偿闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.WindGustL1;
    annotation(__MWORKS(hide=false));
  end WindGustL1;

  model WindGustLinearMPC
    "横向阵风：线性 MPC 闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.WindGustLinearMPC;
    annotation(__MWORKS(hide=false));
  end WindGustLinearMPC;

  model SafetyQPNMPC
    "安全滤波：QP/NMPC 闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.SafetyQPNMPC;
    annotation(__MWORKS(hide=false));
  end SafetyQPNMPC;

  model SafetyReturnLand
    "安全滤波：返航降落闭环"
    extends QuadrotorExperiments.RobustFaultScenarios.SafetyReturnLand;
    annotation(__MWORKS(hide=false));
  end SafetyReturnLand;
end Robustness;
