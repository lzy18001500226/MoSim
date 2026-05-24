using LinearAlgebra
using BenchmarkTools

Xd = Diagonal([1, 2, 3, 4])
# 4x4 Diagonal{Int64, Vector{Int64}}:
# 1 . . .
# . 2 . .
# . . 3 .
# . . . 4

X = collect(Xd)
# 4x4 Matrix{Int64}:
# 1 0 0 0
# 0 2 0 0
# 0 0 3 0
# 0 0 0 4

Xd == X
# true

Xd = Diagonal(rand(512));

X = collect(Xd);

@btime Xd * Xd;

@btime X * X;

Xd * Xd == X * X
# true

function mysum(A)
    rst = zero(eltype(A))
    @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end
# mysum (generic function with 1 method)

@btime mysum(Xd);

@btime mysum(X);

mysum(X::Diagonal) = mysum(X.diag)
# mysum (generic function with 2 methods)

@btime mysum(Xd);
# 43.735 ns (1 allocation: 16 bytes)
