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
foo.abc # 3




