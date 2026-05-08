using TyOptimization
fcoff = [2, 1, 3, 2, 1, 3, 4, 1, 3, 2, 1, 3, 2, 1, 1, 2, 1, 3, 2, 2];#运输费用的向量的形式
#线性约束的不等式矩阵
#可以使用repeat函数，对数组进行复制
A = [1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0;
    0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0;
    0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0;
    0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1];
b = [60, 40, 50, 55];
#线性约束的等式矩阵
Aeq = [1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
    0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0;
    0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0;
    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1];
beq = [20, 35, 33, 34, 30]

lb = zeros(20)#决策变量下限
ub = []; #决策变量上限
#可以对比两次的算法结果
#单纯形法
options = optimoptions(:linprog, Algorithm="dual-simplex");
#设置选项
x1, fval, exitflag, output = linprog(fcoff, A, b, Aeq, beq, lb, ub, options)
x1=reshape(x1,4,5)
#内点法

options = optimoptions(:linprog, Algorithm="interior-point-legacy");#设置选项
x2, fval, exitflag, output = linprog(fcoff, A, b, Aeq, beq, lb, ub, options)
x2=reshape(x2,4,5)
#将x的结果转换
#x=reshape(x,4,5)
#将两个x的结果进行比对，得出结论