model ROSDrive_Control_V1 "具身智能无人船仿真平台模型"
constant Real pi=Modelica.Constants.pi;
  Components.USV130_3DOF_Dynamic_Model1 uSV130_3DOF_Dynamic_Model 
    annotation (Placement(transformation(origin={94,99.5264}, 
extent={{-33,-31.9378},{33,31.9378}})));
  TYUtility.SignalRouting.Goto Parameter[13](redeclare Modelica.Blocks.Interfaces.RealInput u) 
    annotation (Placement(transformation(origin={232.0691,28.005}, 
extent={{-11.9309,-9.30611},{11.9309,8.82887}})),HideResult=true);
  Modelica.Blocks.Sources.RealExpression L(y=1.3) 
    annotation (Placement(transformation(origin={178.9851,109.667}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression B(y=0.64) 
    annotation (Placement(transformation(origin={178.9851,96.0166}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Bhull(y=0.21) 
    annotation (Placement(transformation(origin={178.9851,82.3662}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression mass(y=50) 
    annotation (Placement(transformation(origin={178.9851,68.7162}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression LCG(y=0.45) 
    annotation (Placement(transformation(origin={178.9851,55.0664}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression g(y=9.8) 
    annotation (Placement(transformation(origin={178.9851,41.4164}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression T(y=0.12) 
    annotation (Placement(transformation(origin={178.9851,27.7664}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Cd(y=0.5) 
    annotation (Placement(transformation(origin={178.9851,14.1164}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression rho(y=1000) 
    annotation (Placement(transformation(origin={178.9851,0.466761}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Xu_linear(y=75.55) 
    annotation (Placement(transformation(origin={178.9851,-13.1832}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Xuu_linear(y=-70.92) 
    annotation (Placement(transformation(origin={178.9851,-41.9632}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Xu_poly(y=25) 
    annotation (Placement(transformation(origin={178.9441,-27.8406}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.RealExpression Xuu_poly(y=0) 
    annotation (Placement(transformation(origin={178.828,-56.3406}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.init init(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor)) 
    annotation (Placement(transformation(origin={-114,117.3662}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.routePlane routePlan(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02) 
    annotation (Placement(transformation(origin={-114,-58.2439}, 
extent={{-10,-9.99998},{10,10}})));
  ImportedTypes.getModelCommand getModelCommand(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02) 
    annotation (Placement(transformation(origin={-114,47.121904}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.setModelReply setModelReply(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02) 
    annotation (Placement(transformation(origin={-114,12}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.getModelParams getModelParams(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02) 
    annotation (Placement(transformation(origin={-114,82.24384}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.ContinuousClock continuousClock 
    annotation (Placement(transformation(origin={-170.1382,117.3662}, 
extent={{-10,-10},{10,10}})));
  TYUtility.SignalRouting.From from[13](redeclare connector OutputConnectorType = Modelica.Blocks.Interfaces.RealOutput,y=Parameter.u) 
    annotation (Placement(transformation(origin={-168.2073,2.36115}, 
extent={{-11.9309,-9.30611},{11.9309,8.82887}})),HideResult=true);
  Components.Navigation.NavSys navSys(routeWPRadius=5) 
    annotation (Placement(transformation(origin={-10,99.5264}, 
extent={{-33,-31.9378},{33,31.9378}})));
  Components.ModeSwitch.Auto_Switch auto_Switch 
    annotation (Placement(transformation(origin={-10,-41.9382}, 
extent={{-33,-31.9377},{33,31.9378}})));
  ImportedTypes.getShipStatus getShipStatus(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02) 
    annotation (Placement(transformation(origin={-114,-23.122}, 
extent={{-10,-9.99999},{10,10}})));
  Utilities.joystick.joystick joystick1(combiTimeTable(table={{0.0, 0}, {1, 0}}),combiTimeTable1(table={{0.0, 0}, {1, 0}})) 
    annotation (Placement(transformation(origin={-10,26.2645}, 
extent={{-14.5,-14.4252},{14.5,14.4252}})));
  Animation.Ship ship(x = uSV130_3DOF_Dynamic_Model.n_global[1], y = uSV130_3DOF_Dynamic_Model.n_global[2], z = 0, phi = 0, theta = 0, psi = uSV130_3DOF_Dynamic_Model.n_global[3],prismatic1(n={0,1,0}),prismatic2(n={0,0,1})) 
    annotation (Placement(transformation(origin={94,-39.9381}, 
extent={{-28.5,-25.93795},{28.5,25.93795}})));
  annotation(experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.1,StartTime=0,StopTime=inf,Tolerance=1e-06),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=30,ContinueTimeVector)),Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={93,26}, 
lineColor={195,255,190}, 
fillColor={195,255,190}, 
fillPattern=FillPattern.Solid, 
extent={{-161,124},{161,-124}}, 
radius=5), Rectangle(origin={-134,26}, 
lineColor={255,249,198}, 
fillColor={255,249,198}, 
fillPattern=FillPattern.Solid, 
extent={{-60,124},{60,-124}}, 
radius=5), Rectangle(origin={-10,26}, 
lineColor={0,0,128}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-50,114},{50,-114}}, 
radius=5), Text(origin={-10,59.0621}, 
lineColor={0,0,128}, 
extent={{-21,6.0043},{21,-6.0043}}, 
textString="导航算法", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}), Rectangle(origin={94,26.2645}, 
lineColor={0,0,128}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-50,114},{50,-114}}, 
radius=5), Text(origin={94,30.6897}, 
lineColor={0,0,128}, 
extent={{-33,10},{33,-10}}, 
textString="被控对象", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}), Text(origin={-171,-89.9957}, 
lineColor={0,0,128}, 
extent={{-21,6.0043},{21,-6.0043}}, 
textString="ROS通信", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}), Rectangle(origin={198,26}, 
lineColor={0,0,128}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-50,114},{50,-114}}, 
radius=5), Text(origin={218,134.26}, 
lineColor={0,0,128}, 
extent={{-26,6.0043},{26,-6.0043}}, 
textString="参数设置区域", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}), Text(origin={-10,4.46246}, 
lineColor={0,0,128}, 
extent={{-21,6.0043},{21,-6.0043}}, 
textString="外接设备", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128}), Text(origin={-10,-80}, 
lineColor={0,0,128}, 
extent={{-21,6.0043},{21,-6.0043}}, 
textString="模式切换", 
fontName="黑体", 
textStyle={TextStyle.Bold}, 
textColor={0,0,128})}));
  package ImportedTypes
    model TCPIPServer
      annotation (
        Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          preserveAspectRatio = false, 
          grid = {2.0, 2.0})), 
        Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}}, 
          grid = {2.0, 2.0}), graphics = {Polygon(origin = {-1.4210854715202004e-14, -2.0}, 
          lineColor = {0, 0, 255}, 
          fillColor = {255, 255, 255}, 
          pattern = LinePattern.None, 
          fillPattern = FillPattern.Solid, 
          points = {{0.0, -100.0}, {-80.0, -100.0}, {-88.0, -98.0}, {-94.0, -94.0}, {-98.0, -88.0}, {-100.0, -80.0}, {-100.0, 80.0}, {-98.0, 88.0}, {-94.0, 94.0}, {-88.0, 98.0}, {-80.0, 100.0}, {80.0, 100.0}, {88.0, 98.0}, {94.0, 94.0}, {98.0, 88.0}, {100.0, 80.0}, {100.0, -80.0}, {98.0, -88.0}, {94.0, -94.0}, {88.0, -98.0}, {80.0, -100.0}, {0.0, -100.0}}), Text(origin = {-1.4210854715202004e-14, -2.0}, 
          lineColor = {204, 204, 204}, 
          extent = {{-92.0, 94.99999999999999}, {92.0, -94.99999999999999}}, 
          textString = "S", 
          textStyle = {TextStyle.None}, 
          textColor = {204, 204, 204}, 
          horizontalAlignment = LinePattern.None), Line(origin = {0.0, 0.0}, 
          points = {{0.0, -100.0}, {-80.0, -100.0}, {-88.0, -98.0}, {-94.0, -94.0}, {-98.0, -88.0}, {-100.0, -80.0}, {-100.0, 80.0}, {-98.0, 88.0}, {-94.0, 94.0}, {-88.0, 98.0}, {-80.0, 100.0}, {80.0, 100.0}, {88.0, 98.0}, {94.0, 94.0}, {98.0, 88.0}, {100.0, 80.0}, {100.0, -80.0}, {98.0, -88.0}, {94.0, -94.0}, {88.0, -98.0}, {80.0, -100.0}, {0.0, -100.0}}, 
          color = {0, 64, 127}, 
          thickness = 0.5), Line(origin = {0.0, 0.0}, 
          points = {{-80.0, 0.0}, {80.0, 0.0}}, 
          color = {0, 127, 0}), Ellipse(origin = {-80.0, 0.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Rectangle(origin = {-40.0, 30.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Rectangle(origin = {-10.0, -30.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Rectangle(origin = {20.0, 30.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Rectangle(origin = {50.0, -30.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Line(origin = {-40.0, 10.0}, 
          points = {{0.0, -10.0}, {0.0, 10.0}}, 
          color = {0, 127, 0}), Line(origin = {-10.0, -10.0}, 
          points = {{0.0, -10.0}, {0.0, 10.0}}, 
          color = {0, 127, 0}), Line(origin = {20.0, 10.0}, 
          points = {{0.0, -10.0}, {0.0, 10.0}}, 
          color = {0, 127, 0}), Line(origin = {50.0, -10.0}, 
          points = {{0.0, -10.0}, {0.0, 10.0}}, 
          color = {0, 127, 0}), Ellipse(origin = {80.0, 0.0}, 
          lineColor = {0, 127, 0}, 
          fillColor = {0, 127, 0}, 
          fillPattern = FillPattern.Solid, 
          extent = {{-10.0, 10.0}, {10.0, -10.0}}), Text(origin = {-9.999999999999996, 113.99999999999999}, 
          extent = {{-150.0, 20.0}, {150.0, -20.0}}, 
          textString = "%name")}), 
        __MWorks(Cosim(Model(Name = ""), Simulator(Type = "PythonSim", Version = "", Platform = ""), Environment(Host = "127.0.0.1", ModelDir = "", ModelPosi = "Slave"), Simulation(StartTime = "0", StopTime = "100", TimeStep = "0.01"), SQL(Server = "", Database = "", User = "", Passwd = "", Project = "", Network = ""), Description = "Cosim")), 
        Documentation(info = "<p>模型通过外部对象调用TCPIP模块对数据进行处理，并将处理过的数据返回模型。</p>
<div>
<p>详细使用说明请参考：<a href=\"modelica://TYModelInterfaces/Resources/Document/TCPIP.pdf\">用户使用手册</a>。</p>
</div>"    ));
      import Modelica;
      constant Integer id = 1 "model identity";
      //parameter Modelica.SIunits.Period mdlSampleTime = 0.01 "model step size";
      constant Real cosimSampleTime = 0.01 "model step size";
      parameter Real realOutputStart[:] = {1,1,1,1};
      parameter Integer intOutputStart[:] = {1};
      parameter Boolean boolOutputStart[:] = {true};

      TYModelInterfaces.SoftwareInterfaces.CommunicationServer.BaseComp mda(modelID = id, cosimSampleTime = cosimSampleTime, 
        inputsDim = {3, 13}, inputsDimInt = {0}, inputsDimBool = {0}, outputsDim = {1, 1, 1, 1}, outputsDimInt = {0}, outputsDimBool = {0}, 
        realOutputStart = realOutputStart, intOutputStart = intOutputStart, boolOutputStart = boolOutputStart,inNum=0,outNum=0) 

        annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealInput in1[3] 
      annotation (Placement(transformation(origin = {-110, 33.3333}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "0,0,0",TypeSet = "double" ,Note = "");
      Modelica.Blocks.Interfaces.RealInput in2[13] 
      annotation (Placement(transformation(origin = {-110, -33.3333}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "0,0,0,0,0,0,0,0,0,0,0,0,0",TypeSet = "double" ,Note = "");
      Modelica.Blocks.Interfaces.RealOutput out1 
      annotation (Placement(transformation(origin = {110, 60}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "",TypeSet = "double" ,Note = "");
      Modelica.Blocks.Interfaces.RealOutput out2 
      annotation (Placement(transformation(origin = {110, 20}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "",TypeSet = "double" ,Note = "");
      Modelica.Blocks.Interfaces.RealOutput out3 
      annotation (Placement(transformation(origin = {110, -20}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "",TypeSet = "double" ,Note = "");
      Modelica.Blocks.Interfaces.RealOutput out4 
      annotation (Placement(transformation(origin = {110, -60}, 
      extent = {{-10, -10}, {10, 10}}),visible = true), ID = "", InitialValue = "",TypeSet = "double" ,Note = "");
      equation
      connect(in1[:], mda.inputs[1:3]) 
      annotation (Line(origin = {-61, 15}, 
                             points = {{-49, 18.3333}, {0, 18.3333}, {0, -17.9333}, {49, -17.9333}}, 
                             color = {0, 0, 127}));
      connect(in2[:], mda.inputs[4:16]) 
      annotation (Line(origin = {-61, -18}, 
                             points = {{-49, -15.3333}, {0, -15.3333}, {0, 15.0667}, {49, 15.0667}}, 
                             color = {0, 0, 127}));
      connect(out1, mda.outputs[1]) 
      annotation (Line(origin = {60, 28}, 
                             points = {{50, 32}, {0, 32}, {0, -30.9333}, {-49, -30.9333}}, 
                             color = {0, 0, 127}));
      connect(out2, mda.outputs[2]) 
      annotation (Line(origin = {60, 8}, 
                             points = {{50, 12}, {0, 12}, {0, -10.9333}, {-49, -10.9333}}, 
                             color = {0, 0, 127}));
      connect(out3, mda.outputs[3]) 
      annotation (Line(origin = {60, -11}, 
                             points = {{50, -9}, {0, -9}, {0, 8.06667}, {-49, 8.06667}}, 
                             color = {0, 0, 127}));
      connect(out4, mda.outputs[4]) 
      annotation (Line(origin = {60, -31}, 
                             points = {{50, -29}, {0, -29}, {0, 28.0667}, {-49, 28.0667}}, 
                             color = {0, 0, 127}));
      end TCPIPServer;
    function UseConstructorWindowspython37 
      "Construct an external Function that can be used to store a Python Function - Windows"
    extends PythonIO.Communication.PythonFunction.constructor;
    external "C" initPythonMemory() 
    annotation(Library = { "python_io_python37", "" }, 
    LibraryDirectory ="modelica://PythonIO/Resources/Library");
    annotation(Documentation);
    end UseConstructorWindowspython37;
    function FunctionUseExchangeDataWindowspython37 
      "Function that communicates with Python"
    extends PythonIO.Communication.PythonFunction.exchangeData;
    external "C" stepFunction(pythonPath, pythonFilePath, moduleName, functionName, 
    inputs, inputs_int, inputs_str, inputDims, 
    inputTypes, 
    size(inputDims, 1), size(inputDims, 2), 
    outputDims, outputTypes, 
    size(outputDims, 1), size(outputDims, 2), 
    outputs, outputs_int, outputs_str, 
    hasInput, hasOutput) 
    annotation(Library = { "python_io_python37", "" }, 
    LibraryDirectory ="modelica://PythonIO/Resources/Library", 
    IncludeDirectory ="modelica://PythonIO/Resources/C-Sources", 
    Include = "#include \"pythonWrapper.c\"");
    end FunctionUseExchangeDataWindowspython37;
    function ObjectUseExchangeDataWindowspython37 
      "Function that communicates with Python"
    extends PythonIO.Communication.PythonObject.exchangeData;
    external "C" stepImpl(pythonPath, pythonFilePath, moduleName, className, 
    inputs, inputs_int, inputs_str, inputDims, 
    inputTypes, 
    size(inputDims, 1), size(inputDims, 2), 
    outputDims, outputTypes, 
    size(outputDims, 1), size(outputDims, 2), 
    outputs, outputs_int, outputs_str, 
    hasInput, hasOutput) 
    annotation(Library = { "python_io_python37", "" }, 
    LibraryDirectory ="modelica://PythonIO/Resources/Library", 
    IncludeDirectory ="modelica://PythonIO/Resources/C-Sources", 
    Include = "#include \"pythonWrapper.c\"");
    end ObjectUseExchangeDataWindowspython37;
    function UseDestructorWindowspython37 
      "Release memory"
    extends PythonIO.Communication.PythonFunction.destructor;
    external "C" freePythonMemory() 
    annotation(Library = { "python_io_python37", "" }, 
    LibraryDirectory ="modelica://PythonIO/Resources/Library");
    annotation(Documentation);
    end UseDestructorWindowspython37;
    package ArrayConverter
      model _A2V_1D_Real 
      "1 dimension Real array to Real vector"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[dims[1]] 
          annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[product(dims)] 
          annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[pos] := u[i1];
          pos := pos + 1;
        end for;
      end _A2V_1D_Real;
      model _V2A_1D_Real 
      "Real vector to 1 dimension Real array"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := u[pos];
          pos := pos + 1;
        end for;
      end _V2A_1D_Real;
      model _A2V_1D_Integer 
      "1 dimension Integer array to Real vector"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.IntegerInput u[dims[1]] 
          annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[product(dims)] 
          annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[pos] := u[i1];
          pos := pos + 1;
        end for;
      end _A2V_1D_Integer;
      model _V2A_1D_NPY_Object 
      "Real vector to 1 dimension NPY_Object array"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.IntegerInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.IntegerOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := u[pos];
          pos := pos + 1;
          y[i1] := u[pos];
          pos := pos + 1;
        end for;
      end _V2A_1D_NPY_Object;
      model _V2A_1D_Boolean 
      "Real vector to 1 dimension Boolean array"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.BooleanOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := noEvent(if u[pos] > 0.5 then true else false);
          pos := pos + 1;
        end for;
      end _V2A_1D_Boolean;
      model _V2A_1D_Integer 
      "Real vector to 1 dimension Integer array"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.IntegerOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := noEvent(integer(u[pos] + 0.5));
          pos := pos + 1;
        end for;
      end _V2A_1D_Integer;
      model _A2V_1D_Boolean 
      "1 dimension Boolean array to Real vector"
        extends Modelica.Icons.InterfacesPackage;
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.BooleanInput u[dims[1]] 
          annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[product(dims)] 
          annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[pos] := if u[i1] then 1 else 0;
          pos := pos + 1;
        end for;
      end _A2V_1D_Boolean;

    end ArrayConverter;
    model com
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1}},outputTypes={0},hasOutput=true,output_str_name={"output1"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226",functionName="com",moduleName="test4") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_output1_converter.y[1], output1) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_output1_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end com;
    model getDataToRos
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0,0},hasOutput=true,output_str_name={"output1","output2","output3","output4","output5","output6"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226",functionName="getDataToRos",moduleName="test4") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput output2 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 60})));
      ArrayConverter._V2A_1D_Real out_output2_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 60})));
      Modelica.Blocks.Interfaces.RealOutput output3 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 20})));
      ArrayConverter._V2A_1D_Real out_output3_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 20})));
      Modelica.Blocks.Interfaces.RealOutput output4 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -20})));
      ArrayConverter._V2A_1D_Real out_output4_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -20})));
      Modelica.Blocks.Interfaces.RealOutput output5 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -60})));
      ArrayConverter._V2A_1D_Real out_output5_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -60})));
      Modelica.Blocks.Interfaces.RealOutput output6 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_output6_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_output1_converter.y[1], output1) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_output1_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_output2_converter.y[1], output2) 
      annotation(Line(origin={0,0}, 
      points={{110,60},{80,60}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_output2_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,60}}, 
      color={255,0,0}));
      connect(out_output3_converter.y[1], output3) 
      annotation(Line(origin={0,0}, 
      points={{110,20},{80,20}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_output3_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,20}}, 
      color={255,0,0}));
      connect(out_output4_converter.y[1], output4) 
      annotation(Line(origin={0,0}, 
      points={{110,-20},{80,-20}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_output4_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-20}}, 
      color={255,0,0}));
      connect(out_output5_converter.y[1], output5) 
      annotation(Line(origin={0,0}, 
      points={{110,-60},{80,-60}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_output5_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-60}}, 
      color={255,0,0}));
      connect(out_output6_converter.y[1], output6) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[6], out_output6_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end getDataToRos;
    model getDataFromRos
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0,0,0,0,0,0,0,2},hasOutput=true,output_str_name={"lng","lat","realSpeed","heading","destLng","destLat","prevLng","prevLat","shipToPrevWPDistance","shipToNextWPDistance","shipToRouteDistance","workmode"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226",functionName="getDataFromRos",moduleName="test4") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput lng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_lng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput lat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 81.8182})));
      ArrayConverter._V2A_1D_Real out_lat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 81.8182})));
      Modelica.Blocks.Interfaces.RealOutput realSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 63.6364})));
      ArrayConverter._V2A_1D_Real out_realSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 63.6364})));
      Modelica.Blocks.Interfaces.RealOutput heading 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 45.4545})));
      ArrayConverter._V2A_1D_Real out_heading_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 45.4545})));
      Modelica.Blocks.Interfaces.RealOutput destLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 27.2727})));
      ArrayConverter._V2A_1D_Real out_destLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 27.2727})));
      Modelica.Blocks.Interfaces.RealOutput destLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 9.09091})));
      ArrayConverter._V2A_1D_Real out_destLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 9.09091})));
      Modelica.Blocks.Interfaces.RealOutput prevLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -9.09091})));
      ArrayConverter._V2A_1D_Real out_prevLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -9.09091})));
      Modelica.Blocks.Interfaces.RealOutput prevLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -27.2727})));
      ArrayConverter._V2A_1D_Real out_prevLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -27.2727})));
      Modelica.Blocks.Interfaces.RealOutput shipToPrevWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -45.4545})));
      ArrayConverter._V2A_1D_Real out_shipToPrevWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -45.4545})));
      Modelica.Blocks.Interfaces.RealOutput shipToNextWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -63.6364})));
      ArrayConverter._V2A_1D_Real out_shipToNextWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -63.6364})));
      Modelica.Blocks.Interfaces.RealOutput shipToRouteDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -81.8182})));
      ArrayConverter._V2A_1D_Real out_shipToRouteDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -81.8182})));
      Modelica.Blocks.Interfaces.BooleanOutput workmode 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Boolean out_workmode_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_lng_converter.y[1], lng) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_lng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_lat_converter.y[1], lat) 
      annotation(Line(origin={0,0}, 
      points={{110,81.8182},{80,81.8182}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_lat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,81.8182}}, 
      color={255,0,0}));
      connect(out_realSpeed_converter.y[1], realSpeed) 
      annotation(Line(origin={0,0}, 
      points={{110,63.6364},{80,63.6364}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_realSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,63.6364}}, 
      color={255,0,0}));
      connect(out_heading_converter.y[1], heading) 
      annotation(Line(origin={0,0}, 
      points={{110,45.4545},{80,45.4545}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_heading_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,45.4545}}, 
      color={255,0,0}));
      connect(out_destLng_converter.y[1], destLng) 
      annotation(Line(origin={0,0}, 
      points={{110,27.2727},{80,27.2727}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_destLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,27.2727}}, 
      color={255,0,0}));
      connect(out_destLat_converter.y[1], destLat) 
      annotation(Line(origin={0,0}, 
      points={{110,9.09091},{80,9.09091}}, 
      color={255,0,0}));
      connect(base.outputs[6], out_destLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,9.09091}}, 
      color={255,0,0}));
      connect(out_prevLng_converter.y[1], prevLng) 
      annotation(Line(origin={0,0}, 
      points={{110,-9.09091},{80,-9.09091}}, 
      color={255,0,0}));
      connect(base.outputs[7], out_prevLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-9.09091}}, 
      color={255,0,0}));
      connect(out_prevLat_converter.y[1], prevLat) 
      annotation(Line(origin={0,0}, 
      points={{110,-27.2727},{80,-27.2727}}, 
      color={255,0,0}));
      connect(base.outputs[8], out_prevLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-27.2727}}, 
      color={255,0,0}));
      connect(out_shipToPrevWPDistance_converter.y[1], shipToPrevWPDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-45.4545},{80,-45.4545}}, 
      color={255,0,0}));
      connect(base.outputs[9], out_shipToPrevWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-45.4545}}, 
      color={255,0,0}));
      connect(out_shipToNextWPDistance_converter.y[1], shipToNextWPDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-63.6364},{80,-63.6364}}, 
      color={255,0,0}));
      connect(base.outputs[10], out_shipToNextWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-63.6364}}, 
      color={255,0,0}));
      connect(out_shipToRouteDistance_converter.y[1], shipToRouteDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-81.8182},{80,-81.8182}}, 
      color={255,0,0}));
      connect(base.outputs[11], out_shipToRouteDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-81.8182}}, 
      color={255,0,0}));
      connect(out_workmode_converter.y[1], workmode) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[12], out_workmode_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end getDataFromRos;
    model init
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1}},outputTypes={0,0},hasOutput=true,output_str_name={"uo","pid"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="init",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput uo 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_uo_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput pid 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_pid_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_uo_converter.y[1], uo) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_uo_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_pid_converter.y[1], pid) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_pid_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end init;
    model routePlane
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1}},outputTypes={0,1,2,0,0,0,0,0,0,0,0},hasOutput=true,output_str_name={"uo","workModel","valid","nextPointIndex","destLng","destLat","prevLng","prevLat","shipToPrevWPDistance","shipToNextWPDistance","shipToRouteDistance"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="routePlane",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput uo 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_uo_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.IntegerOutput workModel 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 80})));
      ArrayConverter._V2A_1D_Integer out_workModel_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 80})));
      Modelica.Blocks.Interfaces.BooleanOutput valid 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 60})));
      ArrayConverter._V2A_1D_Boolean out_valid_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 60})));
      Modelica.Blocks.Interfaces.RealOutput nextPointIndex 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 40})));
      ArrayConverter._V2A_1D_Real out_nextPointIndex_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 40})));
      Modelica.Blocks.Interfaces.RealOutput destLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 20})));
      ArrayConverter._V2A_1D_Real out_destLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 20})));
      Modelica.Blocks.Interfaces.RealOutput destLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_destLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealOutput prevLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -20})));
      ArrayConverter._V2A_1D_Real out_prevLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -20})));
      Modelica.Blocks.Interfaces.RealOutput prevLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -40})));
      ArrayConverter._V2A_1D_Real out_prevLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -40})));
      Modelica.Blocks.Interfaces.RealOutput shipToPrevWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -60})));
      ArrayConverter._V2A_1D_Real out_shipToPrevWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -60})));
      Modelica.Blocks.Interfaces.RealOutput shipToNextWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -80})));
      ArrayConverter._V2A_1D_Real out_shipToNextWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -80})));
      Modelica.Blocks.Interfaces.RealOutput shipToRouteDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_shipToRouteDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_uo_converter.y[1], uo) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_uo_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_workModel_converter.y[1], workModel) 
      annotation(Line(origin={0,0}, 
      points={{110,80},{80,80}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_workModel_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,80}}, 
      color={255,0,0}));
      connect(out_valid_converter.y[1], valid) 
      annotation(Line(origin={0,0}, 
      points={{110,60},{80,60}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_valid_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,60}}, 
      color={255,0,0}));
      connect(out_nextPointIndex_converter.y[1], nextPointIndex) 
      annotation(Line(origin={0,0}, 
      points={{110,40},{80,40}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_nextPointIndex_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,40}}, 
      color={255,0,0}));
      connect(out_destLng_converter.y[1], destLng) 
      annotation(Line(origin={0,0}, 
      points={{110,20},{80,20}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_destLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,20}}, 
      color={255,0,0}));
      connect(out_destLat_converter.y[1], destLat) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[6], out_destLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(out_prevLng_converter.y[1], prevLng) 
      annotation(Line(origin={0,0}, 
      points={{110,-20},{80,-20}}, 
      color={255,0,0}));
      connect(base.outputs[7], out_prevLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-20}}, 
      color={255,0,0}));
      connect(out_prevLat_converter.y[1], prevLat) 
      annotation(Line(origin={0,0}, 
      points={{110,-40},{80,-40}}, 
      color={255,0,0}));
      connect(base.outputs[8], out_prevLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-40}}, 
      color={255,0,0}));
      connect(out_shipToPrevWPDistance_converter.y[1], shipToPrevWPDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-60},{80,-60}}, 
      color={255,0,0}));
      connect(base.outputs[9], out_shipToPrevWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-60}}, 
      color={255,0,0}));
      connect(out_shipToNextWPDistance_converter.y[1], shipToNextWPDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-80},{80,-80}}, 
      color={255,0,0}));
      connect(base.outputs[10], out_shipToNextWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-80}}, 
      color={255,0,0}));
      connect(out_shipToRouteDistance_converter.y[1], shipToRouteDistance) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[11], out_shipToRouteDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end routePlane;
    model getShipStatus
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0,0},hasOutput=true,output_str_name={"uo","lng","lat","realSpeed","realRotateSpeed","heading"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="getShipStatus",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput uo 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_uo_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput lng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 60})));
      ArrayConverter._V2A_1D_Real out_lng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 60})));
      Modelica.Blocks.Interfaces.RealOutput lat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 20})));
      ArrayConverter._V2A_1D_Real out_lat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 20})));
      Modelica.Blocks.Interfaces.RealOutput realSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -20})));
      ArrayConverter._V2A_1D_Real out_realSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -20})));
      Modelica.Blocks.Interfaces.RealOutput realRotateSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -60})));
      ArrayConverter._V2A_1D_Real out_realRotateSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -60})));
      Modelica.Blocks.Interfaces.RealOutput heading 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_heading_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_uo_converter.y[1], uo) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_uo_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_lng_converter.y[1], lng) 
      annotation(Line(origin={0,0}, 
      points={{110,60},{80,60}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_lng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,60}}, 
      color={255,0,0}));
      connect(out_lat_converter.y[1], lat) 
      annotation(Line(origin={0,0}, 
      points={{110,20},{80,20}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_lat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,20}}, 
      color={255,0,0}));
      connect(out_realSpeed_converter.y[1], realSpeed) 
      annotation(Line(origin={0,0}, 
      points={{110,-20},{80,-20}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_realSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-20}}, 
      color={255,0,0}));
      connect(out_realRotateSpeed_converter.y[1], realRotateSpeed) 
      annotation(Line(origin={0,0}, 
      points={{110,-60},{80,-60}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_realRotateSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-60}}, 
      color={255,0,0}));
      connect(out_heading_converter.y[1], heading) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[6], out_heading_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end getShipStatus;
    model getModelCommand
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0},hasOutput=true,output_str_name={"adviseThrottlePercent","adviseRudderPercent","realSpeedX","realSpeedY","realSpeedZ"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="getModelCommand",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput adviseThrottlePercent 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_adviseThrottlePercent_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput adviseRudderPercent 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 50})));
      ArrayConverter._V2A_1D_Real out_adviseRudderPercent_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 50})));
      Modelica.Blocks.Interfaces.RealOutput realSpeedX 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_realSpeedX_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealOutput realSpeedY 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -50})));
      ArrayConverter._V2A_1D_Real out_realSpeedY_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -50})));
      Modelica.Blocks.Interfaces.RealOutput realSpeedZ 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_realSpeedZ_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_adviseThrottlePercent_converter.y[1], adviseThrottlePercent) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_adviseThrottlePercent_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_adviseRudderPercent_converter.y[1], adviseRudderPercent) 
      annotation(Line(origin={0,0}, 
      points={{110,50},{80,50}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_adviseRudderPercent_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,50}}, 
      color={255,0,0}));
      connect(out_realSpeedX_converter.y[1], realSpeedX) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_realSpeedX_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(out_realSpeedY_converter.y[1], realSpeedY) 
      annotation(Line(origin={0,0}, 
      points={{110,-50},{80,-50}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_realSpeedY_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-50}}, 
      color={255,0,0}));
      connect(out_realSpeedZ_converter.y[1], realSpeedZ) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_realSpeedZ_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end getModelCommand;
    model getModelParams
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{13}},outputTypes={0},hasOutput=true,output_str_name={"modelparams"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="getModelParams",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput modelparams[13] 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_modelparams_converter(dims={13}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
    equation
      connect(out_modelparams_converter.y, modelparams) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1:13], out_modelparams_converter.u) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));

    end getModelParams;
    model setModelReply
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1},{-1},{-1},{-1},{13}},inputTypes={0,0,0,0,0},hasInput=true,period=period,outputDims={{-1}},outputTypes={0},hasOutput=true,output_str_name={"pid"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="setModelReply",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput pid 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_pid_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 100})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 100})));
      Modelica.Blocks.Interfaces.RealInput finalSpeedX 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 50})));
      ArrayConverter._A2V_1D_Real in_finalSpeedX_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 50})));
      Modelica.Blocks.Interfaces.RealInput finalSpeedY 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 0})));
      ArrayConverter._A2V_1D_Real in_finalSpeedY_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 0})));
      Modelica.Blocks.Interfaces.RealInput finalYaw 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -50})));
      ArrayConverter._A2V_1D_Real in_finalYaw_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -50})));
      Modelica.Blocks.Interfaces.RealInput params[13] 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -100})));
      ArrayConverter._A2V_1D_Real in_params_converter(dims={13}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -100})));
    equation
      connect(out_pid_converter.y[1], pid) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_pid_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,100},{0,0}}, 
      color={255,0,0}));
      connect(finalSpeedX, in_finalSpeedX_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,50},{80,50}}, 
      color={255,0,0}));
      connect(in_finalSpeedX_converter.y[1], base.inputs[2]) 
      annotation(Line(origin={0,0}, 
      points={{80,50},{0,0}}, 
      color={255,0,0}));
      connect(finalSpeedY, in_finalSpeedY_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(in_finalSpeedY_converter.y[1], base.inputs[3]) 
      annotation(Line(origin={0,0}, 
      points={{80,0},{0,0}}, 
      color={255,0,0}));
      connect(finalYaw, in_finalYaw_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-50},{80,-50}}, 
      color={255,0,0}));
      connect(in_finalYaw_converter.y[1], base.inputs[4]) 
      annotation(Line(origin={0,0}, 
      points={{80,-50},{0,0}}, 
      color={255,0,0}));
      connect(params, in_params_converter.u) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(in_params_converter.y, base.inputs[5:17]) 
      annotation(Line(origin={0,0}, 
      points={{80,-100},{0,0}}, 
      color={255,0,0}));

    end setModelReply;
    model navigation
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1},{-1}},inputTypes={0,1,0,0,0,0,0,2,0,0,0,0,0,0,0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0},hasOutput=true,output_str_name={"uo","advisedspeed","advisedrudder","advisedheading"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="navigation",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput uo 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_uo_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput advisedspeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 33.3333})));
      ArrayConverter._V2A_1D_Real out_advisedspeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 33.3333})));
      Modelica.Blocks.Interfaces.RealOutput advisedrudder 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -33.3333})));
      ArrayConverter._V2A_1D_Real out_advisedrudder_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -33.3333})));
      Modelica.Blocks.Interfaces.RealOutput advisedheading 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_advisedheading_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 100})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 100})));
      Modelica.Blocks.Interfaces.IntegerInput workModel 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 85.7143})));
      ArrayConverter._A2V_1D_Integer in_workModel_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 85.7143})));
      Modelica.Blocks.Interfaces.RealInput lng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 71.4286})));
      ArrayConverter._A2V_1D_Real in_lng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 71.4286})));
      Modelica.Blocks.Interfaces.RealInput lat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 57.1429})));
      ArrayConverter._A2V_1D_Real in_lat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 57.1429})));
      Modelica.Blocks.Interfaces.RealInput realSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 42.8571})));
      ArrayConverter._A2V_1D_Real in_realSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 42.8571})));
      Modelica.Blocks.Interfaces.RealInput realRotateSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 28.5714})));
      ArrayConverter._A2V_1D_Real in_realRotateSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 28.5714})));
      Modelica.Blocks.Interfaces.RealInput heading 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 14.2857})));
      ArrayConverter._A2V_1D_Real in_heading_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 14.2857})));
      Modelica.Blocks.Interfaces.BooleanInput valid 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -1.06581e-14})));
      ArrayConverter._A2V_1D_Boolean in_valid_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -1.06581e-14})));
      Modelica.Blocks.Interfaces.RealInput destLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -14.2857})));
      ArrayConverter._A2V_1D_Real in_destLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -14.2857})));
      Modelica.Blocks.Interfaces.RealInput destLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -28.5714})));
      ArrayConverter._A2V_1D_Real in_destLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -28.5714})));
      Modelica.Blocks.Interfaces.RealInput prevLng 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -42.8571})));
      ArrayConverter._A2V_1D_Real in_prevLng_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -42.8571})));
      Modelica.Blocks.Interfaces.RealInput prevLat 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -57.1429})));
      ArrayConverter._A2V_1D_Real in_prevLat_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -57.1429})));
      Modelica.Blocks.Interfaces.RealInput shipToPrevWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -71.4286})));
      ArrayConverter._A2V_1D_Real in_shipToPrevWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -71.4286})));
      Modelica.Blocks.Interfaces.RealInput shipToNextWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -85.7143})));
      ArrayConverter._A2V_1D_Real in_shipToNextWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -85.7143})));
      Modelica.Blocks.Interfaces.RealInput shipToRouteDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -100})));
      ArrayConverter._A2V_1D_Real in_shipToRouteDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -100})));
    equation
      connect(out_uo_converter.y[1], uo) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_uo_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,100}}, 
      color={255,0,0}));
      connect(out_advisedspeed_converter.y[1], advisedspeed) 
      annotation(Line(origin={0,0}, 
      points={{110,33.3333},{80,33.3333}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_advisedspeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,33.3333}}, 
      color={255,0,0}));
      connect(out_advisedrudder_converter.y[1], advisedrudder) 
      annotation(Line(origin={0,0}, 
      points={{110,-33.3333},{80,-33.3333}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_advisedrudder_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-33.3333}}, 
      color={255,0,0}));
      connect(out_advisedheading_converter.y[1], advisedheading) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_advisedheading_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,100},{0,0}}, 
      color={255,0,0}));
      connect(workModel, in_workModel_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,85.7143},{80,85.7143}}, 
      color={255,0,0}));
      connect(in_workModel_converter.y[1], base.inputs[2]) 
      annotation(Line(origin={0,0}, 
      points={{80,85.7143},{0,0}}, 
      color={255,0,0}));
      connect(lng, in_lng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,71.4286},{80,71.4286}}, 
      color={255,0,0}));
      connect(in_lng_converter.y[1], base.inputs[3]) 
      annotation(Line(origin={0,0}, 
      points={{80,71.4286},{0,0}}, 
      color={255,0,0}));
      connect(lat, in_lat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,57.1429},{80,57.1429}}, 
      color={255,0,0}));
      connect(in_lat_converter.y[1], base.inputs[4]) 
      annotation(Line(origin={0,0}, 
      points={{80,57.1429},{0,0}}, 
      color={255,0,0}));
      connect(realSpeed, in_realSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,42.8571},{80,42.8571}}, 
      color={255,0,0}));
      connect(in_realSpeed_converter.y[1], base.inputs[5]) 
      annotation(Line(origin={0,0}, 
      points={{80,42.8571},{0,0}}, 
      color={255,0,0}));
      connect(realRotateSpeed, in_realRotateSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,28.5714},{80,28.5714}}, 
      color={255,0,0}));
      connect(in_realRotateSpeed_converter.y[1], base.inputs[6]) 
      annotation(Line(origin={0,0}, 
      points={{80,28.5714},{0,0}}, 
      color={255,0,0}));
      connect(heading, in_heading_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,14.2857},{80,14.2857}}, 
      color={255,0,0}));
      connect(in_heading_converter.y[1], base.inputs[7]) 
      annotation(Line(origin={0,0}, 
      points={{80,14.2857},{0,0}}, 
      color={255,0,0}));
      connect(valid, in_valid_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-1.06581e-14},{80,-1.06581e-14}}, 
      color={255,0,0}));
      connect(in_valid_converter.y[1], base.inputs[8]) 
      annotation(Line(origin={0,0}, 
      points={{80,-1.06581e-14},{0,0}}, 
      color={255,0,0}));
      connect(destLng, in_destLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-14.2857},{80,-14.2857}}, 
      color={255,0,0}));
      connect(in_destLng_converter.y[1], base.inputs[9]) 
      annotation(Line(origin={0,0}, 
      points={{80,-14.2857},{0,0}}, 
      color={255,0,0}));
      connect(destLat, in_destLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-28.5714},{80,-28.5714}}, 
      color={255,0,0}));
      connect(in_destLat_converter.y[1], base.inputs[10]) 
      annotation(Line(origin={0,0}, 
      points={{80,-28.5714},{0,0}}, 
      color={255,0,0}));
      connect(prevLng, in_prevLng_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-42.8571},{80,-42.8571}}, 
      color={255,0,0}));
      connect(in_prevLng_converter.y[1], base.inputs[11]) 
      annotation(Line(origin={0,0}, 
      points={{80,-42.8571},{0,0}}, 
      color={255,0,0}));
      connect(prevLat, in_prevLat_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-57.1429},{80,-57.1429}}, 
      color={255,0,0}));
      connect(in_prevLat_converter.y[1], base.inputs[12]) 
      annotation(Line(origin={0,0}, 
      points={{80,-57.1429},{0,0}}, 
      color={255,0,0}));
      connect(shipToPrevWPDistance, in_shipToPrevWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-71.4286},{80,-71.4286}}, 
      color={255,0,0}));
      connect(in_shipToPrevWPDistance_converter.y[1], base.inputs[13]) 
      annotation(Line(origin={0,0}, 
      points={{80,-71.4286},{0,0}}, 
      color={255,0,0}));
      connect(shipToNextWPDistance, in_shipToNextWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-85.7143},{80,-85.7143}}, 
      color={255,0,0}));
      connect(in_shipToNextWPDistance_converter.y[1], base.inputs[14]) 
      annotation(Line(origin={0,0}, 
      points={{80,-85.7143},{0,0}}, 
      color={255,0,0}));
      connect(shipToRouteDistance, in_shipToRouteDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(in_shipToRouteDistance_converter.y[1], base.inputs[15]) 
      annotation(Line(origin={0,0}, 
      points={{80,-100},{0,0}}, 
      color={255,0,0}));

    end navigation;
    model setDataToRos
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1},{-1},{-1},{-1},{-1},{-1}},inputTypes={0,0,0,0,0,0},hasInput=true,period=period,outputDims={{-1}},outputTypes={0},hasOutput=true,output_str_name={"output1"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0312",functionName="setDataToRos",moduleName="test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealInput u 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 100})));
      ArrayConverter._A2V_1D_Real in_u_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 100})));
      Modelica.Blocks.Interfaces.RealInput adviseSpeed 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 60})));
      ArrayConverter._A2V_1D_Real in_adviseSpeed_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 60})));
      Modelica.Blocks.Interfaces.RealInput adviseRotate 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 20})));
      ArrayConverter._A2V_1D_Real in_adviseRotate_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 20})));
      Modelica.Blocks.Interfaces.RealInput advisedHeading 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -20})));
      ArrayConverter._A2V_1D_Real in_advisedHeading_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -20})));
      Modelica.Blocks.Interfaces.RealInput nextPointIndex 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -60})));
      ArrayConverter._A2V_1D_Real in_nextPointIndex_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -60})));
      Modelica.Blocks.Interfaces.RealInput shipToNextWPDistance 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -100})));
      ArrayConverter._A2V_1D_Real in_shipToNextWPDistance_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -100})));
    equation
      connect(out_output1_converter.y[1], output1) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_output1_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(u, in_u_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(in_u_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,100},{0,0}}, 
      color={255,0,0}));
      connect(adviseSpeed, in_adviseSpeed_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,60},{80,60}}, 
      color={255,0,0}));
      connect(in_adviseSpeed_converter.y[1], base.inputs[2]) 
      annotation(Line(origin={0,0}, 
      points={{80,60},{0,0}}, 
      color={255,0,0}));
      connect(adviseRotate, in_adviseRotate_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,20},{80,20}}, 
      color={255,0,0}));
      connect(in_adviseRotate_converter.y[1], base.inputs[3]) 
      annotation(Line(origin={0,0}, 
      points={{80,20},{0,0}}, 
      color={255,0,0}));
      connect(advisedHeading, in_advisedHeading_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-20},{80,-20}}, 
      color={255,0,0}));
      connect(in_advisedHeading_converter.y[1], base.inputs[4]) 
      annotation(Line(origin={0,0}, 
      points={{80,-20},{0,0}}, 
      color={255,0,0}));
      connect(nextPointIndex, in_nextPointIndex_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-60},{80,-60}}, 
      color={255,0,0}));
      connect(in_nextPointIndex_converter.y[1], base.inputs[5]) 
      annotation(Line(origin={0,0}, 
      points={{80,-60},{0,0}}, 
      color={255,0,0}));
      connect(shipToNextWPDistance, in_shipToNextWPDistance_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(in_shipToNextWPDistance_converter.y[1], base.inputs[6]) 
      annotation(Line(origin={0,0}, 
      points={{80,-100},{0,0}}, 
      color={255,0,0}));

    end setDataToRos;
    end ImportedTypes;
  model Interpreter
   String pythonEnvPath = "E:/Program Files/MWORKS/Sysplorer 2024b_SP1/External/python64";
    function global_constructor = ImportedTypes.UseConstructorWindowspython37 annotation(__MWORKS(hide=true));
    function global_exchangedata_func = ImportedTypes.FunctionUseExchangeDataWindowspython37 annotation(__MWORKS(hide=true));
    function global_exchangedata_obj = ImportedTypes.ObjectUseExchangeDataWindowspython37 annotation(__MWORKS(hide=true));
    function global_destructor = ImportedTypes.UseDestructorWindowspython37 annotation(__MWORKS(hide=true));
   end Interpreter;
  equation
  connect(L.y, Parameter[1].u) 
  annotation(Line(origin={202.1841,65.3874}, 
points={{-12.199,44.2796},{8.41682,44.2796},{8.41682,-37.3824},{15.5679,-37.3824}}, 
color={0,0,127}));
  connect(B.y, Parameter[2].u) 
  annotation(Line(origin={202.1841,58.3874}, 
points={{-12.199,37.6292},{8.39127,37.6292},{8.39127,-30.3824},{15.5679,-30.3824}}, 
color={0,0,127}));
  connect(Bhull.y, Parameter[3].u) 
  annotation(Line(origin={202.1841,51.3874}, 
points={{-12.199,30.9788},{8.49045,30.9788},{8.49045,-23.3824},{15.5679,-23.3824}}, 
color={0,0,127}));
  connect(mass.y, Parameter[4].u) 
  annotation(Line(origin={202.1841,44.3874}, 
points={{-12.199,24.3288},{8.44969,24.3288},{8.44969,-16.3824},{15.5679,-16.3824}}, 
color={0,0,127}));
  connect(LCG.y, Parameter[5].u) 
  annotation(Line(origin={202.1841,37.3874}, 
points={{-12.199,17.679},{8.45053,17.679},{8.45053,-9.3824},{15.5679,-9.3824}}, 
color={0,0,127}));
  connect(g.y, Parameter[6].u) 
  annotation(Line(origin={202.1841,31.3874}, 
points={{-12.199,10.029},{8.46265,10.029},{8.46265,-3.3824},{15.5679,-3.3824}}, 
color={0,0,127}));
  connect(T.y, Parameter[7].u) 
  annotation(Line(origin={202.1841,24.3874}, 
points={{-12.199,3.379},{15.5679,3.379},{15.5679,3.6176}}, 
color={0,0,127}));
  connect(Cd.y, Parameter[8].u) 
  annotation(Line(origin={202.1841,17.3874}, 
points={{-12.199,-3.271},{8.2522,-3.271},{8.2522,10.6176},{15.5679,10.6176}}, 
color={0,0,127}));
  connect(rho.y, Parameter[9].u) 
  annotation(Line(origin={202.1841,10.3874}, 
points={{-12.199,-9.920639},{8.26993,-9.920639},{8.26993,17.6176},{15.5679,17.6176}}, 
color={0,0,127}));
  connect(Xu_linear.y, Parameter[10].u) 
  annotation(Line(origin={202.1841,3.38738}, 
points={{-12.199,-16.57058},{8.37486,-16.57058},{8.37486,24.6176},{15.5679,24.6176}}, 
color={0,0,127}));
  connect(Xu_poly.y, Parameter[11].u) 
  annotation(Line(origin={202.1841,-3.61262}, 
points={{-12.24,-24.22798},{8.37486,-24.22798},{8.37486,31.6176},{15.5679,31.6176}}, 
color={0,0,127}));
  connect(Xuu_linear.y, Parameter[12].u) 
  annotation(Line(origin={202.1841,-10.6122}, 
points={{-12.199,-31.351},{8.26993,-31.351},{8.26993,38.6172},{15.5679,38.6172}}, 
color={0,0,127}));
  connect(Xuu_poly.y, Parameter[13].u) 
  annotation(Line(origin={202.1841,-17.6122}, 
points={{-12.3561,-38.7284},{8.37486,-38.7284},{8.37486,45.6172},{15.5679,45.6172}}, 
color={0,0,127}));
  connect(init.u, continuousClock.y) 
  annotation(Line(origin={-189,97.1868}, 
points={{64,20.1794},{29.8618,20.1794}}, 
color={0,0,127}));
  connect(continuousClock.y, routePlan.u) 
  annotation(Line(origin={105,-22.9365}, 
points={{-264.1382,140.303},{-243,140.303},{-243,-35.30739},{-230,-35.30739}}, 
color={0,0,127}));
  connect(getModelCommand.realSpeedX, uSV130_3DOF_Dynamic_Model.disturbX) 
  annotation(Line(origin={-82,23}, 
points={{-21,24.121904},{18,24.121904},{18,-27},{126,-27},{126,83.2252},{139.41983,83.2252}}, 
color={0,0,127}));
  connect(getModelCommand.realSpeedY, uSV130_3DOF_Dynamic_Model.disturbY) 
  annotation(Line(origin={-82,5}, 
points={{-21,37.121904},{18,37.121904},{18,-9},{126,-9},{126,89.5406},{139.41983,89.5406}}, 
color={0,0,127}));
  connect(uSV130_3DOF_Dynamic_Model.V_local[1], setModelReply.finalSpeedX) 
  annotation(Line(origin={114,21}, 
points={{16.3,62.5575},{26,62.5575},{26,-25},{-252,-25},{-252,-4},{-239,-4}}, 
color={0,0,127}));
  connect(uSV130_3DOF_Dynamic_Model.V_local[2], setModelReply.finalSpeedY) 
  annotation(Line(origin={114,18}, 
points={{16.3,65.5575},{26,65.5575},{26,-22},{-252,-22},{-252,-6},{-239,-6}}, 
color={0,0,127}));
  connect(uSV130_3DOF_Dynamic_Model.V_local[3], setModelReply.finalYaw) 
  annotation(Line(origin={114,15}, 
points={{16.3,68.5575},{26,68.5575},{26,-19},{-252,-19},{-252,-8},{-239,-8}}, 
color={0,0,127}));
  connect(from.y, setModelReply.params) 
  annotation(Line(origin={-277,103.85553}, 
points={{122.632544,-101.856},{152,-101.85553}}, 
color={0,0,127}));
  connect(continuousClock.y, setModelReply.u) 
  annotation(Line(origin={63,83.5618}, 
points={{-222.1382,33.8044},{-201,33.8044},{-201,-61.5618},{-188,-61.5618}}, 
color={0,0,127}));
  connect(navSys.advisedThrottle, auto_Switch.advisedThrottle) 
  annotation(Line(origin={-244,12.9323}, 
points={{270.3,107.886},{280,107.886},{280,-16.9323},{180,-16.9323},{180,-49.5475},{197.7,-49.5475}}, 
color={0,0,127}));
  connect(navSys.advisedRudder, auto_Switch.advisedRudder) 
  annotation(Line(origin={-244,-14.0677}, 
points={{270.3,113.5941},{280,113.5941},{280,10.0677},{180,10.0677},{180,-33.1934},{197.7,-33.1934}}, 
color={0,0,127}));
  connect(continuousClock.y, getShipStatus.u) 
  annotation(Line(origin={-12,-38.4382}, 
points={{-147.1382,155.804},{-126,155.804},{-126,15.3162},{-113,15.3162}}, 
color={0,0,127}));
  connect(getShipStatus.lng, navSys.lng) 
  annotation(Line(origin={-434,-8}, 
points={{331,-9.122},{370,-9.122},{370,136.561},{387.99997,136.561}}, 
color={0,0,127}));
  connect(getShipStatus.lat, navSys.lat) 
  annotation(Line(origin={-434,-18}, 
points={{331,-3.122},{370,-3.122},{370,140.754},{387.99997,140.754}}, 
color={0,0,127}));
  connect(getShipStatus.realSpeed, navSys.realSpeed) 
  annotation(Line(origin={-434,-28}, 
points={{331,2.87801},{370,2.87801},{370,144.947},{387.99997,144.947}}, 
color={0,0,127}));
  connect(getShipStatus.heading, navSys.heading) 
  annotation(Line(origin={-434,-43}, 
points={{331,9.87801},{370,9.87801},{370,154.14},{387.99997,154.14}}, 
color={0,0,127}));
  connect(routePlan.destLng, navSys.destLng) 
  annotation(Line(origin={-434,-73}, 
points={{331,16.7561},{370,16.7561},{370,178.333},{387.99997,178.333}}, 
color={0,0,127}));
  connect(routePlan.destLat, navSys.destLat) 
  annotation(Line(origin={-434,-80}, 
points={{331,21.7561},{370,21.7561},{370,179.5264},{387.99997,179.5264}}, 
color={0,0,127}));
  connect(routePlan.prevLng, navSys.prevLng) 
  annotation(Line(origin={-434,-87}, 
points={{331,26.7561},{370,26.7561},{370,180.72},{387.99997,180.72}}, 
color={0,0,127}));
  connect(routePlan.prevLat, navSys.prevLat) 
  annotation(Line(origin={-434,-94}, 
points={{331,31.7561},{370,31.7561},{370,181.913},{387.99997,181.913}}, 
color={0,0,127}));
  connect(routePlan.shipToPrevWPDistance, navSys.shipToPrevWPDistance) 
  annotation(Line(origin={-434,-101}, 
points={{331,36.7561},{370,36.7561},{370,183.106},{387.99997,183.106}}, 
color={0,0,127}));
  connect(routePlan.shipToNextWPDistance, navSys.shipToNextWPDistance) 
  annotation(Line(origin={-434,-108}, 
points={{331,41.756118},{370,41.756118},{370,184.299},{387.99997,184.299}}, 
color={0,0,127}));
  connect(routePlan.shipToRouteDistance, navSys.shipToRouteDistance) 
  annotation(Line(origin={-434,-115}, 
points={{331,46.7561},{370,46.7561},{370,185.492},{387.99997,185.492}}, 
color={0,0,127}));
  connect(routePlan.valid, auto_Switch.valid) 
  annotation(Line(origin={-333,-104}, 
points={{230,51.7561},{269,51.7561},{269,78.0307},{286.7,78.0307}}, 
color={255,0,255}));
  connect(getModelCommand.u, continuousClock.y) 
  annotation(Line(origin={-129,62.3699}, 
points={{4,-15.247996},{-9,-15.247996},{-9,54.9963},{-30.1382,54.9963}}, 
color={0,0,127}));
  connect(getModelParams.u, continuousClock.y) 
  annotation(Line(origin={53,65.3699}, 
points={{-178,16.8739},{-191,16.8739},{-191,51.9963},{-212.1382,51.9963}}, 
color={0,0,127}));
  connect(auto_Switch.Throttle, uSV130_3DOF_Dynamic_Model.surge) 
  annotation(Line(origin={-86,-16}, 
points={{112.3,-9.96927},{130,-9.96927},{130,133.91},{143.41983,133.91}}, 
color={0,0,127}));
  connect(auto_Switch.Rudder, uSV130_3DOF_Dynamic_Model.yaw) 
  annotation(Line(origin={-86,-58}, 
points={{112.3,0.092975},{130,0.092975},{130,140.856},{143.41983,140.856}}, 
color={0,0,127}));
  connect(routePlan.workModel, auto_Switch.workmodel) 
  annotation(Line(origin={-93,-32}, 
points={{-10,-18.2439},{29,-18.2439},{29,16.6766},{46.7,16.6766}}, 
color={255,127,0}));
  connect(joystick1.Throttle, auto_Switch.RCThrottle) 
  annotation(Line(origin={-18,-12}, 
points={{23.95,44.3231},{40,44.3231},{40,8},{-46,8},{-46,-45.907025},{-28.3,-45.907025}}, 
color={0,0,127}));
  connect(joystick1.Rudder, auto_Switch.RCRudder) 
  annotation(Line(origin={-18,-22}, 
points={{23.95,44.2254},{40,44.2254},{40,18},{-46,18},{-46,-46.5529},{-28.3,-46.5529}}, 
color={0,0,127}));
  end ROSDrive_Control_V1;