from mworks import TySignalProcessing

import numpy as np
from matplotlib import pyplot as plt

fs = 100
t = np.arange(fs + 1) / fs
print(t)
x = np.sin(2 * np.pi * t*3) + 0.25*np.sin(2 * np.pi * t*40)

# 调用信号库函数
y = TySignalProcessing.medfilt1(x, 9)

# 调用图形库函数
plt.plot(t, x, t, y)
plt.legend(np.asarray(["Original", "Filtered"]))
plt.show()