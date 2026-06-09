within MoSimQuadrotorModel;
package Dynamics
  "Sunray150动力学升级（RflySim结构思想迁移，参数仍按来源标注）"

  model HoverSmoke
    "悬停烟测（动力学升级最小验证）"
    extends QuadrotorExperiments.DynamicsUpgrade.RotorHoverSmoke;
  end HoverSmoke;

  model YawStepSmoke
    "偏航阶跃烟测（偏航反扭矩最小验证）"
    extends QuadrotorExperiments.DynamicsUpgrade.RotorYawStepSmoke;
  end YawStepSmoke;

  model WrapperHoverSmoke
    "动力学wrapper悬停烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.WrapperHoverSmoke;
  end WrapperHoverSmoke;

  model WrapperYawStepSmoke
    "动力学wrapper偏航阶跃烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.WrapperYawStepSmoke;
  end WrapperYawStepSmoke;

  model PhysicalWrenchHoverSmoke
    "物理力/力矩悬停施加烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchHoverSmoke;
  end PhysicalWrenchHoverSmoke;

  model PhysicalWrenchYawStepSmoke
    "物理力/力矩偏航阶跃施加烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchYawStepSmoke;
  end PhysicalWrenchYawStepSmoke;
end Dynamics;
