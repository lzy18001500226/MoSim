using TyGlobalOptimization
using TyBase
using TyPlot
function func(x)
    res = dejong5fcn(x)
    return res
end
xi = range(-64, 64, 600)
yi = range(-54, 54, 600)
X, Y = meshgrid2(xi, yi)
A = [reshape(X, :, 1) reshape(Y, :, 1)]
Z = zeros(size(A, 1))
for i = 1:size(A, 1)
    Z[i] = func(A[i, :])
end
Z = reshape(Z, size(X))
surf(X, Y, Z)
# 设定搜索起点和边界
x0 = [0.0, 0.0]
lb = [-64.0, -64.0]
ub = [64.0, 64.0]
# 执行求解
x, fval, output = simulannealbnd(func, x0, lb, ub)
# 打印输出结果
println("最优解 = $x")
println("最优值 = $fval")
