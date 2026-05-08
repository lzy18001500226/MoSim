# ObsAvoidController_Sysblock2.mo

- Source: `培训课程配套材料/02-直播课程配套材料/06-智能无人系统应用挑战赛专项培训/00-模型材料/UGV/Control/ObstacleAvoidanceController/ObsAvoidController_Sysblock2.mo`
- Category: `quadrotor_uav`
- Score: `94`
- Size: `0.06 MB`
- Extract mode: `text`

## Extracted Text

```text
﻿model ObsAvoidController_Sysblock2 "避障控制（Sysblock）"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement(Left(front_dist, rear_dist, left_dist, right_dist), Right(speed, steer)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Dassl,Interval=0.01,InlineIntegrator=false,InlineStepSize=false,StartTime=0,StopTime=1,Tolerance=0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Text(origin={-171,58}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="前方传感器距离", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-171,16}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="后方传感器距离", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-171,-26}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="左方传感器距离", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={-171,-68}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="右方传感器距离", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={221,58}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="预期车速", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None), Text(origin={221,-58}, 
lineColor={0,0,0}, 
extent={{-19,10},{19,-10}}, 
textString="前轮转角", 
textStyle={TextStyle.None}, 
textColor={0,0,0}, 
horizontalAlignment=LinePattern.None)}),Protection(access=Access.diagram));
  SysplorerEmbeddedCoder.Port.Inport front_dist 
    annotation (Placement(transformation(origin={-136,58}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,75}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport rear_dist 
    annotation (Placement(transformation(origin={-136,16}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,25}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport left_dist 
    annotation (Placement(transformation(origin={-136,-26}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,-25}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Inport right_dist 
    annotation (Placement(transformation(origin={-136,-68}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,-75}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport speed 
    annotation (Placement(transformation(origin={178,58}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={101.8,50}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.Port.Outport steer 
    annotation (Placement(transformation(origin={178,-58}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={101.8,-50}, 
extent={{-1.8,-1.8},{1.8,1.8}})),__MWORKS(BlockSystem(Type(inherit=InheritType.none ,ref="double") ,Dimension(dimensionType=DimensionType.none)=1 ,SampleTime(group="D1")=0.01)));
  Chart chart 
    annotation (Placement(transformation(origin={-18,-7}, 
extent={{-29,-29},{29,29}})),__MWORKS(ComponentNamePlacement(BOTTOM),BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Sum sum1(isSaturate=false,inputs="+-") 
    annotation (Placement(transformation(origin={140,28}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="-",instance="u2")))));
  SysplorerEmbeddedCoder.MathOperation.Sum sum2(isSaturate=false,inputs="++") 
    annotation (Placement(transformation(origin={52,-26.5}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="+",instance="u1"),label(text="+",instance="u2")))));
  SysplorerEmbeddedCoder.Sources.Constant constant1(k=pi) 
    annotation (Placement(transformation(origin={1,-58}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.MathOperation.RoundingFunction roundingFunction 
    annotation (Placement(transformation(origin={62,16}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Product product1(isSaturate=false,inputs="*/") 
    annotation (Placement(transformation(origin={94,-31.5}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=1)),Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap) ,SampleTime(group="D1")=0.01),PortLabels(labelType="CustomType",labels(label(text="*",instance="u1"),label(text="/",instance="u2")))));
  SysplorerEmbeddedCoder.Sources.Constant constant2(k=2*pi) 
    annotation (Placement(transformation(origin={52,-58}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D1")=0.01,Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.MathOperation.Gain gain(k=2*pi) 
    annotation (Placement(transformation(origin={94,16}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Abs abs1 
    annotation (Placement(transformation(origin={-98,58}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Abs abs2 
    annotation (Placement(transformation(origin={-98,16}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Abs abs3 
    annotation (Placement(transformation(origin={-98,-26}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.MathOperation.Abs abs4 
    annotation (Placement(transformation(origin={-98,-68}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(Instance(u(Type(ref="double") ,Dimension=1) ,y(Type(ref="double") ,Dimension=1)),SampleTime(group="D1")=0.01)));
  block Chart "状态机"
    annotation (__MWORKS(BlockSystem(blockKind = BlockKind.stateMachine,SampleTime(auto = true),independent = true,StateMachine(virtual = false,functionPack = FunctionPack.auto,functionName = "",sourceFile = "",parallel=true)),PortArrangement(Left(df, db, dl, dr), Right(speed, steer)),sourceModel=SysplorerEmbeddedCoder.StateMachine.Chart,independentInstance=true,hide=true), 
      defaultComponentName = "chart", 
      Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
        grid = {2.0, 2.0}), graphics = {Rectangle(origin = {0.0, 0.0}, 
        lineColor = {74, 84, 154}, 
        fillColor = {255, 255, 255}, 
        lineThickness = 1.0, 
        extent = {{-100.0, 100.0}, {100.0, -100.0}}, 
        radius = 11.0), Rectangle(origin = {0.0, 27.0}, 
        lineColor = {74, 84, 154}, 
        fillColor = {255, 255, 255}, 
        lineThickness = 1.0, 
        extent = {{-25.0, 20.0}, {25.0, -20.0}}, 
        radius = 10.0), Rectangle(origin = {-40.0, -27.0}, 
        lineColor = {74, 84, 154}, 
        fillColor = {255, 255, 255}, 
        lineThickness = 1.0, 
        extent = {{-25.0, 20.0}, {25.0, -20.0}}, 
        radius = 10.0), Rectangle(origin = {40.0, -27.0}, 
        lineColor = {74, 84, 154}, 
        fillColor = {255, 255, 255}, 
        lineThickness = 1.0, 
        extent = {{-25.0, 20.0}, {25.0, -20.0}}, 
        radius = 10.0), Line(origin = {-40.0, 13.0}, 
        points = {{-10.0, -13.0}, {-10.0, 7.0}, {10.0, 13.0}}, 
        color = {74, 84, 154}, 
        thickness = 1.0, 
        arrow = {Arrow.None, Arrow.Filled}, 
        arrowSize = 8.0, 
        smooth = Smooth.Bezier), Line(origin = {41.0, 13.0}, 
        points = {{-9.0, 13.0}, {9.0, 11.0}, {9.0, -13.0}}, 
        color = {74, 84, 154}, 
        thickness = 1.0, 
        arrow = {Arrow.None, Arrow.Filled}, 
        arrowSize = 8.0, 
        smooth = Smooth.Bezier), Line(origin = {0.0, -28.0}, 
        points = {{10.0, 0.0}, {-10.0, 0.0}}, 
        color = {74, 84, 154}, 
        thickness = 1.0, 
        arrow = {Arrow.None, Arrow.Filled}, 
        arrowSize = 8.0, 
        smooth = Smooth.Bezier), Text(origin = {0.0, -120.0}, 
        lineColor = {74, 84, 154}, 
        extent = {{0, 20.0}, {0, -20.0}}, 
        textString = "%name", 
        fontSize = 14, 
        textStyle = {TextStyle.None}, 
        textColor = {74, 84, 154}, 
        verticalAlignment = TextAlignment.Top)}),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
  grid={2,2})),Protection(access=Access.diagram));
    SysplorerEmbeddedCoder.Port.Inport df annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Inport db annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Inport dl annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Inport dr annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Outport speed(start=0) annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Outport steer(start=0) annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransforma
```
