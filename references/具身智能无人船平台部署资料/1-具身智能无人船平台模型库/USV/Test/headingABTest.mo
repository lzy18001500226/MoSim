model headingABTest
  annotation(__MWORKS(version = "2025a"));
  Real a = 122;
  Real b = 35;
  Real c = 100;
  Real d = 38;
  Real r;
equation
  r = USV.Components.Navigation.Functions.headingAB(a,b,c,d);

end headingABTest;