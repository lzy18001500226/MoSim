model calcGPSDistanceTest
  annotation(__MWORKS(version = "2025a"));
  Real a = 122.3514;
  Real b = 35.3514;
  Real c = 122.3564;
  Real d = 35.3564;
  Real r;
equation
  r = USV.Components.Navigation.Functions.calcGPSDistance(a,b,c,d);

end calcGPSDistanceTest;