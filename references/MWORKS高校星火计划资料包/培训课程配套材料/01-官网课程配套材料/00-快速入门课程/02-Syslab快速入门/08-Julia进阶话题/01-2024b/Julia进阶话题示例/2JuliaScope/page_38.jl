# s = 0 # global `s`
# for i = 1:5
#     s = s + i # local `s`
#     println("Inside for loop: s=$s")
# end
# println("Outside for loop: s=$s")


function foo()
    s = 0 # local `s`
    for i = 1:5
        s = s + i # assign existing local `s`
        println("Inside for loop: s=$s")
    end
    println("Outside for loop: s=$s")
end
foo()
