# 24A题 第二问
include("T1_function.jl")

function fun_solve_T2(p, t1, dt)
    d1 = 0.275
    d2 = 0.15
    # 将第一问中的时间t扩至 500s

    θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, _ = fun_solve_T1(p, t1, dt)

    # length_t = length(t1)
    θ_head = θ_dragon[1, :] # 龙头前把手的某时刻下的角度，从16*2*pi开始逐渐减小
    r_head = θ_dragon[1, :] # 极坐标的位置信息
    x_head = x_dragon[1, :] # 直角坐标系的位置信息
    y_head = y_dragon[1, :] # 直角坐标系的位置信息

    θ_2nd = θ_dragon[2, :] # 龙头后把手的某时刻下的角度
    r_2nd = θ_dragon[2, :] # 极坐标的位置信息
    x_2nd = x_dragon[2, :] # 直角坐标系的位置信息
    y_2nd = y_dragon[2, :] # 直角坐标系的位置信息

    θ_3rd = θ_dragon[3, :] # 第一节龙身后把手的某时刻下的角度
    r_3rd = θ_dragon[3, :] # 极坐标的位置信息
    x_3rd = x_dragon[3, :] # 直角坐标系的位置信息
    y_3rd = y_dragon[3, :] # 直角坐标系的位置信息

    k1 = similar(θ_head) # 龙头前后把手之间连线的斜率
    k2 = similar(k1) # 龙头前把手与左上角（外侧上角）之间连线的斜率
    k3 = similar(k1) # 龙头后把手与左下角（外侧下角）之间连线的斜率
    b1 = similar(k1) # 龙头左侧边界所在直线的截距
    x_head_A1 = similar(k1) # 龙头左上角A1的x坐标
    y_head_A1 = similar(k1) # 龙头左上角A1的y坐标
    x_head_A2 = similar(k1) # 龙头左下角A2的x坐标
    y_head_A2 = similar(k1) # 龙头左下角A2的y坐标

    k1 = (y_head - y_2nd) ./ (x_head - x_2nd)

    # k2 = (d2 / d1 .+ k1) ./ (k1 * (d2 / d1) .- 1) #参考论文中有误，需要注意
    k2 = (d2 / d1 .+ k1) ./ (-k1 * (d2 / d1) .+ 1)

    b1 = d2 * sqrt.(k1 .^ 2 .+ 1) + y_head - k1 .* x_head

    if abs.(b1) <= abs.(y_head - k1 .* x_head)
        b1 = -d2 * sqrt.(k1 .^ 2 .+ 1) + y_head - k1 .* x_head
    end

    x_head_A1 = (y_head - k2 .* x_head - b1) ./ (k1 - k2)
    y_head_A1 = (k1 .* y_head - k1 .* k2 .* x_head - k2 .* b1) ./ (k1 - k2)

    k3 = (-d2 / d1 .+ k1) ./ (k1 * (d2 / d1) .+ 1)

    x_head_A2 = (y_2nd - k3 .* x_2nd - b1) ./ (k1 - k3)
    y_head_A2 = (k1 .* y_2nd - k1 .* k3 .* x_2nd - k3 .* b1) ./ (k1 - k3)

    n = Int(t1 * (1 / dt) + 1)  # 已知集合中的数组个数
    collection_i = Vector{Int}[]  # 创建一个数组的数组（元素类型为Vector{Int}）
    collection_ki = Vector{Float64}[]  # 创建一个数组的数组
    collection_di_A1 = Vector{Float64}[]  # 创建一个数组的数组
    collection_di_A2 = Vector{Float64}[]  # 创建一个数组的数组

    for _ in 1:n
        push!(collection_i, Int[])  # 添加空数组或根据需求初始化
        push!(collection_ki, Float64[])  # 添加空数组或根据需求初始化
        push!(collection_di_A1, Float64[])
        push!(collection_di_A2, Float64[])
    end

    for t_i in 1:n
        for i in 1:224
            if θ_dragon[i, t_i] >= θ_dragon[1, t_i] + 1.5pi &&
               θ_dragon[i, t_i] <= θ_dragon[1, t_i] + 2.5pi
                push!(collection_i[t_i], i)
            end
        end
    end

    for t_i in 1:n
        for i in 1:length(collection_i[t_i])
            ki = (y_dragon[collection_i[t_i][i], t_i] - y_dragon[collection_i[t_i][i]+1, t_i]) / (x_dragon[collection_i[t_i][i], t_i] - x_dragon[collection_i[t_i][i]+1, t_i])
            push!(collection_ki[t_i], ki)
        end
    end

    flag = 0
    A1_judge = []
    println("A1点碰撞检测")
    for t_i in 1:n
        for i in 1:length(collection_ki[t_i])

            d_judge = abs(collection_ki[t_i][i] * (x_head_A1[t_i] - x_dragon[collection_i[t_i][i], t_i]) - y_head_A1[t_i] + y_dragon[collection_i[t_i][i], t_i]) / sqrt(collection_ki[t_i][i]^2 + 1)

            if d_judge < d2
                flag = 1
                println([t_i, i, collection_i[t_i][i]])
                push!(A1_judge, [t_i, i, collection_i[t_i][i]])
                break
            end
        end
    end

    # A1点在412.6秒碰撞

    flag = 0
    A2_judge = []
    println("A2点碰撞检测")
    for t_i in 1:n
        for i in 1:length(collection_ki[t_i])

            d_judge = abs(collection_ki[t_i][i] * (x_head_A2[t_i] - x_dragon[collection_i[t_i][i], t_i]) - y_head_A2[t_i] + y_dragon[collection_i[t_i][i], t_i]) / sqrt(collection_ki[t_i][i]^2 + 1)

            if d_judge < d2
                flag = 1
                println([t_i, i, collection_i[t_i][i]])
                push!(A2_judge, [t_i, i, collection_i[t_i][i]])
                break
            end
        end
    end

    if A1_judge[1][1] < A2_judge[1][1]
        t_judge = A1_judge[1][1]
    else
        t_judge = A2_judge[1][1]
    end

    return θ_dragon, r_dragon, x_dragon, y_dragon, v_dragon, t_judge
end







