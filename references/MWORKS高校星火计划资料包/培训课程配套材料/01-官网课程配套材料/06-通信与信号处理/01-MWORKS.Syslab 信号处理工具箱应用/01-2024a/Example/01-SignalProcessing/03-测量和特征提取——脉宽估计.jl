# 示例1：二值波形的脉冲宽度
# 计算以4MHz采样的双电平波形的脉冲宽度。

using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing

pkg_dir = pkgdir(TySignalProcessing)
source_path = pkg_dir * "/examples/Resource/pulseex.mat"
y = load(source_path)
x = y["x"]
t = y["t"]
# 脉冲宽度
figure()
w, = pulsewidth(x, t; plotfig=true)


# 占空比
fs = 1 / (t[2] - t[1])
figure()
d = dutycycle(x, fs; plotfig=true)

# 周期
figure()
p, = pulseperiod(x, t; plotfig=true)

# 脉冲间隔
figure()
s, = pulsesep(x, t; plotfig=true)