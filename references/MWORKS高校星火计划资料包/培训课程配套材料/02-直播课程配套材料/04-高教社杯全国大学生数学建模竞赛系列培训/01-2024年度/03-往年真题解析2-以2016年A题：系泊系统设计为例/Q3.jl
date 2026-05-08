using TyBase
using TyMath
using TyOptimization
using TyPlot
include("f1.jl")
include("f2.jl")

# 锚链长度 m
L0 = 21.78
# Ⅴ型锚链每米的质量 kg/m
m0 = 28.12
# 重物球质量 kg
m = 4460
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
H_water = 20
# 海面风速 m/s
v_wind = 36
# 海水速度 m/s
v_water = 1.5
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
# Ⅴ型锚链每米水流作用力 N
u5 = 57.01
# 钢桶每米水流作用力 N
h1 = 252.45
# 钢管每米水流作用力 N
h2 = 42.08
# 重物球水流作用力 N
h_3 = 374 * pi * ((3 * m) / (4 * ρ * pi))^(2 / 3) * v_water^2
# 浮标每米水流作用力 N
h0 = 1683

γ = 0 / 180 * pi
flag_H_ω_0 = true
H_ω_0 = 1

while flag_H_ω_0
    # 风作用在浮标上的力
    global F = 0.625 * d3 * (h3 - H_ω_0) * v_wind^2
    # 锚点水平力
    global H_x = u5 * (H_water - H_ω_0 - 5) + h_3 + h1 + h2 * 4 + h0 * H_ω_0 + F
    # 锚点竖直力
    global H_y = H_x * tan(γ)
    # 决定吃水深度的竖直力
    W_f = H_y + m3 * g + L0 * ω_0 + ω + ω_1 + ω_2 * 4
    # 浮标吃水深度
    global H_ω = W_f / ((pi * d3^2 / 4 * ρ_water) * g)

    if abs(H_x - (u5 * (H_water - H_ω - 5) + h_3 + h1 + h2 * 4 + h0 * H_ω + F)) > 0.0001
        global H_ω_0 = H_ω
    else
        global flag_H_ω_0 = false
    end

end

flag_L0 = true
while flag_L0
    # 钢桶底端所受重力
    local F_tong_y = L0 * ω_0 + ω + H_y
    # 钢桶底端所受水平力
    local F_tong_x = h1 + h2 * 4 + h0 * H_ω_0 + F
    # 钢桶底端倾斜角度
    local θ1 = atan(F_tong_y / F_tong_x)

    # 钢管底端所受重力
    local F_guan_y = L0 * ω_0 + ω + ω_1 + H_y
    # 钢管底端所受水平力
    local F_guan_x = h2 * 4 + h0 * H_ω_0 + F
    # 钢管底端倾斜角度
    local θ2 = atan(F_guan_y / F_guan_x)

    global K = length(0:0.01:L0+5)
    global T = zeros(K, 1)
    global T[1] = (u5 * (H_water - H_ω_0 - 5) + h_3 + h1 + h2 * 4 + h0 * H_ω_0 + F) / cos(γ)
    global θ = zeros(K, 1)
    global θ[1] = γ
    global x = zeros(K, 1)
    global y = zeros(K, 1)
    Δs = 0.01
    global i = 1
    global s_end = (K-2)/100
    for s = 0:0.01:s_end
        if s < L0
            global T[i+1] = T[i] + (-u5 * cos(θ[i]) * sin(θ[i]) + ω_0 * sin(θ[i])) * Δs
            global θ[i+1] = θ[i] + (u5 * sin(θ[i])^2 + ω_0 * cos(θ[i])) / T[i] * Δs
            global x[i+1] = x[i] + cos(θ[i]) * Δs
            global y[i+1] = y[i] + sin(θ[i]) * Δs
        elseif s < L0 + 0.01
            global θ[i] = θ1
            global T[i+1] = T[i] + (-h1 * cos(θ[i]) * sin(θ[i]) + ω_1 * sin(θ[i])) * Δs
            global θ[i+1] = θ[i] + (h1 * sin(θ[i])^2 + ω_1 * cos(θ[i])) / T[i] * Δs
            global x[i+1] = x[i] + cos(θ[i]) * Δs
            global y[i+1] = y[i] + sin(θ[i]) * Δs
        elseif s < L0 + 1
            global T[i+1] = T[i] + (-h1 * cos(θ[i]) * sin(θ[i]) + ω_1 * sin(θ[i])) * Δs
            global θ[i+1] = θ[i] + (h1 * sin(θ[i])^2 + ω_1 * cos(θ[i])) / T[i] * Δs
            global x[i+1] = x[i] + cos(θ[i]) * Δs
            global y[i+1] = y[i] + sin(θ[i]) * Δs
        elseif s < L0 + 1.01
            global θ[i] = θ2
            global T[i+1] = T[i] + (-h2 * cos(θ[i]) * sin(θ[i]) + ω_2 * sin(θ[i])) * Δs
            global θ[i+1] = θ[i] + (h2 * sin(θ[i])^2 + ω_2 * cos(θ[i])) / T[i] * Δs
            global x[i+1] = x[i] + cos(θ[i]) * Δs
            global y[i+1] = y[i] + sin(θ[i]) * Δs
        else
            global T[i+1] = T[i] + (-h2 * cos(θ[i]) * sin(θ[i]) + ω_2 * sin(θ[i])) * Δs
            global θ[i+1] = θ[i] + (h2 * sin(θ[i])^2 + ω_2 * cos(θ[i])) / T[i] * Δs
            global x[i+1] = x[i] + cos(θ[i]) * Δs
            global y[i+1] = y[i] + sin(θ[i]) * Δs
        end

        global i = i + 1
    end


    if y[end] - (H_water - H_ω_0) > 0.01
        global L0 = L0 - 0.01
        global flag_H_ω_0 = true
    elseif y[end] - (H_water - H_ω_0) < -0.01
        global γ = γ + 0.01/180*pi
        global flag_H_ω_0 = true
    else
        global flag_L0 = false
    end


    while flag_H_ω_0
        # 风作用在浮标上的力
        global F = 0.625 * d3 * (h3 - H_ω_0) * v_wind^2
        # 锚点水平力
        global H_x = u5 * (H_water - H_ω_0 - 5) + h_3 + h1 + h2 * 4 + h0 * H_ω_0 + F
        # 锚点竖直力
        global H_y = H_x * tan(γ)
        # 决定吃水深度的竖直力
        W_f = H_y + m3 * g + L0 * ω_0 + ω + ω_1 + ω_2 * 4
        # 浮标吃水深度
        global H_ω = W_f / ((pi * d3^2 / 4 * ρ_water) * g)
    
        if abs(H_x - (u5 * (H_water - H_ω - 5) + h_3 + h1 + h2 * 4 + h0 * H_ω + F)) > 0.0001
            global H_ω_0 = H_ω
        else
            global flag_H_ω_0 = false
        end
    
    end
end

figure()
plot(x,y)

# 钢桶中部所受重力
F_tong_y = L0 * ω_0 + ω + 0.5 * ω_1 + H_y
# 钢桶中部所受水平力
F_tong_x = h1 + h2 * 4 + h0 * H_ω_0 + F
# 钢桶中部倾斜角度
θ1 = atan(F_tong_y / F_tong_x)
β1 = 90 - θ1 / pi * 180

# 钢管中部所受重力
F_guan_y = L0 * ω_0 + ω + ω_1 + 0.5 * ω_2 + H_y
# 钢管中部所受水平力
F_guan_x = h2 * 4 + h0 * H_ω_0 + F
# 钢管中部倾斜角度
θ2 = atan(F_guan_y / F_guan_x)
β2 = 90 - θ2 / pi * 180


# 浮标吃水深度
H_ω_0
# 锚链拖地长度
L_tuo = 21.78 - L0
# 浮标游动区域半径
r = x[end] + L_tuo
# 钢桶倾斜角
β1
# 钢管倾斜角
β2

Q3_ans = [H_ω_0, L_tuo, r, γ/pi*180, β1, β2]