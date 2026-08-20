within MoSimQuadrotorModel.Control.Px4Ctrl;
block Px4CtrlInputSampler
  "Px4Ctrl input sampling stage — 18 continuous signals → 18 discrete-sampled outputs (18 IN | 18 OUT).
   Plain Modelica block (no SEC) so it can bridge between continuous plant signals and SEC controller_core
   without triggering error 3990 (SEC-to-SEC direct connect unsupported at runner level).
   Uses when-sample ZOH at 100 Hz."

  parameter Real T_s(unit="s") = 0.01 "Sampling period (s)";

  // ── Input ports ──────────────────────────────────────────────────────────────
  Modelica.Blocks.Interfaces.RealInput pos_ref_x 
    annotation(Placement(transformation(origin={-110, 90}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_ref_y 
    annotation(Placement(transformation(origin={-110, 78}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_ref_z 
    annotation(Placement(transformation(origin={-110, 66}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_ref_x 
    annotation(Placement(transformation(origin={-110, 54}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_ref_y 
    annotation(Placement(transformation(origin={-110, 42}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_ref_z 
    annotation(Placement(transformation(origin={-110, 30}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput acc_ref_x 
    annotation(Placement(transformation(origin={-110, 18}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput acc_ref_y 
    annotation(Placement(transformation(origin={-110,  6}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput acc_ref_z 
    annotation(Placement(transformation(origin={-110, -6}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_mea_x 
    annotation(Placement(transformation(origin={-110,-18}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_mea_y 
    annotation(Placement(transformation(origin={-110,-30}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_mea_z 
    annotation(Placement(transformation(origin={-110,-42}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_mea_x 
    annotation(Placement(transformation(origin={-110,-54}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_mea_y 
    annotation(Placement(transformation(origin={-110,-66}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput vel_mea_z 
    annotation(Placement(transformation(origin={-110,-78}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput att_roll 
    annotation(Placement(transformation(origin={-110,-86}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput att_pitch 
    annotation(Placement(transformation(origin={-110,-92}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput att_yaw 
    annotation(Placement(transformation(origin={-110,-98}, extent={{-10,-10},{10,10}})));

  // ── Output ports ─────────────────────────────────────────────────────────────
  Modelica.Blocks.Interfaces.RealOutput s_pos_ref_x 
    annotation(Placement(transformation(origin={110, 90}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_pos_ref_y 
    annotation(Placement(transformation(origin={110, 78}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_pos_ref_z 
    annotation(Placement(transformation(origin={110, 66}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_ref_x 
    annotation(Placement(transformation(origin={110, 54}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_ref_y 
    annotation(Placement(transformation(origin={110, 42}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_ref_z 
    annotation(Placement(transformation(origin={110, 30}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_acc_ref_x 
    annotation(Placement(transformation(origin={110, 18}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_acc_ref_y 
    annotation(Placement(transformation(origin={110,  6}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_acc_ref_z 
    annotation(Placement(transformation(origin={110, -6}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_pos_mea_x 
    annotation(Placement(transformation(origin={110,-18}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_pos_mea_y 
    annotation(Placement(transformation(origin={110,-30}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_pos_mea_z 
    annotation(Placement(transformation(origin={110,-42}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_mea_x 
    annotation(Placement(transformation(origin={110,-54}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_mea_y 
    annotation(Placement(transformation(origin={110,-66}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_vel_mea_z 
    annotation(Placement(transformation(origin={110,-78}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_att_roll 
    annotation(Placement(transformation(origin={110,-86}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_att_pitch 
    annotation(Placement(transformation(origin={110,-92}, extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput s_att_yaw 
    annotation(Placement(transformation(origin={110,-98}, extent={{-10,-10},{10,10}})));

equation
  when sample(0, T_s) then
    s_pos_ref_x = pos_ref_x;
    s_pos_ref_y = pos_ref_y;
    s_pos_ref_z = pos_ref_z;
    s_vel_ref_x = vel_ref_x;
    s_vel_ref_y = vel_ref_y;
    s_vel_ref_z = vel_ref_z;
    s_acc_ref_x = acc_ref_x;
    s_acc_ref_y = acc_ref_y;
    s_acc_ref_z = acc_ref_z;
    s_pos_mea_x = pos_mea_x;
    s_pos_mea_y = pos_mea_y;
    s_pos_mea_z = pos_mea_z;
    s_vel_mea_x = vel_mea_x;
    s_vel_mea_y = vel_mea_y;
    s_vel_mea_z = vel_mea_z;
    s_att_roll  = att_roll;
    s_att_pitch = att_pitch;
    s_att_yaw   = att_yaw;
  end when;

  annotation(Icon(coordinateSystem(preserveAspectRatio=false), graphics={
    Rectangle(extent={{-100,100},{100,-100}}, lineColor={0,100,150},
      fillColor={240,248,255}, fillPattern=FillPattern.Solid),
    Text(origin={0,40}, extent={{-90,16},{90,-16}},
      textString="Px4Ctrl", textColor={0,100,150}),
    Text(origin={0,12}, extent={{-90,16},{90,-16}},
      textString="INPUT SAMPLER", textColor={0,100,150}),
    Text(origin={0,-16}, extent={{-90,14},{90,-14}},
      textString="ZOH 100Hz", textColor={0,100,150}),
    Text(origin={0,-44}, extent={{-90,12},{90,-12}},
      textString="18 IN | 18 OUT", textColor={0,100,150})}),__MWORKS(version="26.3.0"));
end Px4CtrlInputSampler;