# MWORKS.Sysplorer工具箱运行脚本_Python

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/03-扩展接口调用/03-MWORKS.Sysplorer工具箱运行脚本（Python）/01-2024a/MWORKS.Sysplorer工具箱运行脚本（Python）.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P2`
- Source SHA1: `058b357d4c99`
- Pages: `32`
- Notes: Sysplorer Python 脚本运行和自动化接口。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
课程须知
➢本课程适用软件版本：MWORKS.Sysplorer2024a
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 2

```text
MWORKS.Sysplorer工具箱
 运行脚本-Python
李鹏宇
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
1. Python脚本应用概述
2. Python脚本应用-运行典型命令
3. Python脚本应用-高级使用
4. 注意事项
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 4

```text
目录
Python脚本应用概述
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 5

```text
5
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.1 为什么要使用Python脚本
Python 脚本在 Sysplorer 中的作用
脚本命令是工业软件的重要交互方式
Python
Python 作为使用率最高的通用脚本语言，
已被应用到诸多工业软件与工程场景中。
实现自动化建模、仿真、模型测试
将 Sysplorer 擅长的建模仿真能力
和Python 的优化、控制等丰富的
算法相结合，助力生产
以 Sysplorer 作为后台应用，使用
Python 快速开发工业 APP
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 6

```text
6
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.2 Python脚本运行工具简介-Python命令行
MWORKS.Sysplorer 命令窗口支持Python 界面功能命令、编译器命令等接口，供开发脚本程序时参考。
1. 命令交互输入
在命令窗口“>> ”标识后输入命令，键盘“↑”和“↓”方向键可以
在历史输入记录中前后查找，输入完毕后按回车键执行命令。
2. 脚本批量执行
可以将命令脚本文件（.mos 、.scr 或.py ）鼠标拖拽到命令窗口执行
脚本。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 7

```text
7
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.2 Python脚本运行工具简介-Python命令行
MWORKS.Sysplorer 命令窗口支持Python 界面功能命令、编译器命令等接口，供开发脚本程序时参考。
Boolean CheckModel(String model_name="")
命令原型：
检查模型，若命令正确执行则返回True ，执行错
误则返回False ，并说明错误的可能原因。
4. 数据类型说明
命令接口与选项的参数/ 返回值类型如下。
⚫关键字"void" 表示无返回值。
⚫布尔类型 bool ，按照Python 语法，
输入/ 返回 True/False
⚫整型 int 和浮点数 double 无需特别解
释。
⚫字符串类型 string 作为参数输入时使
用单引号或双引号表示，例如
CheckModel('Simple')
CheckModel("Simple")
⚫集合类型 list ，表示数组。
5.缺省参数
如果某个命令接口带有缺省参数，调用
时可以不给出实参，这时系统自动取其
缺省值。
boolean  SimulateModel ( string  model_name, double
start_time= 0, double  stop_time = 1, int
number_of_intervals=500, string  algo='Dassl',
double  tolerance=0.0001, double  integral_step=
0.002, double  store_double=False, double
store_event =False)
命令原型：
命令调用：
SimulateModel ("Simple")
3. 命令输出
执行命令后，根据命令的定义，返回相应的值。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 8

```text
8
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.3 Python脚本运行工具简介-Python编辑器
MWORKS.Sysplorer 提供了Python文本编辑器，可以新建、编辑、运行Python脚本文件。
1. 在工具> 应用中点击运行脚本，即可打开Python编辑器。
⚫新建文件：点击后新建空白的Python脚本。
⚫打开文件：从本地打开.py文件至编辑器，此时脚本内容将显示在
下方的文本编辑区内。
⚫保存文件：将当前脚本保存至本地。
⚫执行脚本：执行当前脚本。
2. 新建、打开文件后，对当前脚本进行编辑。
⚫编辑器提供编码助手功能，提高编辑效率。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 9

```text
9
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.3 Python脚本运行工具简介-Python编辑器
MWORKS.Sysplorer 提供了Python文本编辑器，可以新建、编辑、运行Python脚本文件。
编辑器
命令行窗口输出
3. 执行脚本后，输出显示在Python命令行窗口。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 10

```text
10
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.4 Python脚本运行工具简介-Sysplorer Python API
Sysplorer 提供了一套 Python API，可以在外部的 Python 环境下调用，例如在 Syslab 中调用。
Python 命令行调用
运行 Python 脚本
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 11

```text
11
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
Step1：在Syslab中，新建PowerShell 终端，并cd 到 Sysplorer Python API 安装包的路径
Step2 ：输入安装命令
pip
install
.\mworksengine-1.0.tar.gz
-i
https://pypi.tuna.tsinghua.edu.cn/simple
Step3：验证基本命令
注：由于安装过程需要通过 pip 安装其他 Python 库，通过 pip 官网安装需要国外代理，而通过国内的镜像源安装不需要代理，因此推荐国内用
户使用清华镜像源网站 https://pypi.tuna.tsinghua.edu.cn/simple 安装。高手可忽略。
import mworks
eng = mworks.engine.StartSysplorer()
eng.LoadLibrary("Modelica")
eng.SimulateModel('Modelica.Blocks.Examples.PID_Controller')
eng.ExportResult(r'C:\Users\TR\Documents\MWorks\PID_Controll
er.csv', "csv", ['PI.y', 'PI.u_m',], False)
eng.Exit()
点击“运行”查看结果
1.4 Python脚本运行工具简介-Sysplorer Python API
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 12

```text
12
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.4 Python脚本运行工具简介-Sysplorer Python API
Sysplorer Python API 提供了多种启动方式
1. 启动新的 Sysplorer
mworks.engine.StartSysplorer(start_mode: str = '-gui', processPath: str = None, ip: str = None) -> SysplorerEngine
• start_mode：启动模式，包括'-gui'和'-q'两种，分别表示启动带界面的 Sysplorer 和无界面的 Sysplorer ；
输入参数：
• processPath：软件启动路径，默认使用注册表中记录的路径，即最新安装的 Sysplorer；
• ip：Sysplorer Python API 服务的 ip 地址，默认为 Python 客户端随机找一个可用的 ip，一般无需关心。
返回值：
• SysplorerEngine：Sysplorer 引擎类，所有的 Sysplorer Python API 都是这个类的接口。
示例
import mworks
eng = mworks.engine.StartSysplorer()
eng.LoadLibrary("Modelica")
eng.SimulateModel('Modelica.Blocks.Examples.PID_Controller')
eng.ExportResult(r'C:\Users\TR\Documents\MWorks\PID_Controll
er.csv', "csv", ['PI.y', 'PI.u_m',], False)
eng.Exit()
# 以界面启动的方式启动最新安装的 Sysplorer，获取到 Sysplorer 引擎对象：eng
# 调用 eng 对象的 Sysplorer Python API
• 启动一个新的 Sysplorer。
说明：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 13

```text
13
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1.4 Python脚本运行工具简介-Sysplorer Python API
Sysplorer Python API 提供了多种启动方式
mworks.engine.ConnectSysplorer(port: int = None) -> SysplorerEngine
• port：要连接的端口号，可以根据 FindSysplorer 获取；
输入参数：
2. 连接到已启动的 Sysplorer
需要配合使用多条命令来连接到已启动的 Sysplorer
mworks.engine.FindSysplorer() -> List
说明：
• 查找可连接的 Sysplorer，返回端口号列表。
说明：
EnginePort() -> int:
ShareEngine()
说明：
将正在运行的本Sysplorer 转换为共享引擎。
说明：
返回本共享Sysplore 引擎的可用端口。
（2）Python 部分
（1）Sysplorer 部分
EnginePort() -> int:
说明：
返回本共享Sysplore 引擎的可用端口。
• 给定端口时，若端口为 Sysplorer 共享端口，则连接成功，否则，连接失
败；
• 不给定端口时，若找到可用端口，则连接第一个可以连接的端口；
• 不给定端口时，若找不到可用端口，则启动一个新的 Sysplorer 并连接。
• 要求一个 Python 解释器只能连接一个 Sysplorer；
限制：
• 要求一个 Sysplorer 只能被一个 Python 解释器连接；
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 14

```text
目录
Python脚本应用-运行典型命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 15

```text
15
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.1 运行Python命令
MWORKS.Sysplorer 支持Python原生命令。在命令行中，支持导入Python标准库；在编辑器中，还支持
导入第三方库。
示例2：使用numpy.random.random创建一个10*10的ndarray对象，并求最大值
注意：引用了第三方库numpy，需要在编辑器中使用。见最后注意事项。
import numpy
val = numpy.random.random(size=(10,10))
print(val)
max = val[0][0]
for i in val:
for j in i:
if max < j:
max = j
print(max)
脚本：
输出：
示例1：获取“C:\\Users\\TR\\Pictures”下的 png 文件
说明：可自行修改路径，需使用绝对路径
>> import pathlib
>> from pathlib import Path
>> imgdir = "C:\ Users\ TR\ Pictures"
>> p = Path(imgdir)
>> for i in p.rglob('*.png'):print(i)
脚本：
输出：
使用编辑器输入
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 16

```text
16
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令
MWORKS.Sysplorer 提供了一系列 Sysplorer 命令，供开发脚本程序时参考
主题
说明
基本帮助命令
基本帮助命令的功能说明与示例
系统命令
系统命令的功能说明与示例
文件命令
文件命令的功能说明与示例
仿真命令
仿真命令的功能说明与示例
曲线命令
曲线命令的功能说明与示例
动画命令
动画命令的功能说明与示例
模型对象操作命令
模型对象操作命令的功能说明与示例
命令汇总
命令汇总
变量汇总
变量汇总
脚本示例
Python脚本简单示例
自定义工具库管理
介绍自定义工具库的查看、添加、删除方法
Tips：可以打开软件，在“帮助-接口-Python脚本命令”中查看所有命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 17

```text
17
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> Help()
示例1：显示帮助信息
脚本：
输出：
>> Help(“CheckModel”) 或
>> help CheckModel
示例2：查看指定命令的说明
脚本：
输出：
基本帮助命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 18

```text
18
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> ListFunctions()
示例3：列出所有函数
脚本：
输出：
基本帮助命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 19

```text
19
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> ListVariables()
示例4：列出所有变量
脚本：
基本帮助命令
输出：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 20

```text
20
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> ChangeDirectory(r"D:\03_workspath")
示例5：设置工作目录
脚本：
>> ChangeSimResultDirectory(r"D:\03_workspath")
示例6：设置仿真结果目录
脚本：
等效于在全局设置中设置
系统命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 21

```text
21
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> RunScript(r"D:\03_workspath\test.py")
示例7：执行脚本文件
脚本：
输出：
执行脚本文件，相当于将脚本中的命
令，全部在命令行执行一遍。
系统命令
除了使用RunScript命令外，还可以直接将test.py文件拖拽到命令窗口，实现上述功能
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 22

```text
22
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> LoadLibrary('Modelica','4.0')
示例8：加载模型库
脚本：
输出：
>> OpenModelFile(r"D:\03_workspath\TestModel1.mo",True)
示例9：加载模型
脚本：
输出：
文件命令
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 23

```text
23
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> OpenModel ('TestModel1','text')
示例10：打开模型
脚本：
输出：
>> SimulateModel(model_name = "TestModel1",algo = "Dassl",result_file = r"D:\aa")
示例11：仿真模型
脚本：
输出：
仿真命令
该命令的意思是将模型浏览器中
的某个模型在图形、图标或文本
视图打开。
注意：要与文件命令中的加载模
型命令OpenModelFile加以区分。
仿真命令参数很多，且都是缺省参数，示
例11展示了指定部分缺省参数的仿真命令。
注意：要保证result_file 参数所在的文件
夹存在，否则会仿真失败
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 24

```text
24
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
示例12：创建曲线
脚本：
曲线命令
>> CreatePlot(id=2,x='time',y=['pID_Controller.PI.u_s', 'pID_Controller.PI.y'],legend_layout =10,
curve_vernier=True, result_file=r'D:\aa\TestModel1\Result.msr')
创建编号为2的曲线窗口，显示实例TestModel1中以time为X轴的pID_Controller.PI.u_s
和pID_Controller.PI.y的曲线，图例悬浮在左下，并在该曲线窗口显示游标。
>> ExportPlot('D:/plot.png',PlotFileFormat.Image,2,600,400)
示例13：导出曲线
脚本：
将曲线窗口-2作为600*400大小的图片导出，导出的
文件路径为’D:\Plot.png'。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 25

```text
25
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> CreateAnimation()
示例14：创建动画
脚本：
动画命令
>> RunAnimation()
示例15：播放动画
脚本：
以Modelica.Mechanics.MultiBody.Examples.Elementary.DoublePendulum
模型为例，首先仿真改模型，仿真成功后，执行该脚本
>> AnimationSpeed (0.1)
示例16：设置动画播放速度
脚本：
通过设置动画播放速度，执行播放动画命令，即可开
始播放。
示例14.创建动画
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 26

```text
26
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 运行Sysplorer命令-典型命令介绍
>> GetParamList('pID_Controller')
示例18：获取指定组件前缀层次中的参数列表。
脚本：
模型对象操作命令
示例19：获取参数的值
获取模型‘TestModel1的组件列表
>> SetParamValue('pID_Controller.driveAngle', '2')
示例20：设置参数的值
脚本：
输出：
>> GetParamValue('pID_Controller.driveAngle')
脚本：
输出：
示例17：获取组件列表
>> GetComponents('TestModel1')
脚本：
输出：
输出：
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 27

```text
目录
Python脚本应用-高级使用
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 28

```text
28
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.1 自动化建模仿真
Python脚本自动化建模仿真的功能
import os
#模型存放路径
#获取当前模型存放绝对路径
curDir=os.path.dirname(os.path.abspath(__file__))
#软件恢复初始化
ClearAll()
#加载Modelica3.2.1
LoadLibrary('Modelica','3.2.1’)
#打开用户模型
OpenModelFile(curDir+r"/Systems/package.mo")
#打开Systems.RobotR3.fullRobot模型
OpenModel('Systems.RobotR3.fullRobot',ModelView.Diagram)
#变量axis2.c的值
axis2_c_values=[1,10,5,20]
#对变量axis2.c设置不同的值，获得结果变量曲线和图片
for var in axis2_c_values:
#修改部分参数
SetParamValue('axis2.c', var)
#检查模型
CheckModel('Systems.RobotR3.fullRobot’)
#仿真模型
  SimulateModel(model_name='Systems.RobotR3.fullRobot',stop_time=1.8,algo=Integration.Dassl)
#创建曲线窗口1
CreatePlot(id = 1, position = [100, 120, 590, 600], y = ['axis2.flange.phi’])
#创建子窗口
CreatePlot(id = 1, sub_plot = 2, y = ['axis2.flange.tau’])
#创建曲线窗口2
CreatePlot(id = 2, position = [692, 120, 1200, 600], y =
['controlBus.axisControlBus3.speed_ref’,
controlBus.axisControlBus3.speed’])
#添加曲线
Plot(y=['controlBus.axisControlBus2.motion_ref’])
#导出曲线图片
ExportPlot(curDir+r"/axis2.c值为"+ str(var) + "时axis2的曲线.png",PlotFileFormat.Image,1)
ExportPlot(curDir+r"/axis2.c值为"+ str(var) + "时controlBus的曲线.png",PlotFileFormat.Image,2)
#导出结果文件
ExportPlot(curDir+r"/axis2.c值为"+ str(var) + "时axis2的曲线.csv",PlotFileFormat.Csv,1)
ExportPlot(curDir+r"/axis2.c值为"+ str(var) + "时controlBus的曲线.csv",PlotFileFormat.Csv,2)
#打开动画窗口
CreateAnimation()
#设置动画播放速度
AnimationSpeed(0.1)
#播放动画
RunAnimation()
右侧的Python脚本使用了第4章中介绍的不同分类的命令，包括
清空环境、加载模型库、加载模型、打开模型、设置参数、仿真
模型、创建曲线、导出曲线、创建动画、播放动画等，完成了一
次打开模型、设置参数、仿真、导出数据的自动化建模仿真流程。
自动化建模仿真结果
自动化建模仿真脚本
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 29

```text
29
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.2 Python编辑器的使用
1. 点击“新建文件”，将第五章的自动化脚本
复制到编辑区或点击“打开文件”，直接选择
自动化脚本文件
2. 根据自己的需要，对自动化脚本进行修改，然后点击“执行脚本”。运行
成功后，点击“保存文件” ，保存修改后的脚本
Tips：Python编辑器的脚本运行在UI线程，运行时可能会有卡顿现象，稍等片刻即可恢复
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 30

```text
目录
注意事项
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 31

```text
31
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4. 注意事项
注意事项1：外部库调用
MWORKS.Sysplorer中，有多种执行Python命令的方法。
• 若通过命令窗口运行Python命令或Python脚本文件， 则默认在子线程中执行；
• 若使用Python编辑器运行脚本文件，则默认在主线程（UI线程）中执行。
需要注意的是，外部的GUI调用命令(如Matplotlib工具库)在子线程中无法正确运行，此时需要将命令保存到.py格式的脚本文件中，使用RunInMainThread()执行
该脚本文件，或通过Python编辑器执行该脚本。
此外，由于多线程的影响，在Python命令行中只允许运行Python内置库，而第三方库。比如NumPy等，则需要在Python编辑器中运行。
注意事项2：Python脚本编码格式
➢默认编码格式
Python编辑器的默认编码格式为UTF-8-BOM，若使用其他格式可能出现中文乱
码等情况。
➢保存编码格式方法
1. 使用记事本打开脚本文件。
2. 点击文件 > 另存为 ，选择编码为带有BOM的UTF-8。
3. 点击保存。
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```

## Page 32

```text
32
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
谢谢
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
@苏州同元软控信息技术有限公司版权所有，未经许可，不得复印、传播或以其他形式使用
版权所有，侵权必究
```
