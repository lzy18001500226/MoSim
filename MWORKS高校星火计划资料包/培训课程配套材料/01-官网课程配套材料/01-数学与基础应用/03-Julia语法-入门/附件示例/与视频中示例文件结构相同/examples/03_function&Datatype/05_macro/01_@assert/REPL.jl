# 简单的断言
x = 5
@assert x > 0 "x 必须为正数"

# 没有提供错误信息
z = -1
@assert z >= 0

# 提供错误信息
@assert z >= 0 "z 必须非负数"

