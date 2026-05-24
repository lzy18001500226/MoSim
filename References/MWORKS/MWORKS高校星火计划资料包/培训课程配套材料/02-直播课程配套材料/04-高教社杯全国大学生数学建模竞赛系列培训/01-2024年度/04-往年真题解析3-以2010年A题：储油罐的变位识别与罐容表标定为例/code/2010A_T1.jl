#第一问（1）计算油罐体无变位的情况下，罐内油量体积计算函数
function small_normal(h)
    # 变量注释
    # V 油液体积
    # h 油液高度

    a = 0.89 # 长轴长度
    b = 0.6  # 短轴长度
    L = 2.45 # 罐体长度
    if h <= b
        V = L * ((a / b) * (h - b) * sqrt(2 * b * h - h^2) + a * b * asin(sqrt(2 * b * h - h^2) / b))
    else
        V = L * (pi * a * b - a * b * acos((h - b) / b) + (a / b) * (h - b) * sqrt(2 * b * h - h^2))
    end
    return V
end

#绘制无变位情况下，油罐油位高度与储油量的曲线图
h = 0.01:0.01:1.2
length_h = length(h)
V = zeros(length_h)
for i in 1:length_h
    V[i] = small_normal(h[i]) * 1000
end
plot(h, V)
# 添加坐标轴标签
xlabel("油位高度h/m")
ylabel("储油量V/m3")


#将两列数据写入文件中
h_cm = h .* 100
# 打开一个文件用于写入
file_path = "small_normal.txt"
fileID = fopen(file_path, "w");
# 按列写入向量，使用 '\t' 作为列分隔符，'\n' 作为行分隔符
for i in 1:length(h)
    fprintf(fileID, "%d\t%.2f\n", h_cm[i], V[i])
end
# 关闭文件
fclose(fileID)
#= # 添加图例
l = legend(["无变位数据-n"], loc="southeast") =#

#第一问（2）计算油罐体纵向单变体的情况下，罐内油量体积计算函数
function small_long_displacement(alpha, h)
    # 变量注释
    # V 油液体积
    # alpha 水平倾斜角度
    # h 油液高度
    # H 在坐标系xOz上对应的油面高度(等效高度)

    a = 0.89 # 长轴长度
    b = 0.6  # 短轴长度
    L = 2.45 # 罐体长度
    H = h - 0.825 * tan(alpha)
    z_a = 1.225 * tan(alpha) + H - b
    z_b = H - b - 1.225 * tan(alpha)
    z_a1 = 1.225 * tan(alpha) + H - b
    #油罐倾斜后，z_a = 1.225 * tan(alpha) + H - b <= b，求得h取不到2b,因此要 求h=0.01:0.01:1.2，该函数定义域覆盖不全，因此加此定义域保护
    if z_a >= b
        z_a = b
    end
    if H >= 1.225 * tan(alpha) && H <= 1.2
        V = (a / b) * ((H - b) * cot(alpha) + L / 2) * (z_a * sqrt(abs(b^2 - z_a^2)) + b^2 * asin(z_a / b)) - (a / b) * ((H - b) * cot(alpha) - L / 2) * (z_b * sqrt(abs(b^2 - z_b^2)) + b^2 * asin(z_b / b)) + pi / 2 * a * b * L + 2 * a / (3 * b) * cot(alpha) * ((b^2 - z_a^2)^(3 / 2) - (b^2 - z_b^2)^(3 / 2))
    else
        V = (a / b) * ((H - b) * cot(alpha) + L / 2) * (z_a1 * sqrt(abs(b^2 - z_a1^2)) + b^2 * asin(z_a1 / b) + pi / 2 * b^2) + 2 * a / (3 * b) * cot(alpha) * ((b^2 - z_a1^2)^(3 / 2))
    end
    return V
end

h = 0.01:0.01:1.2
V = zeros(size(h, 1))
V_small_long = zeros(size(h, 1))
length_h = length(h)
delta = zeros(length_h)
error = zeros(length_h)
alpha = 4.1 / 180 * pi
for i in 1:length_h
    V[i] = small_normal(h[i]) * 1000
    V_small_long[i] = small_long_displacement(alpha, h[i]) * 1000
    delta[i] = V_small_long[i] - V[i]
    error[i] = abs(delta[i]) / V_small_long[i]
    # println(i)
end
plot(h, V)
hold("on")
plot(h, V_small_long)

# 添加坐标轴标签
xlabel("油位高度h/m")
ylabel("储油量V/m3")

# 添加图例
l = legend(["无变位数据-n", "变位后数据-n"], loc="southeast")

#将两列数据写入文件中
h_cm = h .* 100
# 打开一个文件用于写入
file_path = "small_normal.txt"
file_path1 = "small_long_displacement.txt"
file_path2 = "small_long_delta_error.txt"
fileID = fopen(file_path, "w");
fileID1 = fopen(file_path1, "w");
fileID2 = fopen(file_path2, "w");

# 按列写入向量，使用 '\t' 作为列分隔符，'\n' 作为行分隔符
for i in 1:length(h)
    fprintf(fileID, "%d\t%.2f\n", h_cm[i], V[i])
    fprintf(fileID1, "%d\t%.2f\n", h_cm[i], V_small_long[i])
    fprintf(fileID2, "%d\t%.2f\t%.4f\n", h_cm[i], abs(delta[i]), error[i])
end
# 关闭文件
fclose(fileID)
fclose(fileID1)
fclose(fileID2)

#第一问（3）与实验数据进行对比，首先对比无变位情况下，以出油数据为例对比
ex_data1_file_name1 = "ex_data1_normal_out.txt"
ex_data1 = readtable(ex_data1_file_name1)
ex_outQ1 = ex_data1[1:end-1, 1]
ex_h1 = ex_data1[1:end-1, 2]
length_ex_h1 = length(ex_h1)
V = zeros(length_ex_h1)
delta_outQ1 = zeros(length_ex_h1)
for i in 1:length_ex_h1
    V[i] = small_normal(ex_h1[i] / 1000) * 1000
end

for i in 1:length_ex_h1-1
    delta_outQ1[i] = V[1] - V[i+1]
end

#绘图比较

plot(ex_h1[1:end-1], ex_outQ1[1:end-1])
hold("on")
plot(ex_h1[1:end-1], delta_outQ1[1:end-1])

## 添加坐标轴标签
xlabel("油位高度")
ylabel("出油量/L")

## 添加图例
l = legend(["实验数据-n", "理论数据-n"], loc="northeast")

#与实验数据进行对比，对比有变位情况下，以出油数据为例对比
ex_data1_file_name2 = "ex_data1_long_out.txt"
ex_data2 = readtable(ex_data1_file_name2)
ex_outQ2 = ex_data2[1:end-1, 1]
ex_h2 = ex_data2[1:end-1, 2]
length_ex_h2 = length(ex_h2)
V_2 = zeros(length_ex_h2)
delta_outQ2 = zeros(length_ex_h2)
alpha = 4.1 / 180 * pi
for i in 1:length_ex_h2
    V_2[i] = small_long_displacement(alpha, ex_h2[i] / 1000) * 1000
end

for i in 1:length_ex_h2-1
    delta_outQ2[i] = V_2[1] - V_2[i+1]
end

#绘图比较

plot(ex_h2[1:end-1], ex_outQ2[1:end-1])
hold("on")
plot(ex_h2[1:end-1], delta_outQ2[1:end-1])

## 添加坐标轴标签
xlabel("油位高度")
ylabel("出油量/L")

## 添加图例
l = legend(["实验数据-l", "理论数据-l"], loc="northeast")

#以上可以验证第一问建立的模型的正确性
