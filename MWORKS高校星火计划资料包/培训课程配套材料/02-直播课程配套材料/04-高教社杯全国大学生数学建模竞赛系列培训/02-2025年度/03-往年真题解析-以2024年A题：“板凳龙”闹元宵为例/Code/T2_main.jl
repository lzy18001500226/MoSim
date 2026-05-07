using TyOptimization
include("T2_function.jl")

# 通用参数
p = 0.55
t1 = 500
dt = 0.1

θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, t_judge = fun_solve_T2(p, t1, dt);

# A2点在415.5秒碰撞，因此在412.6秒，发生龙头与第九节板凳（龙头算第一节）的碰撞

loc_longtou_2 = zeros(3)
loc_1_2 = zeros(3)
loc_51_2 = zeros(3)
loc_101_2 = zeros(3)
loc_151_2 = zeros(3)
loc_201_2 = zeros(3)
loc_longwei_2 = zeros(3)

loc_longtou_2[1] = x_dragon[1, 4126]
loc_1_2[1] = x_dragon[2, 4126]
loc_51_2[1] = x_dragon[52, 4126]
loc_101_2[1] = x_dragon[102, 4126]
loc_151_2[1] = x_dragon[152, 4126]
loc_201_2[1] = x_dragon[202, 4126]
loc_longwei_2[1] = x_dragon[224, 4126]

loc_longtou_2[2] = y_dragon[1, 4126]
loc_1_2[2] = y_dragon[2, 4126]
loc_51_2[2] = y_dragon[52, 4126]
loc_101_2[2] = y_dragon[102, 4126]
loc_151_2[2] = y_dragon[152, 4126]
loc_201_2[2] = y_dragon[202, 4126]
loc_longwei_2[2] = y_dragon[224, 4126]

loc_longtou_2[3] = v_dragon[1, 4126]
loc_1_2[3] = v_dragon[2, 4126]
loc_51_2[3] = v_dragon[52, 4126]
loc_101_2[3] = v_dragon[102, 4126]
loc_151_2[3] = v_dragon[152, 4126]
loc_201_2[3] = v_dragon[202, 4126]
loc_longwei_2[3] = v_dragon[224, 4126]