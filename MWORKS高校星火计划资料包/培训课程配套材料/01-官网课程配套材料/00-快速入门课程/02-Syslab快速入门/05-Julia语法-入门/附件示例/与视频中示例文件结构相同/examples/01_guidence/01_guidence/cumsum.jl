function cumsum(x)
    ret = similar(x)
    _sum = 0.0
    @inbounds for i in eachindex(x)
        _sum += x[i]
        ret[i] = _sum
    end
    return ret
end
x = rand(100);
using BenchmarkTools
@btime ret = cumsum(x);
