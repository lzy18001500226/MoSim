using TyControlSystems
##【示例34】纯比例控制，考虑𝐾_𝑃分别0.5、2.0、2.4、3.0、3.5的情况下，系统的单位阶跃响应
# 创建被控对象模型
s = tf("s")
G = 1 / ((s + 1) * (2 * s + 1) * (5 * s + 1))
Kp = [0.5, 2.0, 2.4, 3.0, 3.5]
# 预定义开环系统
GCp = Array{TyControlSystems.TransferFunction}(undef, length(Kp))
# 不同增益的开环系统定义及闭环阶跃响应计算
for i in 1:length(Kp)
    GCp[i] = pid(Kp[i]) * G
    step(feedback(GCp[i]), 35, ishold=true, linewidth=1.5)
end
grid("on")
hold("on")
# SetPoint绘制
plot([0, 35], [1, 1], "--k", linewidth=1.5)
# legend绘制
Fig = gca().lines
legend([Fig[1], Fig[3], Fig[5], Fig[7], Fig[9], Fig[11]], ["Kp=0.5", "Kp=2.0", "Kp=2.4", "Kp=3.0", "Kp=3.5", "Setpoint=1"])

#-----------------------------------------#

##【示例35】 比例-微分控制，比例系数为𝐾_𝑃=5，考虑微分系数分别为：𝐾_𝐷=0.1、0.7、1.5、3.5、8.0，求系统闭环的单位阶跃响应
# 创建被控对象模型
s = tf("s")
G = 1 / ((s + 1) * (2 * s + 1) * (5 * s + 1))
Kd = [0.1, 0.7, 1.5, 3.5, 8.0]
# 预定义开环系统
GCpd = Array{TyControlSystems.TransferFunction}(undef, length(Kd))
# 不同增益的开环系统定义及闭环阶跃响应计算
for i in 1:length(Kd)
    GCpd[i] = pid(5, 0, Kd[i]) * G
    step(feedback(GCpd[i]), 35, ishold=true, linewidth=1.5)
end
grid("on")
hold("on")
title("系统在PD控制器作用下的阶跃响应，Kp = 5")
# SetPoint绘制
plot([0, 35], [1, 1], "--k", linewidth=1.5)
# legend绘制
Fig1 = gca().lines
legend([Fig1[1], Fig1[3], Fig1[5], Fig1[7], Fig1[9], Fig1[11]], ["Kd=0.1", "Kd=0.7", "Kd=1.5", "Kd=3.5", "Kd=8.0", "Setpoint=1"])

#-----------------------------------------#

##【示例36】比例-积分控制，确定比例系数为𝐾_𝑃=2，考虑积分系数分别为：𝐾_𝐼=1.5、3.0、7.0、10、15，求系统闭环的单位阶跃响应
# 创建被控对象模型
s = tf("s")
G = 1 / ((s + 1) * (2 * s + 1) * (5 * s + 1))
Ki = [1.5, 3, 7, 10, 15]
# 预定义开环系统
GCpi = Array{TyControlSystems.TransferFunction}(undef, length(Kd))
# 不同增益的开环系统定义及闭环阶跃响应计算
for i in 1:length(Kd)
    GCpi[i] = pid(2, 1 / Ki[i]) * G
    step(feedback(GCpi[i]), 100, ishold=true, linewidth=1.5)
end
grid("on")
hold("on")
title("系统在PI控制器作用下的阶跃响应，Kp = 2")
# SetPoint绘制
plot([0, 100], [1, 1], "--k", linewidth=1.5)
# legend绘制
Fig2 = gca().lines
legend([Fig2[1], Fig2[3], Fig2[5], Fig2[7], Fig2[9], Fig2[11]], ["Ki=1.5", "Ki=3.0", "Ki=7.0", "Ki=10", "Ki=15", "Setpoint=1"])

#-----------------------------------------#

##【示例37】PID控制
# 创建被控对象模型
s = tf("s")
G = 1 / ((s + 1) * (2 * s + 1) * (5 * s + 1))
# 定义各类型PID控制器
C = [pid(3.5), pid(3.5, 0, 3.5), pid(3.5, 1 / 2), pid(3.5, 1 / 2, 3.5)]
# 预定义开环系统
GC = Array{TyControlSystems.TransferFunction}(undef, length(C))
# 开环系统定义及闭环阶跃响应计算
for i in 1:length(C)
    GC[i] = C[i] * G
    step(feedback(GC[i]), 60, ishold=true, linewidth=1.5)
end
grid("on")
hold("on")
title("系统在各类PID控制器作用下的阶跃响应")
# SetPoint绘制
plot([0, 60], [1, 1], "--k", linewidth=1.5)
# legend绘制
Cp = raw"$C_{P} = 3.5$"
Cpd = raw"$C_{PD} = 3.5 + 3.5s$"
Cpi = raw"$C_{PI} = 3.5 + \frac{1}{{2s}}$"
Cpid = raw"$C_{PID} = 3.5 + \frac{1}{{2s}} + 3.5s$"
Fig3 = gca().lines
legend([Fig3[1], Fig3[3], Fig3[5], Fig3[7]], [Cp, Cpd, Cpi, Cpid])
