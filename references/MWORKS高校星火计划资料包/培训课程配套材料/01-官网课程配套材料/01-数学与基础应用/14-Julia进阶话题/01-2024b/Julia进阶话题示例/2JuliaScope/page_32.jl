function foo()
    global x
    x = 2
    return x
end
x = 1
foo()
@show x

z = -1
let x = 1, y = 2
    z = x + y
    @show z
end
@show z
