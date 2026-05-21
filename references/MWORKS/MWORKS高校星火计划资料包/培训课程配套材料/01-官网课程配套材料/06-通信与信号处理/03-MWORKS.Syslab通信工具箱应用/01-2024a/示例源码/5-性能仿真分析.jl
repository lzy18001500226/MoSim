using TySignalProcessing
using TyPlot
using TyMath
using TyCommunication
# 示例1
Random.seed!(1234)
c = [-5 -5im 5 5im -3 -3 - 3im -3im 3 - 3im 3 3 + 3im 3im -3 + 3im -1 -1im 1 1im];
sigpower = pow2db(mean(abs.(c) .^ 2));
M = length(c);
# 生成随机符号
data = randi([0 M - 1], 2000, 1);
# 使用genqammod函数调制数据
modData = genqammod(data, c);
# 通过具有 20 dB SNR 的 AWGN 通道传递信号
rxSig = awgn(modData, 20, sigpower);
# 显示接收信号的星座图
scatterplot(rxSig);
hold("on")
# 参考星座的星座图
scatterplot(c)
grid("on")
hold("off")
# 使用genqamdemod函数解调接收到的信号
demodData = genqamdemod(rxSig, c);
# 确定符号错误的数量及误码率
numErrors1, ser1 = symerr(data, demodData)
# 通过具有 10 dB SNR 的 AWGN 通道传递信号
rxSig = awgn(modData, 10, sigpower);
# # 使用genqamdemod函数解调接收到的信号
demodData = genqamdemod(rxSig, c);
# 确定符号错误的数量及误码率
numErrors2, ser2 = symerr(data, demodData)
#========================================================================#
#示例2
rng = MT19937ar(1234)
data = randi(rng, [0 3], 1000, 1);
modsig = pskmod(data, 4, pi / 4);
tmp = awgn(modsig, 10)
sps = 4;
txfilter = comm_RaisedCosineTransmitFilter(; OutputSamplesPerSymbol=sps);
txsig = step(txfilter, tmp);
# 生成未过滤的OPSK信号眼图
eyediagram(tmp, 2 * sps)
# 生成过滤后的OPSK信号眼图
eyediagram(txsig, 2 * sps)
#========================================================================#
#示例3
rng = MT19937ar(1234)
data = randi(rng, [0 1], 6000, 1)
modsig1 = pskmod(data, 2; InputType="bit");
modsig2 = pskmod(data, 4; InputType="bit");
modsig3 = pskmod(data, 8; InputType="bit");
modsig4 = pskmod(data, 16; InputType="bit");
subplot(2, 2, 1)
scatterplot(modsig1)
title("BPSK星座图")
subplot(2, 2, 2)
scatterplot(modsig2)
title("QPSK星座图")
subplot(2, 2, 3)
scatterplot(modsig3)
title("8PSK星座图")
subplot(2, 2, 4)
scatterplot(modsig4)
title("16PSK星座图")
sgtitle("加噪前信号星座图"; fontsize=14)
tightlayout()
# 加噪后
txsig1 = awgn(modsig1, 20)
txsig2 = awgn(modsig2, 20)
txsig3 = awgn(modsig3, 20)
txsig4 = awgn(modsig4, 20)
figure()
subplot(2, 2, 1)
scatterplot(txsig1)
title("BPSK星座图")
subplot(2, 2, 2)
scatterplot(txsig2)
title("QPSK星座图")
subplot(2, 2, 3)
scatterplot(txsig3)
title("8PSK星座图")
subplot(2, 2, 4)
scatterplot(txsig4)
title("16PSK星座图")
sgtitle("加噪后信号星座图"; fontsize=14)
tightlayout()
#========================================================================#
#示例4
# 设置RPC滤波器、调制方案和绘图参数
span = 10;
rolloff = 0.2;
sps = 8;
M = 4;
k = log2(M);
phOffset = pi / 4;
n = 1;
offset = 0;
#创建滤波器系数     
filtCoeff = rcosdesign(rolloff, span, sps);
rng = MT19937ar(5489)
data = randi(rng, [0 M - 1], 5000, 1);
#QPSK调制
dataMod = pskmod(data, M, phOffset);
# 过滤调制数据
txSig = upfirdn(vec(dataMod), filtCoeff, sps);
EbNo = 20;
snr1 = EbNo + 10 * log10(k) - 10 * log10(sps);
rxSig = awgn(txSig, snr1, "measured");
# 应用 RRC 接收过滤器
rxSigFilt = upfirdn(vec(rxSig), filtCoeff, 1, sps);
# 解调过滤后的信号
dataOut = pskdemod(rxSigFilt, M, phOffset, "gray");
# 使用该scatterplot函数显示滤波前后信号的散点图
scatterplot(sqrt(sps) * txSig[sps*span+1:end-sps*span], sps, offset);
hold("on")
scatterplot(rxSigFilt[span+1:end-span], n, offset)
scatterplot(dataMod, n, offset)
legend(["Transmit Signal", "Received Signal", "Ideal", "location", "best"])
xlim([-1 1])
ylim([-1 1])
hold("off")
figure()
# 显示两个符号周期内传输信号眼图的 1000 个点
eyediagram(txSig[sps*span+1:sps*span+1000], 2 * sps)
figure()
# 显示接收信号眼图的 1000 点
eyediagram(rxSig[sps*span+1:sps*span+1000], 2 * sps)
