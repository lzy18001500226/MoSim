s = 0 # global `s`
for i = 1:5
    global s
    s = i # new local `s`
    println("Inside for loop: s=$s")
end
println("Outside for loop: s=$s")
