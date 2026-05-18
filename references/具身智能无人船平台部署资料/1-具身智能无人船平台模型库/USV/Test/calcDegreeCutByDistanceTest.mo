model calcDegreeCutByDistanceTest
  annotation(__MWORKS(version = "2025a"));
  Real a = 100;
  Real ra;
equation
  ra = USV.Components.Navigation.Functions.calcDegreeCutByDistance(a);
end calcDegreeCutByDistanceTest;