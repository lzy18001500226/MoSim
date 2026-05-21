#  使用 Python numpy 的 kurtosis 实现
import numpy as np

def kurtosis(X):
    mu = np.mean(X)
    n = len(X)
    tmp = (X - mu)**2
    fourth_moment = np.sum(tmp**2) / n
    second_moment = np.sum(tmp) / n
    return fourth_moment / (second_moment**2)



