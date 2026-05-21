import numpy as np
def func(x=np.random.rand()):
  print(x)
# 两次运行时的 x 都相同
# np.random.rand() 仅执行了一次
func()
func()




