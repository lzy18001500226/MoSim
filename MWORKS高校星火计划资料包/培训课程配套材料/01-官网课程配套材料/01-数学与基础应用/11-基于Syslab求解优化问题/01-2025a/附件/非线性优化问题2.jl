using TyOptimization
function f1(x)
    y = (x^5 + x^3 + x^2 - 1) / (exp(x^2) + sin(-x))
    return y
end
X, fval, exitflag, output = fminbnd(f1, -2, 2)
