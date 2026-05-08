function f(x)
    if x isa AbstractFloat
        return 3.0 * x
    elseif x isa Integer
        return 2 * x
    else
        return zero(x)
    end
end

@code_warntype f(1.0)

g(x::AbstractFloat) = 3.0 * x
g(x::Integer) = 2 * x
g(x) = zero(x)
