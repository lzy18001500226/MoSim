using TyOptimization
include("T5_function.jl")


dt = 0.1
v_max = 2
for v_i in 1:0.1:1
    v_max_i = fun_solve_T5(v_i, dt)
    if abs(v_max_i - v_max) < 0.2
        println(v_i)
    end
end

# 龙头最大速度在1.2至1.3之间

# 第二轮搜索
for v_i in 1.2:0.01:1.3
    v_max_i = fun_solve_T5(v_i, dt)
    if abs(v_max_i - v_max) < 0.02
        println(v_i)
    end
end

# 龙头最大速度在1.24至1.25之间
