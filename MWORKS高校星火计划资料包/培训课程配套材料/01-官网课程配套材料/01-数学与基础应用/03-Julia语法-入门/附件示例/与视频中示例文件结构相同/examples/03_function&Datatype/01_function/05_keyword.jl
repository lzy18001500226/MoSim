function myprint(a::String, b::String; Delimiter::String=" , ", EndOfLine::String="\n")
    println(a * Delimiter * b * EndOfLine)
end
# myprint (generic function with 1 method)

myprint("Hello", "Julia", Delimiter=" ")
# Hello Julia
