within QuadrotorExperiments;
model Sunray150CompleteSystemGraphical_Sysblock
  "Sunray150 complete graphical system with project AWFF Sysblock data flow"
  parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604
    "Original MWORKS-equivalent hover command before Sunray150 SDF motorConstant calibration";
  parameter Real hover_motor_speed_cmd = 53.562090367172424
    "MWORKS visual rotor hover speed; physical Sunray150 motor speed is 10x by rotorVelocitySlowdownSim";
  parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd
    "Scale legacy controller speed increments to the Sunray150 SDF motorConstant speed domain";

  block PerceptionInterfaceModule
    "Top-level perception interface: GPS/GNSS and Mid360 local-map data"
    Modelica.Blocks.Interfaces.RealInput position_raw[3]
      annotation (Placement(transformation(origin = {-110, 20}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput gps_position[3]
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput local_position[3]
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput obstacle_margin
      annotation (Placement(transformation(origin = {110, -35}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -75}, extent = {{-10, -10}, {10, 10}})));
  equation
    gps_position = position_raw;
    local_position = position_raw;
    obstacle_margin = 5.0;
    health = 1;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 100, 150}, fillColor = {242, 252, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {-38, 24}, extent = {{-48, -36}, {48, 36}}, fileName = "modelica://QuadrotorModel/Resources/Images/GPS.png"),
        Bitmap(origin = {42, 24}, extent = {{-48, -36}, {48, 36}}, fileName = "modelica://QuadrotorModel/Resources/Images/MId360.png"),
        Text(origin = {0, -70}, extent = {{-90, 15}, {90, -15}}, textString = "GPS + Mid360", textColor = {0, 100, 150})}));
  end PerceptionInterfaceModule;

  block V6XFlightControllerModule
    "Top-level V6X/PX6C flight-controller interface"
    Modelica.Blocks.Interfaces.RealInput gps_position[3]
      annotation (Placement(transformation(origin = {-110, 55}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput attitude_raw[3]
      annotation (Placement(transformation(origin = {-110, 10}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput motor_speed_raw[4]
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput position_est[3]
      annotation (Placement(transformation(origin = {110, 55}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput attitude_est[3]
      annotation (Placement(transformation(origin = {110, 10}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput motor_speed_est[4]
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-10, -10}, {10, 10}})));
  equation
    position_est = gps_position;
    attitude_est = attitude_raw;
    motor_speed_est = motor_speed_raw;
    health = 1;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {100, 70, 20}, fillColor = {255, 248, 235}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 20}, extent = {{-88, -58}, {88, 58}}, fileName = "modelica://QuadrotorModel/Resources/Images/V6X.png"),
        Text(origin = {0, -76}, extent = {{-90, 15}, {90, -15}}, textString = "V6X / PX6C", textColor = {100, 70, 20})}));
  end V6XFlightControllerModule;

  block ORINNXMissionComputerModule
    "Top-level ORIN NX mission computer with internal trajectory source"
    Modelica.Blocks.Interfaces.RealInput aircraft_position[3]
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput local_position[3]
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput obstacle_margin
      annotation (Placement(transformation(origin = {-110, -45}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput reference_position[3]
      annotation (Placement(transformation(origin = {110, 50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput yaw_reference
      annotation (Placement(transformation(origin = {110, 5}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput z_reference_rate
      annotation (Placement(transformation(origin = {110, -40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput health
      annotation (Placement(transformation(origin = {110, -80}, extent = {{-10, -10}, {10, 10}})));
    QuadrotorModel.PathPlanning.ClimbPath trajectory(gain(k = 1));
  equation
    reference_position = trajectory.position_command;
    yaw_reference = 0;
    z_reference_rate = 0;
    health = if obstacle_margin >= 0 then 1 else 0;
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {80, 80, 80}, fillColor = {248, 248, 248}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 18}, extent = {{-88, -58}, {88, 58}}, fileName = "modelica://QuadrotorModel/Resources/Images/ORIN_NX.png"),
        Text(origin = {0, -76}, extent = {{-90, 15}, {90, -15}}, textString = "ORIN NX", textColor = {80, 80, 80})}));
  end ORINNXMissionComputerModule;

  block AWFFControllerModule
    "Encapsulated AWFF graphical controller, error generation, hover trim, and motor command scaling"
    parameter Real hover_motor_speed_cmd = 53.562090367172424;
    parameter Real legacy_hover_motor_speed_cmd = 13.985413115099604;
    parameter Real motor_command_scale = hover_motor_speed_cmd / legacy_hover_motor_speed_cmd;
    Modelica.Blocks.Interfaces.RealInput reference_position[3]
      annotation (Placement(transformation(origin = {-110, 70}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput position_est[3]
      annotation (Placement(transformation(origin = {-110, 25}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput attitude_est[3]
      annotation (Placement(transformation(origin = {-110, -20}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput yaw_reference
      annotation (Placement(transformation(origin = {-110, -60}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealInput z_reference_rate
      annotation (Placement(transformation(origin = {-110, -90}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput motor_command[4]
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}})));

    Modelica.Blocks.Math.Feedback x_error;
    Modelica.Blocks.Math.Feedback y_error;
    Modelica.Blocks.Math.Feedback z_error;
    AWFF_FullControllerFlatGraphical_Sysblock controller;
    Modelica.Blocks.Sources.Constant hover_u1(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u2(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u3(k = hover_motor_speed_cmd);
    Modelica.Blocks.Sources.Constant hover_u4(k = -hover_motor_speed_cmd);
    Modelica.Blocks.Math.Gain motor1_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor2_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor3_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Gain motor4_delta_scale(k = motor_command_scale);
    Modelica.Blocks.Math.Add motor1_hover_sum;
    Modelica.Blocks.Math.Add motor2_hover_sum;
    Modelica.Blocks.Math.Add motor3_hover_sum;
    Modelica.Blocks.Math.Add motor4_hover_sum;
  equation
    connect(reference_position[1], x_error.u1);
    connect(position_est[1], x_error.u2);
    connect(reference_position[2], y_error.u1);
    connect(position_est[2], y_error.u2);
    connect(reference_position[3], z_error.u1);
    connect(position_est[3], z_error.u2);
    connect(x_error.y, controller.x_error);
    connect(y_error.y, controller.y_error);
    connect(z_error.y, controller.z_error);
    connect(z_reference_rate, controller.z_ref_rate);
    connect(attitude_est[1], controller.roll_mea);
    connect(attitude_est[2], controller.pitch_mea);
    connect(attitude_est[3], controller.yaw_mea);
    connect(yaw_reference, controller.yaw_ref);
    connect(controller.y, motor1_delta_scale.u);
    connect(controller.y1, motor2_delta_scale.u);
    connect(controller.y2, motor3_delta_scale.u);
    connect(controller.y3, motor4_delta_scale.u);
    connect(motor1_delta_scale.y, motor1_hover_sum.u1);
    connect(motor2_delta_scale.y, motor2_hover_sum.u1);
    connect(motor3_delta_scale.y, motor3_hover_sum.u1);
    connect(motor4_delta_scale.y, motor4_hover_sum.u1);
    connect(hover_u1.y, motor1_hover_sum.u2);
    connect(hover_u2.y, motor2_hover_sum.u2);
    connect(hover_u3.y, motor3_hover_sum.u2);
    connect(hover_u4.y, motor4_hover_sum.u2);
    connect(motor1_hover_sum.y, motor_command[1]);
    connect(motor2_hover_sum.y, motor_command[2]);
    connect(motor3_hover_sum.y, motor_command[3]);
    connect(motor4_hover_sum.y, motor_command[4]);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {0, 130, 0}, fillColor = {240, 255, 240}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 45}, {70, -45}}, lineColor = {0, 130, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Text(origin = {0, 5}, extent = {{-65, 25}, {65, -25}}, textString = "AWFF", textColor = {0, 130, 0}),
        Text(origin = {0, -72}, extent = {{-90, 15}, {90, -15}}, textString = "controller", textColor = {0, 130, 0})}));
  end AWFFControllerModule;

  model MotorDriveModule
    "Motor actuator with speed feedback, shown as one top-level motor block"
    parameter Real initial_speed = 53.562090367172424;
    Modelica.Blocks.Interfaces.RealInput command
      annotation (Placement(transformation(origin = {-110, 0}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Blocks.Interfaces.RealOutput speed
      annotation (Placement(transformation(origin = {110, -45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Rotational.Interfaces.Flange_b flange
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-10, -10}, {10, 10}})));
    QuadrotorModel.Electricals.Actuator actuator(dcpm(wMechanical(start = initial_speed)));
    Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor;
  equation
    connect(command, actuator.u);
    connect(actuator.flange_a, flange);
    connect(actuator.flange_a, speedSensor.flange);
    connect(speedSensor.w, speed);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {130, 0, 130}, fillColor = {252, 244, 255}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 16}, extent = {{-88, -58}, {88, 58}}, fileName = "modelica://QuadrotorModel/Resources/Images/motor.png"),
        Text(origin = {0, -76}, extent = {{-80, 15}, {80, -15}}, textString = "%name", textColor = {130, 0, 130})}));
  end MotorDriveModule;

  model Sunray150AirframeSensorModule
    "Sunray150 airframe, rotor flanges, and sensor outputs"
    Modelica.Mechanics.Rotational.Interfaces.Flange_a rotor_flange[4]
      annotation (Placement(transformation(origin = {-110, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput position[3]
      annotation (Placement(transformation(origin = {110, 45}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput attitude[3]
      annotation (Placement(transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}})));
    QuadrotorModel.Mechanics.QuadChassis chassis;
    QuadrotorModel.Sensors.Sensors sensors;
  equation
    connect(rotor_flange[1], chassis.flange_a);
    connect(rotor_flange[2], chassis.flange_a1);
    connect(rotor_flange[3], chassis.flange_a2);
    connect(rotor_flange[4], chassis.flange_a3);
    connect(chassis.frame_a, sensors.frame_a);
    connect(sensors.PosMea, position);
    connect(sensors.AngleMea, attitude);
    annotation (
      Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}), graphics = {
        Rectangle(extent = {{-100, -100}, {100, 100}}, lineColor = {160, 80, 0}, fillColor = {255, 250, 240}, fillPattern = FillPattern.Solid),
        Bitmap(origin = {0, 18}, extent = {{-88, -58}, {88, 58}}, fileName = "modelica://QuadrotorModel/Resources/Images/Sunray150.png"),
        Text(origin = {0, -76}, extent = {{-90, 15}, {90, -15}}, textString = "Sunray150", textColor = {160, 80, 0})}));
  end Sunray150AirframeSensorModule;

  PerceptionInterfaceModule perception
    annotation (Placement(transformation(origin = {-610, -100}, extent = {{-70, -70}, {70, 70}})));
  V6XFlightControllerModule flight_controller
    annotation (Placement(transformation(origin = {-375, -100}, extent = {{-70, -70}, {70, 70}})));
  ORINNXMissionComputerModule mission_computer
    annotation (Placement(transformation(origin = {-610, 120}, extent = {{-70, -70}, {70, 70}})));
  AWFFControllerModule controller(
    hover_motor_speed_cmd = hover_motor_speed_cmd,
    legacy_hover_motor_speed_cmd = legacy_hover_motor_speed_cmd,
    motor_command_scale = motor_command_scale)
    annotation (Placement(transformation(origin = {-120, 40}, extent = {{-80, -80}, {80, 80}})));
  MotorDriveModule motor1(initial_speed = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {170, 165}, extent = {{-36, -36}, {36, 36}})));
  MotorDriveModule motor2(initial_speed = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {170, 55}, extent = {{-36, -36}, {36, 36}})));
  MotorDriveModule motor3(initial_speed = hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {170, -55}, extent = {{-36, -36}, {36, 36}})));
  MotorDriveModule motor4(initial_speed = -hover_motor_speed_cmd)
    annotation (Placement(transformation(origin = {170, -165}, extent = {{-36, -36}, {36, 36}})));
  Sunray150AirframeSensorModule airframe
    annotation (Placement(transformation(origin = {455, 0}, extent = {{-85, -85}, {85, 85}})));

equation
  connect(airframe.position, perception.position_raw)
    annotation (Line(points = {{548, 38}, {585, 38}, {585, -245}, {-745, -245}, {-745, -86}, {-687, -86}}, color = {0, 0, 127}));
  connect(perception.gps_position, flight_controller.gps_position)
    annotation (Line(points = {{-533, -69}, {-452, -69}}, color = {0, 0, 127}));
  connect(perception.local_position, mission_computer.local_position)
    annotation (Line(points = {{-533, -96}, {-500, -96}, {-500, 120}, {-687, 120}}, color = {0, 0, 127}));
  connect(perception.obstacle_margin, mission_computer.obstacle_margin)
    annotation (Line(points = {{-533, -125}, {-485, -125}, {-485, 88}, {-687, 88}}, color = {0, 0, 127}));
  connect(airframe.attitude, flight_controller.attitude_raw)
    annotation (Line(points = {{548, 0}, {570, 0}, {570, -270}, {-470, -270}, {-470, -93}, {-452, -93}}, color = {0, 0, 127}));
  connect(motor1.speed, flight_controller.motor_speed_raw[1])
    annotation (Line(points = {{210, 149}, {250, 149}, {250, -285}, {-470, -285}, {-470, -131}, {-452, -131}}, color = {0, 0, 127}));
  connect(motor2.speed, flight_controller.motor_speed_raw[2])
    annotation (Line(points = {{210, 39}, {260, 39}, {260, -295}, {-460, -295}, {-460, -125}, {-452, -125}}, color = {0, 0, 127}));
  connect(motor3.speed, flight_controller.motor_speed_raw[3])
    annotation (Line(points = {{210, -71}, {270, -71}, {270, -305}, {-450, -305}, {-450, -119}, {-452, -119}}, color = {0, 0, 127}));
  connect(motor4.speed, flight_controller.motor_speed_raw[4])
    annotation (Line(points = {{210, -181}, {280, -181}, {280, -315}, {-440, -315}, {-440, -113}, {-452, -113}}, color = {0, 0, 127}));
  connect(flight_controller.position_est, mission_computer.aircraft_position)
    annotation (Line(points = {{-298, -69}, {-265, -69}, {-265, 148}, {-687, 148}}, color = {0, 0, 127}));
  connect(mission_computer.reference_position, controller.reference_position)
    annotation (Line(points = {{-533, 155}, {-330, 155}, {-330, 96}, {-208, 96}}, color = {0, 0, 127}));
  connect(flight_controller.position_est, controller.position_est)
    annotation (Line(points = {{-298, -69}, {-250, -69}, {-250, 60}, {-208, 60}}, color = {0, 0, 127}));
  connect(flight_controller.attitude_est, controller.attitude_est)
    annotation (Line(points = {{-298, -93}, {-240, -93}, {-240, 24}, {-208, 24}}, color = {0, 0, 127}));
  connect(mission_computer.yaw_reference, controller.yaw_reference)
    annotation (Line(points = {{-533, 124}, {-315, 124}, {-315, -8}, {-208, -8}}, color = {0, 0, 127}));
  connect(mission_computer.z_reference_rate, controller.z_reference_rate)
    annotation (Line(points = {{-533, 92}, {-300, 92}, {-300, -32}, {-208, -32}}, color = {0, 0, 127}));
  connect(controller.motor_command[1], motor1.command)
    annotation (Line(points = {{-32, 40}, {65, 40}, {65, 165}, {130, 165}}, color = {0, 0, 127}));
  connect(controller.motor_command[2], motor2.command)
    annotation (Line(points = {{-32, 40}, {80, 40}, {80, 55}, {130, 55}}, color = {0, 0, 127}));
  connect(controller.motor_command[3], motor3.command)
    annotation (Line(points = {{-32, 40}, {80, 40}, {80, -55}, {130, -55}}, color = {0, 0, 127}));
  connect(controller.motor_command[4], motor4.command)
    annotation (Line(points = {{-32, 40}, {65, 40}, {65, -165}, {130, -165}}, color = {0, 0, 127}));
  connect(motor1.flange, airframe.rotor_flange[1])
    annotation (Line(points = {{210, 181}, {315, 181}, {315, 34}, {362, 34}}, color = {95, 95, 95}, thickness = 0.5));
  connect(motor2.flange, airframe.rotor_flange[2])
    annotation (Line(points = {{210, 71}, {320, 71}, {320, 42}, {362, 42}}, color = {95, 95, 95}, thickness = 0.5));
  connect(motor3.flange, airframe.rotor_flange[3])
    annotation (Line(points = {{210, -39}, {320, -39}, {320, 50}, {362, 50}}, color = {95, 95, 95}, thickness = 0.5));
  connect(motor4.flange, airframe.rotor_flange[4])
    annotation (Line(points = {{210, -149}, {315, -149}, {315, 58}, {362, 58}}, color = {95, 95, 95}, thickness = 0.5));

  annotation(
    Diagram(coordinateSystem(extent = {{-790, -330}, {610, 260}}, grid = {5, 5}), graphics = {
      Rectangle(origin = {-610, 10}, extent = {{-155, 235}, {155, -245}}, lineColor = {0, 0, 127}, pattern = LinePattern.Dash),
      Text(origin = {-610, 245}, extent = {{-130, 15}, {130, -15}}, textString = "mission and perception", textColor = {0, 0, 127}),
      Rectangle(origin = {-375, -100}, extent = {{-95, 105}, {95, -105}}, lineColor = {100, 70, 20}, pattern = LinePattern.Dash),
      Text(origin = {-375, 20}, extent = {{-105, 15}, {105, -15}}, textString = "flight controller", textColor = {100, 70, 20}),
      Rectangle(origin = {-120, 40}, extent = {{-115, 120}, {115, -120}}, lineColor = {0, 130, 0}, pattern = LinePattern.Dash),
      Text(origin = {-120, 175}, extent = {{-110, 15}, {110, -15}}, textString = "control law", textColor = {0, 130, 0}),
      Rectangle(origin = {170, 0}, extent = {{-75, 215}, {75, -215}}, lineColor = {130, 0, 130}, pattern = LinePattern.Dash),
      Text(origin = {170, 230}, extent = {{-95, 15}, {95, -15}}, textString = "motor drives", textColor = {130, 0, 130}),
      Rectangle(origin = {455, 0}, extent = {{-115, 120}, {115, -120}}, lineColor = {160, 80, 0}, pattern = LinePattern.Dash),
      Text(origin = {455, 135}, extent = {{-115, 15}, {115, -15}}, textString = "Sunray150 airframe", textColor = {160, 80, 0})}),
    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 1, Tolerance = 0.0001, Interval = 0.01));
end Sunray150CompleteSystemGraphical_Sysblock;
