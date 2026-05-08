using TyBase
using TyMath
using TyOptimization
using TyPlot
include("f1.jl")
include("f2.jl")

# 锚链长度 m
L0 = 22.05
# Ⅱ型锚链每米的质量 kg/m
m0 = 7
# 重物球质量 kg
m = 1200
# 重力加速度 m/s^2
g = 9.8
# 钢桶质量 kg
m1 = 100
# 钢桶长度 m
L1 = 1
# 钢桶直径 m
d1 = 0.3
# 钢管质量 kg
m2 = 10
# 浮标质量 kg
m3 = 1000
# 浮标直径 m
d3 = 2
# 浮标高度 m
h3 = 2
# 海水深度 m
H_water = 18
# 海面风速 m/s
v_wind = 12
# 材质密度 kg/m^3
ρ = 7800
# 海水密度 kg/m^3
ρ_water = 1025


# 锚链每米体积
v0 = m0 / ρ
# 锚链每米重力
ω_0 = m0 * g - ρ_water * g * v0
# 重物球体积
v = m / ρ
# 重物球重力
ω = m * g - ρ_water * g * v
# 钢桶体积
v1 = L1 * pi * d1^2 / 4
# 钢桶重力
ω_1 = m1 * g - ρ_water * g * v1
# 钢管体积
v2 = m2 / ρ
# 钢管重力
ω_2 = m2 * g - ρ_water * g * v2

flag_L0 = true
s1 = 0
while flag_L0
    # 锚链全部拉起时浮标承载重力
    W_f = m3 * g + L0 * ω_0 + ω + ω_1 + ω_2 * 4
    # 浮标吃水深度
    H_ω = W_f / ((pi * d3^2 / 4 * ρ_water) * g)
    # 风作用在浮标上的力
    F = 0.625 * d3 * (h3 - H_ω) * v_wind^2

    # 第一段悬垂链方程
    a1 = F / ω_0

    # 第二段悬垂链方程
    # 钢桶底端重力
    W_m0m = L0 * ω_0 + ω
    # 钢桶底端角度
    θ1 = atan(W_m0m / F)
    a2 = F / ω_1

    # 第三段悬垂链方程
    # 钢管底端重力
    W_m0mm1 = L0 * ω_0 + ω + ω_1
    # 钢管底端角度
    θ2 = atan(W_m0mm1 / F)
    a3 = F / ω_2

    # 根据三悬链物理含义求解未知数
    fun = x -> begin
        F1 = a3 * cosh((x[3] - x[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) + a2 * cosh((x[2] - x[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) + a1 * (cosh(x[1] / a1) - 1) - a2 / cos(θ1) - a3 / cos(θ2) - 18 + H_ω
        F2 = a2 * sinh((x[2] - x[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) - a2 * sinh(log((1 + sin(θ1)) / cos(θ1))) - 1
        F3 = a3 * sinh((x[3] - x[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) - a3 * sinh(log((1 + sin(θ2)) / cos(θ2))) - 4
        return [F1, F2, F3]
    end

    x0 = [L0, L0 + 1, L0 + 5]
    global x, = fsolve(fun, x0)

    # 验证第一段悬链弧长，不满足重新迭代
    global s1 = a1 * sinh(x[1] / a1)
    if abs(s1 - L0) > 0.001
        global L0 = s1
    else
        global flag_L0 = false
    end
end

# 锚链部分拉起时浮标承载重力
W_f = m3 * g + L0 * ω_0 + ω + ω_1 + ω_2 * 4
# 浮标吃水深度
H_ω = W_f / ((pi * d3^2 / 4 * ρ_water) * g)
# 风作用在浮标上的力
F = 0.625 * d3 * (h3 - H_ω) * v_wind^2
# 第二段悬垂链方程
# 钢桶中部所受重力
W_m0m = L0 * ω_0 + ω + 0.5* ω_1
# 钢桶中部倾斜角度
θ1 = atan(W_m0m / F)
β1 = 90 - atan(W_m0m / F) / pi * 180

# 第三段悬垂链方程
# 钢管中部所受重力
W_m0mm1 = L0 * ω_0 + ω + ω_1 + 0.5 * ω_2
# 钢管中部倾斜角度
θ2 = atan(W_m0mm1 / F)
β2 = 90 - atan(W_m0mm1 / F) / pi * 180
β3 = 90 - atan((W_m0mm1 + ω_2) / F) / pi * 180
β4 = 90 - atan((W_m0mm1 + ω_2 * 2) / F) / pi * 180
β5 = 90 - atan((W_m0mm1 + ω_2 * 3) / F) / pi * 180
# 浮标半径
r = 22.05 - L0 + x[3]
# 结果汇总
Q1_12_ans = [β1, β2, β3, β4, β5, H_ω, r]


# 绘图
a1 = F / ω_0
a2 = F / ω_1
a3 = F / ω_2
y = zeros(length(0:0.01:x[3]), 1)
i = 1
xx = 0:0.01:x[3]
for xx = 0:0.01:x[3]
    if xx < x[1]
        global y[i] = f1(xx, a1)
    elseif xx < x[2]
        global y[i] = f2(xx, x[1], f1(x[1], a1), a2, θ1)
    else
        global y[i] = f2(xx, x[2], f2(x[2], x[1], f1(x[1], a1), a2, θ1), a3, θ2)
    end
    global i = i + 1
end
plot(xx, y)

#########################
###### 计算临界风速 ######
#########################
# 锚链全长
L0_2 = 22.05
# 锚链全部拉起时浮标承载重力
W_f_2 = m3 * g + L0_2 * ω_0 + ω + ω_1 + ω_2 * 4
# 浮标吃水深度
H_ω_2 = W_f_2 / ((pi * d3^2 / 4 * ρ_water) * g)
# 初始风速
v_wind_2 = 12
flag = true
while flag
    # 风作用在浮标上的力
    local F = 0.625 * d3 * (h3 - H_ω_2) * v_wind_2^2
    local a1 = F / ω_0
    local a2 = F / ω_1
    local a3 = F / ω_2
    # 钢桶底端所受重力
    local W_m0m = L0_2 * ω_0 + ω
    # 钢桶底端倾斜角度
    local θ1 = atan(W_m0m / F)
    # 钢管底端所受重力
    local W_m0mm1 = L0_2 * ω_0 + ω + ω_1
    # 钢管底端倾斜角度
    local θ2 = atan(W_m0mm1 / F)

    fun2 = x_2 -> begin
        F1 = a1 * sinh(x_2[1]/a1) - L0_2
        F2 = a2 * sinh((x_2[2] - x_2[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) - a2 * sinh(log((1 + sin(θ1)) / cos(θ1))) - 1
        F3 = a3 * sinh((x_2[3] - x_2[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) - a3 * sinh(log((1 + sin(θ2)) / cos(θ2))) - 4
        return [F1, F2, F3]
    end

    x0 = [L0, L0 + 1, L0 + 5]
    global x_2, = fsolve(fun2, x0)

    global y_2 = f2(x_2[3], x_2[2], f2(x_2[2], x_2[1], f1(x_2[1], a1), a2, θ1), a3, θ2)
    if abs(y_2 + H_ω_2 - 18) < 0.001
        global flag = false
    else
        global v_wind_2 = v_wind_2 + 0.001
    end
end

###########################################################################
# 当风速为24m/s时的节点位置x_3[1]、x_3[2]、x_3[3]，锚链与海床夹角x_3[4]/pi*180
# 风速为36m/s时，修改下面的v_wind_3 = 36 即可
###########################################################################
fun3 = x_3 -> begin
    global v_wind_3 = 24
    # 浮标吃水深度
    H_ω_3 = (m3 * g + L0_2 * ω_0 + ω + ω_1 + ω_2 * 4 + 0.625 * d3 * h3 * v_wind_3^2 * tan(x_3[4]))/(((pi * d3^2 / 4 * ρ_water) * g) + 0.625 * d3 * v_wind_3^2 * tan(x_3[4]))
    F = 0.625 * d3 * (h3 - H_ω_3) * v_wind_3^2
    a1 = F / ω_0
    a2 = F / ω_1
    a3 = F / ω_2
    # 钢桶末端重力
    W_m0m_3 = L0_2 * ω_0 + ω + 0.625 * d3 * (h3 - H_ω_3) * v_wind_3^2 * tan(x_3[4])
    # 钢桶倾斜角度
    θ1 = atan(W_m0m_3 / F)
    # 钢管末端重力
    W_m0mm1_3 = L0_2 * ω_0 + ω + ω_1 + 0.625 * d3 * (h3 - H_ω_3) * v_wind_3^2 * tan(x_3[4])
    # 钢管倾斜角度
    θ2 = atan(W_m0mm1_3 / F)


    F1 = a1 * sinh((x_3[1]) / a1 + log((1 + sin(x_3[4])) / cos(x_3[4]))) - a1 * sinh(log((1 + sin(x_3[4])) / cos(x_3[4]))) - L0_2
    F2 = a2 * sinh((x_3[2] - x_3[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) - a2 * sinh(log((1 + sin(θ1)) / cos(θ1))) - 1
    F3 = a3 * sinh((x_3[3] - x_3[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) - a3 * sinh(log((1 + sin(θ2)) / cos(θ2))) - 4
    F4 = a3 * cosh((x_3[3] - x_3[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) + a2 * cosh((x_3[2] - x_3[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) + a1 * cosh((x_3[1] / a1) + log((1 + sin(x_3[4]))/cos(x_3[4]))) - a1 / cos(x_3[4]) - a2 / cos(θ1) - a3 / cos(θ2) - 18 + H_ω_3
    return [F1, F2, F3, F4]
end

x0 = [L0_2, L0_2 + 1, L0_2 + 5, 0]
x_3, = fsolve(fun3, x0)

H_ω_3 = (m3 * g + L0_2 * ω_0 + ω + ω_1 + ω_2 * 4 + 0.625 * d3 * h3 * v_wind_3^2 * tan(x_3[4]))/(((pi * d3^2 / 4 * ρ_water) * g) + 0.625 * d3 * v_wind_3^2 * tan(x_3[4]))
F_3 = 0.625 * d3 * (h3 - H_ω_3) * v_wind_3^2
a1 = F_3 / ω_0
a2 = F_3 / ω_1
a3 = F_3 / ω_2
# 钢桶中部所受重力
W_m0m_3 = L0_2 * ω_0 + ω + 0.5 * ω_1 + F_3 * tan(x_3[4]) 
# m锚链与海床夹角
θ0_3 = x_3[end]/pi*180
# 浮标游动区域半径
r_3 = x_3[3]
# 钢桶中部倾斜角度
θ1_3 = atan(W_m0m_3 / F_3)
β1_3 = 90 - atan(W_m0m_3 / F_3) / pi * 180
# 钢管中部所受重力
W_m0mm1_3 = L0_2 * ω_0 + ω + ω_1 + 0.5 * ω_2 + F_3 * tan(x_3[4]) 
# 钢管中部倾斜角度
θ2_3 = atan(W_m0mm1_3 / F_3)
β2_3 = 90 - atan(W_m0mm1_3 / F_3) / pi * 180
β3_3 = 90 - atan((W_m0mm1_3 + ω_2) / F_3) / pi * 180
β4_3 = 90 - atan((W_m0mm1_3 + ω_2 * 2) / F_3) / pi * 180
β5_3 = 90 - atan((W_m0mm1_3 + ω_2 * 3) / F_3) / pi * 180
# 结果汇总
Q1_24_ans = [β1_3, β2_3, β3_3, β4_3, β5_3, H_ω_3, r_3, θ0_3]

# 绘图
y = zeros(length(0:0.01:x_3[3]), 1)
i = 1
xx = 0:0.01:x_3[3]
for xx = 0:0.01:x_3[3]
    if xx < x_3[1]
        global y[i] = f2(xx, 0, 0, a1, θ0_3/180*pi)
    elseif xx < x_3[2]
        global y[i] = f2(xx, x_3[1], f2(x_3[1], 0, 0, a1, θ0_3/180*pi), a2, θ1_3)
    else
        global y[i] = f2(xx, x_3[2], f2(x_3[2], x_3[1], f2(x_3[1], 0, 0, a1, θ0_3/180*pi), a2, θ1_3), a3, θ2_3)
    end
    global i = i + 1
end
figure()
plot(xx, y)

###########################################################################
# 风速为36m/s时，计算合适的重物球质量
###########################################################################
# 锚链全长
L0_3 = 22.05
# 重物球质量
m_4 = 1200
m_4_flag = true
while m_4_flag
    # 重物球体积
    v_4 = m_4 / ρ
    # 重物球重力
    global ω_4 = m_4 * g - ρ_water * g * v_4
    root2d = x_4 -> begin
        global v_wind_4 = 36
        # 浮标吃水深度
        H_ω_4 = (m3 * g + L0_3 * ω_0 + ω_4 + ω_1 + ω_2 * 4 + 0.625 * d3 * h3 * v_wind_4^2 * tan(x_4[4]))/(((pi * d3^2 / 4 * ρ_water) * g) + 0.625 * d3 * v_wind_4^2 * tan(x_4[4]))
        F = 0.625 * d3 * (h3 - H_ω_4) * v_wind_4^2
        a1 = F / ω_0
        a2 = F / ω_1
        a3 = F / ω_2
        # 钢桶末端重力
        W_m0m_4 = L0_3 * ω_0 + ω_4 + 0.625 * d3 * (h3 - H_ω_4) * v_wind_4^2 * tan(x_4[4])
        # 钢桶倾斜角度
        θ1 = atan(W_m0m_4 / F)
        # 钢管末端重力
        W_m0mm1_4 = L0_3 * ω_0 + ω_4 + ω_1 + 0.625 * d3 * (h3 - H_ω_4) * v_wind_4^2 * tan(x_4[4])
        # 钢管倾斜角度
        θ2 = atan(W_m0mm1_4 / F)


        F1 = a1 * sinh((x_4[1]) / a1 + log((1 + sin(x_4[4])) / cos(x_4[4]))) - a1 * sinh(log((1 + sin(x_4[4])) / cos(x_4[4]))) - L0_3
        F2 = a2 * sinh((x_4[2] - x_4[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) - a2 * sinh(log((1 + sin(θ1)) / cos(θ1))) - 1
        F3 = a3 * sinh((x_4[3] - x_4[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) - a3 * sinh(log((1 + sin(θ2)) / cos(θ2))) - 4
        F4 = a3 * cosh((x_4[3] - x_4[2]) / a3 + log((1 + sin(θ2)) / cos(θ2))) + a2 * cosh((x_4[2] - x_4[1]) / a2 + log((1 + sin(θ1)) / cos(θ1))) + a1 * cosh((x_4[1] / a1) + log((1 + sin(x_4[4]))/cos(x_4[4]))) - a1 / cos(x_4[4]) - a2 / cos(θ1) - a3 / cos(θ2) - 18 + H_ω_4
        return [F1, F2, F3, F4]
    end

    fun = root2d
    x0 = [L0_3, L0_3 + 1, L0_3 + 5, 0]
    global x_4, = fsolve(fun, x0)

    # m锚链与海床夹角
    global θ0_4 = x_4[end]/pi*180

    if θ0_4 < 16
        global m_4_flag = false
    else
        global m_4 = m_4 + 0.1
    end
end
H_ω_4 = (m3 * g + L0_3 * ω_0 + ω_4 + ω_1 + ω_2 * 4 + 0.625 * d3 * h3 * v_wind_4^2 * tan(x_4[4]))/(((pi * d3^2 / 4 * ρ_water) * g) + 0.625 * d3 * v_wind_4^2 * tan(x_4[4]))
F_4 = 0.625 * d3 * (h3 - H_ω_4) * v_wind_4^2
a1 = F_4 / ω_0
a2 = F_4 / ω_1
a3 = F_4 / ω_2
# 钢桶末端重力
W_m0m_4 = L0_3 * ω_0 + ω_4 + 0.5 * ω_1 + F_4 * tan(x_4[4])
# 浮标游动区域半径
r_4 = x_4[3]
# 钢桶倾斜角度
θ1_4 = atan(W_m0m_4 / F_4)
β1_4 = 90 - atan(W_m0m_4 / F_4) / pi * 180
# 钢管末端重力
W_m0mm1_4 = L0_3 * ω_0 + ω_4 + ω_1 + 0.5 * ω_2 + F_4 * tan(x_4[4])
# 钢管倾斜角度
θ2_4 = atan(W_m0mm1_4 / F_4)
β2_4 = 90 - atan(W_m0mm1_4 / F_4) / pi * 180
β3_4 = 90 - atan((W_m0mm1_4 + ω_2) / F_4) / pi * 180
β4_4 = 90 - atan((W_m0mm1_4 + ω_2 * 2) / F_4) / pi * 180
β5_4 = 90 - atan((W_m0mm1_4 + ω_2 * 3) / F_4) / pi * 180
# 答案汇总
Q2_ans = [β1_4, β2_4, β3_4, β4_4, β5_4, H_ω_4, r_4, θ0_4, m_4]

# 绘图
y = zeros(length(0:0.01:x_4[3]), 1)
i = 1
xx = 0:0.01:x_4[3]
for xx = 0:0.01:x_4[3]
    if xx < x_4[1]
        global y[i] = f2(xx, 0, 0, a1, θ0_4/180*pi)
    elseif xx < x_4[2]
        global y[i] = f2(xx, x_4[1], f2(x_4[1], 0, 0, a1, θ0_4/180*pi), a2, θ1_4)
    else
        global y[i] = f2(xx, x_4[2], f2(x_4[2], x_4[1], f2(x_4[1], 0, 0, a1, θ0_4/180*pi), a2, θ1_4), a3, θ2_3)
    end
    global i = i + 1
end
figure()
plot(xx, y)