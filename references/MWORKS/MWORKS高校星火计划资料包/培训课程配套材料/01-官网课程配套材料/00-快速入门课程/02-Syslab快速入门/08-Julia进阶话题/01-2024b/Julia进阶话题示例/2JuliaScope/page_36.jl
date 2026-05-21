s = 0 # global `s`
for i = 1:5
    y = s + i # new local `y` 
    println(y)
end
