from tjc_common import *
from tyjuliacall import Main
from tyjuliacall import JuliaEvaluator

# 调用Julia代码
JuliaEvaluator[
    r"""mutable struct S
        x :: Int
        y :: Int
    end"""
]
S = JuliaEvaluator["S"]
s = S(1, 2)
print(s.x)
print(s.y)

# 修改字段
s.x = 10
s.y = 5
print(s.x)
print(s.y)
