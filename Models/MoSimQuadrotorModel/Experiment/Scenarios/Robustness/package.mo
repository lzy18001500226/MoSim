within MoSimQuadrotorModel.Experiment.Scenarios;
package Robustness
  "鲁棒扰动、安全与电机故障场景（审查入口）"
  extends Modelica.Icons.Package;

  model Mass20AWFFBaseline
    "质量 +20%：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1Mass20AntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Mass20AWFFBaseline;

  model Mass20AWFF
    "质量 +20%：AWFF 闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1Mass20AWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Mass20AWFF;

  model Mass20L1
    "质量 +20%：L1 残差补偿闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1Mass20L1SysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Mass20L1;

  model Mass20LinearMPC
    "质量 +20%：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1Mass20LinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Mass20LinearMPC;

  model WindGustAWFF
    "横向阵风：AWFF 闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1WindGustAWFFSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end WindGustAWFF;

  model WindGustAWFFBaseline
    "横向阵风：AWFF 控制器基线"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1WindGustAntiWindupFeedforwardPID;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end WindGustAWFFBaseline;

  model WindGustL1
    "横向阵风：L1 残差补偿闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1WindGustL1SysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end WindGustL1;

  model WindGustLinearMPC
    "横向阵风：线性 MPC 闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1WindGustLinearMPCSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end WindGustLinearMPC;

  model SafetyQPNMPC
    "安全滤波：QP/NMPC 闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1QPNMPCSafetySysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end SafetyQPNMPC;

  model SafetyReturnLand
    "安全滤波：返航降落闭环"
    extends MoSimQuadrotorModel.Experiment.Scenarios.Robustness.Example1QPNMPCSafetyReturnLandSysblockClosedLoop;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end SafetyReturnLand;
  annotation(__MWORKS(version="26.3.0"));

end Robustness;
