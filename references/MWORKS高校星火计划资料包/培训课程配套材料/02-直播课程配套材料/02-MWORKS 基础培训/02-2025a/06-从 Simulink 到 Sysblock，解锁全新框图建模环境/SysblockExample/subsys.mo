model subsys "子系统"
  import BaseWorkspace.*;
  import SysplorerEmbeddedCoder.Types.*;
  annotation(__MWORKS(version="2025a",modelType=Control,PortArrangement(Left(inport), Right(outport)),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true)),SysblockVersion="1.0"),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(Algorithm=Euler,Interval=-1));
  SysplorerEmbeddedCoder.Port.Inport inport 
    annotation (Placement(transformation(origin={-254,-9}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={-101.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})));
  SysplorerEmbeddedCoder.Port.Outport outport 
    annotation (Placement(transformation(origin={-70,-9}, 
extent={{-10,-10},{10,10}}), 
iconTransformation(origin={101.8,0}, 
extent={{-1.8,-1.8},{1.8,1.8}})));
  SubSystem1 subSystem1 annotation(Placement(transformation(origin = {-177.5,-9}, extent = {{-20,-10},{20,10}})));
  block SubSystem1 "选择子系统模块的设置。 要启用涉及代码生成的相关参数, 请选择 '视为原子单元' 。"

    annotation (__MWORKS(PortArrangement(Left(inport), Right(outport),Top()),BlockSystem(blockKind=BlockKind.subSystem, SampleTime(auto=true), SubSystem(virtual=true, functionPack=FunctionPack.auto, functionName="", sourceFile="")),independentInstance=true,hide=true,sourceModel=SysplorerEmbeddedCoder.SubSystems.SubSystem), Icon(coordinateSystem(extent={{-300, -120}, {300, 120}}, grid={2, 2}), graphics={Rectangle(origin = {0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, lineThickness = 1, extent = {{-300, 120}, {300, -120}}), Text(origin = {6.217248937900877e-15, -142}, lineColor = {0, 0, 0}, extent = {{0, 20}, {0, -20}}, textString = "%name", fontSize = 14, textStyle = {TextStyle.None}, textColor = {0, 0, 0}, verticalAlignment = TextAlignment.Top)}),Protection(access=Access.packageDuplicate));
    SysplorerEmbeddedCoder.Port.Outport outport 
      annotation (Placement(transformation(origin={-70,-9}, 
    extent={{-10,-10},{10,10}}), 
    iconTransformation(origin={101.8,0}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
    SubSystem1 subSystem1 annotation(Placement(transformation(origin = {-151,-9}, extent = {{-20,-10},{20,10}})));
    SysplorerEmbeddedCoder.Discontinuities.RateLimiter rateLimiter 
      annotation (Placement(transformation(origin={-204,-9}, 
    extent={{-10,-10},{10,10}})));
    SysplorerEmbeddedCoder.Port.Inport inport 
      annotation (Placement(transformation(origin={-254,-9}, 
    extent={{-10,-10},{10,10}}), 
    iconTransformation(origin={-101.8,0}, 
    extent={{-1.8,-1.8},{1.8,1.8}})));
    block SubSystem1 "选择子系统模块的设置。 要启用涉及代码生成的相关参数, 请选择 '视为原子单元' 。"

      annotation (__MWORKS(PortArrangement(Left(inport), Right(outport),Top()),BlockSystem(blockKind=BlockKind.subSystem, SampleTime(auto=true), SubSystem(virtual=true, functionPack=FunctionPack.auto, functionName="", sourceFile="")),independentInstance=true,hide=true,sourceModel=SysplorerEmbeddedCoder.SubSystems.SubSystem), Icon(coordinateSystem(extent={{-300, -120}, {300, 120}}, grid={2, 2}), graphics={Rectangle(origin = {0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, lineThickness = 1, extent = {{-300, 120}, {300, -120}}), Text(origin = {6.217248937900877e-15, -142}, lineColor = {0, 0, 0}, extent = {{0, 20}, {0, -20}}, textString = "%name", fontSize = 14, textStyle = {TextStyle.None}, textColor = {0, 0, 0}, verticalAlignment = TextAlignment.Top)}),Protection(access=Access.packageDuplicate));
      SysplorerEmbeddedCoder.Port.Outport outport 
        annotation (Placement(transformation(origin={-60,0}, 
      extent={{-10,-10},{10,10}}), 
      iconTransformation(origin={101.8,0}, 
      extent={{-1.8,-1.8},{1.8,1.8}})));
      SysplorerEmbeddedCoder.MathOperation.Sum sum1 
        annotation (Placement(transformation(origin = {-120, 0}, extent = {{-10, -10}, {10, 10}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));
      SysplorerEmbeddedCoder.Sources.Constant constant1 
        annotation (Placement(transformation(origin={-182,-18}, 
      extent={{-10,-10},{10,10}})));
      SysplorerEmbeddedCoder.Port.Inport inport 
        annotation (Placement(transformation(origin={-210,20}, 
      extent={{-10,-10},{10,10}}), 
      iconTransformation(origin={-101.8,0}, 
      extent={{-1.8,-1.8},{1.8,1.8}})));
    equation
      connect(constant1.y, sum1.u2) 
      annotation(Line(origin={-150,-7}, 
      points={{-20.2,-11},{0,-11},{0,2},{18.2,2}}, 
      color={0,0,0}));
      connect(inport, sum1.u1) 
      annotation(Line(origin={-165,13}, 
      points={{-33,7},{17,7},{17,-8},{33.2,-8}}, 
      color={0,0,0}));
      connect(outport, sum1.y) 
      annotation(Line(origin={-90,0}, 
      points={{18,0},{-18.2,2.22045e-16}}, 
      color={0,0,0}));
      end SubSystem1;
  equation
    connect(outport, subSystem1.outport) 
      annotation (Line(origin={0,0}, 
    points={{-82,-9},{-129.2,-9}}, 
    color={0,0,0}));
    connect(rateLimiter.u, inport) 
    annotation(Line(origin={-269,-9}, 
    points={{53.2,0},{27,0}}, 
    color={0,0,0}));
    connect(rateLimiter.y, subSystem1.inport) 
    annotation(Line(origin={-200,-9}, 
    points={{7.8,0},{27.2,0}}, 
    color={0,0,0}));
    end SubSystem1;
  equation
  connect(outport, subSystem1.outport) 
    annotation (Line(origin = {0, 0}, 
              points = { {0, 0}, {0, 0} }, 
              color = { 0, 0, 0 }));
  connect(inport, subSystem1.inport) 
    annotation (Line(origin = {0, 0}, 
              points = { {0, 0}, {0, 0} }, 
              color = { 0, 0, 0 }));
  end subsys;