model EvaluationTest1
  annotation(__MWORKS(version = "2025b"));
  Real yf;
  Real yp;
equation
  yf = Polynomial(time, {1, -2, 2});
  yp = time ^ 2 - 2 * time + 2;
end EvaluationTest1;