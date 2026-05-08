function lambda "由相对粗糙度和雷诺数求摩擦损失系数的分段函数"
  input Modelica.SIunits.ReynoldsNumber Re  "雷诺数";
  input Modelica.SIunits.Diameter d "管道直径";
  input Modelica.SIunits.Height Epsilon = 6e-5 "绝对粗糙度";
  output Real lambda "摩擦损系数";
algorithm
  if Re < 1e-8 then
    lambda := 64 / (1e-8);
    //设定雷诺数最小值，防止雷诺数求解在0附近出错
  elseif Re < 2300 then
    lambda := max(64 / Re, (1.74 - 2 * log10(Epsilon / d)) ^ (-2));
  elseif Re <= 100000.0 then
    lambda := max(0.3164 * Re ^ (-0.25), (1.74 - 2 * log10(Epsilon / d)) ^ (-2));
  elseif Re < 1e6 then
    lambda := max(0.0032 + 0.221 * Re ^ (-0.237), (1.74 - 2 * log10(Epsilon / d)) ^ (-2));
  elseif Re <= 3e6 then
    lambda := max((1.8 * log10(Re) - 1.5) ^ (-2), (1.74 - 2 * log10(Epsilon / d)) ^ (-2));
  else
    lambda := (1.74 - 2 * log10(Epsilon / d)) ^ (-2);
  end if;
  //分段求解，使用 max 函数，确保在这些区域，我们总是选择阻力更大的那个计算值。因为实际的摩擦系数受到粗糙度影响，当粗糙度存在时，摩擦系数不应低于光滑管的情况。max 函数有效地“取了上限”，保证了计算的保守性（即不会低估阻力）。
end lambda;