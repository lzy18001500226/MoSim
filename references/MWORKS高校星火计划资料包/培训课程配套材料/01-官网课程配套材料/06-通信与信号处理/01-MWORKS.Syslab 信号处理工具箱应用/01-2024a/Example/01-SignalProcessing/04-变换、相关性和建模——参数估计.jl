# 示例1：使用协方差法进行参数估计

# 使用多项式系数向量通过过滤 1024 个白噪声样本来生成 AR(4) 过程。使用协方差方法估计系数。
using TyBase
using TyMath
using TyPlot
using TyControlSystems
using TySignalProcessing

rng = MersenneTwister(1234)
A = [1, -2.7607, 3.8106, -2.6535, 0.9238];
y, = filter1([1], A, 0.2 * randn(rng, 1024));
arcoeffs, = armcov(y, 4)

# 生成过程的 50 个实现，每次改变输入噪声的方差。将协方差估计的方差与实际值进行比较。

nrealiz = 50;
noisestdz = rand(rng, 1, nrealiz) .+ 0.5;
randnoise = randn(rng, 1024, nrealiz);
noisevar = zeros(1, nrealiz);
for k = 1:nrealiz
    y, = filter1([1], A, noisestdz[k] * randnoise[:, k])
    arcoeffs, noisevar[k] = arcov(y, 4)
end
plot(noisestdz .^ 2, noisevar, "*")
title("Noise Variance")
xlabel("Input")
ylabel("Estimated")

# 使用函数的多通道语法重复该过程。
Y, = filter1([1], A, noisestdz .* randnoise);
coeffs, variances = arcov(Y, 4);
hold()
plot(noisestdz .^ 2, variances, "o")
hold("off")
legend(["Single channel loop", "Multichannel"])
