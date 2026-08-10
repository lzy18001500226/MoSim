within MoSimQuadrotorModel.Control.Interfaces;
partial model PartialRotorCommandController
  "Offline ROTOR_COMMAND controller contract"

  Modelica.Blocks.Interfaces.RealInput position_ref[3] 
    annotation(Placement(
      transformation(origin = {-110, 60}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, 60}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealInput velocity_ref[3]
    "Reference translational velocity in m/s" 
    annotation(Placement(
      transformation(origin = {-110, 35}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, 35}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealInput acceleration_ref[3]
    "Reference translational acceleration in m/s2" 
    annotation(Placement(
      transformation(origin = {-110, 10}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, 10}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealInput position_mea[3] 
    annotation(Placement(
      transformation(origin = {-110, -20}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, -20}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealInput velocity_mea[3]
    "Runner-owned filtered translational velocity in m/s" 
    annotation(Placement(
      transformation(origin = {-110, -45}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, -45}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealInput attitude_mea[3] 
    annotation(Placement(
      transformation(origin = {-110, -70}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {-110, -70}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Interfaces.RealOutput rotor_command[4] 
    annotation(Placement(
      transformation(origin = {110, 0}, extent = {{-6, -6}, {6, 6}}),
      iconTransformation(origin = {110, 0}, extent = {{-6, -6}, {6, 6}})));
  annotation(__MWORKS(version="26.3.0"));
end PartialRotorCommandController;