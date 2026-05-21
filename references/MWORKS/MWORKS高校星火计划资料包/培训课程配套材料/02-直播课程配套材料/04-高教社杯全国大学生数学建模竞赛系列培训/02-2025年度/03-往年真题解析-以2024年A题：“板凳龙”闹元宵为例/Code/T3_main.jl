using TyOptimization
include("T2_function.jl")

# p = 0.55
t1 = 500
dt = 0.5
D = 9

#第一轮求解-粗略求解

p1 = 0.4:0.02:0.5
length_p1 = length(p1)

for p_i in 1:length_p1
    θ_0 = D * pi / p1[p_i]
    θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, t_judge = fun_solve_T2(p1[p_i], t1, dt)
    if abs(θ_dragon[1, t_judge] - θ_0) < 5
        println(p1[p_i])
    end
end

# 得到 螺距在0.44-0.46之间

#第二轮求解-精细求解

p2 = 0.44:0.005:0.46
length_p2 = length(p2)

p2_final = 0

for p_i in 1:length_p2
    global p2_final
    θ_0 = D * pi / p2[p_i]
    θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, t_judge = fun_solve_T2(p2[p_i], t1, dt)
    if abs(θ_dragon[1, t_judge] - θ_0) < 2
        println(p2[p_i])
    end
end




