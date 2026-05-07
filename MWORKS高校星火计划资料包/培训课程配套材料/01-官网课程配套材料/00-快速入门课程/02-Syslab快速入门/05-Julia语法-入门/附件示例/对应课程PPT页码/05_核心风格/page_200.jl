@time begin
    t = 0:0.01:10
    y = Vector{Float64}(undef, length(t))
    for i in eachindex(t)
        y[i] = sin(t[i])
    end
end
# 耗时约 0.000118 seconds

@time begin
    t = 0:0.01:10
    y = sin.(t)
end
# 耗时约 0.000036 seconds

function loop_sum()
    s = 0.0
    for k = 1:1000_000
        s += 1.0 / (k * k)
    end
    return s
end
@time y = loop_sum()
# 0.001474 seconds (1 allocation: 16 bytes)


function vec_sum()
    k = 1:1:1000_000
    s = sum(1 ./ (k .* k))
    return s
end
@time y = vec_sum()
# 0.001764 seconds (3 allocations: 7.629 MiB)


