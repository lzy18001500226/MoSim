using BenchmarkTools

function mysumf_v1(f, A)
    rst = zero(eltype(A))
    @simd for i in eachindex(A)
        rst += f(A[i])
    end
    return rst
end

f1(x) = x > 0 ? x : 0
f2(x) =  x > 0 ? x : zero(x)

A = rand(64, 64)
@btime mysumf_v1(f1, $A);
@btime mysumf_v1(f2, $A);

f3(x) = x > 0 ? x : []
@btime mysumf_v1(f3, $A);

function f4(x)
    if x > 0
        return x
    elseif x > -1
        return Int32(0)
    elseif x > -2
        return Float32(0)
    else
        return Float16(0)
    end
end
