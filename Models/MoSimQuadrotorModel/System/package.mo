within MoSimQuadrotorModel;
package System
  "系统级图形与硬件抽象（飞控、机载电脑、电调、电池、传感器模块）"

  package Architecture
    "完整系统图形化架构与失效模式入口"
    extends QuadrotorExperiments.SystemArchitecture;
  end Architecture;

  package Modules
    "系统模块抽象（感知、飞控、任务计算、电源和电调）"
    extends QuadrotorExperiments.SystemModules;
  end Modules;
end System;
