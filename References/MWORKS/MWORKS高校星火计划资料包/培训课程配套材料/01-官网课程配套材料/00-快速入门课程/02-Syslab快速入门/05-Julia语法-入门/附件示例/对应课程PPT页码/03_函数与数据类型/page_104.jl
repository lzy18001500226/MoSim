a = 1
typeof(a) #操作系统为64位
max = typemax(Int64)
max + 1 #超限
min = typemin(Int64)
min - 1 #超限
x = typeof(0x123)
Int64(0x123) #转化为Int64



