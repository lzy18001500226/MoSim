using BenchmarkTools

function mysum_v1(A::Matrix{Float64})::Float64
    rst = 0.0::Float64
    @simd for i in eachindex(A)
        rst += A[i]::Float64
    end
    return rst::Float64
end

function mysum_v2(A)
    rst = zero(eltype(A))
    @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(64, 64);
@btime mysum_v1($A);
@btime mysum_v2($A);
