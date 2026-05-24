# C6E1
using WAV
using TyPlot
using TySignalProcessing
using TyMath
using  TyBase
using TyStatistics
using TyOptimization
y, fs = wavread("RES-example.wav")
Full_sig = vec(y)
ptime = [1/fs:1/fs:length(y)/fs;]
ps = [12, 4] # 声源实际坐标
po1 = [0, 20] # 麦克风1实际坐标
po2 = [0, 0] # 麦克风2实际坐标
po3 = [30, 10] # 麦克风3实际坐标
vsound = 340
o1t = sqrt(sum((po1 - ps) .^ 2)) / vsound
o2t = sqrt(sum((po2 - ps) .^ 2)) / vsound
o3t = sqrt(sum((po3 - ps) .^ 2)) / vsound
n1 = floor(Int,o1t * fs)
n2 = floor(Int, o2t * fs)
n3 = floor(Int, o3t * fs)
mFull_sig = [zeros(30000); Full_sig[1:10000]; zeros(80000)]
mptime = ptime[1:120000]
ro1 = [zeros(n1); mFull_sig[1:end-n1]]
ro2 = [zeros(n2); mFull_sig[1:end-n2]]
ro3 = [zeros(n3); mFull_sig[1:end-n3]]
figure("Voice")
subplot(4, 1, 1);plot(mptime, mFull_sig)
legend(["Souce Signal"]);xlim([0.7, 1.0]);grid("on")
subplot(4, 1, 2);plot(mptime, ro1, color=[0.50, 0.50, 0.50])
grid("on");xlim([0.7, 1.0]);legend(["Senser1 Signal"])
subplot(4, 1, 3)
plot(mptime, ro2, color=[0.65, 0.65, 0.65]);
grid("on");legend(["Senser2 Signal"]);xlim([0.7, 1.0])
subplot(4, 1, 4)
plot(mptime, ro3, color=[0.80, 0.80, 0.80])
grid("on");legend(["Senser3 Signal"]);xlim([0.7, 1.0])

# 互相关计算
xCorr33, lags33 = xcorr(ro3)
xCorr13, lags13 = xcorr(ro1, ro3)
xCorr23, lags23 = xcorr(ro2, ro3)
# 绘图，相关性
figure("Cross Correlation")
subplot(2, 1, 1)
plot(lags13 / fs, xCorr13, color=[0.85, 0.33, 0.10])
xlim([-0.1, 0.1])
grid("on")
title("Senser1 Senser3 Signal Cross correlation")
subplot(2, 1, 2)
plot(lags23 / fs, xCorr23)
xlim([-0.1, 0.1])
grid("on")
title("Senser2 Senser3 Signal Cross correlation")

# 检测
_, I33 = findmax(abs.(xCorr33))
_, I13 = findmax(abs.(xCorr13))
_, I23 = findmax(abs.(xCorr23))
dealy13 = (I33 - I13) / fs
dealy23 = (I33 - I23) / fs
figure("Find Delay")
subplot(1, 2, 1)
plot(mptime, ro1)
hold("on")
plot(mptime, ro3)
grid("on")
xlim([0.95, 0.97])
title("delay13 = $dealy13 Second")
subplot(1, 2, 2)
plot(mptime, ro2)
hold("on")
plot(mptime, ro3)
grid("on")
xlim([0.9, 0.98])
title("delay23 = $dealy23 Second")

function fun(x)
        xo1, yo1 = [0, 20]
        xo2, yo2 = [0, 0]
        xo3, yo3 = [30, 10]
        delay13 = -0.0030385489f0
        delay23 = 0.018594105f0
        vsound = 340
        out = [(x[1] - xo1)^2 + (x[2] - yo1)^2 - (x[3] - delay13 * vsound)^2
            (x[1] - xo2)^2 + (x[2] - yo2)^2 - (x[3] - delay23 * vsound)^2
            (x[1] - xo3)^2 + (x[2] - yo3)^2 - x[3]^2]
        return out
    end
x0 = [5, 5, 10]
result = fsolve(fun, x0)
xe = result[1]
    
figure("Estimate Position")
title("Indoor")
u = [-pi:0.01:pi;]
mt1x = 0 .+ sin.(u) * 5
mt1y = 0 .+ cos.(u) * 5
plot(mt1x, mt1y)
hold("on")
mt2x = 8 .+ sin.(u) * 6.8
mt2y = 8 .+ cos.(u) * 6.8
plot(mt2x, mt2y)
mt3x = -8 .+ sin.(u) * 14.5
mt3y = 15 .+ cos.(u) * 14.5
plot(mt3x, mt3y)
text(ps[1], ps[2], "True Position", va="bottom", ha="center", color="blue", bbox=Dict("edgecolor" => "k", "facecolor" => "w"))
text(xe[1], xe[2], "Estimate Position", va="bottom", ha="center", color="blue", bbox=Dict("edgecolor" => "k", "facecolor" => "w"))
grid("on")
xlabel("m")
ylabel("m")
xlim([-25, 25])
ylim([-15, 35])
axis("square")
text(8, 9, "O1", va="bottom", ha="center", color="blue", bbox=Dict("edgecolor" => "k", "facecolor" => "w"))
text(-8, 16, "O2", va="bottom", ha="center", color="blue", bbox=Dict("edgecolor" => "k", "facecolor" => "w"))
text(0, 1, "O3", va="bottom", ha="center", color="blue", bbox=Dict("edgecolor" => "k", "facecolor" => "w"))
plot(0, 0, "r*", 8, 8, "r*", -8, 15, "r*")
plot(2, 4.62757, "r*")


