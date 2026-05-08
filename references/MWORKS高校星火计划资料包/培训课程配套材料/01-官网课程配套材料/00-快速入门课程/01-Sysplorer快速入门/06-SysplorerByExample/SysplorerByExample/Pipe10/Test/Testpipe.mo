model Testpipe
  annotation(__MWORKS(version="2025b"));
  Boundarys.Boundary_P boundary_P 
    annotation (Placement(transformation(origin={-88,-14},
extent={{25,-30},{-25,30}})));
  Boundarys.Boundary_P boundary_P1(p=1.01e5) 
    annotation (Placement(transformation(origin={92,-12.2},
extent={{-28,-24},{28,24}})));
  Components.Pipe pipe 
    annotation (Placement(transformation(origin={4,-12.2},
extent={{-28,-21},{28,21}})));
  inner Sys.System system 
    annotation (Placement(transformation(origin = {-60, 80}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(boundary_P.Porta, pipe.Porta) 
  annotation(Line(origin={-33,-10},
points={{-25,2},{9,2}},
color={0,0,255}));
  connect(pipe.Portb, boundary_P1.Porta) 
  annotation(Line(origin={26,-8},
points={{-19.2,0},{32.4,0},{32.4,0.6}},
color={0,0,255},
thickness=2));
  end Testpipe;