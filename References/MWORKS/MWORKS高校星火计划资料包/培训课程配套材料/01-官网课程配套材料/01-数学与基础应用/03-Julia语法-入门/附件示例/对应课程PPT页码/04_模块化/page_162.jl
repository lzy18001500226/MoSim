module A
module B
export hello
hello() = "Hello"
end # end of B
end # end of A
import .A.B # 注意：导入当前命名空间的模块时需要在模块路径前方加上 . 以启用相对路径导入
B.hello() # 此时无法直接调用 hello() 函数，因为import不会将模块的成员导入至当前命名空间
using .A.B
hello()   # 此时可以直接调用 hello() 函数，因为using会把模块B的导出成员导入当前命名空间
A.B.hello()


