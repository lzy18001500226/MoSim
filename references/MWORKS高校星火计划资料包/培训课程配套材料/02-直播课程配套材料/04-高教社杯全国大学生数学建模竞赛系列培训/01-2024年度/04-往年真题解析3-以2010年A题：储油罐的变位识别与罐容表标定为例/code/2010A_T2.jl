#第一问（1）计算实际油罐体无变位的情况下，罐内油量体积计算函数
function big_normal(h)
    r = 1.5 #圆柱体半径
    R = 1.625 #两端球冠半径
    L = 8 #圆柱体长度
    if h <= r
        V1 = part_V1(R, r, h)
        V = (L + 1 - R) * (r^2 * acos((r - h) / r) - (r - h) * sqrt(2 * h * r - h^2)) + 2 * V1
    else
        V2 = part_V2(R, r, h)
        V = pi * r^2 * (L + 1) + pi / 3 + (L - R + 1) * ((h - r) * sqrt(abs(2 * h * r - h^2)) - r^2 * acos((h - r) / r)) - 2 * V2
    end
end

#数值方法求解复杂积分
function part_V1(R, r, h)
    z_down = -r #积分下限
    z_up = h - r #积分上限
    n = 100 #离散点个数
    dz = (z_up - z_down) / n #均分
    if z_up > z_down
        z = z_down:dz:z_up
        V1_dz = zeros(length(z))
        @.V1_dz = ((R^2 - z^2) * acos((R - 1) / sqrt(abs(R^2 - z^2)))) * dz
        V1 = sum(V1_dz)
    else
        V1 = 0
    end
    return V1
end

function part_V2(R, r, h)
    z_down = h - r
    z_up = r
    n = 100
    dz = (z_up - z_down) / n
    if z_up > z_down
        z = z_down:dz:z_up
        V2_dz = zeros(length(z))
        @.V2_dz = ((R^2 - z^2) * acos((R - 1) / sqrt(abs(R^2 - z^2)))) * dz
        V2 = sum(V2_dz)
    else
        V2 = 0
    end
    return V2
end

h = 0.1:0.1:3
V_big_normal = zeros(size(h, 1))
length_h = length(h)
for i in 1:length_h
    V_big_normal[i] = big_normal(h[i]) * 1000
end
plot(h, V_big_normal)
# 添加坐标轴标签
xlabel("油位高度h/m")
ylabel("储油量V/m3")
# 将两列数据写入文件中
h_cm = h
# 打开一个文件用于写入
file_path = "big_normal.txt"
fileID = fopen(file_path, "w");
# 按列写入向量，使用 '\t' 作为列分隔符，'\n' 作为行分隔符
for i in 1:length(h)
    fprintf(fileID, "%.1f\t%.2f\n", h_cm[i], V_big_normal[i])
end
# 关闭文件
fclose(fileID)


#第二问（2）计算实际油罐体纵向水平变位和横向偏转变位的情况下，罐内油量体积计算函数
function big_long_hor(alpha, beta, h)
    r = 1.5
    R = 1.625
    # L = 8
    H = r + (h - r) / cos(beta) - 2 * tan(alpha) #与书上不一致，以自己推导的为准
    # H = r + (h - r) * cos(beta) - 2 * tan(alpha) #书上公式
    if H >= 4 * tan(alpha)
        V1 = part2_V1(alpha, H, R, r)
        V2 = part2_V2(alpha, H, R, r)
        V3 = part2_V3(alpha, H, r)
        V4 = part2_V4(alpha, H, R, r)
        V5 = part2_V5(alpha, H, r)
        V6 = part2_V6(alpha, H, R, r)
        V7 = part2_V7(alpha, H, R, r)
        V8 = part2_V8(alpha, H, R, r)
        V = 2 * V1 + 2 * V2 + 2 * V3 + 2 * V4 + 13.5 * V5 + 4 * V6 - 2 * V7 - 2 * V8
    else
        V9 = part2_V9(alpha, H, R, r)
        V10 = part2_V10(alpha, H, R, r)
        V11 = part2_V11(alpha, H, r)
        V12 = part2_V12(alpha, H, R, r)
        V = 2 * V9 + 2 * V10 + 2 * V11 + 2 * V12
    end
    return V
end

#数值方法求解复杂积分
function part2_V1(alpha, H, R, r)
    x_a = 3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 + sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) + (H - r) * cos(alpha))^2))
    x_b = H - r + 4 * tan(alpha)
    x_down = x_b
    x_up = x_a
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V1_dx = zeros(length(x))
        f1_r = zeros(length(x))
        @.f1_r = sqrt(abs(R^2 - x^2 - ((-x + H - r) * cot(alpha) + 3.375)^2))
        @.V1_dx = ((-x + H - r) * cot(alpha) + 3.375) * f1_r * dx
        V1 = sum(V1_dx)
    else
        V1 = 0
    end
    return V1
end
function part2_V2(alpha, H, R, r)
    x_a = 3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 + sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) + (H - r) * cos(alpha))^2))
    x_b = H - r + 4 * tan(alpha)
    x_down = x_b
    x_up = x_a
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        f1_r = zeros(length(x))
        x_up = zeros(length(x))
        V2 = 0
        for i in 1:n
            f1_r[i] = sqrt(abs(R^2 - x[i]^2 - ((-x[i] + H - r) * cot(alpha) + 3.375)^2))
            y_down = 0
            y_up = f1_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V2 = V2 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V2 = V2 + 0
            end
        end
    else
        V2 = 0
    end
    return V2
end
function part2_V3(alpha, H, r)
    x_b = H - r + 4 * tan(alpha)
    x_c = H - r - 4 * tan(alpha)
    x_down = x_c
    x_up = x_b
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V3_dx = zeros(length(x))
        f2_r = zeros(length(x))
        @.f2_r = sqrt(abs(r^2 - x^2))
        @.V3_dx = ((-x + H - r) * cot(alpha) + 3.375) * f2_r * dx
        V3 = sum(V3_dx)
    else
        V3 = 0
    end
    return V3
end
function part2_V4(alpha, H, R, r)
    x_b = H - r + 4 * tan(alpha)
    x_c = H - r - 4 * tan(alpha)
    x_down = x_c
    x_up = x_b
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        f2_r = zeros(length(x))
        x_up = zeros(length(x))
        V4 = 0
        for i in 1:n
            f2_r[i] = sqrt(abs(r^2 - x[i]^2))
            y_down = 0
            y_up = f2_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V4 = V4 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V4 = V4 + 0
            end
        end
    else
        V4 = 0
    end
    return V4
end
function part2_V5(alpha, H, r)
    x_c = H - r - 4 * tan(alpha)
    x_e = -r
    x_down = x_e
    x_up = x_c
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V5_dx = zeros(length(x))
        f4_r = zeros(length(x))
        @.f4_r = sqrt(abs(r^2 - x^2))
        @.V5_dx = f4_r * dx
        V5 = sum(V5_dx)
    else
        V5 = 0
    end
    return V5
end
function part2_V6(alpha, H, R, r)
    x_c = H - r - 4 * tan(alpha)
    x_e = -r
    x_down = x_e
    x_up = x_c
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        f4_r = zeros(length(x))
        x_up = zeros(length(x))
        V6 = 0
        for i in 1:n
            f4_r[i] = sqrt(abs(r^2 - x[i]^2))
            y_down = 0
            y_up = f4_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V6 = V6 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V6 = V6 + 0
            end
        end
    else
        V6 = 0
    end
    return V6
end
function part2_V7(alpha, H, R, r)
    x_c = H - r - 4 * tan(alpha)
    x_d = -3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 - sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) - (H - r) * cos(alpha))^2))
    x_down = x_d
    x_up = x_c
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V7_dx = zeros(length(x))
        f3_r = zeros(length(x))
        @.f3_r = sqrt(abs(R^2 - x^2 - ((-x + H - r) * cot(alpha) - 3.375)^2))
        @.V7_dx = ((x - H + r) * cot(alpha) + 3.375) * f3_r * dx
        V7 = sum(V7_dx)
    else
        V7 = 0
    end
    return V7
end
function part2_V8(alpha, H, R, r)
    x_c = H - r - 4 * tan(alpha)
    x_d = -3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 - sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) - (H - r) * cos(alpha))^2))
    x_down = x_d
    x_up = x_c
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        f3_r = zeros(length(x))
        x_up = zeros(length(x))
        V8 = 0
        for i in 1:n
            f3_r[i] = sqrt(abs(R^2 - x[i]^2 - ((-x[i] + H - r) * cot(alpha) - 3.375)^2))
            y_down = 0
            y_up = f3_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V8 = V8 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V8 = V8 + 0
            end
        end
    else
        V8 = 0
    end
    return V8
end

function part2_V9(alpha, H, R, r)
    x_a1 = 3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 + sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) + (H - r) * cos(alpha))^2))
    x_b1 = H - r + 4 * tan(alpha)
    x_down = x_b1
    x_up = x_a1
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V9_dx = zeros(length(x))
        g1_r = zeros(length(x))
        @.g1_r = sqrt(abs(R^2 - x^2 - ((-x + H - r) * cot(alpha) + 3.375)^2))
        @.V9_dx = ((-x + H - r) * cot(alpha) + 3.375) * g1_r * dx
        V9 = sum(V9_dx)
    else
        V9 = 0
    end
    return V9
end
function part2_V10(alpha, H, R, r)
    x_a1 = 3.375 * sin(alpha) * cos(alpha) + (H - r) * (cos(alpha))^2 + sin(alpha) * sqrt(abs(R^2 - (3.375 * sin(alpha) + (H - r) * cos(alpha))^2))
    x_b1 = H - r + 4 * tan(alpha)
    x_down = x_b1
    x_up = x_a1
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        g1_r = zeros(length(x))
        x_up = zeros(length(x))
        V10 = 0
        for i in 1:n
            g1_r[i] = sqrt(abs(R^2 - x[i]^2 - ((-x[i] + H - r) * cot(alpha) + 3.375)^2))
            y_down = 0
            y_up = g1_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V10 = V10 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V10 = V10 + 0
            end
        end
    else
        V10 = 0
    end
    return V10
end
function part2_V11(alpha, H, r)
    x_b1 = H - r + 4 * tan(alpha)
    x_c1 = -r
    x_down = x_c1
    x_up = x_b1
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        V11_dx = zeros(length(x))
        g2_r = zeros(length(x))
        @.g2_r = sqrt(abs(r^2 - x^2))
        @.V11_dx = ((-x + H - r) * cot(alpha) + 3.375) * g2_r * dx
        V11 = sum(V11_dx)
    else
        V11 = 0
    end
    return V11
end
function part2_V12(alpha, H, R, r)
    x_b1 = H - r + 4 * tan(alpha)
    x_c1 = -r
    x_down = x_c1
    x_up = x_b1
    n = 1000
    dx = (x_up - x_down) / n
    if x_up > x_down
        x = x_down:dx:x_up
        g2_r = zeros(length(x))
        x_up = zeros(length(x))
        V12 = 0
        for i in 1:n
            g2_r[i] = sqrt(abs(r^2 - x[i]^2))
            y_down = 0
            y_up = g2_r[i]
            dy = (y_up - y_down) / n
            if y_up > y_down
                y = y_down:dy:y_up
                for ii in 1:n
                    V12 = V12 + sqrt(abs(R^2 - x[i]^2 - y[ii]^2)) * dx * dy
                end
            else
                V12 = V12 + 0
            end
        end
    else
        V12 = 0
    end
    return V12
end

#第二问（3）参数估计和辨识
#读取附件中的实际采集数据表，对前302组数据进行多项式拟合,单位统一为m,升
ex_data_file_name = "ex_data1.txt"
ex_data = readtable(ex_data_file_name)
ex_outQ = ex_data[1:302, 1]
ex_h = ex_data[1:302, 2]
ex_V = ex_data[1:302, 3]

function optim_big_long_hor(para, ex_h)
    alpha = para[1] / 180 * pi
    beta = para[2] / 180 * pi
    r = 1.5
    R = 1.625
    V_data = []#存储不同h下的油液体积
    length_ex_h = length(ex_h)
    for i in 1:length_ex_h
        h = ex_h[i]
        H = r + (h - r) / cos(beta) - 2 * tan(alpha)
        if H >= 4 * tan(alpha)
            V1 = part2_V1(alpha, H, R, r)
            V2 = part2_V2(alpha, H, R, r)
            V3 = part2_V3(alpha, H, r)
            V4 = part2_V4(alpha, H, R, r)
            V5 = part2_V5(alpha, H, r)
            V6 = part2_V6(alpha, H, R, r)
            V7 = part2_V7(alpha, H, R, r)
            V8 = part2_V8(alpha, H, R, r)
            V = 2 * V1 + 2 * V2 + 2 * V3 + 2 * V4 + 13.5 * V5 + 4 * V6 - 2 * V7 - 2 * V8
        else
            V9 = part2_V9(alpha, H, R, r)
            V10 = part2_V10(alpha, H, R, r)
            V11 = part2_V11(alpha, H, r)
            V12 = part2_V12(alpha, H, R, r)
            V = 2 * V9 + 2 * V10 + 2 * V11 + 2 * V12
        end
        if isempty(V_data)
            V_data = V
        else
            V_data = [V_data; V]
        end
    end
    delta_V = zeros(length_ex_h)
    delta_h = zeros(length_ex_h)
    for i in 1:length_ex_h-1
        delta_V[i] = V_data[i] - V_data[i+1]
        delta_h[i] = ex_h[i] - ex_h[i+1]
    end
    return delta_V .* 1000, delta_h .* 1000, V_data .* 1000#将体积转换为升，h转换为毫米mm
end

function Sum_of_difference(para, ex_h, ex_outQ)
    delta_V, delta_h, V_data = optim_big_long_hor(para, ex_h ./ 1000)
    length_V = length(delta_V)
    diff_V = zeros(length_V)
    for i in 1:length_V-1
        diff_V[i] = (ex_outQ[i+1] / delta_h[i] - delta_V[i] / delta_h[i])^2
    end
    sum_of_diff = sum(diff_V[1:end-1])
    return sum_of_diff
end

#横向偏转的影响不大
para_total1 = [[0.5; 0], [1; 0], [1.5; 0], [2; 0], [2.5; 0], [3; 0]]#在[2,0]附近 #极值差值2000
para_total2 = [[2; 0.5], [2; 1], [2; 1.5], [2; 2], [2; 2.5],
    [2; 3], [2; 3.5], [2; 4], [2; 4.5], [2; 5]]  #在[2,5]附近 #极值差值130
para_total3 = [[1.5; 5], [1.6; 5], [1.7; 5], [1.8; 5], [1.9; 5],
    [2; 5], [2.1; 5], [2.2; 5], [2.3; 5], [2.4; 5], [2.5; 5]]

#得出结论，偏转角度在[2,5]附近######----------------

# para_total3为变位参数集
#需要特别注意：替换不同参数集时，需要统一更改 
#sum_of_diff = zeros(size(para_total1, 1))至sum_of_diff = zeros(size(para_total2, 1))  和  
#for para in para_total1 至 for para in para_total2
i = 1
sum_of_diff = zeros(size(para_total1, 1))
for para in para_total1
    sum_of_diff[i] = Sum_of_difference(para, ex_h, ex_outQ)
    i = i + 1
end

min_value, min_index = findmin(sum_of_diff)
max_value, max_index = findmax(sum_of_diff)
max_min = max_value - min_value

#第二问（4）：以偏转角度[2,5]计算储油罐体变位的修正罐容表标定值及修正误差
h = 0.1:0.1:3
optim_big_long_hor_data = zeros(size(h, 1))
length_h = length(h)
para = [2, 5]
delta_V, delta_h, optim_big_long_hor_data = optim_big_long_hor(para, h)
delta = zeros(length_h)
error = zeros(length_h)
for i in 1:length_h
    delta[i] = V_big_normal[i] - optim_big_long_hor_data[i]
    error[i] = abs(delta[i]) / V_big_normal[i]
end
file_path = "optim_big_long_hor_data.txt"
fileID = fopen(file_path, "w");
# 按列写入向量，使用 '\t' 作为列分隔符，'\n' 作为行分隔符
for i in 1:length_h
    fprintf(fileID, "%.1f\t%.2f\t%.2f\t%.2f\t%.4f\n", h[i], V_big_normal[i], optim_big_long_hor_data[i], abs(delta[i]), error[i])
end
# 关闭文件
fclose(fileID)
plot(h, optim_big_long_hor_data)
hold("on")
plot(h, V_big_normal)
# 添加坐标轴标签
xlabel("油位高度h/m")
ylabel("储油量V/m3")

# 添加图例
l = legend(["变位后数据", "未变位数据"], loc="southeast")

#第二问（5）：以偏转角度[2,5]为例，计算第二组实验中的油位高度下的出油量，验证参数估计的正确性
#读取附件中的实际采集数据表，对第304-end组数据进行提取
ex_data_file_name2 = "ex_data1.txt"
ex_data2 = readtable(ex_data_file_name2)
ex_outQ2 = ex_data2[304:end, 1]
ex_h2 = ex_data2[304:end, 2]
ex_V2 = ex_data2[304:end, 3]
para = [2, 5]
delta_V2, delta_h2, V_data2 = optim_big_long_hor(para, ex_h2 ./ 1000)
#绘散点图比较delta_V2[1:299]与ex_outQ2[2:end]
x_h = 1:1:299
scatter(x_h, ex_outQ2[2:end])
hold("on")
s = 20
c = "k"
scatter(x_h, delta_V2[1:299], s, c; filled=true)

## 添加坐标轴标签
xlabel("监测次数")
ylabel("出油量/L")

## 添加图例
l = legend(["实验2数据", "参数估计数据"], loc="northeast")