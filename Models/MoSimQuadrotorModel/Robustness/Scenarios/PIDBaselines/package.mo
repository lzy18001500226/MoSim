within MoSimQuadrotorModel.Robustness.Scenarios;
package PIDBaselines
  "扰动/故障下的 PID 系列对比基线"
  extends Modelica.Icons.Package;

  model Mass20PID
    "质量 +20%：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20PID;
    annotation(__MWORKS(hide=false));
  end Mass20PID;

  model Mass20ImprovedPID
    "质量 +20%：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20ImprovedPID;
    annotation(__MWORKS(hide=false));
  end Mass20ImprovedPID;

  model Mass20EnhancedPID
    "质量 +20%：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Mass20EnhancedPID;
    annotation(__MWORKS(hide=false));
  end Mass20EnhancedPID;

  model WindGustPID
    "横向阵风：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustPID;
    annotation(__MWORKS(hide=false));
  end WindGustPID;

  model WindGustImprovedPID
    "横向阵风：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustImprovedPID;
    annotation(__MWORKS(hide=false));
  end WindGustImprovedPID;

  model WindGustEnhancedPID
    "横向阵风：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1WindGustEnhancedPID;
    annotation(__MWORKS(hide=false));
  end WindGustEnhancedPID;

  model Rotor1LossPID
    "1 号电机损失：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15PID;
    annotation(__MWORKS(hide=false));
  end Rotor1LossPID;

  model Rotor1LossImprovedPID
    "1 号电机损失：改进 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15ImprovedPID;
    annotation(__MWORKS(hide=false));
  end Rotor1LossImprovedPID;

  model Rotor1LossEnhancedPID
    "1 号电机损失：增强 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor1Loss15EnhancedPID;
    annotation(__MWORKS(hide=false));
  end Rotor1LossEnhancedPID;

  model Rotor2LossPID
    "2 号电机损失：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor2Loss15PID;
    annotation(__MWORKS(hide=false));
  end Rotor2LossPID;

  model Rotor3LossPID
    "3 号电机损失：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor3Loss15PID;
    annotation(__MWORKS(hide=false));
  end Rotor3LossPID;

  model Rotor4LossPID
    "4 号电机损失：官方 PID 对比基线"
    extends MoSimQuadrotorModel.Robustness.Scenarios.PIDBaselines.Example1Rotor4Loss15PID;
    annotation(__MWORKS(hide=false));
  end Rotor4LossPID;

end PIDBaselines;
