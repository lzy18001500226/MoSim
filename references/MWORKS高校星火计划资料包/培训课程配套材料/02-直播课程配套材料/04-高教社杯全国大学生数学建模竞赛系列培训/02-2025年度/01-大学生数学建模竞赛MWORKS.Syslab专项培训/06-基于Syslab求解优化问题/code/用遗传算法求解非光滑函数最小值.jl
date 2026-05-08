using TyGlobalOptimization
using TyPlot
using TyBase
xi = range(-6, 2, 300)
yi = range(-4, 4, 300)
X, Y = meshgrid2(xi, yi)
A = [reshape(X, :, 1) reshape(Y, :, 1)]
Z = ps_example(A)
Z = reshape(Z, size(X))
surf(X, Y, Z)
title("ps_example")
ylabel("x(1)")
xlabel("x(2)")
#定义待求解问题
function func(p)
    x1, x2 = p
    return ps_example([x1 x2])[1]
end
lb = [-6.0, -4.0]
ub = [2.0, 4.0]


#执行求解
x, fval, output = ga(func, lb, ub)

#打印优化结果
println("最优解 = $x")
println("最优值 = $fval")
