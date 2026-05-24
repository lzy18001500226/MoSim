function f(x)
    if x < 0.5
        return Int(0)
    else
        return Float64(1.0)
    end
end
@code_warntype f(rand())
@btime sum($([f(rand()) for i in 1:1024]));


function f(x)
    if x < 0.5
        return zero(0)
    else
        return one(1.0)
    end
end
@code_warntype f(rand())
@btime sum($([f(rand()) for i in 1:1024]));


@code_warntype f(1)
@code_warntype f(1.0)