using TyGlobalOptimization
# 目标函数
f1(x) = sin(x[1])
f2(x) = cos(x[1])
f = x-> [f1(x), f2(x)]
# 目标个数
nobj = 2
# 不等式和等式约束
constraint_ueq = ()
constraint_eq = ()
objcon = packfcn(f, constraint_ueq, constraint_eq)
lb = zeros(1)      # 向量，元素个数代表决策变量维数
ub = ones(1)*2*pi
# p_m —— 突变概率
options = gamultiobj_options(p_m=0.1, draw_picture=true)   # 绘制帕累托前沿图
#执行求解 ：PS —— 帕累托解集，PF —— 帕累托前沿
PS, PF, output = gamultiobj(objcon, nobj, lb, ub, options)
