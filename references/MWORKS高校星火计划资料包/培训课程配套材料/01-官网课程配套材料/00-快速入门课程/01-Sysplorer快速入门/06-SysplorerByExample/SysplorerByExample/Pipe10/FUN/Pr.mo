function Pr "普朗特数"
  annotation(__MWORKS(version="2025b"));
  input Modelica.SIunits.DynamicViscosity eta;
  input Modelica.SIunits.SpecificHeatCapacityAtConstantPressure cp;
  input Modelica.SIunits.ThermalConductivity lambda;
  output Modelica.SIunits.PrandtlNumber Pr;
algorithm
  Pr := eta * cp / lambda;
end Pr;