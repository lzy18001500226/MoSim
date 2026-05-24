using BenchmarkTools

# 🚀
function mysum_colwise(A)
    rst = zero(eltype(A))
    @inbounds for j in axes(A, 2)
        @simd for i in axes(A, 1)
            rst += A[i, j]
        end
    end
    return rst
end

A = rand(1024, 1024);
@btime mysum_colwise(A);

# 🐢
function mysum_rowwise(A)
    rst = zero(eltype(A))
    @inbounds for i in axes(A, 1)
        for j in axes(A, 2)
            rst += A[i, j]
        end
    end
    return rst
end

A = rand(1024, 1024);
@btime mysum_rowwise(A);

# 🚀

function mysum(A)
    rst = zero(eltype(A))
    @inbounds @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024);
@btime mysum(A);


# 🚀🚀

using LoopVectorization

function mysum_turbo(A)
    rst = zero(eltype(A))
    @tturbo for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024);
@btime mysum_turbo(A);
