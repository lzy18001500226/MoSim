import numpy as np
A = np.asarray([[1.0+1.0j, 2.0+1.0j],
        [4.0+1.0j, 5.0+1.0j]])
# 转置
A.T
np.transpose(A)
# [[1.+1.j, 4.+1.j],
# [2.+1.j, 5.+1.j]]
# 共轭转置
A.T.conjugate()
# [[1.-1.j, 4.-1.j],
# [2.-1.j, 5.-1.j]]




