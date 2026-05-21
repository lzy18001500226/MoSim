# 字符串
S = "text"
# 字符串
C = 'text'


# 字符串拼接
S = "text" + "123"  # "text123"
# 字符串重复 3 次
S = "ab" * 3  # "ababab"


import numpy as np
# 内置的整数类型不会溢出
2**64  #  18446744073709551616
# numpy 的默认整数类型为 32 位或者 64 位
# windows 上为 dtype('int32')
# linux 上位 dtype('int64')
x = np.array(2)
x.dtype
# 整数运算可能溢出
x**64  # 0


# 创建可存储任意元素的列表
list = [1, "abc", 2.1]
# 往列表内添加元素
list.append("text")
# 创建可存储任意元素的字典
dict = {"a": 1, "b": "abc"}


x = None
# 使用 x is not None 来判断值是不是 None
if x is not None:
    print("abc")
