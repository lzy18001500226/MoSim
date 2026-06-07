within QuadrotorExperiments;
package DynamicsUpgrade
  "Sunray150 动力学升级与物理力矩包装（RflySim-like 结构验证）"
  extends Modelica.Icons.Package;

  model RotorDynamicsCore
    "RflySim-like 转子动力学核心"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150RflyStyleRotorDynamics;
    annotation(__MWORKS(hide=false));
  end RotorDynamicsCore;

  model RotorHoverSmoke
    "转子动力学悬停烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeHoverSmoke;
    annotation(__MWORKS(hide=false));
  end RotorHoverSmoke;

  model RotorYawStepSmoke
    "转子动力学偏航阶跃烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsUpgradeYawStepSmoke;
    annotation(__MWORKS(hide=false));
  end RotorYawStepSmoke;

  model WrapperSurface
    "动力学包装接口：电机命令到合力/合矩"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperSurface;
    annotation(__MWORKS(hide=false));
  end WrapperSurface;

  model WrapperHoverSmoke
    "动力学包装接口悬停烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperHoverSmoke;
    annotation(__MWORKS(hide=false));
  end WrapperHoverSmoke;

  model WrapperYawStepSmoke
    "动力学包装接口偏航阶跃烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150DynamicsWrapperYawStepSmoke;
    annotation(__MWORKS(hide=false));
  end WrapperYawStepSmoke;

  model PhysicalWrenchAdapter
    "物理力/矩施加适配器"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchFrameAdapter;
    annotation(__MWORKS(hide=false));
  end PhysicalWrenchAdapter;

  model PhysicalWrenchHoverSmoke
    "物理力/矩悬停施加烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchHoverSmoke;
    annotation(__MWORKS(hide=false));
  end PhysicalWrenchHoverSmoke;

  model PhysicalWrenchYawStepSmoke
    "物理力/矩偏航施加烟测"
    extends QuadrotorExperiments.DynamicsUpgrade.Sunray150PhysicalWrenchYawStepSmoke;
    annotation(__MWORKS(hide=false));
  end PhysicalWrenchYawStepSmoke;

end DynamicsUpgrade;
