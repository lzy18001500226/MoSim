# Syslab鲁棒控制工具箱

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/02-控制系统设计与应用/04-鲁棒控制工具箱应用/01-2024b/Syslab控制系统之鲁棒控制工具箱.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P1`
- Source SHA1: `cd7d6d4bc75f`
- Pages: `40`
- Notes: 鲁棒控制分析和设计方法。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
Syslab控制系统之
鲁棒控制工具箱
孙懿诚
苏州同元软控信息技术有限公司
2025年5月23日
```

## Page 2

```text
2
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
课程须知
本课程基于云化版本：Syslab2024b构建
本课程课程目标：
本课程介绍鲁棒控制基本定义与工作流程，介绍Syslab控制系统系列工具箱中的鲁棒控制工具箱相关功能、函数用法及工作
流程。
学习本课程之前需要学习：
Syslab基本功能
Julia语法
Syslab控制系统工具箱
自动控制原理等专业知识
运行本课程案例需要预加载以下工具箱：
➢TyBase、TyMath、TyPlot、TyControlSystems、TyRobustControl
本课程内代码为伪代码，具体示例见附件：鲁棒控制示例
```

## Page 3

```text
CONTENTS
目录
Part 1
鲁棒控制工具箱
功能概况
Part 2
不确定模型创建
Part 3
不确定系统分析
Part 4
鲁棒控制器设计
Part 5
系统模型与控制器
简化
Part 6
线性矩阵不等式
```

## Page 4

```text
Part 1
鲁棒控制工具箱功能概况
```

## Page 5

```text
5
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
1. 鲁棒控制工具箱功能概述
不确定模型创建
1
•
不确定元素
•
不确定模型构造
•
不确定模型属性
•
不确定模型连接
不确定模型分析
2
•
盘稳定裕度分析
•
鲁棒性分析
•
蒙特卡洛分析
鲁棒控制器设计
3
•
回路成形设计
•
H∞ 综合
•
μ 综合
系统模型与控制器简化
4
•
平衡截断
•
Hankel 奇异值
•
模态分解
线性矩阵不等式
5
•
定义
•
求解
•
分析
```

## Page 6

```text
Part 2
不确定模型创建
```

## Page 7

```text
7
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.1 不确定模型创建 - 不确定元素和模型
函数及调用方式
说明
uss
创建不确定状态空间（ss）模型
ureal
创建不确定实数
ucomplex
创建不确定复数
ucomplexm
创建不确定复矩阵
ultidyn
创建不确定线性定常（LTI）动力学模型
umargin
创建不确定的增益及相位模块
umat
创建不确定矩阵
ucover
响应集的不确定模型拟合
randatom
生成随机的不确定元素对象
randumat
生成随机不确定矩阵
randuss
生成随机且稳定的不确定状态空间模型
diag
提取不确定矩阵对角线元素
详细用法请参考 Syslab 鲁棒控制工具箱帮助文档
在实际控制系统中，被控对象的数学模型往往带有未建模动态、近似参数等不确定因素。
Syslab 目前提供以下函数用于创建不确定元素和不确定模型：
```

## Page 8

```text
8
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.1 不确定模型创建 - 不确定元素和模型
示例1.1：创建含有不确定实数和不确定复数的不确定矩阵
# 标称值为 5，变化范围为 [2,6] 的不确定实数
a = ureal("a",5,Range=[2,6]);
# 标称值为 1，变化率为 [-10%,10%] 的不确定实数
b = ureal("b",1,Percentage=10);
# 标称值为 3+4im，变化半径为 0.1 的不确定复数
c = ucomplex("c",3+4im,Radius=0.1);
# 不确定元素与确定元素拼接成不确定矩阵
M = [a b;b*a 7;c-a b^2];
示例1.2：创建不确定状态空间模型
# 创建不确定元素
p1 = ureal("p1",10,Percentage=50);
p2 = ureal("p2",3,PlusMinus=[-0.5,1.2]);
# 创建不确定矩阵
A = [-p1 p2; 0 -p1];
B = [-p2; p2];
C = umat([1 0; 1 1]);
D = umat([0; 0]);
# 创建不确定状态空间模型
usys = ss(A,B,C,D);
julia> a
不确定实数 "a" ，标称值 5 ，变化范围 [2, 6] 。
julia> b
不确定实数 "b" ，标称值 1 ，变化量 [-10, 10]% 。
julia> c
标称值为 3 + 4im ，变化半径为 0.1 的不确定复数 "c"
julia> M.NominalValue
3×2 Matrix{Complex{Int64}}:
5+0im
1+0im
5+0im
7+0im
-2+4im
1+0im
julia> get(M)
NominalValue: Complex{Int64}[5 + 0im 1 + 0im; 5 + 0im 7 + 0im; 3 + 4im 1 + 0im]
Uncertainty: 3-entry Dict
SamplingGrid: 0-entry Dict
Name: ""
# 创建状态空间模型
A = [-10 3; 0 -10];
B = [-3; 3];
C = [1 0; 1 1];
D = [0; 0];
sys = ss(A,B,C,D)
# 转化为对应的不确定模型
usys = uss(sys)
julia> usys.NominalValue
A =
-10
3
0
-10
B =
-3
3
C =
1  0
1  1
D =
0
0
连续时间状态空间模型
julia> usys.Uncertainty
Dict{Any, Any} with 2 entries:
"p2" => 不确定实数 "p2" ，标称值 3 ，变化量 [-0.5, 1.2] 。
  "p1" => 不确定实数 "p1" ，标称值 10 ，变化量 [-50, 50]% 。
julia> usys.NominalValue
A =
-10
3
0
-10
B =
-3
3
C =
1
0
1
1
D =
0
0
连续时间状态空间模型
julia> usys.Uncertainty
Dict{Any, Any}()
②. 方法2：直接将确定模型转
化为不确定模型
①. 方法1：基于不确定元素创建不确定模型
通过该方法创建的不确定模型
不包含任何不确定元素
```

## Page 9

```text
9
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
2.2 不确定模型创建 - 不确定模型属性
函数及调用方式
说明
getNominal
不确定模型的标称值
uscale
缩放模块的不确定度
actual2normalized
将实际值转换为标准化值
normalized2actual
将归一化坐标中原子的值转换为相应的实际值
getLimits
不确定参数（UReal）的有效范围
isuncertain
检查参数是否是不确定的类型
lftdata
将不确定模型分解为确定部分和归一化不确定部分
这些函数用法比较简单，因此不再举例说明，详细用法请参考Syslab鲁棒控制工具箱帮助文档
Syslab目前提供以下函数用于获取或更改不确定对象的属性：
```

## Page 10

```text
Part 3
不确定系统分析
```

## Page 11

```text
11
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.1 不确定系统分析- 基于圆盘的增益裕度和相位裕度
一.  盘稳定裕度（diskmargin）
稳定裕度(stability margin) VS 盘稳定裕度(disk margin)
经典稳定裕度仅适用于SISO系统，且将相位和幅值分开考虑；盘稳定裕度能够应用于SISO系统和MIMO系统，且能够同时考虑相位和幅值。
② 对于MIMO系统，模型允许不确定性在每个通道中单独变化：
1
[(1
) / 2]
1
[(1
) / 2]
j
j
j
F






+
−
= −
+
该模型将MIMO开环响应𝐿替换为𝐿∗𝐹，其中
1
0
0
0
0
0
0
N
F
F
F




= 





1
[(1
) / 2]
1
[(1
) / 2]
j
j
j
F






+
−
= −
+
① 对于SISO系统𝐿，基于盘稳定裕度分析的不确定模型中包含一个复不确定性𝐹，作为乘积摄动代入回路传递函数中。𝐹的表达式如下：
式中：
⚫𝛅是一个增益有界动态不确定性，归一化数值只在单位圆盘内变化，即𝛿< 1。
⚫𝛂设置模型𝐹的增益和相位变化量。当参数𝜎固定，𝛼控制的就是圆盘的大小。当𝛼= 0时，乘子𝐹为1，传递函数对应标称值𝐿。
⚫𝛔称为偏斜度，使模型的不确定性偏向增益增加或增益减少。
反馈回路的盘稳定裕度实现步骤如下：
1. 构建增益和相位不确定性模型
L
F
+
-
```

## Page 12

```text
12
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.1 不确定系统分析- 基于圆盘的增益裕度和相位裕度
一.  盘稳定裕度（diskmargin）
➢P. Seiler, A. Packard and P. Gahinet, "An Introduction to Disk Margins [Lecture Notes]," in IEEE Control Systems Magazine, vol. 40, no. 5, pp. 78-95, Oct. 2020, doi: 10.1109/MCS.2020.3005277.
2. 基于圆盘分析法计算稳定裕度
    给定的偏斜度𝜎，当闭环系统单位负反馈对所有的𝐹稳定时，盘裕度最大。为了求出这个值，diskmargin()求出最大的𝛼，使得闭环系统对不确定性圆盘Δ(𝛼，𝜎)
中的所有𝐹都稳定。
1
[(1
) / 2]
Δ( ,
)
{
, | | 1}
1
[(1
) / 2]
F








+
−
=
=

−
+
① 对于SISO系统，鲁棒稳定性分析可以得到
max
1
(
1) / 2
S



=
+
−
其中，𝑆是灵敏度函数(1 + 𝐿)−1。
其中，𝜇Δ是对角线结构的结构化奇异值(mussv)
② 对于MIMO系统，鲁棒稳定性分析可以得到
max
Δ
1
(
1)
2
I
S



=
−


+




1
0
0
0
0
0
0
Δ
N






= 





𝛿j是每个𝐹𝑗的归一化不确定性。
```

## Page 13

```text
13
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.1 不确定系统分析- 基于圆盘的增益裕度和相位裕度
一.  盘稳定裕度（diskmargin）
示例3.1：计算MIMO反馈回路的盘稳定裕度
   给定如下图所示双通道MIMO反馈回路，分别计算一次回
路的盘稳定裕度和多次回路的盘稳定裕度。
计算被控对象的输出盘稳定裕度，被控对象输出端的负
反馈开环响应为𝐿𝑜= 𝑃𝐶。
a = [0 10;-10 0]
b = eye(2)
c = [1 10;-10 1]
P = ss(a,b,c,0)
C = ss([1 -2;0 1])
Lo = P*C
# DMo 数组储存一次回路盘稳定裕度
# MMo 储存多次回路盘稳定裕度
DMo,MMo = diskmargin(Lo)
① 两反馈通道一次回路盘稳定裕度：输出结果非常好（无限增益裕度和 90° 相位裕度）。
julia> DMo[2]
Disk margin with:
GainMargin: [0.0, Inf]
PhaseMargin: [-90.0, 90.0]
DiskMargin: 2.0
Frequency: 0.0 rad/s,  0.0 Hz
DelayMargin: Inf s
Skew: 0
WorstPerturbation: 0.0 - 0.0im
julia> DMo[1]
Disk margin with:
GainMargin: [0.0, Inf]
PhaseMargin: [-90.0, 90.0]
DiskMargin: 2.0
Frequency: Inf rad/s,  Inf Hz
DelayMargin: 0.0 s
Skew: 0
WorstPerturbation: Inf + 0.0im
julia> MMo
Disk margin with:
GainMargin: [0.6834, 1.4633]
PhaseMargin: [-21.3031, 21.3031]
DiskMargin: 0.3762
Frequency: 0.0 rad/s,  0.0 Hz
DelayMargin: 371808.7261 s
Skew: 0
WorstPerturbation: missing
②多次回路盘稳定裕度：考虑了两个反馈回路中独立和并发的增益/相位变化。输出结果就
更加现实的评估。
```

## Page 14

```text
14
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.1 不确定系统分析- 基于圆盘的增益裕度和相位裕度
函数及调用方式
说明
DGM = getDGM(GM,PM,"tight")
DGM = getDGM(GM,PM,"balanced")
DGM,DPM = getDGM(___)
将增益和相位变化转换为基于圆盘的增益变化
DPM = getDPM(DGM)
DPM = getDPM(GM)
将基于圆盘的增益变化转换为基于圆盘的相位变化
GM,PM = dm2gm(alpha)
DGM,DPM = dm2gm(alpha,sigma)
将圆盘大小和偏斜度转换为基于圆盘的增益和相位变化
alpha,sigma = gm2dm(DGM)
alpha,sigma = gm2dm(GM)
将基于圆盘的增益裕度转换为圆盘大小和偏斜度
在基于圆盘法的不确定系统分析中，圆盘大小、偏斜度、增益变化、相位变化之间的转换关系存在如图所示4个函数：
二.  与盘稳定裕度相关的其余函数
圆盘大小
𝛼
增益变化
DGM/GM
偏斜度
𝜎
相位变化
DPM/PM
dm2gm
gm2dm
getDPM
getDGM
```

## Page 15

```text
15
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.2 不确定系统分析- 正规化互质分解
互质性：若两个多项式没有阶次大于等于 1 的公因子，则称这两个多项式是互质的。
最小实现：传递函数的一个具有可能的最小维度的实现，需要满足分子多项式和分母多项式的互质性（即没有零极点相消）。
正规化互质分解是利用正规化互质因子进行计算的第一步，在后续的模型简化(reducespec)和控制器合成(ncfsyn)中均有需要。
一.  正规化左互质分解（lncf）
1
,
l
l
l
l
l
l
sys
M
N
M M
N N
I
−


=
+
=
式子中，𝑀𝑙
∗表示𝑀𝑙的共轭。lncf返回稳定系统的最小状态空
间实现[𝑀𝑙, 𝑁𝑙]，及互质因子𝑀𝑙和𝑁𝑙。
计算动态系统模型的正规化左互质分解。因式分解为：
1
,
l
l
l
l
l
l
sys
M
N
M M
N N
I
−


=
+
=
计算动态系统模型的正规化右互质分解。因式分解为：
式子中，𝑀𝑟
∗表示𝑀𝑟的共轭。rncf返回稳定系统的最小状
态空间实现[𝑀𝑟; 𝑁𝑟]，及互质因子𝑀𝑟和𝑁𝑟。
二.  正规化右互质分解（rncf）
①计算分解因子：
sys = zpk([1 -1+2im -1-2im], [-1 2+1im 2-1im], 1);
fact, Ml, Nl = lncf(sys);
示例3.2：计算SISO系统的正规化左互质分解
( )
(
)(
)
(
)(
)
2
2
1
2s
5
1
4s
5
s
s
G s
s
s
−
+
+
=
+
−
+
julia> sigma(fact)
③证实分解性质：系统[𝑴𝒍(𝒋𝝎), 𝑵𝒍(𝒋𝝎)]在所有频
率下都是单位向量。考察fa c t 的奇异值，即
[𝑀𝑙(𝑗𝜔), 𝑁𝑙(𝑗𝜔)]的稳定最小实现。在很小的数值
误差范围内，fact的奇异值在所有频率下均为
1(0dB)。
输出
②检验分解因子：因子Ml和Nl的分子分别是sys的分母和分子。因此，sys=Ml\Nl成立。
julia> zpk(ss(Ml))
(1.0s + 1.0000000000000004)(1.0s^2 - 3.9999999999999982s + 5.0)
0.7071067811865475----------------------------------------------------------------------------
(1.0s^2 + 3.162277660168379s + 5.000000000000005)(1.0s + 0.9999999999999842)
Delay: 0.0
连续时间传递函数模型
julia >zpk(ss(Nl))
(1.0s - 1.000000000000001)(1.0s^2 + 2.0s + 5.0000000000000036)
0.7071067811865475----------------------------------------------------------------------------
(1.0s^2 + 3.162277660168379s + 5.000000000000005)(1.0s + 0.9999999999999842)
Delay: 0.0
连续时间传递函数模型
```

## Page 16

```text
16
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.3 不确定系统分析- 结构奇异值
结构奇异值（Structured Singular Value），通常用 𝜇 表示，用于分析具有特定结构的不确定性系统的鲁棒性和稳定性。
一.  计算结构奇异值上界（mussv）
(
)
( )
(
)


max
1
min
:det
0,



=
−
=

M
M
I




函数及调用方式
说明
Bounds,MuInfo = mussv(M,BlockStructure)
Bounds,MuInfo = mussv(M,BlockStructure,Options)
根据指定扰动块结构，计算 M 的结构奇异值上界，输入参数含义如下：
M:2 维矩阵、多维数组或FRD 系统模型
BlockStructure:扰动块结构，具体含义如下：
• BlockStructure[i,:] = [-r 0] → 𝛿𝑖  为 r×r 重复的对角实标量扰动；
• BlockStructure[i,:] = [r 0] → 𝛿𝑖  为 r×r 对角复标量扰动；
• BlockStructure[i,:] = [r c] →  𝛿𝑖 为 r×c 复数满块扰动
Options:计算选项，指定为字符串。（详细信息，请参考帮助文档）
输出参数含义如下：
Bounds:结构奇异值 µ 的上下界向量
MuInfo:字典（详细信息，请参考帮助文档）
VDelta = mussvextract(MuInfo)
VDelta,VSigma = mussvextract(MuInfo;nargout=2)
VDelta,VSigma,VLmi = mussvextract(MuInfo;nargout=3)
提取 mussv 计算结果的详细信息

1
n







= 





• 斜体 ∆：具有块对角结构的结构不确定性
• 𝜎max ∆𝑠
： ∆ 的最大奇异值
• 正体 ∆：所有允许的不确定性结构集合
```

## Page 17

```text
17
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.3 不确定系统分析- 结构奇异值
using Random
Random.seed!(0);
# 固定随机数种子
M = randn(5,5) + im*randn(5,5);
BlockStructure = [-1 0;-1 0;1 1;2 0];
Bounds, MuInfo = mussv(M,BlockStructure);
julia> Bounds
1×2 Matrix{Float64}:
4.10643  4.10619
julia> propertynames(MuInfo)
(:bnds, :dvec, :pvec, :gvec, :sens, :blk)
julia> MuInfo.bnds
1×2 Matrix{Float64}:
4.10643  4.10619
julia> MuInfo.blk
4×2 Matrix{Int64}:
-1  0
-1  0
1  1
2  0
VDelta = mussvextract(MuInfo);
# nargout 默认等于 1
_, VSigma = mussvextract(MuInfo;nargout=2);
_, _, VLmi = mussvextract(MuInfo;nargout=3);
julia> VDelta
5×5 Matrix{ComplexF64}:
-0.243535+0.0im       0.0+0.0im        0.0+0.0im            0.0+0.0im             0.0+0.0im
0.0+0.0im  0.243535+0.0im        0.0+0.0im            0.0+0.0im             0.0+0.0im
0.0+0.0im       0.0+0.0im  0.0232757-0.24242im        0.0+0.0im             0.0+0.0im
0.0+0.0im       0.0+0.0im        0.0+0.0im      -0.118551-0.212732im        0.0+0.0im
0.0+0.0im       0.0+0.0im        0.0+0.0im            0.0+0.0im       -0.118551-0.212732im
julia> collect(keys(VSigma))
5-element Vector{String}:
"DRight"
"GRight"
"GMiddle"
"DLeft"
"GLeft“
julia> collect(keys(VLmi))
4-element Vector{String}:
"Dc"
"Grc"
"Dr"
"Gcr"
有关mussvextract() 的输出变量的具体含义，请参阅帮助文档
①. 计算不确定矩阵的奇异奇异值
②. 提取结构奇异值计算的附加信息
示例3.3：计算不确定矩阵的结构奇异值，并提取附加信息
```

## Page 18

```text
18
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.4 不确定系统分析- 鲁棒性分析
一.  不确定系统的鲁棒稳定性裕度（robstab）
二.  不确定系统的鲁棒增益裕度（robgain）
robstab() 计算不确定系统的鲁棒稳定性裕度的上界和下界。
• 稳定裕度大于 1：系统对于其建模的不确定性取值都是稳定的；
• 稳定裕度小于 1：对于某些不确定元素在其允许范围内的一些取值，系统会失
去稳定性。
robgain() 计算不确定系统的鲁棒增益裕度的上界和下界。
• 增益裕度大于 1 ：对于系统建模的所有不确定性值，系统峰值增益始终低于指
定的 Gamma 值；
• 增益裕度小于 1 ：在某些频率下，对于不确定元素在其允许范围内的一些取值，
系统峰值增益会超过指定的 Gamma 值。
函数及调用方式
说明
StabMarg,Wcu,Info = robstab(Usys)
StabMarg,Wcu,Info = robstab(Usys,Opts)
计算不确定系统 Usys 的鲁棒稳定裕度。输出参数的含义如下：
StabMarg：字典，包含的键及其含义如下：
• "LowerBound"：鲁棒稳定裕度的下界
• "UpperBound"：鲁棒稳定裕度的上界
• "CriticalFrequency"：最小稳定裕度对应的频率
Wcu：字典，导致系统不稳定的干扰值
Info：字典，储存有关稳定裕度的其他信息
PerfMarg,Wcu,Info = robgain(Usys,Gamma)
PerfMarg,Wcu,Info = robgain(Usys,Gamma,Opts)
计算不确定系统 Usys 对于指定水平 Gamma 的鲁棒增益裕度。输出参数的含义如下：
PerfMarg：字典，包含的键及其含义如下：
• "LowerBound"：鲁棒增益裕度的下界
• "UpperBound"：鲁棒增益裕度的上界
• "CriticalFrequency"：最小增益裕度对应的频率
Wcu：字典，导致系统峰值增益达到 Gamma 的干扰值
Info：字典，储存有关增益裕度的其他信息
```

## Page 19

```text
19
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
3.4 不确定系统分析- 鲁棒性分析
P = tf(1,[1 0]) + ultidyn("delta",[1,1],Bound=0.4);
BW = 0.8;
K = tf(BW,[1/(25*BW) 1]);
S = feedback(uss(1),P*K);
示例3.4：计算不确定系统的鲁棒稳定性裕度和鲁棒增益裕度：
# 计算鲁棒稳定裕度与鲁棒增益裕度
stabmarg,_ = robstab(S);
perfmarg1,_ = robgain(S,1.05);
# 相对于 1.05 的增益裕度
perfmarg2,_ = robgain(S,2);
# 相对于 2 的增益裕度
julia> gpeak
1.0316119085179376
robgain 指定的 Gamma 值不
能低于标称系统的峰值增益
julia> S
不确定连续时间状态空间模型：1 输出，1 输入，2 状态
包含以下不确定模块：
  delta：不确定LTI对象，最大增益 = 0.4
gpeak,_ = getPeakGain(S.NominalValue);
①. 构造不确定系统
③. 计算鲁棒稳定性裕度和鲁棒增益裕度
②. 计算标称系统的峰值增益
julia> stabmarg
Dict{String, Float64} with 3 entries:
"LowerBound"        => 3.12649
"CriticalFrequency" => 3.70294
"UpperBound"        => 3.12649
julia> perfmarg1
Dict{String, Float64} with 3 entries:
"LowerBound"        => 0.058286
"CriticalFrequency" => 6.61474
"UpperBound"        => 0.058286
julia> perfmarg2
Dict{String, Float64} with 3 entries:
"LowerBound"        => 1.52678
"CriticalFrequency" => 4.92388
"UpperBound"        => 1.52678
系统的不确定性的 5.8% 左右
会导致其峰值增益超过 1.05
系统峰值增益始终不超过 2
系统始终保持稳定
```

## Page 20

```text
Part 4
鲁棒控制器设计
```

## Page 21

```text
21
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.1 鲁棒控制器设计 - 回路成形
一.  指定具有单调增益曲线的加权函数（makeweight）
makeweight调用方式
说明
W = makeweight(dcgain,[freq,mag],hfgain)
创建单调增益曲线的一阶连续时间加权函数，其中
dcgain:低频增益，满足 W(0) = dcgain
hfgain:高频增益，满足 W(Inf) = hfgain
freq:特定频率
mag:特定频率下的增益，频率为 freq 时增益为 mag
（增益需要指定为绝对单位，即放大倍数）
W = makeweight(dcgain,[freq,mag],hfgain,Ts)
创建单调增益曲线的一阶离散时间加权函数，其中
dcgain:低频增益，满足 W(1) = dcgain
hfgain:高频增益，满足 W(-1) = hfgain
Ts:离散时间
freq:特定频率，满足 0 < freq < π/Ts
mag:特定频率下的增益，频率为 freq 时增益为 mag
W = makeweight(dcgain,[freq,mag],hfgain,Ts,N)
创建单调增益曲线的高阶连续/离散时间加权函数。Ts = 0 时创建连续时间加权函
数。
阶数 N 越大，增益曲线越陡峭。
W = makeweight(dcgain,wc,hfgain,___)
指定交叉频率 wc，即增益达到 0 dB 时的频率点。
该语法等价于 W = makeweight(dcgain,[wc,1],hfgain,___)
加权函数是鲁棒控制器设计过程的重要的设计参数，直接影响到控制系统的性能和稳定性。
利用makeweight()快速指定具有特定增益曲线的加权函数，以用于后续的回路成形设计、鲁棒控制器设计、混合灵敏度问题分析等应用。
```

## Page 22

```text
22
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.1 鲁棒控制器设计 - 回路成形
一.  指定具有单调增益曲线的加权函数（makeweight）
示例4.1：创建一阶连续时间加权函数
# 低频增益为 40 dB，高频增益滚降至 -20 dB，1 rad/s 时增益为 10 dB
Wl = makeweight(100,[1,3.16],0.1)
# 低频增益为 -10 dB，高频增益为 40 dB，交叉频率为 10 rad/s
Wh = makeweight(0.316,10,100)
# 绘制伯德图
bodemag(Wl,Wh)
legend(["Wl", "Wh"])
bodegrid(true)
julia> Wl
A =
-0.03159995441764031
B =
2.0
C =
1.5784177231611336
D =
0.1
连续时间状态空间模型
julia> Wh
A =
-1053.9555343737468
B =
256.0
C =
-410.40040425200226
D =
100.0
连续时间状态空间模型
示例4.2：创建高阶连续时间加权函数
分贝(dB)和放大倍数(A)之间的换算关系：
dB = 20log(A)
# 低频增益为 -10 dB，高频增益为 40 dB，1 rad/s 时增益为 6 dB，阶数为 3
W3 = makeweight(0.316,[1,2],100,0,3);
# 低频/高频增益与 W3 相同，阶数为 1
W1 = makeweight(0.316,[1,2],100);
# 绘制伯德图，比较两者的区别
bodemag(W3,W1)
legend(["W3","W1"],loc="northwest")
bodegrid(true)
高阶加权函数的增益曲
线更加陡峭！
```

## Page 23

```text
23
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.1 鲁棒控制器设计 - 回路成形
+
-
K
G
y
u
e
w
+
-
K
G
1z
2z
3z
y
u
e
w
1
W
2
W
3
W
考虑下图所示的典型控制系统：
引入加权函数
对原受控系统进行增广
从输入 𝒘到输出 𝒛= 𝑧1; 𝑧2; 𝑧3 的传递函数为
1
2
3
zw




= 





W S
T
W KS
W T
其中，
𝑺= 𝐈+ 𝑮𝑲−1为系统灵敏度，决定系统跟踪性能；
𝑻= 𝑮𝑲𝐈+ 𝑮𝑲−1为补灵敏度，决定系统的鲁棒稳定性；
𝑲𝑺= 𝑲𝐈+ 𝑮𝑲−1为控制器灵敏度；
加权函数𝑾1, 𝑾2, 𝑾3分别对误差信号𝒆、控制信号𝒖和
输出信号𝒚加权。
该类系统控制器的设计问题被称为混合灵敏度问题。
混合灵敏度控制器设计目标就是寻找一种控制器 𝑲，使系
统具有闭环稳定性，同时满足：
一般情况下将其转化为标准问题，即 𝛾= 1。
由于 𝑺+ 𝑻= 𝐈，所以系统性能和鲁棒稳定性之间存
在矛盾，需要折中处理。因此在实际应用中需要回
路成形设计，即通过加权函数的选择，将回路形状
（奇异值幅频特性）调节至期望形状。
加权函数一般根据以下原则进行选择：
由于外界干扰主要发生在低频段，𝑾1 在低频段应
具有较大增益，高频段无要求；
𝑾3 的选择和系统的不确定性相关。一般情况下高
频段系统标称模型与实际模型之间存在较大差异，
因此 𝑾3 在高频段应具有较大增益。
𝑾2 的选择由控制输入 u 决定。一般情况下不考
虑 𝑾2。
尽量选择低阶加权函数，以获得较为简单的低阶
控制器。
1
2
3
zw



=

W S
T
W KS
W T
二.  混合灵敏度问题的鲁棒 H∞ 回路成形设计方法（mixsyn）
```

## Page 24

```text
24
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.1 鲁棒控制器设计 - 回路成形
二.  混合灵敏度问题的鲁棒 H∞ 回路成形设计方法（mixsyn）
mixsyn调用方式
说明
K,CL,Gamma = mixsyn(G,W1,W2,W3)
生成混合灵敏度问题下的 H∞ 最优控制器，支持ss、tf、zpk类型系统。输出参数分别代表：
K：控制器
CL：闭环系统传递函数，CL = lft(G,K)
Gamma：系统性能水平，即闭环系统 CL 的 H∞ 范数
K,CL,Gamma = mixsyn(G,W1,W2,W3,GammaTry)
计算目标性能水平 GammaTry 的控制器。
如果 GammaTry 无法达到，则 mixsyn 返回的 K 为空白模型，Gamma 为 Inf。
K,CL,Gamma = mixsyn(G,W1,W2,W3,GammaRange)
在 GammaRange 范围内搜索控制器的最佳性能水平，GammaRange 为 [Gmin,Gmax] 形式
的二元向量。
限制搜索范围可以减少 mixsyn 为测试不同性能水平而进行的迭代次数，从而加快计算速
度。
K,CL,Gamma = mixsyn(___,Opts)
指定额外的计算选项。Opts 为 HinfSynOptions 类型的选项集。
```

## Page 25

```text
25
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.1 鲁棒控制器设计 - 回路成形
( )
(
)
2
1
1
s
G s
s
−
=
+
示例4.3：构建下面的双输入双输出系统状态空间模型
二.  混合灵敏度问题的鲁棒 H∞ 回路成形设计方法（mixsyn）
s = zpk('s')
G = (s-1)/(s+1)^2
# W1 低频段增益为 20 dB，高频段增益 -40 dB，1 rad/s 时增益为 -20 dB
W1 = makeweight(10,[1,0.1],0.01);
# W2 低频段增益为 -20 dB，高频段增益 0 dB，32 rad/s 时增益为 -10 dB
W2 = makeweight(0.1,[32,0.32],1);
# W3 低频段增益 -40 dB，高频段增益 20 dB，1 rad/s 时增益为 -20 dB
W3 = makeweight(0.01,[1,0.1],10);
bodemag(W1,W2,W3)
K,CL,Gamma = mixsyn(G,W1,W2,W3);
julia> Gamma
0.2521874999639112
S = feedback(1,G*K);
KS = K*S;
T = 1-S;
sigma(S,"b",KS,"r",T,"g",Gamma/W1,"b-.",ss(Gamma/W2),"r-.",Gamma/W3,"g-.")
legend(["S","KS","T","GAM/W1","GAM/W2","GAM/W3"],loc="southwest")
bodegrid(true)
1
1
1
2
1
3



−

−

−




S
W
KS
W
T
W
1
2
3



W S
W KS
W T
𝛾 远小于 1，闭环系统
满足设计要求
①. 定义系统模型和加权函数
②. 计算控制器
③. 分析奇异值曲线：
闭环系统满足设计要求
```

## Page 26

```text
26
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
回路成形设计相关主要Syslab函数，其余函数请参阅Syslab-鲁棒控制工具箱帮助文档
函数及调用方式
说明
K,CL,Gamma,info = ncfsyn(G)
K,CL,Gamma,info = ncfsyn(G,W1)
K,CL,Gamma,info = ncfsyn(G,W1,W2)
K,CL,Gamma,info = ncfsyn(___,tol=Value)
采用 Glover-McFarlane 法进行回路设计
sys = mkfilter(CF,Ord,Type)
sys = mkfilter(CF,Ord,Type,PR)
生成巴特沃斯、贝塞尔、切比雪夫或 RC 滤波器
P = augw(G,W1,W2,W3)
用于加权混合灵敏度 H∞ 和 H2 回路成形设计的受控系统增广
4.1 鲁棒控制器设计 - 回路成形
```

## Page 27

```text
27
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
w
K
z
u
y
P
4.2 鲁棒控制器设计 – H∞分析
一.  生成 𝑯∞最优控制器（hinfsyn）
对于如图所示的系统：
1
2
1
11
12
2
21
22
dx
Ax
B w
B u
z
C x
D w
D u
y
C x
D w
D u
=
+
+


=
+
+


=
+
+

图中，w 代表扰动输入；u 代表控制输入；z 代表性能输出；y 代表测量输出。
( )
( )
( )
( )
( )
1
2
11
12
1
11
12
21
22
2
21
22
A
B
B
P
s
P
s
P s
C
D
D
P
s
P
s
C
D
D






=
= 











对应的状态空间方程为：
𝐻∞最优设计问题是设计反馈控制器 K ，使闭环系统稳定，同时使从 w 到
z 的闭环传递函数矩阵 𝑻𝑧𝑤 的 𝐻∞ 范数最小，即
( )
minimize
zw s

T
(
)
1
11
12
22
21
I
zw
T
P
P K
P K
P
−
=
+
−
符合上述条件的控制器 K 一般不是唯一的。在实际应用中，通常会放宽限
制条件，转而求解𝐻∞次优设计问题：即给定被控对象 P 和性能指标 𝛾> 0，
设计反馈控制器 K，使闭环系统稳定，同时闭环传递函数矩阵 𝑻𝑧𝑤 的 𝐻∞
范数满足
( )
zw s


T
对于上述次优设计问题，可以通过递减 𝛾进行迭代运算的方式，不断逼近
最优解。
从 w 到 z 之间的闭环传递函数为
传递函数 P 的实现具有如下形式：
```

## Page 28

```text
28
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.2 鲁棒控制器设计 – H∞分析
一.  生成 𝑯∞最优控制器（hinfsyn）
hinfsyn调用方式
说明
K,CL,Gamma = hinfsyn(P,Nmeas,Ncon)
计算受控系统 P 的 H∞ 最优稳定控制器，Nmeas 和 Ncon 分别是测量输出y和控制输入u的维
度。
K：控制器
CL：闭环系统传递函数，CL = lft(P,K)
Gamma：系统性能水平，即闭环系统 CL 的 H∞ 范数
K,CL,Gamma = hinfsyn(P,Nmeas,Ncon,GammaTry)
计算目标性能水平 GammaTry 的控制器。
如果 GammaTry 无法达到，则 mixsyn 返回的 K 为空白模型，Gamma 为 Inf。
K,CL,Gamma = hinfsyn(P,Nmeas,Ncon,GammaRange)
在 GammaRange 范围内搜索控制器的最佳性能水平，GammaRange 为 [Gmin,Gmax] 形式的二
元向量。
限制搜索范围可以减少 hinfsyn 为测试不同性能水平而进行的迭代次数，从而加快计算速度。
K,CL,Gamma = hinfsyn(___,Opts)
指定额外的计算选项。Opts 为 HinfSynOptions 类型的选项集。
```

## Page 29

```text
29
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
4.2 鲁棒控制器设计 – H∞分析
示例4.4：为系统G设计一个混合灵敏度控制
器，并用以下受控回路成形滤波器进行增广
# 假设测量输出维度（B2的列数）为 1
Nmeas = 1;
# 假设控制输入维度（C2的行数）为 1
Ncon = 1;
K,CL,Gamma = hinfsyn(P,Nmeas,Ncon);
sigma(CL,ss(Gamma))
legend(["CL","Gamma"])
①. 被控对象定义
②. 生成 𝐻∞ 稳定控制器
julia> K
A =
-0.010000000000019327
-3.552713678800501e-15
-175.5577518722622
-69.52271916909726
B =
0.1118061938551518
4.4722477542060525e-5
C =
-392.5492538000678
-153.21762776816834
D =
9.99999999999996e-5
连续时间状态空间模型
julia> Gamma
0.1844399890346652
# 定义受控系统 G
s = zpk('s');
G = (s-1)/(s+1);
# 定义加权函数 W1,W2,W3
W1 = 0.1*(s+100)/(100*s+1);
W2 = ss(0.1);
W3 = nothing;
# 构造增广系统 P
P = augw(G,W1,W2,W3);
返回的控制器 K 具有 Nmeas 个输入，
Ncon 个输出，状态数与被控对象 P 相同
③. 检查闭环系统的奇异值图
一.  生成 𝑯∞最优控制器（hinfsyn）
( )
1
1
s
G s
s
−
=
+
( )
( )
( )
1
2
1
0.1
,
0.1,
0
100
1
W s
W
s
W s
s
=
=
=
+
闭环系统 CL 的最大奇异值（即 𝐻∞ 范数）
不超过 Gamma，满足设计要求
```

## Page 30

```text
30
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
w
K
z
u
y
P
4.2 鲁棒控制器设计 – H∞分析
二.  生成 𝑯2 最优控制器（h2syn）
示例4.4：针对受控系统模型设计 𝐻2 最优控制器：
# 假设测量输出维度（B2的列数）为 2
Nmeas = 2;
# 假设控制输入维度（C2的行数）为 1
Ncon = 1;
K,CL,Gamma,Info = h2syn(P,Nmeas,Ncon);
pole(CL)
julia> pole(CL)
6-element Vector{ComplexF64}:
-31.6235904580711 + 0.0im
-12.646049256002659 + 3.8044787361003194im
-12.646049256002659 - 3.8044787361003194im
-9.607336259720187 + 0.0im
-9.239311846488453 + 0.0im
-8.693885387955788 + 0.0im
①. 被控对象定义
②. 生成 𝐻2最优稳定控制器
系统极点均位于左半平面，闭环系统稳定
julia> K
A =
-1645.345678403497
-780.4615013409963
724.2540155649751
-2136.187098378665
-1001.6038488675041
941.6008131306859
-1318.334139122738
-592.6348821461788
568.2792826901878
B =
-1.9671324701038566
-2.2424588651268347
-2.888306328827665
-1.454117223473145
-2.066622917530499
0.32760767703331617
C =
-140.4933520818729
-62.78358937907453
61.374655483620586
D =
0.0
0.0
连续时间状态空间模型
julia> Gamma
877.5182497429581
A = [5 6 -6;6 0 5;-6 5 4];
B = [0 4 0 0;1 1 -2 -2;4 0 0 -3];
C = [-6 0 8;0 5 0;-2 1 -4;4 -6 -5;0 -15 7];
D = [0 0 0 0;0 0 0 1;0 0 0 0;0 0 3 6;8 0 -7 0];
P = ss(A,B,C,D);
返回的控制器 K 具有 Nmeas 个输入，
Ncon 个输出，状态数与被控对象 P 相同
③. 检验闭环系统的稳定性：
( ) 2
minimize
zw s
T
𝐻2 最优设计问题是设计反馈控制器 K ，使闭环系统稳
定，同时使从 w 到 z 的闭环传递函数矩阵 𝑻𝑧𝑤 的 𝐻2 范
数最小，即
𝐻2 设计问题和 𝐻∞设计问题的主要区别：
𝐻2 问题的目标是最小化系统的 𝐻2 范数，代表信号功率
的最大放大倍数。
𝐻∞ 问题的目标是最小化系统的 𝐻∞ 范数，代表信号能量
的最大放大倍数。
两种设计问题的核心思想都是抑制外界扰动和模型不确定对
系统输出的影响。
```

## Page 31

```text
Part 5
系统模型与控制器简化
```

## Page 32

```text
32
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5.1 系统模型与控制器简化
函数及调用方式
说明
ncfmr
基于归一化互质分解的模型降阶
reduce
基于 Hankel 奇异值的模型降阶的简化调用方法
balancmr
基于平方根法的平衡模型截断
bstmr
基于 Schur 方法的平衡随机模型截断（BST）
hankelmr
无平衡的 Hankel 最小度近似（MDA）
hankelsv
计算稳定/不稳定或连续/离散系统的 Hankel 奇异值
modreal
系统模态形式实现与投影
schurmr
基于 Schur 法的平衡模型截断
dcgainmr
基于最小直流增益截断的模型降阶
slowfast
快慢模态分解
详细用法请参考 Syslab 鲁棒控制工具箱帮助文档
复杂模型并非始终是良好控制所需。通常情况下，基于 H∞、H2 和 µ 综合等最优控制理论的优化方法生成的控制器的状态个数至少与被控模型相同。此类别提供的模
型降阶函数可以帮助您得到简化后的近似被控模型和控制器模型。
Syslab目前提供以下函数用于模型与控制器简化：
```

## Page 33

```text
33
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5.1 系统模型与控制器简化
一.  基于归一化互质分解的模型降阶（ncfmr）
示例5.1：基于归一化互质分解方法计算
MIMO 系统的模型降阶：
# 定义原系统
using Random
Random.seed!(0);
# 固定随机数种子
G = rss(30,3,3);
# 30 阶随机系统
# 系统降阶
G1, _ = ncfmr(G,10);
# 10 阶降阶模型
G2, _ = ncfmr(G,20);
# 20 阶降阶模型
sigma(G,G-G1,G-G2)
# 比较近似误差
算法步骤
①. 计算输入模型 G 的左归一化互质分解𝑀𝑙𝑠
𝑁𝑙𝑠；
②. 利用 k 阶平衡模型截断法，计算𝑀𝑙𝑠
𝑁𝑙𝑠
的 k 阶
近似值𝑀𝑙𝑟𝑠
𝑁𝑙𝑟𝑠（可参考balred() 函数）；
③. 计算降阶模型 𝐺𝑟𝑒𝑑𝑠
( )
( )
( )
1
red
lr
lr
G
s
M
s N
s
−
=
互质分解：将系统的传递函数分解为两个互质的的传递
函数（即没有共享的零极点）
左归一化互质分解：存在 𝑈𝑙和 𝑉𝑙，满足：
右归一化互质分解：存在 𝑈𝑟和 𝑉𝑟，满足：
( )
( )
( )
1
I
l
l
l
l
l
l
G s
M
s N
s
N U
M V
−
=
+
=
( )
( )
( )
1
I
r
r
r
r
r
r
G s
N
s M
s
U N
V M
−
=
+
=
函数及调用方式
说明
GRed,Info = ncfmr(G,Order)
通过全阶模型互质分解中的模型截断，计算系统的近似降阶模型
Gred：降阶系统模型
Info：类型为 NcfmrInfo 的附加信息结构体，包含以下字段：
•
Info.GL: G 的左归一化互质分解
•
Info.HSV：GL 的 Hankel 奇异值向量
•
Info.ErrorBound：最大近似误差向量，第 i 个元素代表简化
到i 个状态所对应的最大近似误差
GRed,Info =
ncfmr(G,Order,MaxError=Value
,...)
指定降阶系统的 Hankel 奇异值之和与原系统的最大允许误差
ncfmr() 通过截断全阶模型的互质分解中的模态来计算模
型的降阶近似。
降阶系统阶数
越大，近似误
差越小
```

## Page 34

```text
34
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5.1 系统模型与控制器简化
二.  计算系统的 Hankel 奇异值（hankelsv）
示例5.2：计算稳定/不稳定系统的 Hankel 奇异值：
# 被控对象定义
G1 = tf(1,[1,5,6]);
# 稳定系统
G2 = tf(1,[1,1,-6]);
# 不稳定系统
# 直接计算 Hankel 奇异值
sv_stab1, sv_unstab1 = hankelsv(G1);
sv_stab2, sv_unstab2 = hankelsv(G2);
julia> sv_stab1
# G1 稳定子系统的 Hankel 奇异值
2-element Vector{Float64}:
0.10000000000000003
0.01666666666666667
julia> sv_unstab1
# G1 不稳定子系统的 Hankel 奇异值
Int64[]
julia> sv_stab2
# G2 稳定子系统的 Hankel 奇异值
1-element Vector{Float64}:
0.03333333333333351
julia> sv_unstab2
# G2 不稳定子系统的 Hankel 奇异值
1-element Vector{Float64}:
0.05
T
T
T
T
0
0
AP
PA
BB
A Q
QA
C C
+
+
=
+
+
=
计算方式：
给定被控对象 𝐺𝑠= 𝐶𝑠I −𝐴−1𝐵+ 𝐷：
①. 根据 Lyapunov 方程求解可控 Gramian 矩阵 P 和可观 Gramian 矩阵 Q :
②. 计算 P 和 Q 奇异值（特征值）分解：
③. 计算 P 和 Q 平方根：
④. 计算 𝐿𝑜𝑇𝐿𝑟 奇异值矩阵 Σ，即 Hankel 奇异值矩阵：
1 2
1 2

r
p
p
o
q
q
L
U
L
U
=

=

T
T
T
T
p
p
p
p
p
p
q
q
q
q
q
q
P
U
V
U
U
Q
U
V
U
U
=

=

=

=

物理意义：
Hankel 奇异值用于评估系统的：
⚫可控性和可观测性：较大的奇异值对应于系统中可观测性和可控性较强
的状态，较小的奇异值对应于系统中可观测性和可控性较弱的状态；
⚫模型阶数：通过 Hankel 奇异值的大小，忽略较小奇异值对应的状态，
判断系统的最小阶数。
T
T
o
r
L L
U V

=
```

## Page 35

```text
35
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
5.1 系统模型与控制器简化
三.  系统模态形式实现与投影（modreal）
示例5.3：系统模态形式实现与模态分解
G1,G2 = modreal(G);
①. 定义状态空间模型
②. 模态形式转换
A = [0 1 0 0;0 -0.1 3 0;0 0 0 1;0 -0.5 30 0];
B = [0; 2; 0; 5];
C = [1 0 0 0;0 0 1 0];
D = [0;0];
G = ss(A,B,C,D)
模态形式：模态形式下系统的 A 矩阵具有对角线分块
形式。系统实特征值对应于对角线上的 1 x 1 块，复特
征值 𝑎+ 𝑏𝑗 对应于对角线上的 2 x 2 块，具体形式为
最小实现：指的是一个状态空间模型，其状态变量数量
最少，同时仍然能够完全描述系统的输入输出行为；
应用：
• 简化状态空间模型：减少状态变量的数量，从而降低计
算复杂度；
• 提高系统性能：移除不必要的状态变量，从而提高系统
的稳定性和响应速度
a
b
b
a




−


G1,G2 = modreal(G,2);
julia> G1
A =
0.0  -0.9998607698246718
0.0  -0.04999583368055563
B =
0.0033331943634500928
-1.499917198320145
C =
1.0   0.0
0.0  -0.016665734743533535
D =
-0.01666944294006559
-0.1666527719926695
连续时间状态空间模型
julia> G2
A =
5.4525087661353275   0.0
0.0                 -5.502512932454771
B =
2.460599498674898
2.623740441480088
C =
0.017879214444927564  -0.01803790486098624
0.18043168463268386   -0.17873998795862822
D =
0.0
0.0
连续时间状态空间模型
③. 根据可选输入 cut 分解模态
julia> G1
A =
0.0   0.0                  0.0                 0.0
0.0  -0.04999583368055527  0.0                 0.0
0.0   0.0                  5.452508766135327   0.0
0.0   0.0                  0.0                -5.502512932454772
B =
30.000000000000167
-30.03414342128311
2.473180176222291
2.636088196756005
C =
1.0   0.998752199617591      0.017788265700515477  -0.017953413137534784
0.0  -0.0008322934939024666  0.1795138571061975    -0.17790274828203068
D =
0.0
0.0
连续时间状态空间模型
julia> G2
D =
0.0
0.0
连续时间状态空间模型
```

## Page 36

```text
Part 6
线性矩阵不等式
```

## Page 37

```text
37
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
6 线性矩阵不等式 – LMI 系统指定
LMI是线性矩阵不等式
其中𝑳𝑁是对称常数矩阵，𝑥𝑁是决策变量，𝒙为决策向量
在大多数控制问题涉及的 LMI 并不是传统意义上的 LMI，问题的变量
通常表达为矩阵形式。例如稳定性问题需要求解的 Lyapunov 矩阵不等
式：
或者代数黎卡提方程：
其中，𝑨、𝑩、𝑷、𝑹、𝑸均为已知常数矩阵，且𝑹、𝑸为对称矩阵。
( )
0
1
1
0
N
N
x
x
=
+
+
+

L x
L
L
L
T
0
+

A X
XA
T
1
T
0
−
+
−
+

A X
XA
PBR B P
Q
T
T
T
T
T
0




+


−





−


I
I
A X
XA
XC
B
N
CX
D
N
B
D
项
外因子
内因子
矩阵变量
LMI 的相关术语含义如下：
𝑿和𝛾称为矩阵变量（Matrix variables），标量可以被视为 1 × 1 的矩阵变量；
𝑨T𝑿，𝑿𝑨，𝑩等称为项（Term），可以分为常数项和变量项；
𝑵和𝑵T称为外因子（Outer factor），它们未必是方阵，并且在一般的控制问题中不涉及；
位于中间位置的分块矩阵是内因子（Inner factor），为对称块矩阵。
LMI 是线性矩阵不等式（Linear Matrix Inequality）的缩写。由于LMI 解的集合是凸集，因此被广泛用于求解各种优化问题。LMI 已经成为研究后现代控
制理论的基本工具。利用LMI表示的控制问题具有以下优点：
各种设计规范和约束条件都可以用 LMI 表示；
利用 LMI 表示的控制问题可以通过高效的凸优化算法精确求解；
作为一种数值方法，LMI 法可以求解许多无法利用解析法求解的问题。
```

## Page 38

```text
38
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
6 线性矩阵不等式 – LMI 系统指定
Syslab LMI系统指定函数
说明
hLMI = setlmis(LMI0)
LMI 系统描述初始化
X,n,sX = lmivar(Type,Struct)
定义 LMI 系统中指定类型的矩阵变量
lmiterm(TermID,A)
lmiterm(TermID,A,B)
lmiterm(TermID,A,B,:s)
定义 LMI 系统的项
newlmi()
Tag = newlmi()
为现有 LMI 系统添加一个新的LMI
lmisys = getlmis()
获取 LMI 系统内部描述
newsys = delmvar(lmisys,X)
从 LMI 系统中删除一个矩阵变量
ndec = decnbr(LMISys)
LMI 系统的决策变量总数
具体使用方法及示例，可参考Syslab帮助文档，这里不再赘述
需要说明的是，Syslab鲁棒控制工具箱函数目前仍在完善过程中，后续版本中将提供更多 LMI 求解与分析函数
```

## Page 39

```text
39
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
6 线性矩阵不等式 – LMI 系统指定
T
T
T
T
T
T
T
2
3
1
1
1
T
1
2
0
0
x
f




−
+
+





−
−




I
AX A
E
D D
B X
CX C
CX C
M
M
X B
X
# 初始化LMI系统
hLMI = setlmis([]);
# 定义矩阵变量
X1, _, _ = lmivar(2,[3 3]);
X2, _, _ = lmivar(1,[3 1]);
x3, _, _ = lmivar(1,[1 1]);
# 定义常数矩阵
A = B = [1 2 3;4 5 6;7 8 9];
C = D = [1 2 3;0 1 0;3 2 1];
E = eye(3);
M = 2 * eye(6);
f = 3;
其中𝑿1和𝑿2分别代表类型 2 （非对称矩阵）和类型 1 （对称矩阵）的矩阵变量，𝑥3为标量变量（视为类型 1 矩阵变量）
示例6.1：在Syslab中定义LMI如下
①. 定义矩阵变量和常数矩阵
# 定义新的LMI
nlmi = newlmi()
# 定义LMI不等号左侧的项
lmiterm([nlmi,1,1,X2],2*A,A')  # 2*A*X2*A'
lmiterm([nlmi,1,1,x3],-1,E)    # -x3*E
lmiterm([nlmi,1,1,0],D*D')     # D*D'
lmiterm([nlmi,2,1,-X1],1,B)    # X1'*B
lmiterm([nlmi,2,2,0],-1)       # -I
# 定义LMI不等号右侧的项
lmiterm([-nlmi,0,0,0],M)          # 外因子 M
lmiterm([-nlmi,1,1,X1],C,C',:s)   # C*X1*C'+C*X1'*C'
lmiterm([-nlmi,2,2,X2],-f,1)      # -f*X2
②. 定义LMI的项
③. 获取LMI内部描述
lmisys = getlmis()
注意：使用getlmis()后，
工作区变量 hLMI 将被清空。
在此之后，如果需要定义一
个新的 LMI 系统，请再次使
用setlmis()进行系统初始
化。
注意：在使用lmivar()和lmiterm()描
述新的 LMI 系统之前，必须首先使用
setlmis()初始化其内部描述。同时输出
必须命名为 ”hLMI”。
232-element Vector{Int64}:
1
3
8
12
9
97
135
16
0
0
⋮
2
1
0
1
1
-3
1
1
1
1
输出
```

## Page 40

```text
40
Copyright © 2025 苏州同元软控信息技术有限公司
All rights reserved
感谢倾听
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
```
