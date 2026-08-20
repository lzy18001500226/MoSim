within MoSimQuadrotorModel.Control.PID;
block YawDampedAmplitudeRouter
  "Yaw-rate D-term injection before the mapper.
   Mixes a filtered yaw-rate derivative into each rotor amplitude using
   the same CCW/CW sign convention as the PID core mixer:
     rotors 1,3 (CCW): +k_yd * yaw_rate
     rotors 2,4  (CW): -k_yd * yaw_rate"
  parameter Real k_yd(min = 0) = 3.0
    "Yaw-rate damping gain (rad/s -> amplitude units)";
  parameter Real T_filt(min = 1e-6) = 0.02
    "Derivative filter time constant (s)";
  Modelica.Blocks.Interfaces.RealInput amplitude_in_1 
    annotation(Placement(transformation(origin={-110,60},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_in_2 
    annotation(Placement(transformation(origin={-110,20},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_in_3 
    annotation(Placement(transformation(origin={-110,-20},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput amplitude_in_4 
    annotation(Placement(transformation(origin={-110,-60},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput yaw_mea
    "Yaw angle measurement (rad) — derivative taken internally" 
    annotation(Placement(transformation(origin={0,-110},
      extent={{-10,-10},{10,10}}, rotation=90)));
  Modelica.Blocks.Interfaces.RealOutput amplitude_out_1 
    annotation(Placement(transformation(origin={110,60},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_out_2 
    annotation(Placement(transformation(origin={110,20},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_out_3 
    annotation(Placement(transformation(origin={110,-20},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput amplitude_out_4 
    annotation(Placement(transformation(origin={110,-60},
      extent={{-10,-10},{10,10}})));
protected
  Modelica.Blocks.Continuous.Derivative deriv(
    k = 1.0, T = T_filt, x_start = 0.0);
equation
  connect(yaw_mea, deriv.u);
  amplitude_out_1 = amplitude_in_1 + k_yd * deriv.y;
  amplitude_out_2 = amplitude_in_2 - k_yd * deriv.y;
  amplitude_out_3 = amplitude_in_3 + k_yd * deriv.y;
  amplitude_out_4 = amplitude_in_4 - k_yd * deriv.y;
  annotation(
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={
      Rectangle(extent={{-100,100},{100,-100}},
        lineColor={0,100,150}, fillColor={235,245,255},
        fillPattern=FillPattern.Solid),
      Text(origin={0,30}, extent={{-90,20},{90,-20}},
        textString="Yaw Damp", textColor={0,100,150}),
      Text(origin={0,-10}, extent={{-90,20},{90,-20}},
        textString="Router", textColor={0,100,150}),
      Text(origin={0,-50}, extent={{-90,16},{90,-16}},
        textString="k=%k_yd", textColor={100,130,160})}),
    __MWORKS(version="26.3.0"));
end YawDampedAmplitudeRouter;