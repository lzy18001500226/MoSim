within MoSimQuadrotorModel.Control.PID;
block BodyFramePreprocessor
  "World-to-body-frame coordinate preprocessor for the PID core.
   Rotates world-frame XY references and measurements into body frame
   using the current yaw angle:
     x_body =  x_world*cos(yaw) + y_world*sin(yaw)
     y_body = -x_world*sin(yaw) + y_world*cos(yaw)
   Also extracts roll/pitch/yaw scalars and passes z through unchanged."
  Modelica.Blocks.Interfaces.RealInput pos_ref[3]
    "World-frame position reference [x,y,z] from trajectory generator" 
    annotation(Placement(transformation(origin={-110,50},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput pos_mea[3]
    "World-frame position measurement [x,y,z] from perception" 
    annotation(Placement(transformation(origin={-110,0},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealInput attitude[3]
    "Euler angles [roll, pitch, yaw] from plant" 
    annotation(Placement(transformation(origin={-110,-50},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput x_ref 
    annotation(Placement(transformation(origin={110,80},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput y_ref 
    annotation(Placement(transformation(origin={110,56},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput z_ref 
    annotation(Placement(transformation(origin={110,32},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput x_mea 
    annotation(Placement(transformation(origin={110,8},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput y_mea 
    annotation(Placement(transformation(origin={110,-16},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput z_mea 
    annotation(Placement(transformation(origin={110,-40},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput roll_mea 
    annotation(Placement(transformation(origin={110,-56},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput pitch_mea 
    annotation(Placement(transformation(origin={110,-68},
      extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput yaw_mea 
    annotation(Placement(transformation(origin={110,-80},
      extent={{-10,-10},{10,10}})));
equation
  x_ref     =  pos_ref[1] * Modelica.Math.cos(attitude[3]) + pos_ref[2] * Modelica.Math.sin(attitude[3]);
  y_ref     = -pos_ref[1] * Modelica.Math.sin(attitude[3]) + pos_ref[2] * Modelica.Math.cos(attitude[3]);
  z_ref     =  pos_ref[3];
  x_mea     =  pos_mea[1] * Modelica.Math.cos(attitude[3]) + pos_mea[2] * Modelica.Math.sin(attitude[3]);
  y_mea     = -pos_mea[1] * Modelica.Math.sin(attitude[3]) + pos_mea[2] * Modelica.Math.cos(attitude[3]);
  z_mea     =  pos_mea[3];
  roll_mea  =  attitude[1];
  pitch_mea =  attitude[2];
  yaw_mea   =  attitude[3];
  annotation(
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={
      Rectangle(extent={{-100,100},{100,-100}},
        lineColor={0,100,150}, fillColor={240,250,235},
        fillPattern=FillPattern.Solid),
      Text(origin={0,30}, extent={{-88,20},{88,-20}},
        textString="Body Frame", textColor={0,100,150}),
      Text(origin={0,0}, extent={{-88,20},{88,-20}},
        textString="Preprocessor", textColor={0,100,150}),
      Text(origin={0,-38}, extent={{-88,16},{88,-16}},
        textString="3+3+3 IN | 9 OUT", textColor={100,130,160})}),
    __MWORKS(version="26.3.0"));
end BodyFramePreprocessor;