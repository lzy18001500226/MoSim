using TyControlSystems
using  TyPlot
##【示例18】计算并绘制系统的阶跃响应】
G = tf([2 25], [1 4 25])
# 阶跃响应基础绘图 
step(G, 3.5)

# 图形修饰 
step(G, 0:0.05:3.5, "-ro", linewidth=1, markersize=5, markeredgecolor="#0072BD", markerfacecolor="#EDB120")
grid("on")

# 多个系统响应绘图叠加 
step(G, 3.5, "-b")
step(c2d(G, 0.1), 3.5, "-r", ishold=true)
grid("on")

# 获取输出结构体数据 
res = step(G, 3.5, fig=false)
# 直接获取阶跃响应数据 
y, t = step(G, fig=false)

#-----------------------------------------#

##【示例19】计算并绘制双输入双输出系统的阶跃响应
# 定义系统矩阵 
A = [-1 -1; 6.5 0]
B = [1 1; 1 0]
C = [1 0; 0 1]
D = zeros(2, 2)
# 创建状态空间模型 
G = ss(A, B, C, D)
# 计算系统阶跃响应 
step(G)
grid("on")

# 获取输出结构体数据 
res = step(G, fig=false)

#-----------------------------------------#

##【示例20】计算并绘制标准二阶系统阶跃响应曲线及响应面
## 1.阶跃响应曲线计算与绘制
# 时间向量定义 
t = 0:0.2:10
# 阻尼比定义
ζ = 0:0.05:1.2  # \zeta<Tab>
# 传递函数及响应变量预定义
num = [0];
den = [0 0 0];
y = zeros(length(t), length(ζ))
ty = zeros(length(t), length(ζ))
# 计算不同阻尼比下的二阶系统阶跃响应
for i in 1:length(ζ)
    num = [1]
    den = [1, 2 * ζ[i], 1]
    y[:, i], ty[:, i] = step(tf(num, den), t, fig=false)
end
# 绘制\zeta = 0的阶跃响应曲线
plot(t, y[:, 1])
hold("on")
# 绘制\zeta = 0.2,0.4,0.6,0.8,1.0,1.2的阶跃响应曲线
for j in 5:4:length(ζ)
    plot(t, y[:, j])
end
# 图形修饰
grid("on")
title(raw"二阶系统阶跃响应曲线，其中：$\omega _n$=1、$\zeta$=0,0.2,0.4,0.6,0.8,1.0,1.2")
xlabel("time(s)")
ylabel("Amplitude")
legend(raw"$\zeta$=0", raw"$\zeta$=0.2", raw"$\zeta$=0.4", raw"$\zeta$=0.6", raw"$\zeta$=0.8", raw"$\zeta$=1.0", raw"$\zeta$=1.2")

## 2.阶跃响应面绘制
# 构造ζ、t构成的网格 
zeta, T = meshgrid2(ζ, t)
# 三维响应面绘制 
s = mesh(T, zeta, y; facealpha=0.95)
grid("off")
# 三维响应面图形修饰 
xlabel("time(s)")
ylabel(raw"$\zeta$")
zlabel("Response")
s.set_facecolor("flat")
s.set_edgecolor("#dddddd")
plt_update()

#-----------------------------------------#

##【示例21】获取系统的阶跃响应特性
G = tf([25], [1 3 25])

# 计算并获取系统阶跃响应特性 
res = stepinfo(G)
# 上升时间 
res.RiseTime
# 最大超调 
res.Overshoot
# 峰值 
res.Peak
# 峰值时间 
res.PeakTime
# 调整时间 
res.SettlingTime

#-----------------------------------------#

##【示例22】计算系统脉冲响应
H = tf([1], [1, 0.2, 1])
impulse(H)

# 图形修饰 
H = tf([1], [1, 0.2, 1])
impulse(H, 0:0.4:40, "-rd", linewidth=1, markersize=5, markeredgecolor="#0072BD", markerfacecolor="#EDB120")
grid("on")

#-----------------------------------------#

#【示例23】针对示例22，通过阶跃函数求取其脉冲响应
s = tf('s')
H = tf([1], [1, 0.2, 1])
# 通过阶跃函数step求取H的脉冲响应
step(s * H, 40, "-r", linewidth=2)

#-----------------------------------------#

##【示例24】计算系统的斜坡响应
# 定义Laplace算子 
s = tf('s')
# 定义状态空间矩阵
A = [0 1; -1 -1]
B = [0; 1]
C = [1 0]
D = [0]
# 创建系统模型
G = ss(A, B, C, D)
# 指定时间向量
t = 0:0.15:10
# 通过step计算斜坡响应
step((tf(G) / s), t, "ro")
hold("on")
# 绘制斜坡输入信号
plot(t, t, "-b")
legend("斜坡响应", "斜坡信号")
grid("on")

#-----------------------------------------#

##【示例25】计算系统对自定义斜坡阶跃信号的响应
## 输入信号在 t = 0 时从 0 开始，在 t = 1 时从 0 开始单位斜坡 1s 到 1，然后在 1 处保持稳定
# 定义系统
sys = tf([3], [1, 2, 3])
# 创建输入信号
t = 0:0.08:8
u = max.(0, min.(t .- 1, 1))
# 计算系统响应
lsim(sys, reshape(u, 1, length(u)), t, "-ro", linewidth=1, markersize=5, markeredgecolor="#0072BD", markerfacecolor="#EDB120")
grid("on")
legend("系统响应", "输入信号")

#-----------------------------------------#

##【示例26】考虑以下系统在输入信号 𝑢=𝑒^(−𝑡) 作用下的响应情况，假设初始状态为 𝒙(0)=𝟎
A = [-1 0.5; -1 0]
B = [0; 1]
C = [1 0]
D = 0
G = ss(A, B, C, D)
# 创建输入信号
t = 0:0.2:12
u = exp.(-t)
u = reshape(u, 1, length(u))
lsim(G, u, t, "ro", markeredgecolor="#0072BD", markerfacecolor="#EDB120")
grid("on")
legend("系统响应", "输入信号")

# 改变初始状态值
x0=[-0.2, 1.0]
lsim(G, u, t, x0, "rp", markeredgecolor="#0072BD", markerfacecolor="#D95319")
legend("系统响应", "输入信号")
title("线性仿真结果，初值 x0=[-0.2,1.0]")
grid("on")