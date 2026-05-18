model toPercentTest
  annotation(__MWORKS(version = "2025a"));
  Real a = 1;
  Real b = 1;
  Real ra;
  Real rb;
equation
  (ra,rb) = USV.Components.Navigation.Functions.toPercent(a,b);
end toPercentTest;