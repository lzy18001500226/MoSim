within MoSimQuadrotorModel;
package Dynamics
  "Sunray150动力学升级（RflySim结构思想迁移，参数仍按来源标注）"

  model RotorActuatorCore
    "旋翼执行器核心（电机指令、转速滞后、推力和偏航反扭矩）"
    extends QuadrotorExperiments.DynamicsUpgrade.RotorDynamicsCore;
  end RotorActuatorCore;

  model HoverSmoke
    "悬停烟测（动力学升级最小验证）"
    extends QuadrotorExperiments.DynamicsUpgrade.RotorHoverSmoke;
  end HoverSmoke;

  model YawStepSmoke
    "偏航阶跃烟测（偏航反扭矩最小验证）"
    extends QuadrotorExperiments.DynamicsUpgrade.RotorYawStepSmoke;
  end YawStepSmoke;

  model WrapperSurface
    "动力学wrapper接口面（后续正式机体替换入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.WrapperSurface;
  end WrapperSurface;

  model WrapperHoverSmoke
    "动力学wrapper悬停烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.WrapperHoverSmoke;
  end WrapperHoverSmoke;

  model WrapperYawStepSmoke
    "动力学wrapper偏航阶跃烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.WrapperYawStepSmoke;
  end WrapperYawStepSmoke;

  model PhysicalWrenchAdapter
    "物理力/力矩适配器（外部wrench边界）"
    extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchAdapter;
  end PhysicalWrenchAdapter;

  model PhysicalWrenchHoverSmoke
    "物理力/力矩悬停施加烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchHoverSmoke;
  end PhysicalWrenchHoverSmoke;

  model PhysicalWrenchYawStepSmoke
    "物理力/力矩偏航阶跃施加烟测（正式入口）"
    extends QuadrotorExperiments.DynamicsUpgrade.PhysicalWrenchYawStepSmoke;
  end PhysicalWrenchYawStepSmoke;
end Dynamics;
