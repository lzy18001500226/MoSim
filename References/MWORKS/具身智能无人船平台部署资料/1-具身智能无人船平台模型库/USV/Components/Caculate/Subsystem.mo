model Subsystem "船速输出"
  Modelica.Blocks.Interfaces.RealInput V_local[3] 
    "船速" annotation (Placement(transformation(origin={-110.645,3.22581e-6}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput V_local1[3] 
    "船速" annotation (Placement(transformation(origin={111.49,-0.234665}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput disturbX 
    "X方向扰动" annotation (Placement(transformation(origin={-110.419,89.7907}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput disturbY 
    "Y方向扰动" annotation (Placement(transformation(origin={-110.047,-89.2478}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.TransferFunction transferFunction(a={0.5,1}) 
    annotation (Placement(transformation(origin={-48.5204,89.9493}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Continuous.TransferFunction transferFunction1(a={0.5,1}) 
    annotation (Placement(transformation(origin={-39.8267,-89.4668}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Feedback feedback 
    annotation (Placement(transformation(origin={0.373233,64.0096}, 
extent={{-10,10},{10,-10}})));
  Modelica.Blocks.Math.Add feedback1 
    annotation (Placement(transformation(origin={0.669154,-69.3122}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain(k=-0.3) 
    annotation (Placement(transformation(origin={-38.0278,-9.8879e-5}, 
extent={{-6.20235,-6.20235},{6.20235,6.20235}})));
  Modelica.Blocks.Nonlinear.DeadZone deadZone(uMax=5) 
    annotation (Placement(transformation(origin={18.5165,-0.0422072}, 
extent={{-6.20235,-6.20235},{6.20235,6.20235}})));
  USV.Utilities.Math.R2D r2D 
    annotation (Placement(transformation(origin={-9.88369,-0.0131355}, 
extent={{-6.20235,-6.20235},{6.20235,6.20235}})));
  Modelica.Blocks.Nonlinear.Limiter limiter(uMax=40) 
    annotation (Placement(transformation(origin={51.3368,-0.147896}, 
extent={{-6.20235,-6.20235},{6.20235,6.20235}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={10,10})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={10,10}),graphics = {Rectangle(origin={-0.256586,0.769759}, 
lineColor={0,0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,-100},{100,100}}, 
radius=25), Text(origin={7.05613,-4.49026}, 
lineColor={255,0,0}, 
extent={{-56.0641,32.4582},{56.0641,-32.4582}}, 
textString="Subsystem", 
textStyle={TextStyle.None}, 
textColor={255,0,0}, 
horizontalAlignment=LinePattern.None)}));
equation
  connect(transferFunction.u, disturbX) 
  annotation(Line(origin={-85,90.1226}, 
points={{24.4796,-0.173287},{-25.419,-0.173287},{-25.419,-0.331899}}, 
color={0,0,127}));
  connect(transferFunction.y, feedback.u2) 
  annotation(Line(origin={-18,69.1226}, 
points={{-19.5204,20.8267},{18.3732,20.8267},{18.3732,2.88692}}, 
color={0,0,127}));
  connect(V_local[1], feedback.u1) 
  annotation(Line(origin={-59,12}, 
points={{-51.645,-12},{-1.09064,-12},{-1.09064,52.0096},{51.3732,52.0096}}, 
color={0,0,127}));
  connect(V_local[2], feedback1.u1) 
  annotation(Line(origin={-58,-15}, 
points={{-52.645,15},{-2.09064,15},{-2.09064,-54.3122},{50.6692,-54.3122}}, 
color={0,0,127}));
  connect(feedback1.u2, transferFunction1.y) 
  annotation(Line(origin={-13.8134,-83.8163}, 
points={{2.48255,8.5041},{-6.49074,8.5041},{-6.49074,-5.6505},{-15.0133,-5.6505}}, 
color={0,0,127}));
  connect(transferFunction1.u, disturbY) 
  annotation(Line(origin={-80.8134,-89.8163}, 
points={{28.9867,0.349507},{-29.234,0.349507},{-29.234,0.5685}}, 
color={0,0,127}));
  connect(feedback.y, V_local1[1]) 
  annotation(Line(origin={60,12}, 
points={{-50.626767,52.0096},{10.3546,52.0096},{10.3546,-12.2347},{51.4895,-12.2347}}, 
color={0,0,127}));
  connect(feedback1.y, V_local1[2]) 
  annotation(Line(origin={60,-16}, 
points={{-48.330846,-53.3122},{10.3771,-53.3122},{10.3771,15.7653},{51.4895,15.7653}}, 
color={0,0,127}));
  connect(gain.u, V_local[3]) 
  annotation(Line(origin={-78,0}, 
points={{32.5294,-9.8879e-5},{-32.645,-9.8879e-5},{-32.645,3.22581e-6}}, 
color={0,0,127}));
  connect(r2D.u, deadZone.u) 
  annotation(Line(origin={3.46203,-0.30802}, 
points={{-6.51494,0.272069},{7.61161,0.272069},{7.61161,0.265813}}, 
color={0,0,127}));
  connect(r2D.w, gain.y) 
  annotation(Line(origin={-23.538,-0.30802}, 
points={{6.76688,0.261039},{-7.66722,0.261039},{-7.66722,0.307921}}, 
color={0,0,127}));
  connect(deadZone.y, limiter.u) 
  annotation(Line(origin={34,0}, 
points={{-8.660915,-0.0422072},{9.89393,-0.0422072},{9.89393,-0.147896}}, 
color={0,0,127}));
  connect(limiter.y, V_local1[3]) 
  annotation(Line(origin={84,0}, 
points={{-25.8407,-0.147896},{27.4895,-0.147896},{27.4895,-0.234665}}, 
color={0,0,127}));
  end Subsystem;