using BenchmarkTools

# 🚀
function mysum(A)
    rst = zero(eltype(A))
    @inbounds @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024)

@btime mysum(A)

# 🐢
function mysum(A)
    rst = 0
    @inbounds @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024)

@btime mysum(A)

# 🐢🐢

function mysum(A)
    rst = 0
    @inbounds @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

f() = rand(Bool) ? 0 : 0.5
A = [f() for i in 1:1024, j in 1:1024];
@btime mysum(A);

# 🐢🐢🐢
function mysum(A)
    rst = 0
    for i in 1:size(A, 1)
        for j in 1:size(A, 2)
            rst += A[i, j]
        end
    end
    return rst
end

f() = rand(Bool) ? 0 : 0.5
A = [f() for i in 1:1024, j in 1:1024];
@btime mysum(A);
