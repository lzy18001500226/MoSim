function Polynomial "多项式计算-定义函数的关键词function"
  annotation(__MWORKS(version = "2025b"));
  input Real x "Independent variable";
  input Real c[:] "Polynomial coefficients多项式系数";
  output Real y "Computed polynomial value";
protected
//定义禁止外部访问的前缀
  Integer n = size(c, 1);
algorithm
  y := c[1];
  for i in 2:n loop
    y := y * x + c[i];
  end for;
end Polynomial;