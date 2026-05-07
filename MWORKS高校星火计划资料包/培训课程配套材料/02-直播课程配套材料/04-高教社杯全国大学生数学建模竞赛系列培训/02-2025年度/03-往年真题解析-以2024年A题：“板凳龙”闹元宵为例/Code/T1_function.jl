# 24A题 第一问的所需函数

# 先算龙头，已知t，得到弧长，计算弧长对应的角度
# 输入时间，输出弧长（龙头）
function L_t(t)
    v = 1 #龙头前进速度，单位m/s
    L = v * t
    return L
end

# 输入弧长，输出对应角度（已知积分上限，求解积分下限）
function θ_L(p, L, θ_up)

    b = p / 2 / pi
    L_fun(θ) = sqrt((b * θ)^2 + b^2)#弧长与角度积分计算公式
    L_fun2 = θ_down -> begin
        target_L_fun = integral(L_fun, θ_down[1], θ_up)[1] - L
        return [target_L_fun]
    end
    θ_down_bound = [0]
    θ = fsolve(L_fun2, θ_down_bound)
    Δθ = θ_up .- θ[1]
    return θ[1][1], Δθ[1]
end

# 输入变化角度，输出r
function r_θ(p, θ)
    b = p / 2 / pi
    r = b * θ
    return r
end

# 输入r,θ,输出x,y
function x_y_r_θ(r, θ)
    x = r .* cos.(θ)
    y = r .* sin.(θ)
    return x, y
end

# 计算后面板凳的把手的x，y位置
function fun_r2_θ2(p, r1, θ1, l)
    # 参数说明
    # r1 = 一个板凳的前把手对应的极径
    # θ1 = 一个板凳的前把手对应的角度，从圆心开始
    # r2 = 一个板凳的后把手对应的极径
    # θ2 = 一个板凳的后把手对应的角度，从圆心开始
    # l = 一个板凳的前后把手之间的距离
    # 设x[1] = r2, x[2] = θ2

    # 已知r1, θ1, l，求解r2，θ2
    fun_r2_θ2_1 = (x, r1, θ1, l) -> begin
        F1 = x[1] - r1 - (p / 2 / pi) * (x[2] - θ1)
        F2 = r1^2 + x[1]^2 - 2 * r1 * x[1] * cos(x[2] - θ1) - l^2
        return [F1, F2]
    end
    fun = x -> fun_r2_θ2_1(x, r1, θ1, l)
    x0 = [r1, θ1]
    x, = fsolve(fun, x0)
    return x[1], x[2]
end

# 现得到每个板凳把手在每个时刻的x，y，求解每个板凳后把手运动的速度v2
function fun_v2(x1, y1, θ1, x2, y2, θ2, v1)
    k1 = (sin(θ1) + θ1 * cos(θ1)) / (cos(θ1) - θ1 * sin(θ1))
    k2 = (sin(θ2) + θ2 * cos(θ2)) / (cos(θ2) - θ2 * sin(θ2))
    k = (y1 - y2) / (x1 - x2)
    alpha = atan(abs((k1 - k) / (1 + k * k1)))
    beta = atan(abs((k2 - k) / (1 + k * k2)))
    v2 = v1 * cos(alpha) / cos(beta)
    return v2
end

function fun_solve_T1(p, t1, dt)

    t = 0:dt:t1
    # 初始化
    length_t = length(t)
    L_head = zeros(length_t) # 龙头的运动长度
    θ_head = zeros(length_t) # 龙头的某时刻下的角度，从16*2*pi开始逐渐减小
    Δθ_head = zeros(length_t)# 龙头的相对运动角度，Delta值
    r_head = zeros(length_t) # 极坐标的位置信息
    x_head = zeros(length_t) # 直角坐标系的位置信息
    y_head = zeros(length_t) # 直角坐标系的位置信息
    θ_up = 16 * 2 * pi       # 龙头位置信息的积分上限

    for i in 1:length_t
        L_head[i] = L_t(t[i])
        θ_head[i], Δθ_head[i] = θ_L(p, L_head[i], θ_up)
        r_head[i] = r_θ(p, θ_head[i])
        x_head[i], y_head[i] = x_y_r_θ(r_head[i], θ_head[i])
    end

    # 构建该节龙身与前一节之间的ds,第224位存储龙尾后把手的位置
    Δs = zeros(224)
    Δs[2] = (341 - 27.5 * 2) / 100
    for Δs_i in 3:224
        Δs[Δs_i] = (220 - 27.5 * 2) / 100
    end

    # 初始化
    θ_dragon = zeros(224, length_t)
    r_dragon = zeros(224, length_t)
    x_dragon = zeros(224, length_t)
    y_dragon = zeros(224, length_t)
    v_dragon = zeros(224, length_t)

    θ_dragon[1, :] = θ_head
    r_dragon[1, :] = r_head
    x_dragon[1, :] = x_head
    y_dragon[1, :] = y_head


    # for t_i in 1:121    #测试用
    for t_i in 1:length_t
        for dz_i in 1:223
            # for dz_i in 1:1  #测试用
            r_dragon[dz_i+1, t_i], θ_dragon[dz_i+1, t_i] = fun_r2_θ2(p, r_dragon[dz_i, t_i], θ_dragon[dz_i, t_i], Δs[dz_i+1])
            x_dragon[dz_i+1, t_i], y_dragon[dz_i+1, t_i] = x_y_r_θ(r_dragon[dz_i+1, t_i], θ_dragon[dz_i+1, t_i])
        end
    end

    v_dragon[1, :] = ones(1, length_t)
    for t_i in 1:length_t
        for dz_i in 1:223
            v_dragon[dz_i+1, t_i] = fun_v2(x_dragon[dz_i, t_i], y_dragon[dz_i, t_i], θ_dragon[dz_i, t_i], x_dragon[dz_i+1, t_i], y_dragon[dz_i+1, t_i], θ_dragon[dz_i+1, t_i], v_dragon[dz_i, t_i])
        end
    end

    x_y_dragon = []
    for i in 1:224
        push!(x_y_dragon, x_dragon[i, :])
        push!(x_y_dragon, y_dragon[i, :])
    end

    file_path1 = "result1_loc.txt"
    file_path2 = "result1_velc.txt"
    fileID1 = fopen(file_path1, "w")
    fileID2 = fopen(file_path2, "w")
    x_y_dragon2 = zeros(448, length_t)
    for i in 1:448
        for ii in 1:length_t
            x_y_dragon2[i, ii] = x_y_dragon[i][ii]
        end
        fprintf(fileID1, "%.6f\t", x_y_dragon2[i, :])
        fprintf(fileID1, "\n")
    end

    for i in 1:224
        fprintf(fileID2, "%.6f\t", v_dragon[i, :])
        fprintf(fileID2, "\n")
    end

    fclose(fileID1)
    fclose(fileID2)

    loc_longtou = zeros(3, 6)
    loc_1 = zeros(3, 6)
    loc_51 = zeros(3, 6)
    loc_101 = zeros(3, 6)
    loc_151 = zeros(3, 6)
    loc_201 = zeros(3, 6)
    loc_longwei = zeros(3, 6)

    # 给出 0 s、60 s、120 s、180 s、240 s、300 s 时，龙头前把手、龙头后面第 1、51、101、151、201 节龙身前把手和龙尾后把手的位置和速度
    para = Int.([1, 61, 121, 181, 241, 301])
    m = 1
    for para_i in para
        loc_longtou[1, m] = x_dragon[1, para_i]
        loc_1[1, m] = x_dragon[2, para_i]
        loc_51[1, m] = x_dragon[52, para_i]
        loc_101[1, m] = x_dragon[102, para_i]
        loc_151[1, m] = x_dragon[152, para_i]
        loc_201[1, m] = x_dragon[202, para_i]
        loc_longwei[1, m] = x_dragon[224, para_i]

        loc_longtou[2, m] = y_dragon[1, para_i]
        loc_1[2, m] = y_dragon[2, para_i]
        loc_51[2, m] = y_dragon[52, para_i]
        loc_101[2, m] = y_dragon[102, para_i]
        loc_151[2, m] = y_dragon[152, para_i]
        loc_201[2, m] = y_dragon[202, para_i]
        loc_longwei[2, m] = y_dragon[224, para_i]

        loc_longtou[3, m] = v_dragon[1, para_i]
        loc_1[3, m] = v_dragon[2, para_i]
        loc_51[3, m] = v_dragon[52, para_i]
        loc_101[3, m] = v_dragon[102, para_i]
        loc_151[3, m] = v_dragon[152, para_i]
        loc_201[3, m] = v_dragon[202, para_i]
        loc_longwei[3, m] = v_dragon[224, para_i]
        m = m + 1
    end
    return θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, loc_longtou, loc_1, loc_51, loc_101, loc_151, loc_201, loc_longwei
end