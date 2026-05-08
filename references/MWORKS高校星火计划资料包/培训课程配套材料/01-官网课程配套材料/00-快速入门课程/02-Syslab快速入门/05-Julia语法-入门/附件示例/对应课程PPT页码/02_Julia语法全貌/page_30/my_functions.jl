# 使用数学等式定义函数
myfunc1(x) = x^2 + 3 * x + 1
r1 = myfunc1(2)
println("myfunc1(2) = $r1")

# 使用 function 关键字定义函数
function myfunc2(x)
    x^2 + 3 * x + 1
end
r2 = myfunc2(2)
println("myfunc1(2) = $r2")

function myfunc3(x)
    return x^2 + 3 * x + 1
    x
end
r3 = myfunc3(2)
println("myfunc1(2) = $r3")



