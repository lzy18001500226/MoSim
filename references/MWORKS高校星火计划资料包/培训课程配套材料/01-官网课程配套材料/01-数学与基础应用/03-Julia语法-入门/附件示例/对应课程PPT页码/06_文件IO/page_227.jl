lines = readlines("example.txt")
for line in lines
    println(line)
end
open("example.txt", "r") do file
    for line in eachline(file)
        println(line)
    end
end



