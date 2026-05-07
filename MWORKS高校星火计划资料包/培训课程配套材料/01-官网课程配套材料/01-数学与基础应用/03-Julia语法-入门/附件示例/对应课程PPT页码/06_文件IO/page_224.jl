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



