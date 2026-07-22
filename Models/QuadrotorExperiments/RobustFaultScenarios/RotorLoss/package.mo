within MoSimQuadrotorModel.Robustness.Scenarios;
package RotorLoss
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "单电机损失与故障分配场景"
  extends Modelica.Icons.Package;

  model Rotor1AWFF
    "1 号电机损失：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1AWFF;

  model Rotor1AWFFBaseline
    "1 号电机损失：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=true));
  end Rotor1AWFFBaseline;

  model Rotor1L1
    "1 号电机损失：L1 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1SysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1L1;

  model Rotor1L1FaultAllocation
    "1 号电机损失：L1 故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1L1FaultAllocation;

  model Rotor1L1OnlineFaultAllocation
    "1 号电机损失：L1 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1L1OnlineFaultAllocation;

  model Rotor1L1MultiFaultIsolation
    "1 号电机损失：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1L1MultiFaultIsolation;

  model Rotor1LinearMPC
    "1 号电机损失：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1LinearMPC;

  model Rotor1LinearMPCOnlineFaultAllocation
    "1 号电机损失：线性 MPC 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1LinearMPCOnlineFaultAllocation;

  model Rotor2AWFF
    "2 号电机损失：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor2AWFF;

  model Rotor3AWFF
    "3 号电机损失：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor3AWFF;

  model Rotor4AWFF
    "4 号电机损失：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor4AWFF;

  model Rotor1WindGustAWFF
    "1 号电机损失 + 阵风：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1WindGustAWFF;

  model Rotor1WindGustAWFFFaultCompensation
    "1 号电机损失 + 阵风：AWFF 故障补偿闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1WindGustAWFFFaultCompensation;

  model Rotor1WindGustL1MultiFaultIsolation
    "1 号电机损失 + 阵风：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1WindGustL1MultiFaultIsolation;

  model Rotor1WindGustLinearMPCOnlineFaultAllocation
    "1 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor1WindGustLinearMPCOnlineFaultAllocation;

  model Rotor2WindGustAWFF
    "2 号电机损失 + 阵风：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor2WindGustAWFF;

  model Rotor2L1MultiFaultIsolation
    "2 号电机损失：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor2L1MultiFaultIsolation;

  model Rotor2WindGustL1MultiFaultIsolation
    "2 号电机损失 + 阵风：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor2WindGustL1MultiFaultIsolation;

  model Rotor2WindGustLinearMPCOnlineFaultAllocation
    "2 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor2WindGustLinearMPCOnlineFaultAllocation;

  model Rotor3WindGustAWFF
    "3 号电机损失 + 阵风：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor3WindGustAWFF;

  model Rotor3L1MultiFaultIsolation
    "3 号电机损失：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor3L1MultiFaultIsolation;

  model Rotor3WindGustL1MultiFaultIsolation
    "3 号电机损失 + 阵风：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor3WindGustL1MultiFaultIsolation;

  model Rotor3WindGustLinearMPCOnlineFaultAllocation
    "3 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor3WindGustLinearMPCOnlineFaultAllocation;

  model Rotor4WindGustAWFF
    "4 号电机损失 + 阵风：AWFF 闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor4WindGustAWFF;

  model Rotor4L1MultiFaultIsolation
    "4 号电机损失：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor4L1MultiFaultIsolation;

  model Rotor4WindGustL1MultiFaultIsolation
    "4 号电机损失 + 阵风：L1 多故障隔离闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor4WindGustL1MultiFaultIsolation;

  model Rotor4WindGustLinearMPCOnlineFaultAllocation
    "4 号电机损失 + 阵风：线性 MPC 在线故障分配闭环"
    extends MoSimQuadrotorModel.Robustness.Scenarios.RotorLoss.Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop;
    annotation(__MWORKS(hide=true));
  end Rotor4WindGustLinearMPCOnlineFaultAllocation;
  annotation(__MWORKS(hide=true));

end RotorLoss;