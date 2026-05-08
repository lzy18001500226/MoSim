# 示例1：中值滤波的噪声抑制
# 生成采样频率为 100 Hz 持续时间为 1 秒的正弦信号。 添加更高频率的正弦信号来模拟噪声。
using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing

fs = 100
t = 0:1/fs:1-1/fs
x = sin.(2*pi*t*3)+0.25*sin.(2*pi*t*40)
    
# 使用 10 阶中值滤波器来平滑信号,并绘制结果。

y = medfilt1(x,10)
plot(t,x,t,y)
legend(["Original","Filtered"])

# 示例2：带有尖峰和缺失样本的多通道信号
# 产生由不同频率的正弦波组成的双通道信号。在任意位置放置峰值。使用 NAN 随机添加缺失样本。重置随机数生成器以获得可重现的结果。画出信号。

rng = MersenneTwister(1234)
n = 59
x = sin.(pi ./ [15 10]' * transpose((1:n)[:]) .+ pi / 3)'
spk = rand(rng, 1:2*n, 9, 1)
x[spk] = x[spk] * 2

x[rand(rng, 1:2*n, 6, 1)] .= NaN
figure()
plot(x)

# 使用带有默认设置的 medfilt1 过滤信号。绘制滤波后的信号图。默认情况下，滤波器将 NaN 分配给任何缺失样本段的中值。

y = medfilt1(x)
figure()
plot(y)

# 对原始信号进行转置。再次对其进行筛选，指定该函数沿行运行。计算中位数时排除丢失的样本。如果将第二个参数保留为空，则 medfilt1 使用默认的滤波器阶数3。

y = medfilt1(x', [], [], 2; nanflag = "omitnan")
figure()
plot(y')

# 函数不能给只给包含 NAN 的段赋值。增加段的长度来解决这个问题。此次更改还更彻底地删除了异常值。

y = medfilt1(x, 4, [], []; nanflag = "omitnan")
figure()
plot(y)

# 默认的零填充会导致函数低估边缘的信号值。为了减少这种影响，可以使用减小窗口来计算端点的中位数。

y = medfilt1(x, 4, [], []; nanflag = "omitnan", padding = "truncate");
figure()
plot(y)