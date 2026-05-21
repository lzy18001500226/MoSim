function mysum_v1(X)
    rst = 0.0
    for x in X
        rst += x
    end
    return rst
end

function mysum_v2(X::Vector{Float64})
    rst = 0.0
    for x in X
        rst += x
    end
    return rst
end

using BenchmarkTools
X = rand(4096);
@btime mysum_v2($X);
@btime mysum_v2($X);
