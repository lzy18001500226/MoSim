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




