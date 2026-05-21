using TyOptimization
fcoff = -[75, 120 ,90, 105]; #目标函数系数向量
A = [9 4 7 5;4 5 6 10;5 10 8 5;3 8 9 7;7 6 4 8]; #约束不等式系数矩阵
b = [3600 ,2900 ,3000, 2800 ,2200]; #约束不等式右端向量
Aeq = []; #约束等式系数矩阵
beq = [];#约束等式右端向量
lb = 50*ones(4);#决策变量下限
ub = []; #决策变量上限
options = optimoptions(:linprog,Algorithm="dual-simplex");#设置选项
x,fval,exitflag,output= linprog(fcoff,A,b,Aeq,beq,lb,ub,options)
fval = - fval