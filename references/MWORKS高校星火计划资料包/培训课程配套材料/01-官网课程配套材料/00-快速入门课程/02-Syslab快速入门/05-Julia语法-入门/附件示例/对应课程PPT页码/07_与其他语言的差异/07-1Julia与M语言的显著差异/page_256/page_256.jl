A = [1 2 3; 4 5 6; 7 8 9]
# 以下用法与Matlab的 sum(A,'all') 等价
sum(A) # 返回45
# 以下用法与Matlab的 sum(A) 或 sum(A,1) 等价
sum(A, dims=1)
# [12  15  18]
# 以下用法与Matlab的 sum(A,2) 等价
sum(A, dims=2)
#=
3×1 Matrix{Int64}:
 6
15
24
=#




