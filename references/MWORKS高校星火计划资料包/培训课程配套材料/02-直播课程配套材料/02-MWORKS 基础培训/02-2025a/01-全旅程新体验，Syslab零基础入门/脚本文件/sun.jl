## 
dec = 23.4 # 太阳偏角: 23° 24'
lat = 31 + 30 / 60  # 纬度: 31° 30' ​
dec = deg2rad(dec)  # 将角度转换为弧度
lat = deg2rad(lat)
t = 5:0.25:19     # 默认时间从早上5点开始，到19点结束
# 计算太阳与电池板之间的夹角的函数
sunangle = sin(dec) * sin(lat) .+ cos(dec) .* cos(lat) .* cosd.(15 .* (t .- 12)) 
plot(t, sunangle) # 绘制夹角与时间的曲线

T_inc = 1.4883 * 0.7 .^ (sunangle .^ -0.678) # 考虑大气层影响
production_theory = 270 * T_inc .* sunangle # 计算电池板理论产量
k = find(production_theory .> 207) # 考虑电池板最大输出为207kw
production_theory[k] .= 207
plot(t, production_theory) # 绘制理论产量与时间的曲线
xlabel("时间") # 添加X轴标签
ylabel("产量(kW)") # 添加Y轴标签
title("理论数据") # 添加图标题

## 
production = readtable("太阳能电池板产量数据.xlsx") # 读取实际监测数据
plot(production.Timestamp, production.AH3)# 绘制整月的实际产量与时间的曲线

June2018 = reshape(production.AH3, 96, 30) # 将产量的向量数据转换为矩阵数据，每列为一天内的数据
dayofinterest = June2018[:, 26] # 索引26号的数据
tfullday = 0:0.25:23.75 # 定义一天内的时间

plot(tfullday, dayofinterest, ".-")
plot(tfullday, dayofinterest, ".-", t, production_theory) # 对比绘制26号的实际产量和理论产量与时间的曲线
xlabel("时间")
ylabel("产量(kW)")
legend("实际数据", "理论数据")