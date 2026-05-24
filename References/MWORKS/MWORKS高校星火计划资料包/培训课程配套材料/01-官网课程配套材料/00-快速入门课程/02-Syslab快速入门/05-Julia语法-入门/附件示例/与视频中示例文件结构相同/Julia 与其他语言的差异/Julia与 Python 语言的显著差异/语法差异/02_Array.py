import numpy as np
# 创建向量 [1,2,3]
np.asarray([1, 2, 3])
# 创建 2x3 的矩阵
np.asarray([[1, 2, 3], [4, 5, 6]])


import numpy as np
x = np.asarray([1, 2, 3, 4, 5])
# 取第 1 个元素
x[0]  # 1
# 取最后一个（第 5 个）元素
x[-1]  # 5
# 取第 2 个到第 4 个元素
x[1:4]  # [2, 3, 4]

# 取第 2 个到最后一个元素
x[1:]  # [2, 3, 4, 5]


import numpy as np
x = np.asarray([1, 2, 3, 4, 5, 6])
# 取偶数位的元素
x[1::2]  # [2, 4, 6]
# 数组翻转，也可使用 np.flip(x)
x[::-1]  # [6, 5, 4, 3, 2, 1]


import numpy as np
A = np.asarray([[1, 2, 3], [4, 5, 6]])
A.flatten()  # [1,2,3,4,5,6]


import numpy as np
A = np.asarray([[1, 2, 3], [4, 5, 6]])
# 线性索引取第 3 个元素
# 按行主序方向遍历
A.flat[2]  # 3
# 取矩阵的第二行
A[1]   # [4,5,6]
A[1, :]  # [4,5,6]






import numpy as np
A = np.asarray([[1, 2, 3], [4, 5, 6]])
# 创建新的数组，修改B不会影响A
B = np.copy(A[0, :])
B[0] = 100
# 创建视图，修改C,A也会被修改
C = A[0, :]
C[0] = 100
"""
A=[[100,2,3],
[4,5,6]]
"""


import numpy as np
A = np.asarray([[1, 2, 3], [4, 5, 6]])
# 每个元素都增加 1
A + 1  # [[2, 3 4], [5 6 7]]
# 第 1,2,3 列分别乘以 1,2,3
A * np.asarray([[1, 2, 3]])
# [[1, 4, 9], [4, 10, 18]]
# 和 1 维向量广播时
# 1 维向量扩展为 1xn 的矩阵
# 第 1,2,3 列分别减去 1,2,3
A - np.asarray([1, 2, 3])
# [[0, 0, 0], [3, 3, 3]]







import numpy as np
A = np.asarray([[1, 2], [3, 4]])
B = np.asarray([[0, 1], [1, 0]])
# 矩阵乘法
A @ B
# [[2, 1],
# [4, 3]]


import numpy as np
A = np.asarray([[1.0 + 1.0j, 2.0 + 1.0j],
                [4.0 + 1.0j, 5.0 + 1.0j]])
# 转置
A.T
np.transpose(A)

# 共轭转置
A.T.conjugate()
# [[1.-1.j, 4.-1.j],
# [2.-1.j, 5.-1.j]]




import numpy as np
x = np.asarray([[1., 2., 3.], [4., 5., 6.]])
# 垂直拼接
np.vstack((x, np.ones((1, 3))))



# 水平拼接
np.hstack((x, np.ones((2, 1))))

