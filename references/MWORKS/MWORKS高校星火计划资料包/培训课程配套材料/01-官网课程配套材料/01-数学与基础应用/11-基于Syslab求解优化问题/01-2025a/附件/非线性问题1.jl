using TyOptimization
objfun = x -> exp(x[1]) * (4 * x[1]^2 + 2 * x[2]^2 + 4 * x[1] * x[2] + 2 * x[2] + 1);
# 约束条件的函数为：
mycon = x -> begin
    c = [1.5 + x[1] * x[2] - x[1] - x[2]; -x[1] * x[2] - 10]
    ceq = []
    return c, ceq
end
x0=[-1; 1];
options = optimoptions(:fmincon,Algorithm="sqp")
x,fval,exitflag,output=fmincon(objfun,x0,[],[],[],[],[],[],mycon,options)
