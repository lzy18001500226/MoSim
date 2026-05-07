function myprint(a::String, b::String; Delimiter::String=" , ", EndOfLine::String="\n")
    println(a * Delimiter * b * EndOfLine)
end

myprint("Hello", "Julia", Delimiter=" ")
myprint("Hello", "Julia", EndOfLine=".")
myprint("Hello", "Julia")



