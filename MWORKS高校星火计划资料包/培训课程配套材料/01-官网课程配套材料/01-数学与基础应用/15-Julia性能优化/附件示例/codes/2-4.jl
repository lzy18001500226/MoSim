using BenchmarkTools

# 🐢
function mysum(A)
    rst = zero(eltype(A))
    @simd for i in eachindex(A)
        rst += A[i]
    end
    return rst
end

gen_data(f, n::Int) = [f() for i in 1:n, j in 1:n]

f_slow() = rand(Bool) ? 0 : 1.0
h(n) = mysum(gen_data(f_slow, 1024))

@btime h(1024);

# 🚀
f_fast() = rand(Bool) ? 0.0 : 1.0
h(n) = mysum(gen_data(f_fast, 1024))

@btime h(1024);
