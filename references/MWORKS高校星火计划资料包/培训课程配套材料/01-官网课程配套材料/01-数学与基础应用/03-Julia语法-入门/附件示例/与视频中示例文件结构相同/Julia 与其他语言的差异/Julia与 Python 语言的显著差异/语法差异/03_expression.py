# txt 字符串非空时，条件成立
txt = "somthing"
if txt:
    print("abc")
# txt 字符串为空，条件不成立
txt = ""
if txt:
    print("edf")  # 不打印


# 最后一个形参名 args 前加 * 号表示不定长参数
def add(x, *args):
    res = 0
    for i in args:
        res += i
    return res + 2 * x


print(add(1, 2, 3, 4, 5))  # 16


# 不定长的关键词参数使用 **kwargs 表示
def mul(x, y, **kwargs):
    z = 0
    if "z" in kwargs:
        z = kwargs["z"]

    return x + 2 * y + z


mul(y=2, x=1, z=1)

import numpy as np


def func(x=np.random.rand()):
    print(x)


# 两次运行时的 x 都相同
# np.random.rand() 仅执行了一次
func()
func()


# 匿名函数，: 之前为形参
def myf(x): return x + 1


myf(1)  # 2


def func(x):
    # 使用 isinstance 判断 x 是否是 int 类型
    if isinstance(x, int):
        print("int")
    else:
        print("not int")


func(1)  # "int"


# 定义 class
class Foo():
    baz: int
    qux: float

    def __init__(self, baz, qux):
        self.baz = baz
        self.qux = qux


 # 创建实例
foo = Foo(23, 1.5)
# 新增字段
foo.abc = 3
foo.abc  # 3


class Bar:
    def func(self, x):
        if isinstance(x, int):
            return 1
        elif isinstance(x, str):
            return 2


bar = Bar()
bar.func(1)     # 1
bar.func("abc")  # 2


# 三元运算符
1 if True else 0  # 1


not False  # 取非， true
2 ** 2   # 幂运算，4
3 // 2   # 整除，1
1 ^ 0    # 异或，1
7 % -2   # 取模，-1

