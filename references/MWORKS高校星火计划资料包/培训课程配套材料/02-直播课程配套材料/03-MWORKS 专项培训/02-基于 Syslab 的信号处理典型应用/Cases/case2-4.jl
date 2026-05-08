using TySignalProcessing
using TyBase

pkg_dir = pkgdir(TySignalProcessing)
source_path1 = pkg_dir * "/examples/Resource/transitionex.mat"
source_path2 = pkg_dir * "/examples/Resource/negtransitionex.mat"
y = TyBase.load(source_path1)
y2 = TyBase.load(source_path2)
x = y["x"]
x2 = y2["x"]
figure(1)
R, = risetime(x, t; plotfig=true)
# 上升时间
figure(2)
F, = falltime(x2, t; plotfig=true)
# 下降时间
figure(3)
O, = overshoot(x,t; plotfig=true)
# 超调
