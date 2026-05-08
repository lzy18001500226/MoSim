# 单线程 sum
using BenchmarkTools

function mysum(A)
    rst = zero(eltype(A))
    @inbounds @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024)

@btime mysum(A)

# 多线程 sum
using BenchmarkTools
using LoopVectorization

function mysum(A)
    rst = zero(eltype(A))
    @tturbo for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024)

@btime mysum(A)
