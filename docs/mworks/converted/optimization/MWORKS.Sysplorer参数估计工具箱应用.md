# MWORKS.Sysplorer参数估计工具箱应用

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/05-基于模型的设计优化/02-参数估计工具箱应用/01-2023b/MWORKS.Sysplorer参数估计工具箱应用.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P1`
- Source SHA1: `8239faae4554`
- Pages: `15`
- Notes: 模型参数估计、仿真对齐和优化流程。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
MWORKS.Sysplorer设计优化
参数估计应用
MWORKS.Sysplorer 2023b
苏州同元软控信息技术有限公司
2023年9月28日
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 2

```text
2
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
目录
2. 参数估计简介
1. MWORKS.Sysplorer设计优化工具概况
3. 参数估计应用- 不定义边界
4. 参数估计应用- 定义边界
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 3

```text
目录
MWORKS.Sysplorer
设计优化工具概况
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 4

```text
4
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
1. MWORKS.Sysplorer 设计优化工具概况
设计优化工具箱面向Modelica模型的设计和优化，为模型
试验设计、敏感度分析、参数估计和响应优化提供应用程序
和算法。
Sysplorer
设
计
优
化
参数敏感度分析
待调节参数
实验数据
鲁棒性分析
Modelica模型
关联实验数据和仿真结果
参数估计
设计需求
对仿真结果添加约束和期望
响应优化
MWORKS.Sysplorer设计优化
Sysplorer Design Optimzation
敏感度分析APP
多类型采样方法
模型试验设计
参数敏感度分析
模型需求设计
需求偏差可视化
系统鲁棒性评估
参数估计APP
数据预处理
多工况设计
支持多边界参数估计
参数评估
参数验证
迭代数据可视化
响应优化APP
模型需求设计
需求可视化
需求评估
多目标优化
模型线性化转换
迭代数据可视化
Modelica模型
（Sysplorer）
DOE & DOE结果可视化
参数采样
敏感度分析方法
全局敏感度分析
局部敏感度分析
优化方法
模拟退火算法
参数估计
多边界工况配置
迭代可视化
工况导入
模式搜索
响应优化
频域/时域需求
迭代可视化
拉丁超立方
霍尔顿(Halton)采样
DoE方法
需求可视化
估计报告
优化报告
Sysplorer SDK
模型线性化
并行仿真
结果管理
操作
对象
ToolBox
APP
仿真实例池、仿真任务调度
模型试验APP
参数矩阵
组件选型
批量组件设计
组件排列自动生成系统模型
批量仿真
多类型可视化
多类型结果视图
批量仿真设计
试验设计设计
蒙特卡洛设计
响应面设计
...
组件排列
顺序排列
全排列
模型翻译
需求评估
敏感度分析量化
敏感度结果可视化
批量组件设计
算法运行控制
残差计算
需求计算
粒子群算法
LM算法
遗传算法
单纯性搜索法
数据处理方法
去除奇异点
...
估值方法
四方位值
...
多边界/多目标聚合方法
线性加权法
...
最大目标函数值
基于惩罚的边界交叉
系统模型自动生成
仿真结果导出
组件自动生成
model System “ 待优化的系统模型”
parameter Real param1;
// 针对参数设计和优化
parameter Integer param2;
equation
...
end model
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 5

```text
目录
参数估计简介
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 6

```text
6
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2. 参数估计简介
系统仿真分析往往会遇到部分参数因为一些客观原因导致无法获取的情况，如何设置参数值才能提高模型精度，使得仿真结果逼近实验测量数据
成为难题。传统的参数估计方式是通过大量和反复人工测试最终确定出一个比较符合预期的参数，但是该操作时间成本高、效率低。
参数估计支持用户通过简单的待估计参数、目标变量和试验数据设置，基于工具提供的优化算法，快速估计系统模型参数。
• 应用于基于单一工况下的测试数据/标准
结果的模型参数估计
不定义边界
• 具有单值性条件的系统建模仿真
• 应用于基于多个不同工况下的测试数据/
标准结果的模型参数估计
多边界
• 粒子群算法
• 遗传算法
• 模式搜索算法
• …
优化算法
等待翻译完成
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 7

```text
7
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2. 参数估计简介
通过对比不同模型参数值的仿真结果和测量数据的吻合程度来不断调整模型参数值使模型仿真结果逼近测量数据的过程就是参数估计。使用参数
估计，可以更快的调优模型以达到实验预期目标，明晰调参方向，降低人工调整参成本。此外，通过不断更新参数来优化模型，提高模型仿真精
度，达成模型仿真结果逼近物理实验的效果。
Engine
engineInertia
J=0.4
cardanInertia
J=0.01
wheelInertias
J=4
finalDriveGear=3.46
wheel=1 / R
carBody
gearBox=4.17
engineTorque
模型仿真结果和实验数据对比
初始参数仿真结果
优化后参数仿真结果
Modelica 模型
[iter = 30] [residual = 0.0151548]
Parameter
Value
engineTorque.tau_0
263.108
gearBox.lossTable[1,2]
0.792696
[iter = 0]     [residual = 6.61729]
Parameter                     Value
engineTorque.tau_0            320
gearBox.lossTable[1, 2]       1
参数估计APP运行结果.MP4
残差轨迹
仿真结果和实验数据对比
参数轨迹
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 8

```text
8
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
2. 参数估计简介
通过对比不同模型参数初值的仿真结果和测量数据的吻合程度来不断调整模型参数初值使模型仿真结果逼近测量数据的过程就是参数估计。使用
参数估计，可以更快的调优模型以达到实验预期目标，明晰调参方向，降低人工调整参成本。此外，通过不断对参数进行更新来优化模型，使得
模型不仅能够在测试数据上表现很好，而且可以在验证数据集上面表现的很好。
Engine
engineInertia
J=0.4
cardanInertia
J=0.01
wheelInertias
J=4
finalDriveGear=3.46
wheel=1 / R
carBody
gearBox=4.17
engineTorque
模型仿真结果和实验数据对比
系统IO数据可视化
残差轨迹
仿真结果和实验数据对比
参数轨迹
估计报告
初始参数仿真结果
优化后参数仿真结果
[iter = 30] [residual = 0.0151548]
Parameter
Value
engineTorque.tau_0
263.108
gearBox.lossTable[1,2]
0.792696
[iter = 0]     [residual = 6.61729]
Parameter                     Value
engineTorque.tau_0            320
gearBox.lossTable[1, 2]       1
Modelica 模型
参数估计APP
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 9

```text
目录
参数估计应用
- 不定义边界
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 10

```text
10
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
简易小车模型，发动机通过啮齿和轴承传动装置推动车身前进，在车身上安装传感器测量简易小车加速度，速度和移动距离，探究恒定扭矩发动
机的扭矩和传动系统的效率。
根据小车原理，在MWORKS.Sysplorer中搭建该小车模型，使用恒定扭矩发动机模型（Engine）驱动小车，具有啮合效率和轴承摩擦的齿轮
（gearBox）和带惯性的1D 旋转组件传动，其他传动齿轮和齿轮箱均选择无惯性模型忽略影响，推动车身前进，计算车身加速度。
Engine
engineInertia
J=0.4
cardanInertia
J=0.01
wheelInertias
J=4
finalDriveGear=3.46
wheel=1 / R
carBody
gearBox=4.17
engineTorque
engineTorque
gearBox
恒定扭矩发动机模型
具有啮合效率和轴承摩擦的齿轮
carBody
具有惯性的滑动质量块
3.参数估计应用– 不定义边界
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 11

```text
11
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
实验中在车身上安装传感器测得加速度，通过模型仿真和参数估计工具估计gearBox的传动系统的效率lossTable[1, 2] 和engineTorque力矩
tau_0 ，使得传感器捕获到的加速度acc 数据和carBody.a 仿真结果的残差最小。
Engine
engineInertia
J=0.4
cardanInertia
J=0.01
wheelInertias
J=4
finalDriveGear=3.46
wheel=1 / R
gearBox=4.17
engineTorque
参数
tau_0
320
N.m
tau_max
450
N.m
w_max
7200 * Modelica.Constants.pi / 60
rad/s
参数
i
4.17
传输比
lossTable
[0, 1, 1, 0, 0]
啮合效率和轴承摩擦阵列
time
v
a
0
*
*
0.02
*
*
0.04
*
*
0.06
*
*
0.08
*
*
0.1
*
*
0.12
*
*
0.14
*
*
0.16
*
*
0.18
*
*
…
*
*
6.22
*
*
6.24
*
*
carBody
model SlidingMass "Sliding mass with inertia"
extends Interfaces.Rigid;
parameter SI.Mass m(min = 0) = 1 "mass of the sliding mass";
SI.Velocity v "absolute velocity of component";
SI.Acceleration a "absolute acceleration of component";
end SlidingMass
Modelica简易汽车模型
engineTorque
gearBox
time speed
dist
acc
0
0
0
0.22
0.02
0.2
0
0.33
0.04
0.3
0
0.45
0.06
0.4
0.01
0.56
0.08
0.5
0.01
0.68
0.1
0.6
0.01
0.82
0.12
0.7
0.02
0.98
0.14
0.9
0.02
1.23
0.16
1
0.03
1.42
0.18
1.2
0.03
1.62
…
…
…
…
6.22
99.8
95.53
2.35
6.24
100
96.09
2.33
传感器数据
仿真结果
time
acc
a
0
0.22
*
0.02
0.33
*
0.04
0.45
*
0.06
0.56
*
0.08
0.68
*
0.1
0.82
*
0.12
0.98
*
0.14
1.23
*
0.16
1.42
*
0.18
1.62
*
…
…
*
6.22
2.35
*
6.24
2.33
*
结果关联
a & acc 对比
a & acc 残差变化轨迹
tau_0  & lossTable[1, 2]
估计轨迹
3.参数估计应用– 不定义边界
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 12

```text
目录
参数估计应用
- 定义边界
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 13

```text
13
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
4.参数估计应用- 定义边界
汽车空调蒸发器是汽车空调系统中的一个重要组成部分，主要用于将压缩机压缩的高压制冷剂蒸发成低压的气体，制冷剂蒸发吸热实现空调系统
的制冷效果，换热器设计完成后需要通过调整修正系数以提高空调的性能和效率。
通过实验测得稳态条件下的压降系数和换热系数，探究蒸发器的冷媒和空气压降系数修正系数和换热系数修正系数。
压差和压降：压差是指制冷剂在蒸发器中的入口和出
口之间的压力差异。压降是指制冷剂在通过蒸发器时
由于流动阻力而产生的压力降低。压差和压降的大小
直接影响制冷剂在蒸发器中的流动速度和热交换效果。
温差：温差是指制冷剂在蒸发器中的入口和出口之间
的温度差异。温差的大小取决于蒸发器的设计和工作
条件，对于空调系统的制冷效果起着重要作用。
压降系数修正系数：在稳态条件下，蒸发器内部制冷
剂流动时产生的压降与理论计算值之间的修正系数。
由于蒸发器内部存在一定的阻力和流动不均匀性，实
际压降会比理论值大，因此需要修正系数进行修正。
换热系数修正系数：蒸发器内部换热效果的修正系数。
蒸发器内部的翅片和管道结构会影响制冷剂与空气之
间的热交换效果，实际换热系数会受到多种因素的影
响，如流速、流动状态、表面积等，因此需要修正系
数进行修正。
Modelica蒸发器模型
边界：传热过程的热流体建模仿真中的单值性条件。导热微分方程式是根据热力学定律所建
立起来的描写物体的温度随空间和时间变化的关系式，它全然没有涉及到某一特定导热过程
的具体特点，欲从众多不同的导热过程中区分出我们所研究的某一特定的导热过程，还需对
该过程作进一步的具体说明，这些补充说明条件总称为单值性条件。
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 14

```text
14
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
4.参数估计应用- 定义边界
本例为单体换热器模型，通常实验数据为多组固定边界条件的组合形式（热侧进口流量温度，冷侧进口流量温度进行组合），待估计的变量为换
热量和换热器内部压降。，通过参数估计工具箱估计稳态多边界工况下的压降系数（冷媒和空气）的修正系数和换热系数（冷媒和空气）的修正
系数。
组合参数后，可针对当前换热器模型中使用的4个待估计参数进行调整，修正热侧和冷侧的压降值和换热量，使其在给定边界条件范围内和实验
数据趋于一致。
参数
mdot_air
0.3
T_air
320
CF_dp_ref
1
N.m
CF_dp_air
1.125
N.m
CF_heat_ref
1.5
rad/s
CF_heat_air
1
边界
待估计参数
boundary2
boundary3
boundary4
boundary1
关联变量
关联变量
关联变量
关联变量
聚合残差
参数优化
多边界参数估计流程
序号
mdot
p
dp
heat
bound1
0.1
100000
res1
res2
bound2
0.2
100000
res3
res4
bound3
0.3
100000
res5
res6
bound4
0.14
100000
res7
res8
bound5
0.7
103000
res9
res10
bound6
0.35
103000
res11
res12
bound7
0.6
103000
res13
res14
bound8
0.2
103000
res15
res16
结果变量关联列表
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 15

```text
15
Copyright © 2023 苏州同元软控信息技术有限公司
All rights reserved
请各位专家指正！
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
苏州同元软控技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```
