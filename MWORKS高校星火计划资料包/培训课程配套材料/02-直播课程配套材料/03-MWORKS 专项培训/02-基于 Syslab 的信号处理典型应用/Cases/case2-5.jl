using TySignalProcessing
using TyMath

rng = MT19937ar(1234)
t = 0:0.001:1-0.001;
x = cos.(2 * pi * 100 * t) + randn(rng, size(t));
# 高斯白噪声中创建100Hz余弦波
x = vec(x)
pband = bandpower(x, 1000, [50 150]);
# 50Hz和150Hz频率总功率
ptot = bandpower(x, 1000, [0 500]);
per_power = 100 * (pband / ptot)
# 确定指定频率功率百分比
