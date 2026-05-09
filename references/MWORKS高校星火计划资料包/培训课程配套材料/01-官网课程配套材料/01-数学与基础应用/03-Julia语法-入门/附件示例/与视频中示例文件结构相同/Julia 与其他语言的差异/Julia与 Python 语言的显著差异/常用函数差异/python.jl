
import numpy as np
# 设置全局随机数生成器的 seed
np.random.seed(1234)
# 使用全局随机数，生成 2x3 的均匀分布随机数
np.random.normal(size=(2, 3))
# 新建 seed 为 42 的随机数生成器
rng = np.random.default_rng(seed=42)
# 使用随机数生成器rng，生成 2x4 的正态分布随机数
rng.normal(size=(2, 4))
# 使用随机数生成器rng，生成 2x3 的均匀分布随机数
rng.random(size=(2, 3))


import numpy as np
A = np.asarray([[1., 2.], [3., 4.]])
A + np.eye(2)
# [[2., 2.],
# [3., 5.]]


import numpy as np
np.linspace(-0.1, 0.3, num=5)
# [-0.1, 0. , 0.1, 0.2, 0.3]
