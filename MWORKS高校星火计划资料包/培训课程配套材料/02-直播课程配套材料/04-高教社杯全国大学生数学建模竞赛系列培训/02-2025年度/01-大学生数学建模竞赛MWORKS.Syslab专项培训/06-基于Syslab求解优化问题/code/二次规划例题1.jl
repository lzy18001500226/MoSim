using TyOptimization
using TyMath
H = [1 -1; -1 2]
f = [-2, -6]
A = [1 1; -1 2; 2 1]
b = [2, 2, 3]
lb=[0,0]
#options = optimoptions(:quadprog,Algorithm="active-set")
x,fval,exitflag,output,lambda = quadprog(H,f,A,b,[],[],lb,[],[])
