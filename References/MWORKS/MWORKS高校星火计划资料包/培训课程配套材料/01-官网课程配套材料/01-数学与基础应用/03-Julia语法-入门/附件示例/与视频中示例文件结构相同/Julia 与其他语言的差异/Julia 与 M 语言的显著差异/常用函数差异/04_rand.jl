using TyRandom

# 使用该种子，可以产生与Matlab一致的随机数
rng = MT19937ar(5489)
rand(rng, 2, 3)
#=
2×3 Matrix{Float64}:
0.814724 0.126987 0.632359
0.905792 0.913376 0.0975404
=#




