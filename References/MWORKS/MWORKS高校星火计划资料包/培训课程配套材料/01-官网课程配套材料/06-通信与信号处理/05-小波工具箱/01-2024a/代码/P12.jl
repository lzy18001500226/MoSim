# 载入啁啾信号
using TyWavelet
pkg_dir = pkgdir(TyWavelet)
source_path = pkg_dir * "/examples/Resources/quadchirp.mat"
y = load(source_path)
quadchirp = y["quadchirp"]
tquad = y["tquad"]
# 绘制信号
figure()
plot(tquad[501:1500], quadchirp[501:1500])
# 同步挤压小波变换 sst为小波系数，f为小波系数对应的频率轴
sst, f = wsst(quadchirp)
# 提取小波脊，fridge为瞬时频率，iridge为瞬时频率对应的索引
fridge, iridge = wsstridge(sst)
# 绘制时频谱
figure()
h = pcolor(tquad, f, abs.(sst))
h.set_edgecolor("flat")
title("Synchrosqueezed Transform")
hold("on")
plot(tquad, fridge; linewidth=2)
title("Synchrosqueezed Transform with Overlaid Ridge")
