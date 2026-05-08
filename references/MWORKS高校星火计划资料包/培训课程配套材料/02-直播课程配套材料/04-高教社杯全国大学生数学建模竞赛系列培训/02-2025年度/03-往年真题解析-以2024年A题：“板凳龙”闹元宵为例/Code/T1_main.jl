# 24A题 求解第一问主函数
using TyOptimization
include("T1_function.jl")

p = 0.55
t1 = 300
dt = 1
θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, loc_longtou, loc_1, loc_51, loc_101, loc_151, loc_201, loc_longwei = fun_solve_T1(p, t1, dt)


