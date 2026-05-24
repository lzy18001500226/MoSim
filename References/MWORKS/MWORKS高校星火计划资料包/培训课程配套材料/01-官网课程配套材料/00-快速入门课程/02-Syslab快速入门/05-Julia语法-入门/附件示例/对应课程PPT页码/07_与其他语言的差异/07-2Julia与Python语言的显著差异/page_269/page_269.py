import numpy as np
# 内置的整数类型不会溢出
2**64 #  18446744073709551616
# numpy 的默认整数类型为 32 位或者 64 位
# windows 上为 dtype('int32')
# linux 上位 dtype('int64')
x = np.array(2)
x.dtype
# 整数运算可能溢出
x**64 # 0

