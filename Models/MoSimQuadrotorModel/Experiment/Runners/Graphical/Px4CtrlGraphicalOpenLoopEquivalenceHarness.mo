within MoSimQuadrotorModel.Experiment.Runners.Graphical;
model Px4CtrlGraphicalOpenLoopEquivalenceHarness
  "Driven graphical PX4CTRL versus EquationBridge outer-loop comparison"

  parameter Real comparison_epsilon(min = 1e-15) = 1e-12;

  MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock graphical 
    annotation(
      Placement(transformation(origin = {-100, 75}, extent = {{-55, -55}, {55, 55}})),
      __MWORKS(SECInstance = true));
  MoSimQuadrotorModel.Control.Adapters.Px4CtrlAttitudeThrustAdapter equation_adapter 
    annotation(Placement(transformation(origin = {100, 75}, extent = {{-55, -55}, {55, 55}})));
  Modelica.Blocks.Sources.RealExpression ref_px_source(y = ref_px_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_py_source(y = ref_py_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_pz_source(y = ref_pz_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_vx_source(y = ref_vx_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_vy_source(y = ref_vy_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_vz_source(y = ref_vz_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_ax_source(y = ref_ax_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_ay_source(y = ref_ay_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_az_source(y = ref_az_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression px_source(y = px_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression py_source(y = py_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression pz_source(y = pz_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression vx_source(y = vx_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression vy_source(y = vy_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression vz_source(y = vz_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression yaw_mea_source(y = yaw_mea_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Sources.RealExpression ref_yaw_source(y = ref_yaw_in) annotation(Placement(transformation(extent={{-15,-50},{15,-10}})));
  Modelica.Blocks.Math.Gain graphical_output_capture[8](each k = 1);

  Real ref_px_in annotation(Placement(transformation(extent={{-15,-384},{15,-344}})));
  Real ref_py_in annotation(Placement(transformation(extent={{-15,-436},{15,-396}})));
  Real ref_pz_in annotation(Placement(transformation(extent={{-15,-488},{15,-448}})));
  Real ref_vx_in annotation(Placement(transformation(extent={{-15,-540},{15,-500}})));
  Real ref_vy_in annotation(Placement(transformation(extent={{-15,-592},{15,-552}})));
  Real ref_vz_in annotation(Placement(transformation(extent={{-15,-644},{15,-604}})));
  Real ref_ax_in annotation(Placement(transformation(extent={{-15,-228},{15,-188}})));
  Real ref_ay_in annotation(Placement(transformation(extent={{-15,-280},{15,-240}})));
  Real ref_az_in annotation(Placement(transformation(extent={{-15,-332},{15,-292}})));
  Real px_in annotation(Placement(transformation(extent={{-15,-72},{15,-32}})));
  Real py_in annotation(Placement(transformation(extent={{-15,-124},{15,-84}})));
  Real pz_in annotation(Placement(transformation(extent={{-15,-176},{15,-136}})));
  Real vx_in annotation(Placement(transformation(extent={{-15,-1216},{15,-1176}})));
  Real vy_in annotation(Placement(transformation(extent={{-15,-1268},{15,-1228}})));
  Real vz_in annotation(Placement(transformation(extent={{-15,-1320},{15,-1280}})));
  Real yaw_mea_in annotation(Placement(transformation(extent={{-15,-1372},{15,-1332}})));
  Real ref_yaw_in annotation(Placement(transformation(extent={{-15,-696},{15,-656}})));

  Real graphical_desired_acc_x annotation(Placement(transformation(extent={{-15,292},{15,332}})));
  Real graphical_desired_acc_y annotation(Placement(transformation(extent={{-15,240},{15,280}})));
  Real graphical_desired_acc_z annotation(Placement(transformation(extent={{-15,188},{15,228}})));
  Real graphical_roll_cmd annotation(Placement(transformation(extent={{-15,32},{15,72}})));
  Real graphical_pitch_cmd annotation(Placement(transformation(extent={{-15,84},{15,124}})));
  Real graphical_yaw_cmd annotation(Placement(transformation(extent={{-15,-20},{15,20}})));
  Real graphical_collective_thrust_n annotation(Placement(transformation(extent={{-15,344},{15,384}})));
  Real graphical_normalized_thrust annotation(Placement(transformation(extent={{-15,136},{15,176}})));
  Real graphical_collective_thrust_delta annotation(Placement(transformation(extent={{-15,396},{15,436}})));

  Real equation_desired_acc_x annotation(Placement(transformation(extent={{-15,760},{15,800}})));
  Real equation_desired_acc_y annotation(Placement(transformation(extent={{-15,708},{15,748}})));
  Real equation_desired_acc_z annotation(Placement(transformation(extent={{-15,656},{15,696}})));
  Real equation_roll_cmd annotation(Placement(transformation(extent={{-15,500},{15,540}})));
  Real equation_pitch_cmd annotation(Placement(transformation(extent={{-15,552},{15,592}})));
  Real equation_yaw_cmd annotation(Placement(transformation(extent={{-15,448},{15,488}})));
  Real equation_collective_thrust_n annotation(Placement(transformation(extent={{-15,812},{15,852}})));
  Real equation_normalized_thrust annotation(Placement(transformation(extent={{-15,604},{15,644}})));
  Real equation_collective_thrust_delta annotation(Placement(transformation(extent={{-15,864},{15,904}})));

  Real delta_desired_acc_x annotation(Placement(transformation(extent={{-15,1228},{15,1268}})));
  Real delta_desired_acc_y annotation(Placement(transformation(extent={{-15,1176},{15,1216}})));
  Real delta_desired_acc_z annotation(Placement(transformation(extent={{-15,1124},{15,1164}})));
  Real delta_roll_cmd annotation(Placement(transformation(extent={{-15,968},{15,1008}})));
  Real delta_pitch_cmd annotation(Placement(transformation(extent={{-15,1020},{15,1060}})));
  Real delta_yaw_cmd annotation(Placement(transformation(extent={{-15,916},{15,956}})));
  Real delta_collective_thrust_n annotation(Placement(transformation(extent={{-15,1280},{15,1320}})));
  Real delta_normalized_thrust annotation(Placement(transformation(extent={{-15,1072},{15,1112}})));
  Real delta_collective_thrust_delta annotation(Placement(transformation(extent={{-15,1332},{15,1372}})));
  Real relative_delta_desired_acc_x annotation(Placement(transformation(extent={{-15,-852},{15,-812}})));
  Real relative_delta_desired_acc_y annotation(Placement(transformation(extent={{-15,-904},{15,-864}})));
  Real relative_delta_desired_acc_z annotation(Placement(transformation(extent={{-15,-956},{15,-916}})));
  Real relative_delta_roll_cmd annotation(Placement(transformation(extent={{-15,-1112},{15,-1072}})));
  Real relative_delta_pitch_cmd annotation(Placement(transformation(extent={{-15,-1060},{15,-1020}})));
  Real relative_delta_yaw_cmd annotation(Placement(transformation(extent={{-15,-1164},{15,-1124}})));
  Real relative_delta_collective_thrust_n annotation(Placement(transformation(extent={{-15,-800},{15,-760}})));
  Real relative_delta_normalized_thrust annotation(Placement(transformation(extent={{-15,-1008},{15,-968}})));
  Real relative_delta_collective_thrust_delta annotation(Placement(transformation(extent={{-15,-748},{15,-708}})));

equation
  // Each profile combines a step, sinusoid, and a second step. The amplitudes
  // exercise high commands while retaining an unambiguous Euler extraction.
  ref_px_in = (if time < 0.10 then 0 else 2.2) + 0.35 * sin(2 * Modelica.Constants.pi * 0.70 * time)
    + (if time < 0.70 then 0 else -2.8);
  ref_py_in = (if time < 0.18 then 0 else -1.8) + 0.30 * sin(2 * Modelica.Constants.pi * 0.55 * time)
    + (if time < 0.82 then 0 else 2.4);
  ref_pz_in = (if time < 0.14 then 0 else 3.2) + 0.25 * sin(2 * Modelica.Constants.pi * 0.40 * time)
    + (if time < 0.76 then 0 else -4.2);
  ref_vx_in = (if time < 0.10 then 0 else 0.85) + 0.18 * sin(2 * Modelica.Constants.pi * 0.70 * time)
    + (if time < 0.70 then 0 else -1.05);
  ref_vy_in = (if time < 0.18 then 0 else -0.70) + 0.16 * sin(2 * Modelica.Constants.pi * 0.55 * time)
    + (if time < 0.82 then 0 else 0.95);
  ref_vz_in = (if time < 0.14 then 0 else 0.75) + 0.14 * sin(2 * Modelica.Constants.pi * 0.40 * time)
    + (if time < 0.76 then 0 else -1.10);
  ref_ax_in = 0.45 * sin(2 * Modelica.Constants.pi * 0.70 * time)
    + (if time < 0.35 then 0 else 0.70) + (if time < 0.90 then 0 else -1.10);
  ref_ay_in = 0.40 * sin(2 * Modelica.Constants.pi * 0.55 * time)
    + (if time < 0.42 then 0 else -0.65) + (if time < 0.88 then 0 else 1.00);
  ref_az_in = 0.55 * sin(2 * Modelica.Constants.pi * 0.40 * time)
    + (if time < 0.30 then 0 else 2.20) + (if time < 0.80 then 0 else -3.10);
  px_in = 0.20 * sin(2 * Modelica.Constants.pi * 0.32 * time);
  py_in = -0.15 * sin(2 * Modelica.Constants.pi * 0.28 * time);
  pz_in = 0.10 * sin(2 * Modelica.Constants.pi * 0.36 * time);
  vx_in = 0.12 * cos(2 * Modelica.Constants.pi * 0.32 * time);
  vy_in = -0.09 * cos(2 * Modelica.Constants.pi * 0.28 * time);
  vz_in = 0.08 * cos(2 * Modelica.Constants.pi * 0.36 * time);
  yaw_mea_in = 0.22 * sin(2 * Modelica.Constants.pi * 0.25 * time);
  // Px4CtrlAttitudeThrustAdapter has no reference-yaw input and assigns
  // core.ref_yaw = 0. Keep both implementations in their shared input domain.
  // The measured-yaw sine above still exercises the yaw-frame transformation.
  ref_yaw_in = 0;

  connect(ref_px_source.y, graphical.ref_px);
  connect(ref_py_source.y, graphical.ref_py);
  connect(ref_pz_source.y, graphical.ref_pz);
  connect(ref_vx_source.y, graphical.ref_vx);
  connect(ref_vy_source.y, graphical.ref_vy);
  connect(ref_vz_source.y, graphical.ref_vz);
  connect(ref_ax_source.y, graphical.ref_ax);
  connect(ref_ay_source.y, graphical.ref_ay);
  connect(ref_az_source.y, graphical.ref_az);
  connect(px_source.y, graphical.px);
  connect(py_source.y, graphical.py);
  connect(pz_source.y, graphical.pz);
  connect(vx_source.y, graphical.vx);
  connect(vy_source.y, graphical.vy);
  connect(vz_source.y, graphical.vz);
  connect(yaw_mea_source.y, graphical.yaw_mea);
  connect(ref_yaw_source.y, graphical.ref_yaw);

  connect(graphical.desired_acc_x, graphical_output_capture[1].u);
  connect(graphical.desired_acc_y, graphical_output_capture[2].u);
  connect(graphical.desired_acc_z, graphical_output_capture[3].u);
  connect(graphical.roll_cmd, graphical_output_capture[4].u);
  connect(graphical.pitch_cmd, graphical_output_capture[5].u);
  connect(graphical.yaw_cmd, graphical_output_capture[6].u);
  connect(graphical.collective_thrust_n, graphical_output_capture[7].u);
  connect(graphical.normalized_thrust, graphical_output_capture[8].u);

  // This is the production EquationBridge route. Its Euler-to-quaternion
  // conversion supplies the same attitude source to both core quaternion buses.
  equation_adapter.position_ref = {ref_px_in, ref_py_in, ref_pz_in};
  equation_adapter.velocity_ref = {ref_vx_in, ref_vy_in, ref_vz_in};
  equation_adapter.acceleration_ref = {ref_ax_in, ref_ay_in, ref_az_in};
  equation_adapter.position_mea = {px_in, py_in, pz_in};
  equation_adapter.velocity_mea = {vx_in, vy_in, vz_in};
  equation_adapter.attitude_mea = {0, 0, yaw_mea_in};

  graphical_desired_acc_x = graphical_output_capture[1].y;
  graphical_desired_acc_y = graphical_output_capture[2].y;
  graphical_desired_acc_z = graphical_output_capture[3].y;
  graphical_roll_cmd = graphical_output_capture[4].y;
  graphical_pitch_cmd = graphical_output_capture[5].y;
  graphical_yaw_cmd = graphical_output_capture[6].y;
  graphical_collective_thrust_n = graphical_output_capture[7].y;
  graphical_normalized_thrust = graphical_output_capture[8].y;
  graphical_collective_thrust_delta = graphical_collective_thrust_n - 9.80665;

  equation_desired_acc_x = equation_adapter.core.desired_acc_x;
  equation_desired_acc_y = equation_adapter.core.desired_acc_y;
  equation_desired_acc_z = equation_adapter.core.desired_acc_z;
  equation_roll_cmd = -equation_adapter.attitude_ref[1];
  equation_pitch_cmd = equation_adapter.attitude_ref[2];
  equation_yaw_cmd = equation_adapter.attitude_ref[3];
  equation_collective_thrust_delta = equation_adapter.collective_thrust_delta;
  equation_collective_thrust_n = equation_collective_thrust_delta
    + equation_adapter.hover_collective_thrust_n;
  equation_normalized_thrust = equation_adapter.core.normalized_thrust;

  delta_desired_acc_x = graphical_desired_acc_x - equation_desired_acc_x;
  delta_desired_acc_y = graphical_desired_acc_y - equation_desired_acc_y;
  delta_desired_acc_z = graphical_desired_acc_z - equation_desired_acc_z;
  delta_roll_cmd = graphical_roll_cmd - equation_roll_cmd;
  delta_pitch_cmd = graphical_pitch_cmd - equation_pitch_cmd;
  delta_yaw_cmd = graphical_yaw_cmd - equation_yaw_cmd;
  delta_collective_thrust_n = graphical_collective_thrust_n - equation_collective_thrust_n;
  delta_normalized_thrust = graphical_normalized_thrust - equation_normalized_thrust;
  delta_collective_thrust_delta = graphical_collective_thrust_delta - equation_collective_thrust_delta;

  relative_delta_desired_acc_x = abs(delta_desired_acc_x) / max(comparison_epsilon,
    max(abs(graphical_desired_acc_x), abs(equation_desired_acc_x)));
  relative_delta_desired_acc_y = abs(delta_desired_acc_y) / max(comparison_epsilon,
    max(abs(graphical_desired_acc_y), abs(equation_desired_acc_y)));
  relative_delta_desired_acc_z = abs(delta_desired_acc_z) / max(comparison_epsilon,
    max(abs(graphical_desired_acc_z), abs(equation_desired_acc_z)));
  relative_delta_roll_cmd = abs(delta_roll_cmd) / max(comparison_epsilon,
    max(abs(graphical_roll_cmd), abs(equation_roll_cmd)));
  relative_delta_pitch_cmd = abs(delta_pitch_cmd) / max(comparison_epsilon,
    max(abs(graphical_pitch_cmd), abs(equation_pitch_cmd)));
  relative_delta_yaw_cmd = abs(delta_yaw_cmd) / max(comparison_epsilon,
    max(abs(graphical_yaw_cmd), abs(equation_yaw_cmd)));
  relative_delta_collective_thrust_n = abs(delta_collective_thrust_n) / max(comparison_epsilon,
    max(abs(graphical_collective_thrust_n), abs(equation_collective_thrust_n)));
  relative_delta_normalized_thrust = abs(delta_normalized_thrust) / max(comparison_epsilon,
    max(abs(graphical_normalized_thrust), abs(equation_normalized_thrust)));
  relative_delta_collective_thrust_delta = abs(delta_collective_thrust_delta) / max(comparison_epsilon,
    max(abs(graphical_collective_thrust_delta), abs(equation_collective_thrust_delta)));

  annotation(
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1.2, Tolerance = 0.000001, Interval = 0.01),
    Diagram(coordinateSystem(extent = {{-220, -150}, {220, 150}}, grid = {2, 2})),
    __MWORKS(version = "26.3.0"));
end Px4CtrlGraphicalOpenLoopEquivalenceHarness;