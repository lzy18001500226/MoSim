# Syslab与Sysplorer双向集成_2024a

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/07-MWORKS.Syslab和MWORKS.Sysplorer双向集成(2024a)/01-MWORKS.Syslab和MWORKS.Sysplorer双向集成.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P0`
- Source SHA1: `0151ecdc646c`
- Pages: `26`
- Notes: Syslab/Sysplorer 双向数据、仿真与 API 集成流程。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
课程须知
➢本课程适用软件版本：MWORKS.Syslab2024a
MWORKS.Sysplorer 2024a
➢本课程示例运行需要软件首选项加载：
  基础库
  数学库
  图形库
信号处理库
  控制系统库
DSP系统库
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 2

```text
MWORKS.Syslab和
MWORKS.Sysplorer双向融合
新一代科学计算与系统建模平台MWORKS
耿建
苏州同元软控信息技术有限公司
2025年5月23日
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 3

```text
3
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
目录
3. From Workspace
2. To Workspace
4. Syslab Function
5. Sysplorer API
1. 背景-使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 4

```text
4
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
信息域
物理域
网络
计算
软件
物理
组件
环境
模型
机械
电气
流体
热
磁
测试测量
......
人工智能
基于方程
面向对象
多领域统一
Algorithm算法
Function 函数
数据科学
控制算法
......
Syslab
科学计算环境
Sysplorer
系统建模仿真环境
1.1 信息物理融合系统(CPS)
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 5

```text
5
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.1 信息物理融合系统(CPS)
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 6

```text
6
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
在Syslab菜单栏中点击Sysplorer，自动打开Sysplorer软件并加载SyslabWorkspace模型库
使用须知：
1.
如不能打开Sysplorer软件，则需要确
认Syslab首选项中Sysplorer可执行文
件路径是否正确
2.
Syslab和Sysplorer均需2022版以上
3.
Sysplorer软件编译器为64位
1.2 使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 7

```text
7
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
目录
3. From Workspace
2. To Workspace
4. Syslab Function
5. Sysplorer API
1. 背景-使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 8

```text
8
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2. To Workspace
将Sysplorer的仿真结果发送至Syslab工作空间中
Syslab
科学计算环境
Sysplorer
系统建模仿真环境
To Workspace子库中包含4个组件，分别为：
•
ToWorkspace_Scale：输出为标量数据
•
ToWorkspace_Vector：输出为一维数组
•
ToWorkspace_Matrix：输出为数组
•
ToWorkspace_3D_Array：输出为三维数组
拖拽式建模
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-
Demo_ToWorkspace_PID_Controller
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 9

```text
9
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2. To Workspace
仿真
using TyPlot
t = out.tout
w = out.w
plot(t, w)
#在Syslab中进行输出变量的后处理
使用Syslab对仿真
结果进行处理分析
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-
Demo_ToWorkspace_PID_Controller
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 10

```text
10
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
目录
3. From Workspace
2. To Workspace
4. Syslab Function
5. Sysplorer API
1. 背景-使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 11

```text
11
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3. From Workspace
Sysplorer从Syslab工作空间中读取数据并作为输入
Syslab
科学计算环境
Sysplorer
系统建模仿真环境
FromWorkspace子库中包含5个组件，分别为：
•
FromWorkspace_Scale：获取标量数据
•
FromWorkspace_Vector：获取一维数组
•
FromWorkspace_Matrix：获取二维数组
•
FromWorkspace_3D_Array：获取三维数组
•
FromWorkspaceTimeTable：获取表格矩阵，并通过线性插值来生成（可能是不连续的）信号
拖拽式建模
注意：FromWorkspace传递的量均为变量，不能直接作为组件参数，需将组件参数处理为输入接口或变量。
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-
Demo_FromWorkspace_RollingWheelSetPulling
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 12

```text
12
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3. From Workspace
# Julia代码
table = [0 1 0 0
1 1 0 0
2 0 2 0
3 0 2 0]
combiTimeTableX = table[:,[1,2]] #取1,2两列
combiTimeTableY = table[:,[1,3]] #取1,3两列
combiTimeTableZ = table[:,[1,4]] #取1,4两列
代码运行
使用FromWorkspace组件
设定参数
名与工作空间变量名需完全一致
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-
Demo_FromWorkspace_RollingWheelSetPulling
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 13

```text
13
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3. From Workspace
From Workspace Functions 以函数的形式从 Syslab 工作区中读取数据，因此可以直接将获取的数据作为其
他组件的参数值。
#Syslab脚本：
# 标量
i_val = 5
f_val = 7.5
b_val = true
# 向量
i_vec = [1, 2, 3]
f_vec = [1, 2.5, 3.5]
b_vec = [true, false, true]
# 矩阵
i_mtx = [1 2 3; 4 5 6]
f_mtx = [1 2.5 3.5; 4 5.5 6.5]
b_mtx = [true false true; false true false]
# 三维数组
i_arr = fill(1, (2, 3, 4))
i_arr[2, 1, 3] = 17
f_arr = fill(2.5, (2, 3, 4))
f_arr[2, 1, 3] = 17
b_arr = fill(true, (2, 3, 4))
b_arr[2, 1, 3] = false
model SubModel
    import SyslabWorkspace.FromWorkspace.Functions.*;
    //标量
    parameter Integer int_x = FwInt("i_val") "整型标量";
    parameter Real real_x = FwReal("f_val") "实型标量";
    parameter Boolean bool_x = FwBool("b_val") "布尔型标量";
    //向量
    parameter Integer int_vec[:] = FwIntVector("i_vec", 3) "整型向量";
    parameter Real real_vec[:] = FwRealVector("f_vec", 3) "实型向量";
    parameter Boolean bool_vec[:] = FwBoolVector("b_vec", 3) "布尔型向量";
    //矩阵
    parameter Integer int_mtx[:,:] = FwIntMatrix("i_mtx", 2, 3) "整型矩阵";
    parameter Real real_mtx[:,:] = FwRealMatrix("f_mtx", 2, 3) "实型矩阵";
    parameter Boolean bool_mtx[:,:] = FwBoolMatrix("b_mtx", 2, 3) "布尔型矩阵";
    //三维数组
   parameter Integer int_arr[:,:,:] = FwInt3DArray("i_arr", 2, 3, 4) "整型三维数组";
    parameter Real real_arr[:,:,:] = FwReal3DArray("f_arr", 2, 3, 4) "实型三维数组";
    parameter Boolean bool_arr[:,:,:] = FwBool3DArray("b_arr", 2, 3, 4) "布尔型三维数组";
   annotation (…);
  end SubModel;
Syslab中计算出结果
Sysplorer中模型通过函数读取工作空间值作为参数
注：函数调用见：Modelica语法-函数；参数定义见Modelica语法-类与内置类型
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 14

```text
14
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
目录
3. From Workspace
2. To Workspace
4. Syslab Function
5. Sysplorer API
1. 背景-使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 15

```text
15
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
将Syslab中构建的Julia复杂算法封装至Sysplorer中
Syslab
科学计算环境
Sysplorer
系统建模仿真环境
拖拽式建模
Function API中包含2个组件：
•
SyslabGlobalConfig：用于全局声明，包括导入包及全局变量声明等。
•
SyslabFunction：用于嵌入 Julia函数，并将Syslab Function模块的输入
和输出数据指定为参数和返回值。
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 16

```text
16
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
右击SyslabGlobalConfig模型，选择Syslab初始化配置，即可转到Syslab中的全局声明代码
# Julia代码-设置全局声明
P = []
xhat = []
residual =[]
xhatOut =[]
sample = 1; #采样间隔
next_t = 0.01; #采样点
# Modelica代码-自动生成参数
FunctionAPI.SyslabGlobalConfig syslabGlobalConfig(scriptText =
"P = []
xhat = []
residual =[]
xhatOut =[]
sample = 1; #采样间隔
next_t = 0.01;  #采样点")
annotation(...);
自动同步
Julia代码构建
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 17

```text
17
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
右击SyslabFunction模型，选择编辑Syslab函数脚本，即可转到Syslab中的算法函数代码
function EXTKALMAN(meas, deltat, time)
# Initialization
global P;
global xhat;
global residual;
global xhatOut;
global next_t; #采样点
  global sample; #采样间隔(s)
if isempty(P)
xhat = [0.001; 0.01; 0.001; 400;;]; # 4x1矩阵
    P = zeros(4, 4);
end
...
Julia算法
注意：
SyslabFunction组件认为脚本中的
第一个函数为本组件的主函数，其他
函数均为服务于主函数的辅助函数。
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 18

```text
18
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
SyslabFunction模型会根据第一个函数的输入参数和返回值自动生成输入输出接口；
如需手动配置：右击SyslabFunction模型，选择设置Syslab函数端口，手动配置输入输出接口。
配置输入输出接口
说明：
•
主函数的输入不要指定类型，不要指定具名参数；
•
主函数的输出必须使用return指定，且必须为函数体中已经
出现的变量符号；
•
输入输出配置需要设定数据类型和维度。
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 19

```text
19
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
使用To Workspace，
在Syslab中处理仿真结果
示例详见：Sysplorer内置模型库SyslabWorkspace-Examples-Demo_SyslabFunction_RadarTracking-RadarTracking
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 20

```text
20
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function
将Syslab中Julia对象进行动态系统建模和处理流式数据
Syslab
科学计算环境
Sysplorer
系统建模仿真环境
using ObjectOriented
@oodef mutable struct SyslabObject
# Description (用于生成Modelica组件描述)
  # Template for syslab object block.
# Parameter (用于生成 Modelica 组件参数，包括名称、类型、描述)
  # 格式：参数名::参数类型 = 参数值  # 参数注释
  # 例如：
  gain::Real = 1.0
# 增益
  # Private (Julia内部变量)
  # 格式：变量名::类型 = 值  # 变量说明
  # 例如：
  _count::Integer = -1
# 计数器
  # Methods (主要调用算法，包括setupImpl，stepImpl，releaseImpl)
# 初始化函数：函数名固定，函数形参与stepImpl函数形参一致
  function setupImpl(self, u)
self._count = 0
# ...
return nothing
end #setupImpl
# 单步计算函数：函数名固定，第一个函数形参必须是self，
# 其余函数形参将作为Modelica组件的输入端口，函数返回值作为输出端口
  function stepImpl(self, u)
self._count += 1
# ...
y = u * self.gain
return y
end #stepImpl
# 释放资源函数：函数名固定，且只能有一个函数参数self
function releaseImpl(self)
# ...
return nothing
end #releaseImpl
# 其它自定义函数，第一个函数形参数必须是self
# function xx(self)
#
...
# end
end
拖拽组件
新建或选择脚本路径
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 21

```text
21
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. Syslab Function


using TyCommunication
using TyBase
using TyMath
using TySignalProcessing
using ObjectOriented
@oodef mutable struct DSBAmplitudeDemodulator
# Description
# Parameter
InputSignalOffset::Float64 = 1
CarrierFrequency::Float64 = 100
InitialPhase::Float64 = 0
SampleFrequency::Float64 = 1000
FilterOrder::Int64 = 4
CutoffFrequency::Float64 = 100
PassbandRipple::Float64 = 0.1
StopbandAttenuation::Float64 = 50
LowPassFilterMethod::String = "Butterworth"
# Private
Samplepoint = 0
b = 0
a = 0
zi = 0
# Methods
function setupImpl(self, data)
#...
if self.SampleFrequency <= 0
throw(ArgumentError("Fs must be a real, positive scalar."))
end
# check that Fs must be greater than 2*Fc
if self.SampleFrequency < 2 * self.CarrierFrequency
throw(ArgumentError("Fs must be at least 2*Fc."))
end
if self.LowPassFilterMethod == "Butterworth"
……
end
self.zi = zeros(Float64, (max(length(self.a),length(self.b)) - 1))
return nothing
end #setupImpl
function stepImpl(self, data)
#...
temp = data .* cos(2 * pi * self.CarrierFrequency * self.Samplepoint / self.SampleFrequency + self.InitialPhase)
……
return out
end #stepImpl
function releaseImpl(self)
#...
return nothing
end #releaseImpl
end
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 22

```text
22
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
目录
3. From Workspace
2. To Workspace
4. Syslab Function
5. Sysplorer API
1. 背景-使用前的准备
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 23

```text
23
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5. Sysplorer API
Syslab 命令窗口(REPL)或脚本中可直接调用Sysplorer API
接口
类别
命令接口
含义
系统命令
ClearScreen
清空命令窗口
SaveScreen
保存命令窗口内容至文件
ChangeDirectory
更改工作目录
ChangeSimResultDirectory
更改仿真结果目录
RunScript
执行脚本文件
GetLastErrors
获取上一条命令的错误信息
ClearAll
移除所有模型
Echo
打开或关闭命令执行状态的输出
Exit
退出MWORKS.Sysplorer
文件命令
OpenModelFile
加载指定的Modelica模型文件
LoadLibrary
加载Modelica模型库
ImportFMU
导入FMU文件
EraseClasses
删除子模型或卸载顶层模型
ExportIcon
把图标视图导出为图片
ExportDiagram
把组件视图导出为图片
ExportDocumentation
把模型文档信息导出到文件
ExportFMU
模型导出为FMU
ExportVeristand
模型导出为Veristand模型
ExportSFunction
模型导出为Simulink的S-Function
类别
命令接口
含义
仿真命令
OpenModel
打开模型窗口
CheckModel
检查模型
TranslateModel
翻译模型
SimulateModel
仿真模型
RemoveResults
移除所有结果
RemoveResult
移除最后一个结果
ImportInitial
导入初值文件
ExportInitial
导出初值文件
GetInitialValue
获取变量初值
SetInitialValue
设置变量初值
ExportResult
导出结果文件
SetCompileSolver64
设置翻译时编译器平台位数
GetCompileSolver64
获取翻译时编译器平台位数
SetCompileFmu64
设置fmu导出时编译器平台位数
GetCompileFmu64
获取fmu导出时编译器平台位数
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 24

```text
24
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5. Sysplorer API
类别
命令接口
含义
曲线命令
CreatePlot
按指定的设置创建曲线窗口
Plot
在最后一个窗口中绘制指定变量的曲线
RemovePlots
关闭所有曲线窗口
ClearPlot
清除曲线窗口中的所有曲线
ExportPlot
曲线导出
文件命令
CreateAnimation
新建动画窗口
RemoveAnimatio
ns
关闭所有动画窗口
RunAnimation
播放动画
StopAnimation
停止动画播放
Animation Speed
设置动画播放速度
类别
命令接口
含义
模型对象
操作命令
GetClasses
获取指定模型的嵌套类型
GetComponents
获取指定模型的嵌套组件
GetParamList
获取指定组件前缀层次中的参数
列表
GetModelDescription
获取指定模型的描述文字
SetModelDescription
设置指定模型的描述文字
GetComponentDescripti
on
获取指定模型中组件的描述文字
SetComponentDescripti
on
设置指定模型中组件的描述文字
SetParamValue
设置当前模型指定参数的值
SetModelText
修改模型的Modelica文本内容
GetExperiment
获取模型仿真配置
关于Sysplorer API命令可见Syslab中文帮助文档中“Sysplorer API”
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 25

```text
25
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5. Sysplorer API
在Syslab中对Sysplorer模型进行参数扫动分析
#软件恢复初始化
Sysplorer.ClearAll()
#加载Modelica3.2.1
Sysplorer.LoadLibrary("Modelica", "3.2.1")
# 打开模型
Sysplorer.OpenModel("Modelica.Mechanics.Rotational.Exa
mples.CoupledClutches",
Sysplorer.ModelView.Diagram)
# 扫动变量值，扫动序列为：0.9、1.0、1.1、1.2、1.3
para_sweep = [0.9, 1.0, 1.1, 1.2, 1.3]
# 结果数组
J1_w_list = []
J2_w_list = []
time_list = []
# 开始实验
for i in 1:5
println("sweep case-$i: J1.J = $(para_sweep[i])")
# 设置变量
  Sysplorer.SetParamValue("J1.J", string(para_sweep[i]))
# 进行仿真
  Sysplorer.SimulateModel("Modelica.Mechanics.Rotational.Exampl
es.CoupledClutches",
stop_time = 1.2, algo = Sysplorer.Integration.Dassl)
println("case-$i finished")
# 记录结果
  push!(J1_w_list, Sysplorer.GetVarValues("J1.w"))
push!(J2_w_list, Sysplorer.GetVarValues("J2.w"))
push!(time_list, Sysplorer.GetVarValues("time"))
end
# 结果绘图
println("start to plot")
subplot(1, 2, 1)
hold("on")
......
示例详见：Syslab示例Examples-SyslabWorkspace-Demo_SysplorerAPI_ParameterAnalysis
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 26

```text
Thanks！
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```
