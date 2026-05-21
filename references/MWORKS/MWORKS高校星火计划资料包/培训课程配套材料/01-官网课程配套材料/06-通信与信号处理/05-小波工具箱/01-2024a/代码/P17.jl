# 载入ECG数据
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/BabyECGData.mat"
y = load(source_path)
HR = y["HR"]
seconds = Second.(0:16:(2047 * 16))
unix_t = unix2datetime(0)
times = unix_t + seconds

# 绘制时间序列
figure()
plot(times, HR)
xlabel("Hours")
ylabel("Heart Rate")
xticks([times[1] times[451] times[901] times[1351] times[1801]])
xtickformat("%H:%M:%S", true)
title("ECG Data")

# 使用默认参数进行harrt小波变换（11级）
a, d = haart(HR)
# 逆变换，放弃前4级细节系数
HaarHR = ihaart(a, d, 4)

# 绘制逆变换后的时间序列
figure()
plot(times, HaarHR)
xlabel("Hours")
ylabel("Heart Rate")
xticks([times[1] times[451] times[901] times[1351] times[1801]])
xtickformat("%H:%M:%S", true)
title("Haar Approximation of Heart Rate")
