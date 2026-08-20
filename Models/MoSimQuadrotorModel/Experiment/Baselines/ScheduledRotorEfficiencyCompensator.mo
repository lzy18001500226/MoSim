within MoSimQuadrotorModel.Experiment.Baselines;
model ScheduledRotorEfficiencyCompensator
  "Pre-ESC command compensation for a scheduled, partially effective rotor"

  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};
  parameter Real fault_start_s(unit = "s") = 1e9;
  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;
  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;
  parameter Real minimum_compensable_effectiveness(min = 0, max = 1) = 0.25
    "Do not amplify an unavailable or near-unavailable rotor";
  parameter Real maximum_compensation_scale(min = 1) = 2
    "Bounds the requested speed increase before the ESC limit is applied";

  Modelica.Blocks.Interfaces.RealInput command_in[4]
    "Signed nominal rotor-speed commands" 
    annotation(Placement(
      transformation(origin={-110,0}, extent={{-8,-8},{8,8}}),
      iconTransformation(origin={-100,0}, extent={{-8,-8},{8,8}})));
  Modelica.Blocks.Interfaces.RealOutput command_out[4]
    "Fault-compensated signed rotor-speed commands" 
    annotation(Placement(
      transformation(origin={110,0}, extent={{-8,-8},{8,8}}),
      iconTransformation(origin={100,0}, extent={{-8,-8},{8,8}})));

protected
  Real scheduled_fault_effectiveness[4];
  Real effective_thrust_scale[4];
  Real compensation_scale[4];

equation
  for i in 1:4 loop
    scheduled_fault_effectiveness[i] = if i == fault_rotor_index and time >= fault_start_s then 
      fault_rotor_effectiveness else 1;
    effective_thrust_scale[i] = rotor_effectiveness[i] * scheduled_fault_effectiveness[i];
    compensation_scale[i] = if effective_thrust_scale[i] >= minimum_compensable_effectiveness then 
      min(maximum_compensation_scale, 1 / sqrt(effective_thrust_scale[i])) else 1;
    command_out[i] = compensation_scale[i] * command_in[i];
  end for;

  annotation(
    Icon(coordinateSystem(extent={{-100,-100},{100,100}}), graphics={
      Rectangle(extent={{-100,100},{100,-100}},
        lineColor={130,80,0}, fillColor={255,248,235},
        fillPattern=FillPattern.Solid),
      Text(origin={0,20}, extent={{-88,24},{88,-24}},
        textString="Fault", textColor={130,80,0}),
      Text(origin={0,-20}, extent={{-88,24},{88,-24}},
        textString="Compensator", textColor={130,80,0}),
      Text(origin={0,-68}, extent={{-88,16},{88,-16}},
        textString="4 IN | 4 OUT", textColor={160,110,40})}),
    Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, grid={5,5})),
    __MWORKS(version="26.3.0"));
end ScheduledRotorEfficiencyCompensator;