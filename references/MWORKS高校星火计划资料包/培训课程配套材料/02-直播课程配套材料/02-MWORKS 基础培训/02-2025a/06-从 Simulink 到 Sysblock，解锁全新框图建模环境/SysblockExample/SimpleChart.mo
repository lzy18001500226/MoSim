model SimpleChart "简单状态机"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=0.01,InlineIntegrator=false,InlineStepSize=false,IntegratorStep=0.01,StartTime=0,StopTime=1,Tolerance=0.0001),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
  block Chart "状态机"
    annotation (__MWORKS(BlockSystem(blockKind = BlockKind.stateMachine,SampleTime(auto = true),independent = true,StateMachine(virtual = false,functionPack = FunctionPack.auto,functionName = "",sourceFile = "",inEvents={Event_On, Event_Drive, Event_Reverse, Event_LowSpeed, Event_HighSpeed, Event_Off })),PortArrangement(Top(in_event),Right(Speed, Direction)),sourceModel=SysplorerEmbeddedCoder.StateMachine.Chart,independentInstance=true,hide=true), 
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
        verticalAlignment = TextAlignment.Top)}),Protection(access=Access.packageDuplicate));
    block State "状态"
      annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state,SampleTime(auto = true),State),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
       Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
         grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
         lineColor = {74, 84, 154}, 
         fillColor = {255, 255, 255}, 
         lineThickness = 1, 
         extent = {{-100, 100}, {100, -100}}, 
         radius = 11), Line(origin = {0, 80}, 
         points = {{-100, 0}, {100, 0}}, 
         color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
         lineColor = {0, 0, 128}, 
         extent = {{-100, 10}, {100, -10}}, 
         textString = "%name", 
         textStyle = {TextStyle.None}, 
         textColor = {0, 0, 128}), Text(origin = {0, -10}, 
         lineColor = {0, 0, 128}, 
         extent = {{-100, 90}, {100, -90}}, 
         textString = "algorithm", 
         fontSize = 16, 
         textStyle = {TextStyle.None}, 
         textColor = {0, 0, 128}, 
         horizontalAlignment = TextAlignment.Left, 
         verticalAlignment = TextAlignment.Top)}), 
       Diagram(coordinateSystem(extent={{-39,-29},{39,29}}, 
  initialScale=1, 
  grid={2,2}),graphics = {State(origin={0,0}, 
  stateTitle=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-37,21},{37,29}}, 
  textString="%name", 
  fontSize=16, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), 
  stateText=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-37,-29},{37,21}}, 
  textString="%algorithm", 
  fontSize=16, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left, 
  verticalAlignment=TextAlignment.Top), 
  stateLine = Line(origin={0,0}, 
  color = {74, 84, 154}, 
  points={{-40,22},{40,22}}))}),Protection(access=Access.packageDuplicate));
    algorithm
    annotation(__MWORKS(BlockSystem(StateMachine(actionKind = ActionKind.entry))));  Speed := 0;
      Direction := 0;
    end State;
    State Park 
      annotation (Placement(transformation(origin={-191,41}, 
  extent={{-39,-29},{39,29}})),__MWORKS(BlockSystem(StateMachine)));
    State1 Move 
      annotation (Placement(transformation(origin={42,-1}, 
  extent={{-162,-119},{162,119}})),__MWORKS(BlockSystem(StateMachine)));
    SysplorerEmbeddedCoder.Port.Outport Speed(start=0) annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Port.Outport Direction(start=0) annotation (__MWORKS(internalShare = true,BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    SysplorerEmbeddedCoder.Types.InputEvent Event_On=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[1], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEvent Event_Drive=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[2], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEvent Event_Reverse=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[3], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEvent Event_LowSpeed=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[4], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEvent Event_HighSpeed=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[5], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEvent Event_Off=SysplorerEmbeddedCoder.Types.ZeroCrossEvent(in_event[6], TriggerType.either) annotation (__MWORKS(internalShare = true));
    SysplorerEmbeddedCoder.Types.InputEventPort in_event annotation(__MWORKS(BlockSystem(Dimension(dimensionType=DimensionType.none)=[6],Type(ref="double"))),Placement(iconTransformation(extent={{-1.8, -1.8}, {1.8, 1.8}})));
    block State1 "状态"
      annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state, SampleTime(auto = true)),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
       Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
         grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
         lineColor = {74, 84, 154}, 
         fillColor = {255, 255, 255}, 
         lineThickness = 1, 
         extent = {{-100, 100}, {100, -100}}, 
         radius = 11), Line(origin = {0, 80}, 
         points = {{-100, 0}, {100, 0}}, 
         color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
         lineColor = {0, 0, 128}, 
         extent = {{-100, 10}, {100, -10}}, 
         textString = "%name", 
         textStyle = {TextStyle.None}, 
         textColor = {0, 0, 128}), Text(origin = {0, -10}, 
         lineColor = {0, 0, 128}, 
         extent = {{-100, 90}, {100, -90}}, 
         textString = "algorithm", 
         fontSize = 16, 
         textStyle = {TextStyle.None}, 
         textColor = {0, 0, 128}, 
         horizontalAlignment = TextAlignment.Left, 
         verticalAlignment = TextAlignment.Top)}), 
       Diagram(coordinateSystem(extent={{-162,-119},{162,119}}, 
  initialScale=1, 
  grid={2,2}),graphics = {State(origin={0,0}, 
  stateTitle=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-160,111},{160,119}}, 
  textString="%name", 
  fontSize=16, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), 
  stateText=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-160,-119},{160,111}}, 
  textString="%algorithm", 
  fontSize=16, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left, 
  verticalAlignment=TextAlignment.Top))}),Protection(access=Access.packageDuplicate));
      block State "状态"
        annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state,SampleTime(auto = true),State),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
         Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
           grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
           lineColor = {74, 84, 154}, 
           fillColor = {255, 255, 255}, 
           lineThickness = 1, 
           extent = {{-100, 100}, {100, -100}}, 
           radius = 11), Line(origin = {0, 80}, 
           points = {{-100, 0}, {100, 0}}, 
           color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
           lineColor = {0, 0, 128}, 
           extent = {{-100, 10}, {100, -10}}, 
           textString = "%name", 
           textStyle = {TextStyle.None}, 
           textColor = {0, 0, 128}), Text(origin = {0, -10}, 
           lineColor = {0, 0, 128}, 
           extent = {{-100, 90}, {100, -90}}, 
           textString = "algorithm", 
           fontSize = 16, 
           textStyle = {TextStyle.None}, 
           textColor = {0, 0, 128}, 
           horizontalAlignment = TextAlignment.Left, 
           verticalAlignment = TextAlignment.Top)}), 
         Diagram(coordinateSystem(extent={{-40, -30}, {40, 30}}, initialScale=1, grid={2, 2}), graphics = {State(origin = {0.0, 0.0}, 
              stateTitle = Text(origin = {0, 0}, 
              lineColor = {74, 84, 154}, 
              extent = {{-38, 22}, {38, 30}}, 
              textString = "%name", 
              fontSize = 16, 
              horizontalAlignment = TextAlignment.Left, 
              textStyle = {TextStyle.Bold}, 
              textColor = {74, 84, 154}, 
              verticalAlignment = TextAlignment.Center), 
              stateLine = Line(origin={0,0}, 
              color = {74, 84, 154}, 
              points={{-40,22},{40,22}}), 
              stateText = Text(origin = {0.0, 0.0}, 
              lineColor = {74, 84, 154}, 
              extent = {{-38, -30}, {38, 22}}, 
              textString = "%algorithm", 
              fontSize = 16, 
              textColor = {74, 84, 154}, 
              horizontalAlignment = TextAlignment.Left, 
              verticalAlignment = TextAlignment.Top))}),Protection(access=Access.packageDuplicate));
      algorithm
      annotation(__MWORKS(BlockSystem(StateMachine(actionKind = ActionKind.entry))));  Speed := 1;
        Direction := -1;
      end State;
      State Reverse 
        annotation (Placement(transformation(origin={-110,55}, 
  extent={{-40,-30},{40,30}})),__MWORKS(BlockSystem(StateMachine)));
      State1 Drive 
        annotation (Placement(transformation(origin={52,-29}, 
  extent={{-100,-80},{100,80}})),__MWORKS(BlockSystem(StateMachine)));
      block State1 "状态"
        annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state,SampleTime(auto = true),State),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
         Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
           grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
           lineColor = {74, 84, 154}, 
           fillColor = {255, 255, 255}, 
           lineThickness = 1, 
           extent = {{-100, 100}, {100, -100}}, 
           radius = 11), Line(origin = {0, 80}, 
           points = {{-100, 0}, {100, 0}}, 
           color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
           lineColor = {0, 0, 128}, 
           extent = {{-100, 10}, {100, -10}}, 
           textString = "%name", 
           textStyle = {TextStyle.None}, 
           textColor = {0, 0, 128}), Text(origin = {0, -10}, 
           lineColor = {0, 0, 128}, 
           extent = {{-100, 90}, {100, -90}}, 
           textString = "algorithm", 
           fontSize = 16, 
           textStyle = {TextStyle.None}, 
           textColor = {0, 0, 128}, 
           horizontalAlignment = TextAlignment.Left, 
           verticalAlignment = TextAlignment.Top)}), 
         Diagram(coordinateSystem(extent={{-100,-80},{100,80}}, 
  initialScale=1, 
  grid={2,2}),graphics = {State(origin={0,0}, 
  stateTitle=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-98,72},{98,80}}, 
  textString="%name", 
  fontSize=16, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), 
  stateText=Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{-98,-80},{98,72}}, 
  textString="%algorithm", 
  fontSize=16, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left, 
  verticalAlignment=TextAlignment.Top), 
  stateLine = Line(origin={0,0}, 
  color = {74, 84, 154}, 
  points={{-40,22},{40,22}}))}),Protection(access=Access.packageDuplicate));
        block State "状态"
          annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state,SampleTime(auto = true),State),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
           Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
             grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
             lineColor = {74, 84, 154}, 
             fillColor = {255, 255, 255}, 
             lineThickness = 1, 
             extent = {{-100, 100}, {100, -100}}, 
             radius = 11), Line(origin = {0, 80}, 
             points = {{-100, 0}, {100, 0}}, 
             color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
             lineColor = {0, 0, 128}, 
             extent = {{-100, 10}, {100, -10}}, 
             textString = "%name", 
             textStyle = {TextStyle.None}, 
             textColor = {0, 0, 128}), Text(origin = {0, -10}, 
             lineColor = {0, 0, 128}, 
             extent = {{-100, 90}, {100, -90}}, 
             textString = "algorithm", 
             fontSize = 16, 
             textStyle = {TextStyle.None}, 
             textColor = {0, 0, 128}, 
             horizontalAlignment = TextAlignment.Left, 
             verticalAlignment = TextAlignment.Top)}), 
           Diagram(coordinateSystem(extent={{-40, -30}, {40, 30}}, initialScale=1, grid={2, 2}), graphics = {State(origin = {0.0, 0.0}, 
                stateTitle = Text(origin = {0, 0}, 
                lineColor = {74, 84, 154}, 
                extent = {{-38, 22}, {38, 30}}, 
                textString = "%name", 
                fontSize = 16, 
                horizontalAlignment = TextAlignment.Left, 
                textStyle = {TextStyle.Bold}, 
                textColor = {74, 84, 154}, 
                verticalAlignment = TextAlignment.Center), 
                stateLine = Line(origin={0,0}, 
                color = {74, 84, 154}, 
                points={{-40,22},{40,22}}), 
                stateText = Text(origin = {0.0, 0.0}, 
                lineColor = {74, 84, 154}, 
                extent = {{-38, -30}, {38, 22}}, 
                textString = "%algorithm", 
                fontSize = 16, 
                textColor = {74, 84, 154}, 
                horizontalAlignment = TextAlignment.Left, 
                verticalAlignment = TextAlignment.Top))}),Protection(access=Access.packageDuplicate));
        algorithm
        annotation(__MWORKS(BlockSystem(StateMachine(actionKind = ActionKind.entry))));  Speed := 1;
        end State;
        State LowSpeed 
          annotation (Placement(transformation(origin={-50,12}, 
  extent={{-40,-30},{40,30}})),__MWORKS(BlockSystem(StateMachine)));
        State1 HighSpeed 
          annotation (Placement(transformation(origin={54,-44}, 
  extent={{-40,-30},{40,30}})),__MWORKS(BlockSystem(StateMachine)));
        block State1 "状态"
          annotation (__MWORKS(BlockSystem(blockKind=BlockKind.state, SampleTime(auto = true)),showDiagram = true,sourceModel=SysplorerEmbeddedCoder.StateMachine.State,independentInstance=true,hide=true), defaultComponentName = "state", 
           Icon(coordinateSystem(extent={{-100, -100}, {100, 100}}, 
             grid={2, 2}), graphics={Rectangle(origin = {0, 0}, 
             lineColor = {74, 84, 154}, 
             fillColor = {255, 255, 255}, 
             lineThickness = 1, 
             extent = {{-100, 100}, {100, -100}}, 
             radius = 11), Line(origin = {0, 80}, 
             points = {{-100, 0}, {100, 0}}, 
             color = {74, 84, 154}, thickness = 1), Text(origin = {0, 90}, 
             lineColor = {0, 0, 128}, 
             extent = {{-100, 10}, {100, -10}}, 
             textString = "%name", 
             textStyle = {TextStyle.None}, 
             textColor = {0, 0, 128}), Text(origin = {0, -10}, 
             lineColor = {0, 0, 128}, 
             extent = {{-100, 90}, {100, -90}}, 
             textString = "algorithm", 
             fontSize = 16, 
             textStyle = {TextStyle.None}, 
             textColor = {0, 0, 128}, 
             horizontalAlignment = TextAlignment.Left, 
             verticalAlignment = TextAlignment.Top)}), 
           Diagram(coordinateSystem(extent={{-40, -30}, {40, 30}}, initialScale=1, grid={2, 2}), graphics = {State(origin = {0.0, 0.0}, 
                stateTitle = Text(origin = {0, 0}, 
                lineColor = {74, 84, 154}, 
                extent = {{-38, 22}, {38, 30}}, 
                textString = "%name", 
                fontSize = 16, 
                horizontalAlignment = TextAlignment.Left, 
                textStyle = {TextStyle.Bold}, 
                textColor = {74, 84, 154}, 
                verticalAlignment = TextAlignment.Center), 
                stateLine = Line(origin={0,0}, 
                color = {74, 84, 154}, 
                points={{-40,22},{40,22}}), 
                stateText = Text(origin = {0.0, 0.0}, 
                lineColor = {74, 84, 154}, 
                extent = {{-38, -30}, {38, 22}}, 
                textString = "%algorithm", 
                fontSize = 16, 
                textColor = {74, 84, 154}, 
                horizontalAlignment = TextAlignment.Left, 
                verticalAlignment = TextAlignment.Top))}),Protection(access=Access.packageDuplicate));
        end State1;
      equation
        initialState(LowSpeed, true, 1) 
        annotation(Line(origin={42.0979,20.0326}, 
        points={{0,8.03263},{0,-8.03263}}, 
        color={113,119,170}, 
        smooth=Smooth.Bezier),Text(origin={0.311836,-1.24735}, 
        lineColor={74,84,154}, 
        extent={{0,-3},{0,3}}, 
        textString="%condition", 
        fontSize=10, 
        textStyle={TextStyle.Bold}, 
        textColor={74,84,154}), displayText = "[true]");
        transition(LowSpeed, HighSpeed, Event_HighSpeed, reset = false,CA = "Speed = 2") 
        annotation(Line(origin={115.836,-23.1637}, 
  points={{-31.8363,3.27877},{14.2788,-20.8363}}, 
  color={113,119,170}, 
  smooth=Smooth.Bezier),Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{0,-3},{0,3}}, 
  textString="%condition", 
  fontSize=10, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition=true))), displayText ="[Event_HighSpeed]{Speed = 2}");
        transition(HighSpeed, LowSpeed, Event_LowSpeed, reset = false,CA = "Speed = 1") 
        annotation(Line(origin={74.6866,-70.3038}, 
  points={{33.3134,-3.76472},{-14.7743,22.3038}}, 
  color={113,119,170}, 
  smooth=Smooth.Bezier),Text(origin={-28.3488,-6.56004}, 
  lineColor={74,84,154}, 
  extent={{0,-3},{0,3}}, 
  textString="%condition", 
  fontSize=10, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition=true))), displayText = "[Event_LowSpeed]{Speed = 1}");
      algorithm
      annotation(__MWORKS(BlockSystem(StateMachine(actionKind = ActionKind.entry or ActionKind.during))));  Direction := 1;
      end State1;
    equation
      transition(Reverse, Drive, Event_Drive, reset = false) 
      annotation(Line(origin={1.87055,70.0653}, 
      points={{-29.8706,3.42001},{13.2253,-20.0653}}, 
      color={113,119,170}, 
      smooth=Smooth.Bezier),Text(origin={0,0}, 
      lineColor={74,84,154}, 
      extent={{0,-3},{0,3}}, 
      textString="%condition", 
      fontSize=10, 
      textStyle={TextStyle.Bold}, 
      textColor={74,84,154}, 
      horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition = true))), displayText = "[Event_Drive]");
      transition(Drive, Reverse, Event_Reverse, reset = false) 
      annotation(Line(origin={-45.9389,-8.81243}, 
      points={{39.9389,-8.562},{-15.6884,32.8124}}, 
      color={113,119,170}, 
      smooth=Smooth.Bezier),Text(origin={0,0}, 
      lineColor={74,84,154}, 
      extent={{0,-3},{0,3}}, 
      textString="%condition", 
      fontSize=10, 
      textStyle={TextStyle.Bold}, 
      textColor={74,84,154}, 
      horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition = true))), displayText = "[Event_Reverse]");
      initialState(Drive, true, 1) 
      annotation(Line(origin={58.8832,60}, 
  points={{0,10},{0,-10}}, 
  color={113,119,170}, 
  smooth=Smooth.Bezier),Text(origin={0,0}, 
  lineColor={74,84,154}, 
  extent={{0,-3},{0,3}}, 
  textString="%condition", 
  fontSize=10, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}), displayText ="[true]",__MWORKS(BlockSystem(StateMachine(outerTransition=false))));
    end State1;
  equation
    initialState(Park, true, 1) 
    annotation(Line(origin={-206,80}, 
    points={{0,10},{0,-10}}, 
    color={113,119,170}, 
    smooth=Smooth.Bezier),Text(origin={0,0}, 
    lineColor={74,84,154}, 
    extent={{0,-3},{0,3}}, 
    textString="%condition", 
    fontSize=10, 
    textStyle={TextStyle.Bold}, 
    textColor={74,84,154}), displayText = "[true]");
    transition(Park, Move, Event_On, reset = false) 
    annotation(Line(origin={-136,48.7088}, 
  points={{-16,0},{16,0}}, 
  color={113,119,170}, 
  smooth=Smooth.Bezier),Text(origin={-9.94758,-1.02906}, 
  lineColor={74,84,154}, 
  extent={{0,-3},{0,3}}, 
  textString="%condition", 
  fontSize=10, 
  textStyle={TextStyle.Bold}, 
  textColor={74,84,154}, 
  horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition=true))), displayText ="[Event_On]");
    transition(Move, Park, Event_Off, reset = false,CA = "Speed = 0") 
    annotation(Line(origin={-136,32.9299}, 
    points={{16,-3.55271e-15},{-16,3.55271e-15}}, 
    color={113,119,170}, 
    smooth=Smooth.Bezier),Text(origin={-15.676,-6.38017}, 
    lineColor={74,84,154}, 
    extent={{0,-3},{0,3}}, 
    textString="%condition", 
    fontSize=10, 
    textStyle={TextStyle.Bold}, 
    textColor={74,84,154}, 
    horizontalAlignment=TextAlignment.Left), __MWORKS(BlockSystem(StateMachine(outerTransition = true))), displayText ="[Event_Off]{Speed = 0}");
  end Chart;
  model ModelWorkspace
    annotation(__MWORKS(hide = true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
  Chart chart 
    annotation (Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
  SysplorerEmbeddedCoder.SignalRouting.Mux mux(portNumber=6) 
    annotation (Placement(transformation(origin={-42,32.5}, 
extent={{-2,-73.5},{2,73.5}})),__MWORKS(BlockSystem(Instance(u(u1(Type(ref="double") ,Dimension=1) ,u2(Type(ref="double") ,Dimension=1) ,u3(Type(ref="double") ,Dimension=1) ,u4(Type(ref="double") ,Dimension=1) ,u5(Type(ref="double") ,Dimension=1) ,u6(Type(ref="double") ,Dimension=1)) ,y(Type(ref="double") ,Dimension=[6])),SampleTime(group="D0")=0),ComponentNamePlacement(BOTTOM)));
  SysplorerEmbeddedCoder.Sources.Step step(stepTime=0.2,initialValue=0,finalValue=1) 
    annotation (Placement(transformation(origin={-80,93.75}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0 ,Instance(initialValue(Type(ref="double") ,Dimension=1) ,finalValue(Type(ref="double") ,Dimension=1) ,y(Dimension=1) ,stepTime(Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant constant1(k=0) 
    annotation (Placement(transformation(origin={-80,69.25}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Step step1(stepTime=0.3,initialValue=0,finalValue=1) 
    annotation (Placement(transformation(origin={-80,44.75}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0 ,Instance(initialValue(Type(ref="double") ,Dimension=1) ,finalValue(Type(ref="double") ,Dimension=1) ,y(Dimension=1) ,stepTime(Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant constant2(k=0) 
    annotation (Placement(transformation(origin={-80,20.25}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Step step2(stepTime=0.02,initialValue=0,finalValue=1) 
    annotation (Placement(transformation(origin={-80,-28.75}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=false)=0 ,Instance(initialValue(Type(ref="double") ,Dimension=1) ,finalValue(Type(ref="double") ,Dimension=1) ,y(Dimension=1) ,stepTime(Dimension=1)))));
  SysplorerEmbeddedCoder.Sources.Constant constant3(k=0) 
    annotation (Placement(transformation(origin={-80,-4.25}, 
extent={{-10,-10},{10,10}})),__MWORKS(BlockSystem(SampleTime(auto=true,group="D0")=0,Instance(y(Type(ref="double") ,Dimension=1) ,k(Type(ref="double") ,Dimension=1)))));
equation
  connect(mux.y, chart.in_event) 
  annotation(Line(origin={-19,16}, 
  points={{-19.95,4},{19,4},{19,-4.2}}, 
  color={0,0,0}));
  connect(mux.u1, step.y) 
  annotation(Line(origin={-60,71}, 
points={{14.2,22.75},{-8.2,22.75}}, 
color={0,0,0}));
  connect(mux.u2, constant1.y) 
  annotation(Line(origin={-57,69}, 
  points={{11.2,0.25},{-11.2,0.25}}, 
  color={0,0,0}));
  connect(mux.u3, step1.y) 
  annotation(Line(origin={-57,45}, 
  points={{11.2,-0.25},{-11.2,-0.25}}, 
  color={0,0,0}));
  connect(constant2.y, mux.u4) 
  annotation(Line(origin={-57,20}, 
  points={{-11.2,0.25},{11.2,0.25}}, 
  color={0,0,0}));
  connect(constant3.y, mux.u5) 
  annotation(Line(origin={-57,-4}, 
points={{-11.2,-0.25},{11.2,-0.25}}, 
color={0,0,0}));
  connect(step2.y, mux.u6) 
  annotation(Line(origin={-57,-29}, 
  points={{-11.2,0.25},{11.2,0.25}}, 
  color={0,0,0}));
  end SimpleChart;