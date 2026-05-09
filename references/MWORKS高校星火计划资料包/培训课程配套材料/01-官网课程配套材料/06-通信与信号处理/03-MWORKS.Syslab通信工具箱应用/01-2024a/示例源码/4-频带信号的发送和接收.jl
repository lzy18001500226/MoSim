using TyCommunication
using  TyPlot
using  TyMath
# 示例1
fs = 100
t = (0:1/fs:100)
fc = 10
# 一个正弦信号
x = sin.(2 * pi * t)
# 使用 ammod 调制正弦信号
ydouble = ammod(x, fc, fs)
# 使用 amdemod 解调
x1 = amdemod(ydouble, fc, fs)
# 绘制原始信号、调制解调后的信号图
figure()
plot(x)
hold("on")
plot(x1)
legend(["Original Signal", "Demodulated Signal"])
xlabel("Time (s)")
ylabel("Amplitude")
#========================================================================#
#示例2
# 设置采样频率
fs = 270000;
t = (0:1/fs:0.01)';
# 生成原始信号
signal = sin.(2 * pi * 300 .* t) .+ 2 * sin.(2 * pi * 600 .* t);
# 使用 12000 的截止频率和 0 的初始相位
fc = 12000;
initialPhase = 0;
# 使用 ssbmod 将原始信号转换为上边带和下边带调制信号
lowerSidebandSignal = ssbmod(signal, fc, fs, initialPhase);
upperSidebandSignal = ssbmod(signal, fc, fs, initialPhase, "upper");
# 解调下边带和上边带信号
s1 = ssbdemod(lowerSidebandSignal, fc, fs);
s2 = ssbdemod(upperSidebandSignal, fc, fs);
# 将处理后的信号与原始信号进行比较并验证重建
figure(1)
plot(t, signal, "k", t, s1, "r:")
hold("on")
plot(t, s2, "-."; color=(0, 1, 0))
hold("off")
xlabel("Time (s)")
ylabel("Amplitude")
legend([
    "Original Signal",
    "Demodulation of Lower Sideband",
    "Demodulation of Upper Sideband"
]);
#========================================================================#
#示例3
# 将采样频率设置为 1kHz，将载波频率设置为 200Hz
fs = 1000;
fc = 200;
# 生成一个持续时间为 0.2s 的时间向量
t = 0:1/fs:0.2
# 生成两个频率为 30 和 60 Hz 的正弦信号并求和
x = sin.(2 * pi * 30 * t) .+ 2 * sin.(2 * pi * 60 * t)
# 将频率偏差设置为 50 Hz
fDev = 50
# 对信号 x 进行频率调制
y = fmmod(x, fc, fs, fDev)
# 对信号 y 进行频率解调
z = fmdemod(y, fc, fs, fDev)
# 绘制原始信号和解调信号
plot(t, x, "r", t, z, "b--");
xlabel("Time (s)")
ylabel("Amplitude")
legend(["Original Signal", "Demodulated Signal"])
#========================================================================#
#示例4
# 将采样频率设置为 50Hz，生成时间向量
Random.seed!(123)
fs = 50
t = (0:2*fs+1) / fs
# 生成正弦输入信号
x = sin.(2 * pi * t) + sin.(4 * pi * t)
# 设置载波频率和相位偏移
fc = 10
phasedev = pi / 2
# 对信号x进行相位调制
y = pmmod(x, fc, fs, phasedev)
# 将调制后信号加入高斯白噪声
yn = awgn(y, 10, "measured")
# 对信号解调
z = pmdemod(yn, fc, fs, phasedev)
# 绘制原始信号和解调信号
figure()
plot(t, [x z])
legend(["Original signal", "Recovered signal"])
xlabel("Time (s)")
ylabel("Amplitude (V)")
#========================================================================#
#示例5
# 设置函数参数
rng = MersenneTwister(1234)
M = 2;     # Modulation order
k = log2(M);  # Bits per symbol
EbNo = 5;   # Eb/No (dB)
Fs = 16;    # Sample rate (Hz)
nsamp = 8;   # Number of samples per symbol
freqsep = 10; # Frequency separation (Hz)
# 生成随机的符号数据
data = rand(rng, 0:M-1, 5000, 1);
# 频移键控调制
txsig = fskmod(data, M, freqsep, nsamp, Fs);
# 通过AWGN信道传递信号
rxSig = awgn(txsig, EbNo + 10 * log10(k) - 10 * log10(nsamp), "measured", 1234);
# 解调接收的信
dataOut = fskdemod(rxSig, M, freqsep, nsamp, Fs);
# 计算误码率
num, BER = biterr(data, dataOut);
# 确定理论误码率,并与估计的误码率进行比较
BER_theory, = berawgn(EbNo, "fsk", M, "noncoherent");
(BER, BER_theory)
#========================================================================#
#示例6
rng = MersenneTwister(1234)
len = 10000;
M = 16;
# 生成随机的符号数据
msg = rand(rng, 0:(M-1), len, 1);
# 相移键控调制
txpsk = pskmod(msg, M);
# 脉冲幅度调制
txpam = pammod(msg, M);
# 生成随机相位噪声
phasenoise = randn(rng, len, 1) * 0.015;
# 相位噪声加入已调信号中
rxpsk = txpsk .* exp.(2im * pi * phasenoise);
rxpam = txpam .* exp.(2im * pi * phasenoise);
# 相移键控解调
recovpsk = pskdemod(rxpsk, M);
# 脉冲幅度解调
recovpam = pamdemod(rxpam, M);
# 计算误差符号数目
numerrs_psk, = symerr(msg, recovpsk);
numerrs_pam, = symerr(msg, recovpam);
#========================================================================#
#示例7
# 生成一个随机符号的三维数组
rng = MersenneTwister(1234)
x = rand(rng, 0:15, 20, 4, 2);
# 根据 WLAN 标准为 16-QAM 星座图创建一个自定义的符号映射
wlanSymMap = [2 3 1 0 6 7 5 4 14 15 13 12 10 11 9 8];
# 对数据进行调制，并将星座图设置为具有单位平均信号功率，绘制出星座图
y = qammod(x, 16, wlanSymMap, UnitAveragePower=true, PlotConstellation=true);
# 对收到的信号进行解调
z = qamdemod(y, 16, wlanSymMap, UnitAveragePower=true);
# 验证解调后的信号是否与原始数据相等
isequal(x, z)
#========================================================================#
#示例8
# 定义调制阶数和 PSK 环半径的向量
rng = MersenneTwister(1234)
M = [8; 12; 16; 28]
modOrder = sum(M)
radii = [0.5; 1; 1.3; 2]
# 生成 100 个随机比特输入符号
x1 = randi(rng, [0 1], Int64(100 * log2(modOrder)), 1)
# 创建一个二进制映射的自定义符号映射向量
cmap = collect(range(0, stop=63))
# 加入高斯白噪声
snr1 = 20
#rxSig = awgn(txSig, snr1, "measured")
# 调制数据，绘制星座图
y = apskmod(x1, M, radii, SymbolMapping=cmap, InputType="bit", PlotConstellation=true)
# 对接收到的信号进行解调
z = apskdemod(y, M, radii, SymbolMapping=cmap, OutputType="bit")
# 与输入数据进行比较
isequal(x1, z)
#========================================================================#
#示例9
# 定义调制阶数和 PSK 环半径的向量。生成随机的 16 位数据符号
rng = MersenneTwister(1234)
M = [4; 12]
radii = [1; 2]
modOrder = sum(M)
x = randi(rng, [0 modOrder - 1], 1000, 1)
# 对数据进行 APSK 调制
txSig = apskmod(x, M, radii)
# 让调制信号通过噪声信道
snr1 = 20
rxSig = awgn(txSig, snr1, "measured")
# 绘制发射(参考)信号点和有噪声的接收信号点
plot(real(rxSig), imag(rxSig), "b*", markerfacecolor="auto")
hold("on")
grid()
plot(real(txSig), imag(txSig), "r+", markerfacecolor="auto")
xlim([-3 3])
ylim([-3 3])
xlabel("In-Phase")
ylabel("Quadrature")
legend(["Received constellation", "Reference constellation"], loc=loc = "upper right")
hold("off")
# 对接收到的信号进行解调，并与输入数据进行比较
z = apskdemod(rxSig, M, radii)
isequal(x, z)
#========================================================================#
#示例10
# 创建 GFSK 调制器和解调器对
rng = MT19937ar(1234)
gfskMod = comm_CPMModulator(;
    ModulationOrder=2,
    FrequencyPulse="Gaussian",
    BandwidthTimeProduct=0.5,
    ModulationIndex=1,
    BitInput=true
);
gfskDemod = comm_CPMDemodulator(;
    ModulationOrder=2,
    FrequencyPulse="Gaussian",
    BandwidthTimeProduct=0.5,
    ModulationIndex=1,
    BitOutput=true
);
# 生成随机位数据并应用 GFSK 调制，使用眼图查看星座
numSym = 100;
x = randi(rng, [0 1], numSym * gfskMod.SamplesPerSymbol, 1);
y = step(gfskMod, x);
eyediagram(y, 16)
# 解调 GFSK 调制的数据
z = step(gfskDemod, y);
delay = 16;
isequal(x[1:(end-delay)], z[(delay+1):end])
