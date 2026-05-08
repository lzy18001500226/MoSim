import TyRandom, Random
# 设置全局随机数生成器的 seed
Random.seed!(1234)
# 使用全局随机数，生成 2x3 的均匀分布随机数
randn((2, 3))
# 新建 seed 为 42 的随机数生成器
rng = TyRandom.MT19937ar(42)
#使用随机数生成器rng，生成 2x4 的正态分布随机数
randn(rng, (2, 4))
#使用随机数生成器rng，生成 2x3 的均匀分布随机数
rand(rng, (2, 3))


using LinearAlgebra
A = [1.0 2.0; 3.0 4.0]
# 可使用 I 表示单位矩阵
A + I
# [2.0 2.0
# 3.0 5.0]



collect(range(-0.1, 0.3, length=5))
# [-0.1, 0. , 0.1, 0.2, 0.3]
