model DAEexample "DAE系统示例方程"
  parameter Real x0 = 0.9;
  Real x;
  Real y;
initial equation
  x = x0;
equation
  der(y) + (1 + 0.5 * sin(y)) * der(x) = sin(time);
  x - y = exp(-0.9 * x) * cos(y);
end DAEexample;