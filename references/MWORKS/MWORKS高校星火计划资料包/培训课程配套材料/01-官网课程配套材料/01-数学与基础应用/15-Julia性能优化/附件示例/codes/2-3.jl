using BenchmarkTools

# 🐢
function f(x)
    if x < 0.5
        return Int(0)
    else
        return Float64(1.0)
    end
end

@code_warntype f(rand())

@btime sum($([f(rand()) for i in 1:1024]));

# 🚀
function f(x)
    if x < 0.5
        return zero(x)
    else
        return one(x)
    end
end

@code_warntype f(rand())

@btime sum($([f(rand()) for i in 1:1024]));
