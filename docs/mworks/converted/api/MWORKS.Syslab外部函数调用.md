# MWORKS.Syslab外部函数调用

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/01-MWORKS.Syslab外部函数调用/01-2023a/MWORKS.Syslab外部函数调用.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P2`
- Source SHA1: `0427405671c5`
- Pages: `19`
- Notes: Syslab 调用 Python/C/外部函数的参考。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
MWORKS.Syslab 2023a
外部函数调用
张和华宋家豪
苏州同元软控信息技术有限公司
2023年8月16日
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 2

```text
2
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
目录
2. Julia与Python互调用
1. Julia与C/C++互调用
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 3

```text
3
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++
在数值计算领域，存在很多用C或Fortran写的高质量且成熟的库，为了便捷复用现有资产，Julia提供简洁且高效的调用方式，
不需要任何“胶水”代码。
ccall(function_name, library), returntype, (argtype1, ...), argvalue1, ...)
ccall(function_name, returntype, (argtype1, ...), argvalue1, ...)
ccall(function_pointer, returntype, (argtype1, ...), argvalue1, ...)
可以使用ccall 来生成一个对C/C++库函数的调用。ccall定义如下：
注：ccall是Julia内置库Base的关键字，无需加载额外包
ccall(:clock, Int32, ())
调用C库里面的clock函数，空参，返回值类型为Int32
例如：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 4

```text
4
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++
对于C标准库中的函数，Julia可以直接调用。
例如，C标准库中的getenv函数声明：char* getenv (const char* name);
julia> path = ccall(:getenv, Cstring, (Cstring,), “PATH”)#注：函数名前面加冒号表示symbol类型
Cstring(0x00000000028c4f68)
julia> unsafe_string(path)#Copy a string from the address of a C-style，表示从C地址中取字符串值
"C:\\Program Files (x86)\\VMware\\VMware
Workstation\\bin\\;C:\\Windows\\system32;C:\\Windows;C:\\Windows\\System32\\Wbem;C:\\Windows\\System32\\Window
sPowerShell\\v1.0\\;C:\\Windows\\System32\\OpenSSH\\;C:\\Program Files (x86)\\NVIDIA
Corporation\\PhysX\\Common;C:\\Program Files\\TortoiseSVN\\bin;C:\\ProgramData\\chocolatey\\bin;D:\\Program
Files\\Polyspace\\R2020b\\runtime\\win64;D:\\Program Files\\Polyspace\\R2020b\\bin;D:\\P" ⋯788 bytes ⋯
"ingw64\\bin;C:\\Program Files\\CMake\\bin;D:\\Program Files\\MWorks.Syslab 2022\\Syslab\\bin;D:\\Program
Files\\MWorks.Syslab 2022\\Tools\\PortableGit\\cmd;D:\\Program Files\\MWorks.Syslab
2022\\Tools\\PortableGit\\usr\\bin;D:\\Users\\TR\\AppData\\Local\\Programs\\Microsoft VS Code\\bin;C:\\Program
Files\\MWorks.Syslab 2022\\Syslab\\bin;C:\\Program Files\\MWorks.Syslab
2022\\Tools\\PortableGit\\cmd;C:\\Program Files\\MWorks.Syslab 2022\\Tools\\PortableGit\\usr\\bin"
函数名返回值类型参数类型
实参
示例：
ccall(function_name, returntype, (argtype1, ...), argvalue1, ...)
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 5

```text
5
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++
还可以使用另外一种方法@ccall 来调用C函数，更加简洁清晰。和上一种方法使用等价
@ccall 的定义如下：
@ccall library.function_name(argvalue1::argtype1, ...)::returntype
@ccall function_name(argvalue1::argtype1, ...)::returntype
@ccall $function_pointer(argvalue1::argtype1, ...)::returntype
julia> path = @ccall getenv("PATH"::Cstring)::Cstring
Cstring(0x00000000028c4f68)
julia> unsafe_string(path)
例如：
函数名
实参
参数类型返回值类型
比如：ccall(:clock, Int32, ())等价于@ccall clock()::Int32
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 6

```text
6
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++
除了可以直接调用C标准库外，还可以调用用户开发的C++动态库。
#ifndef ARRAYMAKER_H
#define ARRAYMAKER_H
#include "ArrayMaker_global.h"
struct ArrayMaker {
int nNumber;
double* pArray;
};
// 求和
extern "C" ARRAYMAKER_EXPORT double GetSum(double x, double y);
extern "C" ARRAYMAKER_EXPORT ArrayMaker* CreateObj();
extern "C" ARRAYMAKER_EXPORT void DeleteObj(ArrayMaker ** ppobj);
extern "C" ARRAYMAKER_EXPORT double* FillArray(ArrayMaker* pobj, int num, double value);
extern "C" ARRAYMAKER_EXPORT double* SetValue(ArrayMaker* pobj, int nth/*base-1*/, double value);
extern "C" ARRAYMAKER_EXPORT int GetValues(ArrayMaker * pobj, double* out, int len);
#endif
假设，用户开发了一个动态库ArrayMaker.dll，该动态库的C/C++头文件定义如下：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 7

```text
7
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用
通过Libdl 来实现加载和卸载C/C++动态库。libdl函数库为Julia内置函数库，无需手动安装

Julia调用C/C++
除了可以直接调用C标准库外，还可以调用用户开发的C++动态库。
using Libdl
# 加载库
lib_path = joinpath(@__DIR__, "ArrayMaker", "x64", "Release", "ArrayMaker")
lib = Libdl.dlopen(lib_path)
# 获取调用函数的符号
GetSum = Libdl.dlsym(lib, :GetSum)
# 调用函数
c = @ccall $GetSum(2::Cdouble, 3::Cdouble)::Cdouble
...
# 关闭dll
Libdl.dlclose(lib)
库路径
与调用C标准库方法一样
使用的函数帮助文档链接：https://juliacn.gitlab.io/JuliaZH.jl/stdlib/Libdl.html
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 8

```text
8
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++
目前，基本的C/C++值类型可以转换为Julia类型，以C为前缀。标准Julia别名与Julia基本类型没有区别
上面标注红框为常用类型
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 9

```text
9
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用

Julia调用C/C++的一个完整示例
using Libdl
# 加载dll
lib_path = joinpath(@__DIR__, "ArrayMaker", "x64", "Release", "ArrayMaker")
lib = Libdl.dlopen(lib_path)
# 获取符号
CreateObj = Libdl.dlsym(lib, :CreateObj)
DeleteObj = Libdl.dlsym(lib, :DeleteObj)
FillArray = Libdl.dlsym(lib, :FillArray)
# 创建对象指针
pobj = @ccall $CreateObj()::Ptr{Cvoid}
# 填充数组
len = 5
parr = @ccall $FillArray(pobj::Ptr{Cvoid}, len::Cint, 3.5::Cdouble)::Ptr{Cdouble}
arr = [unsafe_load(parr, i) for i = 1:len]
#=
5-element Vector{Float64}:
3.5
3.5
3.5
3.5
3.5
=#
# 销毁对象
@ccall $DeleteObj(Ref(pobj)::Ptr{Ptr{Cvoid}})::Cvoid
pobj = C_NULL
# 关闭dll
Libdl.dlclose(lib)
#ifndef ARRAYMAKER_H
#define ARRAYMAKER_H
#include "ArrayMaker_global.h"
struct ArrayMaker {
int nNumber;
double* pArray;
};
extern "C" ARRAYMAKER_EXPORT ArrayMaker* CreateObj();
extern "C" ARRAYMAKER_EXPORT void DeleteObj(ArrayMaker ** ppobj);
extern "C" ARRAYMAKER_EXPORT double* FillArray(ArrayMaker* pobj, int num, double value);
#endif
备注：
CreateObj：创建数组构造器对象；
DeleteObj：销毁数组构造器对象；
FillArray：填充数组，输入参数为数组长度、数组元素值。初始时，所有数据元素值都为value。
①Julia代码：
②C/C++头文件代码：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 10

```text
10
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.1 Julia与C/C++互调用
#include "ArrayMaker.h"
#include <math.h>
using namespace std;
ArrayMaker* CreateObj()
{
auto p = new ArrayMaker;
p->nNumber = 0;
p->pArray = nullptr;
return p;
}
void DeleteObj(ArrayMaker** ppobj)
{
if (ppobj == nullptr) {
return;
}
auto& pobj = *ppobj;
if (pobj != nullptr) {
//删除数据
if (pobj->pArray != nullptr) {
delete[] pobj->pArray;
pobj->pArray = nullptr;
}
//删除本身
delete pobj;
pobj = nullptr;
}
}
double* FillArray(ArrayMaker* pobj, int num, double value)
{
double* data = nullptr;
if (pobj != nullptr) {
data = pobj->pArray;
if (data != nullptr)
{
delete[] data;
}
data = new double[num];
for (int i = 0; i < num; i++)
{
data[i] = value;
}
pobj->pArray = data;
pobj->nNumber = num;
}
return data;
}
③C/C++源文件代码：

Julia调用C/C++的一个完整示例
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 11

```text
11
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1.2 Julia与C/C++互调用

C/C++调用Julia
C/C++调用Julia，本质上C/C++调用Julia动态库，C/C++工程的编译和运行都依赖Julia及Julia仓库。
C/C++调用Julia的配置方法，详细请参见：https://juliacn.gitlab.io/JuliaZH.jl/manual/embedding.html。
#include <julia.h>
JULIA_DEFINE_FAST_TLS // only define this once, in an executable (not in a shared library) if you want
fast code.
int main(int argc, char *argv[])
{
/* required: setup the Julia context */
jl_init();
/* run Julia commands */
jl_eval_string("print(sqrt(2.0))");
/* strongly recommended: notify Julia that the
program is about to terminate. this allows
Julia time to cleanup pending write requests
and run all finalizers
*/
jl_atexit_hook(0);
return 0;
}
下例为函数展示了使用c++启动julia，并调用Julia的"print(sqrt(2.0))"语句
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 12

```text
12
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
目录
2. Julia与Python互调用
1. Julia与C/C++互调用
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 13

```text
13
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.1 Julia与Python互调用

Julia调用Python
在数值计算领域，存在很多用Python写的高质量且成熟的库，为了便捷复用现有资产，Julia提供简洁且
高效的调用方式，不需要任何“胶水”代码。
Julia调用python扩展库中函数：pyimport 和@pyimport
# 依赖PyCall
using PyCall
# 导入python库
math = pyimport("math")
v = math.sin(pi/2)
println("v = $v")
# v = 1.0
using PyCall
using TyPlot # 同元绘图库
# 导入python库
@pyimport numpy as np
x = np.linspace(0,2pi, 1000)
y = np.sin(x)
# 绘图
plot(x,y)
目前Syslab安装包已经提供了完备的Julia和Python。
若用户想要使用自己的Python环境，需要参考Syslab帮助文档“Syslab-外部语言接口-Python调用Julia”。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 14

```text
14
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.1 Julia与Python互调用

Julia调用Python
直接在Julia中嵌入python代码：py
using PyCall
# 直接嵌入python代码
py"""
str = "3 * 4 + 5"
a = compile(str,'','eval')
print("a =", eval(a))
"""
# a = 17
module MyModule
using PyCall
function __init__()
py"""
def hello(s):
return "hello " + s
"""
end
# 直接调用python函数
hello(s) = py"hello"(s)
end # MyModule
MyModule.hello("julia")
# "hello julia"
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 15

```text
15
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.1 Julia与Python互调用

Julia调用Python
调用python代码文件：
- 将路径添加到python工作目录中
- 导入python文件
- 调用python接口
示例：见Example示例：Julia-Python
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 16

```text
16
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.1 Julia与Python互调用

Julia调用Python
调用python类中的方法：
- 将路径添加到python工作目录中
- 导入python文件
- 获取类对象
- 调用python类中的方法
示例：见Example示例：Julia-Python
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 17

```text
17
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.2 Julia与Python互调用

Python调用Julia
Julia通过PyCall可以很方便地调用Python代码。反过来，Python通过tjc_common、tyjuliacall、julia-numpy等扩展包来
实现对Julia的调用（注，上述三个扩展包都是同元公司开发的）。
其中，tjc_common 主要是利用JuliaSysimage.dll(或.so) 文件来加速Julia包导入，tyjuliacall 主要用来实现Python对Julia代
码的调用，julia-numpy 作为tyjuliacall的底层支撑。
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

示例1-内嵌Julia代码
•
启动Syslab，新建Python文件
•
写入Python代码(如右图)
•
运行得到结果
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 18

```text
18
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2.2 Julia与Python互调用

示例2-调用Julia库函数
•
启动Syslab，新建Python文件
•
写入Python代码(如右图)
•
运行得到结果
from time import time
from tjc_common import *
_t0 = time.time()
from tyjuliacall import TySignalProcessing as sp
# NOQA: E402
from tyjuliacall import TyPlot as tp
# NOQA: E402
print(f"导入同元库耗时: {get_timespan(_t0):.2f} s")
import numpy as np
fs = 100
t = np.arange(fs + 1) / fs
print(t)
x = np.sin(2 * np.pi * t*3) + 0.25*np.sin(2 * np.pi * t*40)
# 调用信号库函数
_t0 = time.time()
y = sp.medfilt1(x, 9)
print(f"调用函数耗时: {get_timespan(_t0):.2f} s")
# 调用图形库函数
tp.plot(t, x, t, y)
tp.legend(np.asarray(["Original", "Filtered"]))
tp.plt.show()
medfilt1是同元信号处理工具箱函数
plot是同元图形工具箱函数
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 19

```text
请各位专家指正！
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```
