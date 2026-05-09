for line in eachline()
    println("Read line: ", line)
end

buf = IOBuffer("Welcome to Syslab.\nHere is...");
for line in eachline(buf)
    println("Read line: ", line)
end

for line in eachline("example.txt", keep=false)
    println("Read line(with newline): ", repr(line))
end

for line in eachline("example.txt", keep=true)
    println("Read line(with newline): ", repr(line))
end



