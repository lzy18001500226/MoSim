# open & close
io = open("example.txt", "a+")
io = open("example.txt"; append=true, read=true)
close(io)

# open
function f(io::IO)
    str = read(io, String)
    return str
end
content = open(f, "example.txt", "r")

content = open("example.txt", "r") do file
    read(file, String)
end
println(content)

# read 
io = IOBuffer("Welcome to Syslab.");
read(io, Char)
io = IOBuffer("Welcome to Syslab.");
read(io, String)

read("example.txt")

read("example.txt", String)

io = IOBuffer("Welcome to Syslab.");
read(io, 3)

print(read(`ping www.bing.com`, String))

# read!
io = IOBuffer("Welcome to Syslab.");
array = Vector{UInt8}(undef, 5);
read!(io, array)

let
    array = Vector{UInt8}(undef, 5)
    read!("example.txt", array)
end

# readeach & skipchars
io = IOBuffer("Welcome to Syslab.");
for c in readeach(io, Char)
    c == '\n' && break
    print(c)
end

buf = IOBuffer("    Welcome to Syslab.");
skipchars(isspace, buf);
read(buf, String)

buf = IOBuffer("  # This line is a comment.\n   Welcome to Syslab.");
skipchars(isspace, buf);
read(buf, String)

# eachline
for line in eachline()
    println("Read line: ", line)
end

buf = IOBuffer(" Welcome to Syslab.\nHere is...");
for line in eachline(buf)
    println("Read line: ", line)
end

for line in eachline("example.txt", keep=false)
    println("Read line(with newline): ", repr(line))
end
for line in eachline("example.txt", keep=true)
    println("Read line(with newline): ", repr(line))
end

# readlines
buf = IOBuffer(" Welcome to Syslab.\nHere is...");
lines = readlines(buf)

lines = readlines("example.txt")

# readuntil
buf = IOBuffer(" Welcome to Syslab.\nHere is...");
readuntil(buf, "\n")
readuntil(buf, "\n")


readuntil("example.txt", "\r\n")
readuntil("example.txt", "\n")

# write

# position & peek & seek & skip …
io = IOBuffer("Welcome to Syslab")

# position: 获取当前位置
println("Current position: ", position(io)) # 应该是0，因为我们还没有读取任何内容

# peek: 查看下一个字节但不移动位置
peeked_char = peek(io, Char)
println("Peeked character: ", peeked_char)
println("Position after peek: ", position(io)) # 位置不变,还是0

# read: 读取一个字符，位置会前进
read_char = read(io, Char)
println("Read character: ", read_char)
println("Position after read: ", position(io)) # 位置前进了一个字符

# mark: 标记当前位置
mark(io)
println("Marked position: ", position(io))

# skip: 跳过指定数量的字节
skip(io, 5) # 跳过 5 个字节
println("Position after skip: ", position(io))
