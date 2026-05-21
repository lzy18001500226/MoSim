using TyGlobalOptimization
#定义问题
function func(x)
  x1, x2 = x
  return -20 * exp(-0.2 * sqrt(0.5 * (x1^2 + x2^2))) - exp(0.5 * (cos(2 * pi * x1) + cos(2 * pi * x2))) + 20 + ℯ
end
lb = [-6.0, -4.0]
ub = [2.0, 4.0]
cons_ueq1(x) = (x[1] - 1)^2 + (x[2] - 0)^2 - 0.5^2 
constraint_ueq = (cons_ueq1,)
#调用 particleswarm 优化该函数
x, fval, output = particleswarm(func, lb, ub, constraint_ueq, ())
#打印优化结果
println("最优解 = $x")
println("最优值 = $fval")

