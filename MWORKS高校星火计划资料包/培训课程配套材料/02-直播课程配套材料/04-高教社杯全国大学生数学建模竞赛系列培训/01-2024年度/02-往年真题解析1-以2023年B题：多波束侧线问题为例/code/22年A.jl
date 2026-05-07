# 定义系统参数
m1 = 10;   # 浮子质量
m2 = 5;    #振子质量
mu = 2;    # 附加质量
eta = 10;  # 阻尼系数
k = 50;    # 线性弹簧系数
g = 9.81;  # 重力加速度
R = 0.5;   # 浮子半径（或相关尺寸）
p = 1000;  # 流体密度
f = 10;    # 波浪激励力振幅
omega  = 2*pi; # 波浪频率

# 定义时间范围
tspan = [0 40*2*pi/omega]; # 前40个波浪周期

# 初始条件
x0 = [0 0]; # 浮子和振子的初始位移
v0 = [0 0]; # 浮子和振子的初始速度

# 将二阶ODE转换为一阶ODE系统
# y = [x1; x2; v1; v2]

function odeFunc(t,y)
    dydt = [y[3]; y[4];(-eta*(y[3]-y[4]) - k*(y[1]-y[2]) - p*g*pi*R^2*y[1] + f*cos(omega*t)) / (m1 + mu);(-eta*(y[4]-y[3]) - k*(y[2]-y[1])) / m2]
    return dydt
end



# odeFunc = @(t, y) [y(3); y(4);
#     (-eta*(y(3)-y(4)) - k*(y(1)-y(2)) - p*g*pi*R^2*y(1) + f*cos(omega*t)) / (m1 + mu);
#     (-eta*(y(4)-y(3)) - k*(y(2)-y(1))) / m2];

# 使用ode45求解
t, y,= ode45(odeFunc, tspan, [x0; v0]);

# 提取位移和速度
x1 = y[:, 1];
x2 = y[:, 2];
v1 = y[:, 3];
v2 = y[:, 4];

# 绘图
figure;
subplot(2, 1, 1);
plot(t, x1, "b-", t, x2, "r--");
title("位移");
xlabel("时间");
ylabel("位移");
legend("浮子", "振子");

subplot(2, 1, 2);
plot(t, v1, "b-", t, v2, "r--");
title("速度");
xlabel("时间");
ylabel("速度");
legend("浮子", "振子"); 
tightlayout()