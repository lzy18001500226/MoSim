using TyOptimization
using TyMath
# include("T1_function.jl")

# 当螺距为1.7m，极径为4.5m时，求解此时的极角θ_r
p = 1.7
r = 4.5
v0 = 1
θ_A = 9 * pi / 1.7

function x_y_r_θ(r, θ)
    x = r .* cos.(θ)
    y = r .* sin.(θ)
    return x, y
end


# 求解切入点A的坐标（-2.711856，-3.591078）
x_A, y_A = x_y_r_θ(r, θ_A)

# 求解此时A点的切线斜率k_AB
function fun_k_A(θ_A)
    k_A = (sin(θ_A) + θ_A * cos(θ_A)) / (cos(θ_A) - θ_A * sin(θ_A))
    return k_A
end
k_A = fun_k_A(θ_A)
k_AB = -1 / k_A

# 求解B点的坐标（x_B，y_B）
f = x -> x^2 + (k_AB * (x - x_A) + y_A)^2 - r^2
fun = f
x0 = 5
x_B, = fzero(fun, x0)
y_B = k_AB * (x_B - x_A) + y_A

# 求解C点的坐标（x_C，y_C）
x_C = -x_A
y_C = -y_A

# 求解AC直线的斜率k_AC
k_AC = y_A / x_A

# 求解AB直线与AC直线的夹角alpha
alpha = atan(abs((k_AC - k_AB) / (1 + k_AC * k_AB)))

# 求解AB与AC的长度
dis_AB = sqrt((x_A - x_B)^2 + (y_A - y_B)^2)
dis_BC = sqrt((x_B - x_C)^2 + (y_B - y_C)^2)

# 求解第二段圆弧半径r_2
r_2 = (dis_AB - dis_BC / tan(2 * alpha)) / 3

# 求解O1的坐标 x[1]为O1的横坐标，x[2]为O1的纵坐标
root2d = x -> begin
    F1 = k_AB * (x[1] - x_A) + y_A - x[2]
    F2 = (x[2] - y_A)^2 + (x[1] - x_A)^2 - (2 * r_2)^2
    return [F1, F2]
end

fun1 = root2d
x0 = [0, 0]
x, = fsolve(fun1, x0)
x_O1 = x[1]
y_O1 = x[2]

# 求解O2的坐标 x1[1]为O2的横坐标，x1[2]为O2的纵坐标
root2d2 = x1 -> begin
    F1_2 = k_AB * (x1[1] - x_C) + y_C - x1[2]
    F2_2 = (x1[2] - y_C)^2 + (x1[1] - x_C)^2 - (r_2)^2
    return [F1_2, F2_2]
end

fun2 = root2d2
x01 = [0, 0]
x1, = fsolve(fun2, x01)
x_O2 = x1[1]
y_O2 = x1[2]

# 求解E的坐标 x2[1]为E的横坐标，x2[2]为E的纵坐标
root2d3 = x2 -> begin
    F1_3 = k_AC * (x2[1] - x_C) + y_C - x2[2]
    F2_3 = (x2[2] - y_C)^2 + (x2[1] - x_C)^2 - (2 * r_2 * cos(alpha))^2
    return [F1_3, F2_3]
end

fun3 = root2d3
x02 = [0, 0]
x2, = fsolve(fun3, x02)
x_E = x2[1]
y_E = x2[2]

# 求解圆弧对应的圆心角phi
ϕ = pi - 2 * alpha

# 龙头到达切入点A的时间（从第一问起点开始计时）,没啥用
b = p / 2 / pi
fun_L(θ) = sqrt((b * θ)^2 + b^2)
L, = integral(fun_L, θ_A, 32pi)

# 龙头到达第一段圆弧结尾的时间t1(从调头开始计时)
t1 = 2 * r_2 * (pi - 2 * alpha) / v0

# 龙头到达第二段圆弧结尾的时间t2(从调头开始计时)
t2 = r_2 * (pi - 2 * alpha) / v0 + t1

dis_OE = sqrt(y_E^2 + x_E^2)

# 设置判断角，
function fun_ϕ(r_2, flag_pre, l)
    # r_2 第二段圆弧半径
    # flag_pre 前把手位于具体哪一段圆弧的标志
    # l 板凳的板长
    D = 9
    d = 1.7

    if flag_pre == 1
        ϕ_judge = 0
    elseif flag_pre == 2 # 第二种情况，当前把手在第一段圆弧上时
        ϕ_judge = acos((8 * r_2^2 - l^2) / 8 * r_2^2)
    elseif flag_pre == 3 # 第三种情况，当前把手在第二段圆弧上时
        ϕ_judge = acos((2 * r_2^2 - l^2) / 2 * r_2^2)
    else # 第四种情况，当前把手在盘出螺线上时
        f_ϕ = ϕ -> (D / 2 + d * ϕ / 2 / pi)^2 + (D / 2)^2 - D * (D / 2 + d / 2 / pi) * cos(ϕ) - l^2
        x0 = -1
        ϕ_judge, = fzero(f_ϕ, x0)
    end
    return ϕ_judge
end

# 计算龙头的各时刻的坐标信息

t = -100:1:101
# 初始化
length_t = length(t)
L_head = zeros(length_t) # 龙头的运动长度
θ_head = zeros(length_t) # 龙头的某时刻下的角度，从θ_A开始逐渐增加

r_head = zeros(length_t) # 极坐标的位置信息
x_head = zeros(length_t) # 直角坐标系的位置信息
y_head = zeros(length_t) # 直角坐标系的位置信息

flag_chair0_con = zeros(length_t)

# 输入弧长，输出对应角度（已知积分下限，求解积分上限）
function θ_L(p, L, θ_down)
    b = p / 2 / pi
    L_fun(θ) = sqrt((b * θ)^2 + b^2)#弧长与角度积分计算公式
    L_fun2 = θ_up -> begin
        target_L_fun = integral(L_fun, θ_down, θ_up[1])[1] - L
        return [target_L_fun]
    end

    θ_up_bound = [0]
    θ = fsolve(L_fun2, θ_up_bound)

    return θ[1][1]
end

function L_t(t)
    v = 1 #龙头前进速度，单位m/s
    L = v * abs(t)
    return L
end
function r_θ(p, θ)
    b = p / 2 / pi
    r = b * θ
    return r
end

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

function zero2(f, a, b, e)

    while b - a >= e
        c = (a + b) / 2
        if f(a) * f(c) < 0
            b = c
        else
            a = c
        end
    end
    return (a + b) / 2
end

d = 1.7
v0 = 1
theta0 = 16.6319611
r = 1.5027088
alpha = 3.0214868
t1 = 9.0808299
t2 = 13.6212449
x1 = -0.7600091
y1 = -1.3057264
x2 = 1.7359325
y2 = 2.4484020
theta1 = 4.0055376
theta2 = 0.8639449


for i in 1:length_t
    if t[i] < 0

        f_theta_head_1 = theta -> theta * sqrt(theta^2 + 1) + log(theta + sqrt(theta^2 + 1))
        f_theta_head_2 = theta -> f_theta_head_1(theta0) - f_theta_head_1(theta) - 4 * v0 * t[i] * pi / d

        θ_head[i] = zero2(f_theta_head_2, theta0, 100, 10^(-8))
        r_head[i] = r_θ(p, θ_head[i])
        x_head[i], y_head[i] = x_y_r_θ(r_head[i], θ_head[i])
        flag_chair0 = 1
    elseif t[i] == 0
        θ_head[i] = theta0
        flag_chair0 = 1
    elseif t[i] < t1
        L_head[i] = v0 * t[i]
        θ_head[i] = L_head[i] / 2 / r_2

        flag_chair0 = 2
    elseif t[i] < t2
        L_head[i] = v0 * (t[i] - t1)
        θ_head[i] = L_head[i] / r_2

        flag_chair0 = 3
    else

        f_theta_head_1 = theta -> theta * sqrt(theta^2 + 1) + log(theta + sqrt(theta^2 + 1))
        f_theta_head_2 = theta -> f_theta_head_1(theta0) - f_theta_head_1(theta) - 4 * v0 * (-t[i] + t2) * pi / d
        θ_head[i] = zero2(f_theta_head_2, theta0, 100, 10^(-8)) - pi

        flag_chair0 = 4
    end
    flag_chair0_con[i] = flag_chair0
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
flag_dragon = zeros(224, length_t)

θ_dragon[1, :] = θ_head
r_dragon[1, :] = r_head
x_dragon[1, :] = x_head
y_dragon[1, :] = y_head
flag_dragon[1, :] = flag_chair0_con

function interation1(theta_last, flag_last, flag_chair)
    # theta_last前把手的对应的极角
    # r_last前把手对应的极径
    # l_last该条板凳的长度
    # flag_last该条板凳前把手所在的位置标志
    # flag_chair板凳的编号

    d = 1.7
    D = 9
    theta0 = 16.6319611
    r = 1.5027088
    alpha = 3.0214868 #两段圆弧的圆心角
    # 根据不同的板凳编号，判断角不同theta_1、theta_2、theta_3
    if flag_chair == 1
        d0 = 3.41 - 0.275 * 2
        theta_1 = 0.9917636
        theta_2 = 2.5168977
        theta_3 = 14.1235657
    else
        d0 = 2.2 - 0.275 * 2
        theta_1 = 0.5561483
        theta_2 = 1.1623551
        theta_3 = 13.8544471
    end

    # 第一段圆弧
    if flag_last == 1

        f_theta0 = theta -> theta^2 + theta_last^2 - 2 * theta * theta_last * cos(theta - theta_last) - 4 * (pi^2) * (d0^2) / (d^2)
        theta = zero2(f_theta0, theta_last, theta_last + pi / 2, 10^(-8))
        flag = 1

    elseif flag_last == 2
        if theta_last < theta_1
            b = sqrt(2 - 2cos(theta_last)) * r * 2
            beta = (alpha - theta_last) / 2
            l = sqrt(b^2 + D^2 / 4 - b * D * cos(beta))
            gamma = asin(b * sin(beta) / l)

            f_theta = theta -> l^2 + d^2 * theta^2 / (4 * pi^2) - d * l * theta * cos(theta - theta0 + gamma) / pi - d0^2
            theta = zero2(f_theta, theta0, theta0 + pi / 2, 10^(-8))
            flag = 1
        else
            theta = theta_last - theta_1
            flag = 2
        end
    elseif flag_last == 3
        if theta_last < theta_2
            a = sqrt(10 - 6 * cos(theta_last)) * r
            phi = acos((4 * r^2 + a^2 - d0^2) / (4 * a * r))
            beta = asin(r * sin(theta_last) / a)
            theta = alpha - phi + beta
            flag = 2
        else
            theta = theta_last - theta_2
            flag = 3
        end
    else
        if theta_last < theta_3
            p = d * (theta_last + pi) / (2 * pi)
            a = sqrt(p^2 + D^2 / 4 - p * D * cos(theta_last - theta0 + pi))
            beta = asin(p * sin(theta_last - theta0 + pi) / a)
            gamma = beta - (pi - alpha) / 2
            b = sqrt(a^2 + r^2 - 2 * a * r * cos(gamma))
            sigma = asin(a * sin(gamma) / b)
            phi = acos((r^2 + b^2 - d0^2) / (2 * r * b))
            theta = alpha - phi + sigma
            flag = 3
        else
            a = theta_last - pi / 2
            b = theta_last

            f_theta1 = theta -> (theta + pi)^2 + (theta_last + pi)^2 - 2 * (theta + pi) * (theta_last + pi) * cos((theta + pi) - (theta_last + pi)) - 4 * pi^2 * (d0^2) / (d^2)
            theta = zero2(f_theta1, a, b, 10^(-8))

            flag = 4

        end
    end
    return theta, flag
end

for t_i in 1:length_t
    for dz_i in 1:223
        theta_last = θ_dragon[dz_i, t_i]
        flag_last = flag_dragon[dz_i, t_i]
        theta, flag = interation1(theta_last, flag_last, dz_i)

        θ_dragon[dz_i+1, t_i] = theta
        flag_dragon[dz_i+1, t_i] = flag
    end
end

for t_i in 1:length_t
    for dz_i in 1:224
        theta = θ_dragon[dz_i, t_i]
        flag = flag_dragon[dz_i, t_i]
        if flag == 1
            p = d * theta / (2 * pi)
            x = p * cos(theta)
            y = p * sin(theta)
        elseif flag == 2
            x = x1 + 2 * r * cos(theta1 - theta)
            y = y1 + 2 * r * sin(theta1 - theta)
        elseif flag == 3
            x = x2 + r * cos(theta2 + theta - alpha)
            y = y2 + r * sin(theta2 + theta - alpha)
        else
            p = d * (theta + pi) / (2 * pi)
            x = p * cos(theta)
            y = p * sin(theta)
        end
        x_dragon[dz_i, t_i] = x
        y_dragon[dz_i, t_i] = y
    end
end

fun_v_k = theta -> (sin(theta) + theta * cos(theta)) / (cos(theta) - theta * sin(theta))

v_dragon[1, :] = ones(1, length_t)

function iteration_vel(v_last, flag_last, flag, theta_last, theta, x_last, y_last, x, y)
    x1 = -0.7600091
    y1 = -1.3057264
    x2 = 1.7359325
    y2 = 2.4484020
    k_chair = (y_last - y) / (x_last - x)
    v = -1
    if flag_last == 1 && flag == 1
        k_v_last = fun_v_k(theta_last)
        k_v = fun_v_k(theta)
    elseif flag_last == 2 && flag == 1
        k_v_last = -(x_last - x1) / (y_last - y1)
        k_v = fun_v_k(theta)
    elseif flag_last == 2 && flag == 2
        v = v_last
    elseif flag_last == 3 && flag == 2
        k_v_last = -(x_last - x2) / (y_last - y2)
        k_v = -(x - x1) / (y - y1)
    elseif flag_last == 3 && flag == 3
        v = v_last
    elseif flag_last == 4 && flag == 3
        theta_last = theta_last + pi
        k_v_last = fun_v_k(theta_last)
        k_v = -(x - x2) / (y - y2)
    else
        theta_last = theta_last + pi
        theta = theta + pi
        k_v_last = fun_v_k(theta_last)
        k_v = fun_v_k(theta)
    end

    if v == -1
        alpha1 = atan(abs((k_v_last - k_chair) / (1 + k_v_last * k_chair)))
        alpha2 = atan(abs((k_v - k_chair) / (1 + k_v * k_chair)))
        v = v_last * cos(alpha1) / cos(alpha2)
    end
    return v
end

for t_i in 1:length_t
    for dz_i in 1:223
        flag_last = flag_dragon[dz_i, t_i]
        theta_last = θ_dragon[dz_i, t_i]
        flag = flag_dragon[dz_i+1, t_i]
        theta = θ_dragon[dz_i+1, t_i]
        x_last = x_dragon[dz_i, t_i]
        y_last = y_dragon[dz_i, t_i]
        x = x_dragon[dz_i+1, t_i]
        y = y_dragon[dz_i+1, t_i]
        v_last = v_dragon[dz_i, t_i]
        v = iteration_vel(v_last, flag_last, flag, theta_last, theta, x_last, y_last, x, y)
        v_dragon[dz_i+1, t_i] = v
    end
end


