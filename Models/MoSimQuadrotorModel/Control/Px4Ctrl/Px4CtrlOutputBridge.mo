within MoSimQuadrotorModel.Control.Px4Ctrl;
block Px4CtrlOutputBridge
  "Px4Ctrl output rotor bridge — applies sign correction for rotors 2 & 4 (4 IN | 4 OUT).
   Plain Modelica block (no SEC) so it can bridge between SEC controller_core and SEC mapper
   without triggering error 3990 (SEC-to-SEC direct connect unsupported at runner level)."

  Modelica.Blocks.Interfaces.RealInput amp_1 
    annotation(Placement(transformation(origin={-110, 60}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amp_2 
    annotation(Placement(transformation(origin={-110, 20}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amp_3 
    annotation(Placement(transformation(origin={-110,-20}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amp_4 
    annotation(Placement(transformation(origin={-110,-60}, extent={{-10,-10},{10,10}})));

  Modelica.Blocks.Interfaces.RealOutput out_1 
    annotation(Placement(transformation(origin={110, 60}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput out_2 
    annotation(Placement(transformation(origin={110, 20}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput out_3 
    annotation(Placement(transformation(origin={110,-20}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput out_4 
    annotation(Placement(transformation(origin={110,-60}, extent={{-10,-10},{10,10}})));

equation
  out_1 =  amp_1;
  out_2 = -amp_2;
  out_3 =  amp_3;
  out_4 = -amp_4;

  annotation(Icon(coordinateSystem(preserveAspectRatio=false), graphics={
    Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,100,150},
      fillColor={240,248,255}, fillPattern=FillPattern.Solid),
    Text(origin={0,40}, extent={{-90,16},{90,-16}},
      textString="Px4Ctrl", textColor={0,100,150}),
    Text(origin={0,10}, extent={{-90,16},{90,-16}},
      textString="OUTPUT BRIDGE", textColor={0,100,150}),
    Text(origin={0,-20}, extent={{-90,14},{90,-14}},
      textString="k=[1,-1,1,-1]", textColor={0,100,150}),
    Text(origin={0,-48}, extent={{-90,12},{90,-12}},
      textString="4 IN | 4 OUT", textColor={0,100,150})}),__MWORKS(version="26.3.0"));
end Px4CtrlOutputBridge;