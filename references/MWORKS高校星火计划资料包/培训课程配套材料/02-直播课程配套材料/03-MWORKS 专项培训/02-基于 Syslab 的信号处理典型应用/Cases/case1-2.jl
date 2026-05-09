using TySignalProcessing
using TyPlot

pkg_dir = pkgdir(TySignalProcessing)
source_path =pkg_dir * "/examples/SignalGenerationAndPreprocessing/SmoothingAndDenoising/sgolayfilt/data_sgolayfilt.jl"
include(source_path)
t = (0:(length(mtlb) - 1)) / Fs;
rd = 9;
fl = 21;
smtlb = sgolayfilt(mtlb, rd, fl);
# SG滤波
kmtlb = sgolayfilt(mtlb, rd, fl, kaiser(fl, 38));
# 指定凯撒窗为权重向量的SG滤波  
subplot(2, 1, 1)
plot(t, mtlb);
axis([0.2 0.22 -3 2]);
title("Original");grid()
subplot(2, 1, 2)
plot(t, smtlb);
hold("on");
title("Filtered");
grid()
plot(t, kmtlb);
axis([0.2 0.22 -3 2]);
hold("off")
tightlayout()