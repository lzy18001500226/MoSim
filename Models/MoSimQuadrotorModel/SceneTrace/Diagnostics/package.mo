within MoSimQuadrotorModel.SceneTrace;
package Diagnostics
  "Factory 轨迹接入隔离烟测（保留历史证据链，不作为最终模型入口）"
  extends Modelica.Icons.Package;

  model FactoryLite
    "Factory-lite 轨迹接入烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryLiteTraceSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end FactoryLite;

  model Iso01FullDisplay
    "隔离 01：完整显示链路烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso01FullDisplaySmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso01FullDisplay;

  model Iso02ControllerOnly
    "隔离 02：控制器独立烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso02ControllerOnlySmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso02ControllerOnly;

  model Iso03PlantHoverStack
    "隔离 03：机体悬停栈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso03PlantHoverStackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso03PlantHoverStack;

  model Iso04ControllerPlantWiring
    "隔离 04：控制器-机体接线烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso04ControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso04ControllerPlantWiring;

  model Iso05CleanHoverSum
    "隔离 05：干净悬停合力烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso05CleanHoverSumSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso05CleanHoverSum;

  model Iso06CleanControllerPlantWiring
    "隔离 06：干净控制器-机体接线烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso06CleanControllerPlantWiringSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso06CleanControllerPlantWiring;

  model Iso07ControllerOpenFeedback
    "隔离 07：控制器开反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso07CleanControllerOpenFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso07ControllerOpenFeedback;

  model Iso08PositionFeedback
    "隔离 08：位置反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso08PositionFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso08PositionFeedback;

  model Iso09PositionAttitudeFeedback
    "隔离 09：位置与姿态反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso09PositionAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso09PositionAttitudeFeedback;

  model Iso10RollFeedback
    "隔离 10：滚转反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso10RollFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso10RollFeedback;

  model Iso11PitchFeedback
    "隔离 11：俯仰反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso11PitchFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso11PitchFeedback;

  model Iso12RollFeedbackNegated
    "隔离 12：滚转反馈取反烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso12RollFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso12RollFeedbackNegated;

  model Iso13PitchFeedbackNegated
    "隔离 13：俯仰反馈取反烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso13PitchFeedbackNegatedSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso13PitchFeedbackNegated;

  model Iso14ConstantAttitudeInput
    "隔离 14：常量姿态输入烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso14ConstantAttitudeInputSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso14ConstantAttitudeInput;

  model Iso15TableAttitudeInput
    "隔离 15：表格姿态输入烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso15TableAttitudeInputSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso15TableAttitudeInput;

  model Iso16RealExpressionAngle
    "隔离 16：RealExpression 角度烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso16RealExpressionAngleSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso16RealExpressionAngle;

  model Iso17SampleHoldAngle
    "隔离 17：角度采样保持烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso17SampleHoldAngleSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso17SampleHoldAngle;

  model Iso18ProjectAttitudeEstimator
    "隔离 18：项目姿态估计器烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso18ProjectAttitudeEstimatorSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso18ProjectAttitudeEstimator;

  model Iso19RollPitchEstimator
    "隔离 19：滚转/俯仰估计器烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso19RollPitchEstimatorSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso19RollPitchEstimator;

  model Iso20RollPitchYawEstimator
    "隔离 20：滚转/俯仰/偏航估计器烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso20RollPitchYawEstimatorSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso20RollPitchYawEstimator;

  model Iso21RateAlias
    "隔离 21：控制器速率别名烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso21ControllerRateAliasSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso21RateAlias;

  model Iso22SensorDisplayReconnect
    "隔离 22：传感器显示重连烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso22SensorDisplayReconnectSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso22SensorDisplayReconnect;

  model Iso23PositionSampleHold
    "隔离 23：位置采样保持桥接烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso23PositionSampleHoldBridgeSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso23PositionSampleHold;

  model Iso24DirectAttitudeFeedback
    "隔离 24：直接姿态反馈烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso24DirectAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso24DirectAttitudeFeedback;

  model Iso25AttitudeSampleHold
    "隔离 25：姿态采样保持桥接烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso25AttitudeSampleHold;

  model Iso26ControllerOutput
    "隔离 26：控制器输出别名烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso26ControllerOutputAliasSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso26ControllerOutput;

  model Iso27ActuatorInput
    "隔离 27：执行器输入别名烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso27ActuatorInputAliasSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso27ActuatorInput;

  model Iso28ActuatorToWrenchBridge
    "隔离 28：执行器输入到物理力矩桥接烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso28ActuatorToWrenchBridgeSmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso28ActuatorToWrenchBridge;

  model Iso29ExternalFrameWrenchBoundary
    "隔离 29：外部 MultiBody frame 力矩边界烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso29ExternalFrameWrenchBoundarySmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso29ExternalFrameWrenchBoundary;

  model Iso30ExternalBodyStateBoundary
    "隔离 30：外部测试体状态响应边界烟测"
    extends MoSimQuadrotorModel.SceneTrace.Diagnostics.FactoryTraceIso30ExternalBodyStateBoundarySmoke;
    annotation(__MWORKS(hide=false,version="26.3.0"));
  end Iso30ExternalBodyStateBoundary;
  annotation(__MWORKS(version="26.3.0"));

end Diagnostics;