function f(io::IO)
    str = read(io, String)
    return str
end
content = open(f, "example.txt", "r")
content = open("example.txt", "r") do file
    read(file, String)
end
println(content)



