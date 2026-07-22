within QuadrotorExperiments;
package DynamicsUpgrade
  // Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel.
  "Sunray150 动力学升级与物理力矩包装（RflySim-like 结构验证）"
  extends Modelica.Icons.Package;

  model RotorDynamicsCore
    "RflySim-like 转子动力学核心"
    extends MoSimQuadrotorModel.Dynamics.RotorActuatorCore;
    annotation(__MWORKS(hide=true));
  end RotorDynamicsCore;

  model RotorHoverSmoke
    "转子动力学悬停烟测"
    extends MoSimQuadrotorModel.Dynamics.HoverSmoke;
    annotation(__MWORKS(hide=true));
  end RotorHoverSmoke;

  model RotorYawStepSmoke
    "转子动力学偏航阶跃烟测"
    extends MoSimQuadrotorModel.Dynamics.YawStepSmoke;
    annotation(__MWORKS(hide=true));
  end RotorYawStepSmoke;

  model RotorEffectivenessSmoke
    "单桨效率退化烟测"
    extends MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke;
    annotation(__MWORKS(hide=true));
  end RotorEffectivenessSmoke;

  model WrapperSurface
    "动力学包装接口：电机命令到合力/合矩"
    extends MoSimQuadrotorModel.Dynamics.WrapperSurface;
    annotation(__MWORKS(hide=true));
  end WrapperSurface;

  model ActuatorCommandMapper
    "归一化执行器命令到有符号可视旋翼转速的mapper"
    extends MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper;
    annotation(__MWORKS(hide=true));
  end ActuatorCommandMapper;

  model ActuatorMappedWrapperSurface
    "归一化执行器命令经mapper接入现有动力学wrapper接口"
    extends MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface;
    annotation(__MWORKS(hide=true));
  end ActuatorMappedWrapperSurface;

  model OptionalDampingGyroLayer
    "默认关闭的旋翼陀螺、机体阻力和角阻尼可选边界层"
    extends MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer;
    annotation(__MWORKS(hide=true));
  end OptionalDampingGyroLayer;

  model WrapperHoverSmoke
    "动力学包装接口悬停烟测"
    extends MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke;
    annotation(__MWORKS(hide=true));
  end WrapperHoverSmoke;

  model WrapperYawStepSmoke
    "动力学包装接口偏航阶跃烟测"
    extends MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end WrapperYawStepSmoke;

  model PhysicalWrenchAdapter
    "物理力/矩施加适配器"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter;
    annotation(__MWORKS(hide=true));
  end PhysicalWrenchAdapter;

  model PhysicalWrenchHoverSmoke
    "物理力/矩悬停施加烟测"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke;
    annotation(__MWORKS(hide=true));
  end PhysicalWrenchHoverSmoke;

  model PhysicalWrenchYawStepSmoke
    "物理力/矩偏航施加烟测"
    extends MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke;
    annotation(__MWORKS(hide=true));
  end PhysicalWrenchYawStepSmoke;
  annotation(__MWORKS(hide=true));

end DynamicsUpgrade;