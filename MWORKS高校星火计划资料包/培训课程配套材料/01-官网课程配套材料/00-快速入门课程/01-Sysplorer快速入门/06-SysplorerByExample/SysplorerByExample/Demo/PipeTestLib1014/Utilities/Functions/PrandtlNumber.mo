function PrandtlNumber "Pr = eta*cp/lambda"

  input Modelica.SIunits.DynamicViscosity eta;
  input Modelica.SIunits.SpecificHeatCapacityAtConstantPressure cp;
  input Modelica.SIunits.ThermalConductivity lambda;
  output Modelica.SIunits.PrandtlNumber Pr;
algorithm
  Pr := eta * cp / lambda;
  annotation (smoothOrder = 5, Documentation(revisions = "<html>
<hr>
</html>"));
end PrandtlNumber;