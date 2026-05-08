using TySignalProcessing
using TyBase

pkg_dir = pkgdir(TySignalProcessing)
source_path = pkg_dir * "/examples/Resource/pulseex.mat"
y = TyBase.load(source_path)
x = y["x"]
figure(1)
d, = dutycycle(x,t; plotfig=true)
# 占空比
figure(2)
p, = pulseperiod(x, t; plotfig=true)
# 脉冲周期
figure(3)
w, = pulsewidth(x, t;plotfig=true)
# 脉宽
