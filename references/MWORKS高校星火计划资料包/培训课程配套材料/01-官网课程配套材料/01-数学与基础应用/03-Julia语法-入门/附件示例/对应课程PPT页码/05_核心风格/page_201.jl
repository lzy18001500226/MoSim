# ok
[1 2 3] .* 2

# ok
a = [0 0 0
    10 10 10
    20 20 20
    30 30 30]
b = [1 2 3]
a .+ b

# ok
a = [0 10 20 30]'
b = [1 2 3]
a .+ b

# 报错
a = [0 0 0
    10 10 10
    20 20 20
    30 30 30]
b = [1 2 3 4]
a .+ b


X = rand(10^6)
@time y1 = sin.(cos.(X))
# 0.013138 seconds (6 allocations: 7.630 MiB)

@time y2 = @. sin(cos(X))
# 0.011807 seconds (6 allocations: 7.630 MiB)

@time y3 = broadcast(x -> sin(cos(x)), X)
# 0.038181 seconds (66.00 k allocations: 12.112 MiB

@time y4 = [sin(cos(x)) for x in X]
# 0.038181 seconds (66.00 k allocations: 12.112 MiB

@time y5 = map(x -> sin(cos(x)), X)
# 0.030999 seconds (25.80 k allocations: 9.350 MiB
