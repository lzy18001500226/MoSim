#case 1
# 依赖PyCall
using PyCall

# 导入python库
math = pyimport("math")

v = math.sin(pi / 2)
println("v = $v")
# v = 1.0


#case 2
using PyCall
using TyPlot # 同元绘图库

# 导入python库
@pyimport numpy as np
x = np.linspace(0, 2pi, 1000)
y = np.sin(x)

# 绘图
plot(x, y)
