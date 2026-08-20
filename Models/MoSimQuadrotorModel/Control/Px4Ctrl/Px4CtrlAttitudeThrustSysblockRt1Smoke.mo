within MoSimQuadrotorModel.Control.Px4Ctrl;
model Px4CtrlAttitudeThrustSysblockRt1Smoke
  "RT1 fixed-input composition smoke for the graphical Px4Ctrl ATTITUDE_THRUST path"

  parameter MoSimQuadrotorModel.Parameters.Sunray150Parameters profile =
    MoSimQuadrotorModel.Parameters.Sunray150Parameters();

  Modelica.Blocks.Sources.Constant position_ref[3](k = {0, 0, 2}) 
    annotation(Placement(transformation(origin={-300,180}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant velocity_ref[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,120}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant acceleration_ref[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,60}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant position_mea[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,0}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant velocity_mea[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,-60}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant attitude_mea[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,-120}, extent={{-20,-20},{20,20}})));
  Modelica.Blocks.Sources.Constant body_rate_mea[3](each k = 0) 
    annotation(Placement(transformation(origin={-300,-180}, extent={{-20,-20},{20,20}})));

  Px4CtrlAttitudeThrustSysblockAdapter adapter(profile = profile) 
    annotation(Placement(transformation(origin={-40,40}, extent={{-80,-80},{80,80}})));
  Px4CtrlRotorAllocator allocator(profile = profile) 
    annotation(Placement(transformation(origin={180,40}, extent={{-70,-70},{70,70}})));

  Real desired_acceleration[3](each unit="m/s2");
  Real attitude_ref[3];
  Real collective_thrust_delta(unit="N");
  Real rotor_command[4](each unit="rad/s");

equation
  connect(position_ref.y, adapter.position_ref);
  connect(velocity_ref.y, adapter.velocity_ref);
  connect(acceleration_ref.y, adapter.acceleration_ref);
  connect(position_mea.y, adapter.position_mea);
  connect(velocity_mea.y, adapter.velocity_mea);
  connect(attitude_mea.y, adapter.attitude_mea);

  connect(adapter.attitude_ref, allocator.attitude_ref);
  connect(attitude_mea.y, allocator.attitude_mea);
  connect(body_rate_mea.y, allocator.body_rate_mea);
  connect(adapter.collective_thrust_delta, allocator.collective_thrust_delta);

  desired_acceleration = adapter.desired_acceleration;
  attitude_ref = adapter.attitude_ref;
  collective_thrust_delta = adapter.collective_thrust_delta;
  rotor_command = allocator.rotor_command;

  annotation(
    experiment(Algorithm=Euler, IntegratorStep=0.01, Interval=0.01,
      StartTime=0, StopTime=0.03, StoreEventValue=0),
    Diagram(coordinateSystem(extent={{-360,-240},{300,240}}, grid={2,2})),
    __MWORKS(version="26.3.0"));
end Px4CtrlAttitudeThrustSysblockRt1Smoke;