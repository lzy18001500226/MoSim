# 载入数据
using TyWavelet
FBGsig = pkgdir(TyWavelet) * "/examples/Resources/FBGsig.mat"
y = load(FBGsig)
smoothed_FBG_signal = y["smoothed_FBG_signal"]
Fs = y["Fs"]
t = (1 / Fs):(1 / Fs):(length(smoothed_FBG_signal) / Fs)
t = t .* 1000
# 绘制数据
plot(t, smoothed_FBG_signal)
xlabel("Time (ms)")
ylabel("Amplitude (V)")

# 补零后信号长度
n = 65536

# 傅里叶变换
Y = ty_fft(smoothed_FBG_signal, n)
f = Fs * (0:(n / 2)) / n

# 绘制单边带谱
P2 = abs.(Y / n)
P1 = P2[1:Int(n / 2 + 1)]
P1[2:(end - 1)] = 2 * P1[2:(end - 1)]
plot(f, P1)
title("Single-Sided Spectrum of Padded Signal")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([0 10000])

# 连续小波变换，指定频率精细度以及频率范围
cfs, fwt, = cwt(smoothed_FBG_signal, Fs; VoicesPerOctave=48, FrequencyLimits=[
    0
    20000
])
img1 = pcolor(t, fwt, abs.(cfs))
img1.set_edgecolor("flat")
xlim([0, 10])
xlabel("Time (ms)")
ylabel("Frequency (Hz)")

# 同步挤压小波变换，指定频率精细度
sst, fsst = wsst(smoothed_FBG_signal, Fs; VoicesPerOctave=48)
img2 = pcolor(t, fsst, abs.(sst))
img2.set_edgecolor("flat")
xlim([0, 10])
ylim([0, 20000])
xlabel("Time (ms)")
ylabel("Frequency (Hz)")

# 选定频率和时间范围，提取小波脊
freqIdx = fsst .> 6000 .&& fsst .< 8200
sigIdx = 1501:3500
fridge, = wsstridge(sst[freqIdx, sigIdx], fsst[freqIdx])
plot(t[sigIdx], fridge)
xlabel("Time (ms)")
ylabel("Frequency (Hz)")

# 小波脊的频率分析
n1 = length(fridge)
Y1 = ty_fft(fridge, n1)
f1 = Fs * (0:(n1 / 2)) / n1
P4 = abs.(Y1 / n1)
P3 = P4[1:(Int(n1 / 2) + 1)]
P3[2:(end - 1)] = 2 * P3[2:(end - 1)]
plot(f1, P3)
title("Single-Sided Spectrum of Padded Signal")
xlabel("f (Hz)")
ylabel("|P1(f)|")
xlim([200, 5000])
ylim([0, 500])
