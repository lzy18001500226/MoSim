open("example.txt", "r") do file
    while !eof(file)
        data = read(file, 1024) # 读取最多 1024 字节
        # 处理数据...
        println(String(data))
    end
end
open("example.txt", "r") do file
    buf = IOBuffer()
    while !eof(file)
        data = read(file, 1024) # 从文件中读取最多 1024 字节
        write(buf, data) # 将读取的数据写入到 IOBuffer 中
    end
    # 处理buf中的数据
    println(String(take!(buf)))
end



