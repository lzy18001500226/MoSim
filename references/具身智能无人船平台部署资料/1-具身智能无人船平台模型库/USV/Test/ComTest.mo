model ComTest
  ImportedTypes.isRosConnected isRosConnected(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),period=0.02) 
    annotation (Placement(transformation(origin={-76,72}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.init init(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=0.02,period=0.02) 
    annotation (Placement(transformation(origin={-76,36}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.getModelParams getModelParams(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3.04,period=0.02) 
    annotation (Placement(transformation(origin={1,72}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.getModelCommand getModelCommand(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3.02,period=0.02) 
    annotation (Placement(transformation(origin={1,36}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.setModelReply setModelReply(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3.06,period=0.02) 
    annotation (Placement(transformation(origin={1,0}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.com com(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3,period=0.02) 
    annotation (Placement(transformation(origin={115,72}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.getDataFromRos getDataFromRos(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3.08,period=0.02) 
    annotation (Placement(transformation(origin={152,72}, 
extent={{-10,-10},{10,10}})));
  ImportedTypes.getDataToRos getDataToRos(base(redeclare function FuncConstructor = Interpreter.global_constructor,redeclare function FuncExchangeData = Interpreter.global_exchangedata_func,redeclare function FuncDestructor = Interpreter.global_destructor),startTime=3.1,period=0.02) 
    annotation (Placement(transformation(origin={152,36}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.ContinuousClock continuousClock 
    annotation (Placement(transformation(origin={78,72}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const(k=0) 
    annotation (Placement(transformation(origin={-76,-6.66134e-16}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Constant const1[5](k={1,2,3,4,5}) 
    annotation (Placement(transformation(origin={-76,-36}, 
extent={{-10,-10},{10,10}})));
  model Interpreter
   String pythonEnvPath = "E:/Program Files/MWORKS/Sysplorer 2024b_SP1/External/python64";
    function global_constructor = ImportedTypes.UseConstructorWindowspython37 annotation(__MWORKS(hide=true));
    function global_exchangedata_func = ImportedTypes.FunctionUseExchangeDataWindowspython37 annotation(__MWORKS(hide=true));
    function global_exchangedata_obj = ImportedTypes.ObjectUseExchangeDataWindowspython37 annotation(__MWORKS(hide=true));
    function global_destructor = ImportedTypes.UseDestructorWindowspython37 annotation(__MWORKS(hide=true));
   end Interpreter;
  package ImportedTypes
    package ArrayConverter
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
    model getModelParams
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(hasInput=false,period=period,outputDims={{-1}},outputTypes={0},hasOutput=true,output_str_name={"output1"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "getModelParams", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
    equation
      connect(out_output1_converter.y[1], output1) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_output1_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));

    end getModelParams;
    model com
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1}},outputTypes={0},hasOutput=true,output_str_name={"output1"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "com", moduleName = "test2") 
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
    model setModelReply
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1},{-1},{-1},{-1}},inputTypes={0,0,0,0},hasInput=true,period=period,hasOutput=false,pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "setModelReply", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealInput finalSpeedX 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 100})));
      ArrayConverter._A2V_1D_Real in_finalSpeedX_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 100})));
      Modelica.Blocks.Interfaces.RealInput finalSpeedY 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, 33.3333})));
      ArrayConverter._A2V_1D_Real in_finalSpeedY_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, 33.3333})));
      Modelica.Blocks.Interfaces.RealInput finalYaw 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -33.3333})));
      ArrayConverter._A2V_1D_Real in_finalYaw_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -33.3333})));
      Modelica.Blocks.Interfaces.RealInput params 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-110, -100})));
      ArrayConverter._A2V_1D_Real in_params_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={-80, -100})));
    equation
      connect(finalSpeedX, in_finalSpeedX_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,100},{80,100}}, 
      color={255,0,0}));
      connect(in_finalSpeedX_converter.y[1], base.inputs[1]) 
      annotation(Line(origin={0,0}, 
      points={{80,100},{0,0}}, 
      color={255,0,0}));
      connect(finalSpeedY, in_finalSpeedY_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,33.3333},{80,33.3333}}, 
      color={255,0,0}));
      connect(in_finalSpeedY_converter.y[1], base.inputs[2]) 
      annotation(Line(origin={0,0}, 
      points={{80,33.3333},{0,0}}, 
      color={255,0,0}));
      connect(finalYaw, in_finalYaw_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-33.3333},{80,-33.3333}}, 
      color={255,0,0}));
      connect(in_finalYaw_converter.y[1], base.inputs[3]) 
      annotation(Line(origin={0,0}, 
      points={{80,-33.3333},{0,0}}, 
      color={255,0,0}));
      connect(params, in_params_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(in_params_converter.y[1], base.inputs[4]) 
      annotation(Line(origin={0,0}, 
      points={{80,-100},{0,0}}, 
      color={255,0,0}));

    end setModelReply;
    model getDataFromRos
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0},hasOutput=true,output_str_name={"output1","output2","output3","output4"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "getDataFromRos", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput output2 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 33.3333})));
      ArrayConverter._V2A_1D_Real out_output2_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 33.3333})));
      Modelica.Blocks.Interfaces.RealOutput output3 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -33.3333})));
      ArrayConverter._V2A_1D_Real out_output3_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -33.3333})));
      Modelica.Blocks.Interfaces.RealOutput output4 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_output4_converter(dims={1}) 
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
      points={{110,33.3333},{80,33.3333}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_output2_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,33.3333}}, 
      color={255,0,0}));
      connect(out_output3_converter.y[1], output3) 
      annotation(Line(origin={0,0}, 
      points={{110,-33.3333},{80,-33.3333}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_output3_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-33.3333}}, 
      color={255,0,0}));
      connect(out_output4_converter.y[1], output4) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_output4_converter.u[1]) 
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
    model getDataToRos
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(inputDims={{-1}},inputTypes={0},hasInput=true,period=period,outputDims={{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0},hasOutput=true,output_str_name={"output1","output2","output3","output4","output5"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "getDataToRos", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput output2 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 50})));
      ArrayConverter._V2A_1D_Real out_output2_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 50})));
      Modelica.Blocks.Interfaces.RealOutput output3 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_output3_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealOutput output4 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -50})));
      ArrayConverter._V2A_1D_Real out_output4_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -50})));
      Modelica.Blocks.Interfaces.RealOutput output5 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_output5_converter(dims={1}) 
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
      points={{110,50},{80,50}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_output2_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,50}}, 
      color={255,0,0}));
      connect(out_output3_converter.y[1], output3) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_output3_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(out_output4_converter.y[1], output4) 
      annotation(Line(origin={0,0}, 
      points={{110,-50},{80,-50}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_output4_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-50}}, 
      color={255,0,0}));
      connect(out_output5_converter.y[1], output5) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_output5_converter.u[1]) 
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
    model getModelCommand
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(hasInput=false,period=period,outputDims={{-1},{-1},{-1},{-1},{-1}},outputTypes={0,0,0,0,0},hasOutput=true,output_str_name={"output1","output2","output3","output4","output5"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "getModelCommand", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Real out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput output2 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 50})));
      ArrayConverter._V2A_1D_Real out_output2_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 50})));
      Modelica.Blocks.Interfaces.RealOutput output3 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Real out_output3_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
      Modelica.Blocks.Interfaces.RealOutput output4 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -50})));
      ArrayConverter._V2A_1D_Real out_output4_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -50})));
      Modelica.Blocks.Interfaces.RealOutput output5 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_output5_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
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
      points={{110,50},{80,50}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_output2_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,50}}, 
      color={255,0,0}));
      connect(out_output3_converter.y[1], output3) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[3], out_output3_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));
      connect(out_output4_converter.y[1], output4) 
      annotation(Line(origin={0,0}, 
      points={{110,-50},{80,-50}}, 
      color={255,0,0}));
      connect(base.outputs[4], out_output4_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-50}}, 
      color={255,0,0}));
      connect(out_output5_converter.y[1], output5) 
      annotation(Line(origin={0,0}, 
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[5], out_output5_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));

    end getModelCommand;
    model isRosConnected
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(hasInput=false,period=period,outputDims={{-1}},outputTypes={2},hasOutput=true,output_str_name={"output1"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "isRosConnected", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.BooleanOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 0})));
      ArrayConverter._V2A_1D_Boolean out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 0})));
    equation
      connect(out_output1_converter.y[1], output1) 
      annotation(Line(origin={0,0}, 
      points={{110,0},{80,0}}, 
      color={255,0,0}));
      connect(base.outputs[1], out_output1_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,0}}, 
      color={255,0,0}));

    end isRosConnected;
    model init
      extends PythonIO.Communication.PythonSampleBase;
      extends Interpreter;
      import Modelica;
      import PythonIO.Communication.PythonFunction;
      annotation(Icon(coordinateSystem(extent={{-100.0, -100.0}, {100.0, 100.0}},grid={2.0, 2.0}),graphics={Rectangle(origin = {0.0, 0.0}, lineColor = {200, 200, 200}, fillColor = {248, 248, 248}, fillPattern = FillPattern.HorizontalCylinder, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Rectangle(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, extent = {{-100.0, -100.0}, {100.0, 100.0}}, radius = 25.0), Ellipse(origin = {0.0, 0.0}, lineColor = {128, 128, 128}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid, extent = {{-30.0, -30.0}, {30.0, 30.0}}), Rectangle(origin = {0.0, 0.0}, fillColor = {239, 239, 239}, fillPattern = FillPattern.Solid, lineThickness = 1.25, extent = {{-100.0, 100.0}, {100.0, -100.0}}), Text(origin = {0.0, 130.0}, lineColor = {0, 0, 255}, extent = {{-150.0, 20.0}, {150.0, -20.0}}, textString = "%name", textColor = {0, 0, 255}), Bitmap(origin = {-0.7500000000000071, 3.75}, extent = {{-89.25, -86.25}, {89.25, 86.25}}, fileName = "modelica://PythonIO/Resources/Images/PythonFunction.svg")}));
      PythonIO.Communication.PythonFunction.PythonFunctionBase base(hasInput=false,period=period,outputDims={{-1},{-1}},outputTypes={2,0},hasOutput=true,output_str_name={"output1","output2"},pythonPath=pythonEnvPath,pythonFilePath="F:/项目资料/生态运营/无人船/ROS/usvlib4ros0226", functionName = "init", moduleName = "test2") 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.BooleanOutput output1 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, 100})));
      ArrayConverter._V2A_1D_Boolean out_output1_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, 100})));
      Modelica.Blocks.Interfaces.RealOutput output2 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={110, -100})));
      ArrayConverter._V2A_1D_Real out_output2_converter(dims={1}) 
      annotation(Placement(transformation(extent={{-10.0, -10.0}, {10.0, 10.0}},origin={80, -100})));
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
      points={{110,-100},{80,-100}}, 
      color={255,0,0}));
      connect(base.outputs[2], out_output2_converter.u[1]) 
      annotation(Line(origin={0,0}, 
      points={{0,0},{80,-100}}, 
      color={255,0,0}));

    end init;
    end ImportedTypes;
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),experiment(Algorithm=Rkfix4,InlineIntegrator=false,InlineStepSize=false,Interval=0.02,StartTime=0,StopTime=inf,Tolerance=0.0001,IntegratorStep=0.02));
equation
  connect(com.u, continuousClock.y) 
  annotation(Line(origin={95,72}, 
points={{9,1.42109e-14},{-6,1.42109e-14},{-6,0}}, 
color={0,0,127}));
  connect(com.output1, getDataFromRos.u) 
  annotation(Line(origin={126,54}, 
points={{0,18},{15,18}}, 
color={0,0,127}));
  connect(const.y, setModelReply.finalSpeedX) 
  annotation(Line(origin={-37,5}, 
  points={{-28,-5},{3,-5},{3,5},{27,5}}, 
  color={0,0,127}));
  connect(const.y, setModelReply.finalSpeedY) 
  annotation(Line(origin={-37,2}, 
  points={{-28,-2},{3,-2},{3,1.33333},{27,1.33333}}, 
  color={0,0,127}));
  connect(const.y, setModelReply.finalYaw) 
  annotation(Line(origin={-37,-2}, 
  points={{-28,2},{3,2},{3,-1.33333},{27,-1.33333}}, 
  color={0,0,127}));
  connect(com.output1, getDataToRos.u) 
  annotation(Line(origin={134,54}, 
  points={{-8,18},{-2,18},{-2,-18},{7,-18}}, 
  color={0,0,127}));
  connect(const.y, setModelReply.params) 
  annotation(Line(origin={-37,-5}, 
  points={{-28,5},{3,5},{3,-5},{27,-5}}, 
  color={0,0,127}));
  end ComTest;