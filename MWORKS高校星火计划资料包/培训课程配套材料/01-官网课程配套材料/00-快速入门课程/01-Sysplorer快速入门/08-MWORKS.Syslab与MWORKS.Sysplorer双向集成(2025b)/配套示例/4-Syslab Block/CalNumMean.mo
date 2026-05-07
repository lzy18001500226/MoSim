model CalNumMean
  package ImportedTypes
    model SyslabFunction1
      "julia function"
      annotation (__MWorks(SyslabFunction(Type = "function",AllFuncNames="stats,avg",Duplicated=true,BlockPort(in_vals(Scope=Input,Type=0,Dims={4},Value=1,Desc=""),out_mean(Scope=Output,Type=0,Dims={-1},Value=1,Desc=""),out_stdev(Scope=Output,Type=0,Dims={-1},Value=1,Desc="")))),
        Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
          grid = {2.0, 2.0})),
        Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={0,0},
extent={{-100,-100},{100,100}},
fileName="Modelica://SyslabWorkspace/Resources/Images/NewFunctionAPI.svg"), Text(origin={0,130},
lineColor={0,0,255},
extent={{-150,20},{150,-20}},
textString="%name",
textColor={0,0,255})}));

      import Modelica;
      import SyslabWorkspace.Communication;
      extends SyslabWorkspace.Communication.SyslabSampleBase;

      Communication.SyslabFunctionBase base(funcName="stats", scriptText = "base64=ZnVuY3Rpb24gc3RhdHModmFscykKICAgICMg6K6h566X5bmz5Z2H5YC85LiO5qCH5YeG5beuCiAgICBsZW4gPSBsZW5ndGgodmFscyk7CiAgICBtZWFuID0gYXZnKHZhbHMsbGVuKTsKICAgIHN0ZGV2ID0gc3FydChzdW0oKCh2YWxzLi1hdmcodmFscyxsZW4pKS5eMikpL2xlbik7CiAgICByZXR1cm4gbWVhbixzdGRldgplbmQKCiPmsYLlubPlnYflgLwKZnVuY3Rpb24gYXZnKGFycmF5LHNpemUpCiAgICBtZWFuID0gc3VtKGFycmF5KS9zaXplOwplbmQ=", startTime = startTime, period = period, inputDims = {{4}}, inputTypes = {0}, outputDims = {{-1}, {-1}}, outputTypes = {0, 0}, hasInput = true, hasOutput = true,outputNames={"out_mean", "out_stdev"}) 
        annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.RealInput in_vals[4] 
      annotation(Placement(transformation(origin={-110,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Real in_vals_converter(dims = {4}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_mean 
      annotation(Placement(transformation(origin={110,50},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_mean_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,50},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_stdev 
      annotation(Placement(transformation(origin={110,-50},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_stdev_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,-50},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      equation
      connect(in_vals, in_vals_converter.u) 
      annotation (Line(origin = {-95, 0},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_vals_converter.y, base.inputs[1:4]) 
      annotation (Line(origin = {-44, 32},
              points = {{-36, -32}, {0, -32}, {0, 33}, {36, 33}},
              color = {255, 127, 0}));
      connect(out_mean, out_mean_converter.y[1]) 
      annotation (Line(origin = {95, 50},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_mean_converter.u[1], base.outputs[1]) 
      annotation (Line(origin = {36, 57},
              points = {{44, -7}, {0, -7}, {0, 8}, {-44, 8}},
              color = {255, 127, 0}));
      connect(out_stdev, out_stdev_converter.y[1]) 
      annotation (Line(origin = {95, -50},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_stdev_converter.u[1], base.outputs[2]) 
      annotation (Line(origin = {36, 7},
              points = {{44, -57}, {0, -57}, {0, 58}, {-44, 58}},
              color = {255, 127, 0}));
      end SyslabFunction1;
    package ArrayConverter
      model _A2V_1D_Real
      "1 dimension Real array to Real vector"
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
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
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
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

    end ArrayConverter;

  end ImportedTypes;
  ImportedTypes.SyslabFunction1 syslabFunction1_1 
    annotation (Placement(transformation(origin={-94,4.440892098500626e-16},
extent={{-10,-10},{10,10}})));

  Modelica.Blocks.Sources.RealExpression realExpression[4](y={4,5,6,2}) 
    annotation (Placement(transformation(origin={-152,0},
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2})));equation
  connect(realExpression.y, syslabFunction1_1.in_vals) 
  annotation(Line(origin={-123,0},
  points={{-18,0},{18,4.44089e-16}},
  color={0,0,127}));
  end CalNumMean;