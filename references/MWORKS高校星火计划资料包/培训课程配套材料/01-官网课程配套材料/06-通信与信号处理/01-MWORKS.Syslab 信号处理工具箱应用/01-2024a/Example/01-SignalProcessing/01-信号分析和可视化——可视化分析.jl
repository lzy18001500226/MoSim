
# 示例1：调频正弦曲线的条形图
# 在 0.25 秒的条带中绘制两秒的调频正弦波。指定 1 kHz 的采样率。

using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing
using TyOptimization
using   TyStatistics

fs = 1000;
t = [0:(1 / fs):2;];
x = vco(sin.(2 * pi * t), [10, 490], fs);

strips(x, 0.25, fs);

# 示例2：语音信号的条形图
# 加载以 Fs =7418Hz 采样的语音信号。

pkg_dir = pkgdir(TySignalProcessing);
source_path = pkg_dir * "/examples/Resource/mtlb.mat";
y = load(source_path);
    
# 在 0.18 秒长的条带中绘制该信号。

mtlb = y["mtlb"];
Fs = y["Fs"];
strips(mtlb, 0.18, Fs);