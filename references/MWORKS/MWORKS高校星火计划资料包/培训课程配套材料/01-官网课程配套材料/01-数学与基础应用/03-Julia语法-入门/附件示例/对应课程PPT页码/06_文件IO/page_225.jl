# ismarked: 检查是否有标记
println("Is marked? ", ismarked(io))# reset: 重置到最近的标记
reset(io)
println("Position after reset: ", position(io)) # 回到标记的位置# unmark: 移除标记
unmark(io)
println("Is marked after unmark? ", ismarked(io))
# seek: 移动到指定位置
seek(io, 10)
println("Position after seek: ", position(io))
# seekstart: 移动到开始
seekstart(io)
println("Position after seekstart: ", position(io))
# seekend: 移动到末尾
seekend(io)
println("Position after seekend: ", position(io))
# 关闭 IOBuffer
close(io)



