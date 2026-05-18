model caculate
  USV.Components.Caculate.caculate caculate1(subsystem(gain(k=-0.3)),unitDelay(samplePeriod=0.001)) 
    annotation (Placement(transformation(origin={61.8331,2.64446}, 
extent={{-29.6083,-27.6142},{29.6083,27.6142}})));
  Modelica.Blocks.Sources.Sine sine[3](f(displayUnit="rad/s")=0.159154943091895) 
    annotation (Placement(transformation(origin={-79.7452,2.31206}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Sine const(f(displayUnit="rad/s")=0.159154943091895) 
    annotation (Placement(transformation(origin={-78.0842,-47.8718}, 
extent={{-10,-10},{10,10}})));
equation
  connect(sine.y, caculate1.V_local) 
  annotation(Line(origin={-31.9592,-0.138935}, 
points={{-36.786,2.45099},{61.3277,2.45099},{61.3277,2.79064}}, 
color={0,0,127}));
  connect(const.y, caculate1.disturbY) 
  annotation(Line(origin={-18.9592,-12.1389}, 
points={{-48.125,-35.7329},{-17.2493,-35.7329},{-17.2493,36.7322},{47.9084,36.7322}}, 
color={0,0,127}));
  connect(const.y, caculate1.disturbX) 
  annotation(Line(origin={-18.9592,-33.1389}, 
points={{-48.125,-14.7329},{-17.2493,-14.7329},{-17.2493,13.7607},{47.9875,13.7607}}, 
color={0,0,127}));
  end caculate;