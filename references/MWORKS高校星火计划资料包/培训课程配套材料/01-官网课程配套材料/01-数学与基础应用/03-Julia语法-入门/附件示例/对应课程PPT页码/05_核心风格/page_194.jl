function mysum(A)
    rst = 0
    @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

A = rand(1024, 1024);
@btime mysum($A);

@code_warntype mysum(rand(4, 4))


function mysum(A)
    rst = zero(eltype(A))
    @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end
A = rand(1024, 1024);
@btime mysum($A);