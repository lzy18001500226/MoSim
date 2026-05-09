using TyCommunication
using  TyPlot
# 示例1

# 生成数据序列
data = collect(2:2:12)
# 使用 μ - 律压缩器压缩数据序列,将 μ 的值设置为 255.
compressed = compand(data, 255, maximum(data), "mu/compressor")
# 使用 μ - 律展开器展开压缩数据序列
expanded = compand(compressed, 255, maximum(data), "mu/expander")
# 计算原始数据序列与扩展序列之间的差值
diffvalue = expanded - data

# 生成数据序列
data = collect(1:1:5)
# 使用 A - 律压缩器压缩数据序列,将 A 的值设置为 87.6
compressed = compand(data, 87.6, maximum(data), "A/compressor")
# 使用 A - 律展开器展开压缩数据序列
expanded = compand(compressed, 87.6, maximum(data), "A/expander")
# 计算原始数据序列与扩展序列之间的差值
diffvalue = expanded - data
#========================================================================#
#示例2
ini_codebook = 2^4
# 生成正弦信号
t = (0:100) * pi ./ 20
training_set = cos.(t)
# 生成分界点partition 和 codebook
partition, codebook = lloyds(training_set, ini_codebook)
#量化信号
index, quant, distor = quantiz(training_set, partition, codebook)
# 绘制量化信号及原信号
plot(t, training_set, t, quant, "r.")
legend("original", "Quantized")
#========================================================================#
#示例3
# 生成指数信号
sig = exp.(-4:0.1:4)
V = maximum(sig)
# 量化指数信号
partition = collect(0:2^6-1)
codebook = collect(0:2^6)
_, qsig, distortion = quantiz(sig, partition, codebook)
# 压缩-量化-扩展指数信号
mu = 255 # mu-law parameter
csig_compressed = compand(sig, mu, V, "mu/compressor")
_, quants = quantiz(csig_compressed, partition, codebook)
csig_expanded = compand(quants, mu, maximum(quants), "mu/expander")
distortion2 = sum((csig_expanded - sig) .^ 2) ./ length(sig)
# 比较均方误差
[distortion distortion2]
# 绘图
hold("on")
plot.([sig', qsig', csig_expanded'])
title("Comparison Between Original, Quantized, and Expanded Signals")
xlabel("Interval")
ylabel("Apmlitude")
legend(["Original", "Quantized", "Expanded", "location", "nw"])
axis([0 70 0 20])
