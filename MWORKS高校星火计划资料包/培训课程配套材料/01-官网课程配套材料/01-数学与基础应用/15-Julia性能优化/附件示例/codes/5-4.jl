using BenchmarkTools

function f(X, Y, Z)
    M = X .> Y
    C = similar(X)
    C[M] .= X[M] .* Z[M]
    M .= .!M
    C[M] .= X[M] .+ Y[M]
    return C
end

function g(x, y, z)
    return x > y ? x * z : x + y
end


X, Y, Z = rand(4096), rand(4096), rand(4096);
f(X, Y, Z) == g.(X, Y, Z)
@btime f($X, $Y, $Z);
@btime g.($X, $Y, $Z);
