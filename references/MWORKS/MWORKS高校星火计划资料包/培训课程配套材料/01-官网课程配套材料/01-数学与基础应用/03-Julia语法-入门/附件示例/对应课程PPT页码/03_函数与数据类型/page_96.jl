function g(x, y)::Int8
    return x * y
end

typeof(g(1, 2))
function printx(x)
    println("x = $x")
    return nothing
end

r = printx("hello!")
println(r === nothing)



