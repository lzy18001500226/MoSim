#
# 该示例演示了如何调用python函数
# 参考：https://blog.csdn.net/wowotuo/article/details/115583435
# 

# 调用python现成库中函数

using PyCall

#case 1
math = pyimport("math")

v = math.sin(pi/2)
println("v = $v")

#case 2
using TyPlot
@pyimport numpy as np
x = np.linspace(0, 2π, 1000)
y = np.sin(x)
plot(x,y)
