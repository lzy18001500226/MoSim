model Test1
  annotation (Diagram(coordinateSystem(extent = {{-140.0, -100.0}, {140.0, 100.0}},
    preserveAspectRatio = false,
    grid = {2.0, 2.0})),
    Icon(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
      preserveAspectRatio = false,
      grid = {2.0, 2.0})));
  inner System system 
    annotation (Placement(transformation(origin = {-48.96588552856289, 50.94705781523115},
      extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  Components.Pipe_with pipe_with 
    annotation (Placement(transformation(origin = {-70, 0}, extent = {{-10, -10}, {10, 10}})));
  Components.BoundaryMdot boundaryMdot 
    annotation (Placement(transformation(origin={-114,0},
extent={{-10,-10},{10,10}})));
  Components.BoundaryP boundaryP(p=2e5) 
    annotation (Placement(transformation(origin={-12,10},
extent={{-10,-10},{10,10}})));
  // Components.Pipe_with pipe1(redeclare model HeatTransfer = Components.BasicModel.HeatTransfer.DittusBoelterAdjustable) annotation (Placement(transformation(origin = {-14.86760314146767, 19.789487162738126},
  //     extent = {{-10.0, -10.0}, {10.0, 10.0}})));
  equation
  connect(boundaryMdot.port_a, pipe_with.port_a) 
  annotation(Line(origin={-115,-5},
points={{11,5},{35,5}},
color={0,127,255}));
  connect(pipe_with.port_b, boundaryP.port_a) 
  annotation(Line(origin={-8,-10},
points={{-52,10},{9,10},{9,20},{6,20}},
color={0,127,255}));
  end Test1;