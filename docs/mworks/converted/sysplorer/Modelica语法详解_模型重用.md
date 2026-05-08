# Modelica语法详解_模型重用

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/05-Modelica语法详解/09-Modelica语法详解-模型重用.pdf`
- Converted by: `local PyMuPDF fallback`
- Conversion date: `2026-05-08`
- Review status: `unchecked; MinerU retry recommended`
- Priority: `P0`
- Source SHA1: `f03b21456c58`
- Pages: `39`
- Notes: 继承、替换、参数化和可复用模型结构。

> MinerU MCP was attempted first in this environment, but the current network path to MinerU returned SSL EOF/disconnect errors. This file is a local text-extraction fallback for search and implementation reference.

## Page 1

```text
模型重用
Modelica语法详解
苏州同元软控信息技术有限公司
2024年2月27日
软件版本号：MWORKS.Sysplorer 2024a
标准库版本号：Version 3.2.3
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 2

```text
2
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
目录
1. 继承重用
2. 实例化重用
3. 重声明重用
4. 本章回顾
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 3

```text
3
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model Resistor
import SI=Modelica.Siuints;
Parameter SI.Resistance R(start=1)=1;
SI.Voltage v;
SI.Current i;
…Interfaces.PositivePin p;
…Interfaces.NegativePin n;
equation
V=p.v-n.v;
0=p.i+n.i;
i=p.i;
R*i=v;
end Resistor
仔细观察下面的三个模型的代码，有何特点？
三个组件模型，绝大部分代码是相同的，出现大量的重复代码，给后期代码的修改和维护造成很大的不便。
冗余是一切罪恶的根源
电阻
电感
电容
1. 继承重用
model Capacitor
import SI=Modelica.Siuints;
Parameter SI.Resistance C(start=1)=1;
SI.Voltage v;
SI.Current i;
…Interfaces.PositivePin p;
…Interfaces.NegativePin n;
equation
V=p.v-n.v;
0=p.i+n.i;
i=p.i;
i=C*der(v);
end Capacitor
model Inductor
import SI=Modelica.Siuints;
Parameter SI.Resistance L=1;
SI.Voltage v;
SI.Current i;
…Interfaces.PositivePin p;
…Interfaces.NegativePin n;
equation
V=p.v-n.v;
0=p.i+n.i;
i=p.i;
L*der(i)=v;
end Inductor
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 4

```text
4
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
再阅读下面的代码，和前面的代码进行比较，有何不同？
电阻
电感
电容
基类
通过继承重用的方式，大大简化组件模型代码，避免不必要的冗余，避免了模型维护和修改时的繁琐。
1. 继承重用
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 5

```text
5
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
1. 继承connector，设计不同的图标和连接线
2. 继承partial类，完善模型行为方程
场景1：继承connector，设计不同的图标和连接线
原始接口
入口
出口
1. 继承重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 6

```text
6
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
场景2：继承partial类，完善模型行为方程
每个模型都需要一个入口和一个出口，
并且都需要选择流过模型的介质
1. 继承重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 7

```text
7
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
一般结构：
extends + 基类路径(参数/变量变型)
record ColorData
parameter Real red = 0.2;
parameter Real blue = 0.6;
Real green;
end ColorData;
model Color
extends ColorData;
equation
red + blue + green = 1;
end Color;
model Color
parameter Real red = 0.2;
parameter Real blue = 0.6;
Real green;
equation
red + blue + green = 1;
end Color;
等价
record ColorData
parameter Real red = 0.2;
parameter Real blue = 0.6;
Real green;
end ColorData;
model Color
extends ColorData(red = 0.3);
equation
red + blue + green = 1;
end Color;
model Color
parameter Real red = 0.3;
parameter Real blue = 0.6;
Real green;
equation
red + blue + green = 1;
end Color;
等价
继承时要改变值怎么办？
1. 继承重用-一般结构
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 8

```text
8
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
1.继承保护
model AccessDemo
extends ModelicaGrammar.Reuse.Public;
extends ModelicaGrammar.Reuse.Protected;
equation
a1 + a2 = 7;
a3 + a2 = 3;
a2 + a3 = 2;
end CalProtected;
model Protected
Real a2;
protected
Real a3;
end Protected;
model Public
Real a1;
end Public;
x = access.a1;
访问
数据
x = access.a2;
x = access.a3;
model AccessTest
  AccessDemo access;
  Real x;
equation
  x = access.a1;
end AccessTest;
注意：
将extends继承语句放在protected关键字的作用区域中, 那么继承后，该基类中的所有
元素在派生类中也是protected访问权限。
1. 继承重用-注意事项


苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 9

```text
9
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
record ColorData
parameter Real red = 0.2;
parameter Real blue = 0.6;
Real green;
end ColorData;
model Color
extends ColorData;
parameter Real red = 0.2;
parameter Real blue = 0.6;
equation
red + blue + green = 1;
end Color;
model Color
extends ColorData;
parameter Real red = 0.2;
parameter Real blue = 0.3;
equation
red + blue + green = 1;
end Color;
思考：左侧的两种声明方式是否会报错？
声明单一继承规则：
•
继承后如果有多个相同的声明，只保留一个声明。
•
继承后如果对同一个元素有多个不同的声明，会报错。
2.单一继承
1. 继承重用-注意事项
第一种声明方式
第二种声明方式
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 10

```text
10
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
基类
派生类
package
function
type
record
connector
block
model
package
√
function
√
type
√
record
√
connector
√
√
√
block
√
√
model
√
√
√
record RecordA
...
end RecordA;
model ModelA
extends RecordA; //正确
end ModelA;
package PackageA
...
end PackageA;
model ModelB
extends PackageA; //错误
end ModelB;
打√为派生类可继承的基类
3.继承限制
1. 继承重用-注意事项
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 11

```text
11
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
目录
1. 继承重用
2. 实例化重用
3. 重声明重用
4. 本章回顾
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 12

```text
12
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-使用场景
1. 接口实例化
2. 模型封装
3. 系统仿真模型构建
场景1：接口实例化
新开发的模型中需要接口，可直
接通过实例化的方式进行引用
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 13

```text
13
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-使用场景
场景2：模型封装
PID控制器，由比例单元(P)、积分单元(I)和微分单元(D)组成
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 14

```text
14
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-使用场景
场景3：系统仿真模型构建
蔡氏电路：一种简单的非线性电子电路设计，它可以表
现出标准的混沌理论行为。
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 15

```text
15
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-一般结构
Interfaces.FluidInterfaces.FluidPort_a port_a(p(start = p_start))；
Modelica.Media.Water.WaterIF97_base.ThermodynamicState state;
Modelica.Electrical.Analog.Basic.Resistor R3(R = 1.e-3);
•
connector重用
•
record重用
•
model重用
一般结构：
父类模型路径+ 实例化名（参数、变量、特殊类变型）
Modelica.SIunits.Pressure p(displayUnit = "MPa");
•
type重用
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 16

```text
16
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-一般结构
父类模型路径：待实例化的类在模型库中的路径，可通过拖拽类的方式直接生成
实例化名：符合Modelica命名规则，并能形象描述实例化类的作用
变型：对实例化后的类参数、变量初始值、变量、显示单位、特殊类（replaceable/
redeclare 单独讲解）进行变型
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 17

```text
17
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model CauerLowPassAnalog
extends Modelica.Icons.Example;
Modelica.Electrical.Analog.Basic.Capacitor C1(C = c1, v(start = 0, fixed = true))
annotation (…);
Modelica.Electrical.Analog.Basic.Capacitor C2(C = c2)
annotation (…);
Modelica.Electrical.Analog.Basic.Capacitor C3(C = c3, v(start = 0, fixed = true))
annotation (…);
Modelica.Electrical.Analog.Basic.Capacitor C4(C = c4)
annotation (…);
Modelica.Electrical.Analog.Basic.Capacitor C5(C = c5, v(start = 0, fixed = true))
annotation (…);
…
end CauerLowPassAnalog;
2. 实例化重用-使用方式
实例化C1、C2、C3、C4、C5，通过变型设置电容值，这样就不必因为电
容参数的不同而建立多个电容模型。
注意：
目前遇到的大多数示例中，被变型的组件属性都是参数。尽管Modelica规
范中没有明确禁止对变量、常量等进行变型，但鉴于Modelica参数的设计
意图，不推荐对变量、常量等进行变型。
1.参数变型
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 18

```text
18
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-使用方式
model Array
  parameter Real x[2];
  parameter Real y;
end Array;
model ArrayUse
  Array A1[2](x = [1, 2; 1, 2], y = {2, 5});
end ArrayUse;
model ArrayUse
  Array A1[2](each x = {1, 2}, y = {2, 5});
end ArrayUse;
model ArrayUseError
  Array A1[2](x = [1, 2; 1, 2], y[1] = 2);
end ArrayUse;
注意：
•
使用“each”对所有数组元素
中的某个属性赋相同的值。
•
必须对整个数组进行变型，不
可以对单个数组元素进行变型。
2.数组变型
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 19

```text
19
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-使用方式
在一次变型中，不能对一个元素的同一个属性进行两次赋值修改
model M1
Real x[3];
end M1;
ModelicaGrammar.Reuse.M1 M2(x = ones(3));
ModelicaGrammar.Reuse.M1 M3(x = ones(3),x[2]=2);
正确
错误
3.单一变型
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 20

```text
20
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
2. 实例化重用-注意事项
model C1
parameter Real a;
end C1;
model C2
parameter Real b, c;
end C2;
model C3
final parameter Real x1 = 1;
parameter Real x2 = 2;
C1 x3[2](each a = 33);
C2 x4(b = 4);
C1 x5(a = 5);
extends C1;
extends C2(b = 6, c = 77);
end C3;
model C4
extends C3(x2 = 22, x4(c = 44), x5 = x3, a = 55, b = 66);
end C4;
变量
结果
x1
1
x2
22
x3[1].a
33
x3[2].a
33
x4.b
4
x4.c
44
x5.a
x3.a
a
55
b
66
c
77
C4变量赋值结果
注意：
•
每个元素只能赋值一次；
•
final元素不能进行赋值；
•
each表示数组中的每个变量均赋相同的值；
•
变形按照外层覆盖内层的原则进行合并；
变型合并
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 21

```text
21
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
目录
1. 继承重用
2. 实例化重用
3. 重声明重用
4. 本章回顾
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 22

```text
22
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
1. 架构模型设计
2. 介质数据库
场景1：架构模型设计
如何快速的替
换控制器？
可替换重申明（replaceable/ redeclare ）是其中一种快速替换
模型的方法。
①. 观察该系统的控制器，有三个接口，两个输入，一个输出，
那么我们需要替换的控制器具有相同的接口数量和接口类型。
②. 设计一个架构模型，它只包含了接口，两个输入、一个输出
3. 重声明重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 23

```text
23
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
③. 继承架构模型，开发不同的控制器模型
控制器1
控制器2
3. 重声明重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 24

```text
24
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
④. 封装一个控制器模型，用于系统模型构建
⑤. 采用封装后的控制器模型替代原系统模型中的控制组件
3. 重声明重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 25

```text
25
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
场景2：介质数据库
设想一个场景，用Modelica语言开发了一个水管
模型，如果想把水管中流动的水改变为油液，用
于油路系统中，该如何处理？
介质模型
设备模型：管道
实例化模型
实例化
重申明
采用可替换重申明（replaceable/ redeclare ）
的方法，将设备模型与介质模型分离，开发设备
模型时调用介质模型模板，实例化设备模型时，
将具体介质与设备关联，得到带有介质的实例化
设备模型。
①. 介质模板
②. 水介质物性计算
3. 重声明重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 26

```text
26
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
③. 设备模型开发时与介质模板关联，并调用介质模板函数
进行代码编写
④. 实例化管道模型，并替换介质模板，得到带
有介质的管道实例化模型
3. 重声明重用-使用场景
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 27

```text
27
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
重申明重用，在语法中通过replaceable/ redeclare关键字实现，根据Modelica标准语法语义
的规定可以对所有的类、参数、变量进行重申明，但是在实际的使用中以model、package、
function这三种类的重申明为主，以实现通用化模型的开发。
关键字: replaceable：表示类型或组件可以被替换
redeclare：表示替换类型或组件
3. 重声明重用-使用方法
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 28

```text
28
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model PartialGeometry
Modelica.SIunits.Area A "横截面积";
Modelica.SIunits.Length l "周长";
end PartialGeometry;
基类模型
model cycle "圆形"
  extends PartialGeometry;
  parameter Modelica.SIunits.Diameter d = 0.01;
equation
  A = Modelica.Constants.pi * d ^ 2 / 4;
  l = Modelica.Constants.pi * d;
end cycle;
model triangle "三角形"
  extends PartialGeometry;
  parameter Modelica.SIunits.Length a = 0.01;
equation
  A = 0.5 * a * a * sqrt(3) / 2;
  l = 3 * a;
end triangle;
model square "正方形"
  extends PartialGeometry;
  parameter Modelica.SIunits.Length a = 0.01;
equation
  A = a ^ 2;
  l = 4 * a;
end square;
圆形
三角形
正方形
model Test_Geometry
replaceable model Geometry = cycle
     constrainedby PartialGeometry
      annotation (choicesAllMatching = true);
  Geometry geometry;
  Modelica.SIunits.Area A "横截面积";
  Modelica.SIunits.Length l "周长";
equation
  A = geometry.A;
  l = geometry.l;
end Test_Geometry;
1.model重申明
3. 重声明重用-使用方法
实例化后使用模型
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 29

```text
29
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
典型应用场景：模型的几何结构、不同换热计算方法、不同流阻计算方法等
典型应用案例：标准库中DynamicPipe模型换热模式和流阻计算公式的切换，模型路径：
Modelica.Fluid.Pipes.DynamicPipe
3. 重声明重用-使用方法
1.model重申明
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 30

```text
30
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
package PartialSolidMedium "固体介质基类"
  replaceable partial function Cp_T "返回定压比热"
    input SI.Temperature T;
    output SI.SpecificHeatCapacity Cp "定压比热";
  end Cp_T;
  replaceable partial function thermalConductivity_T "计算导热系数"
    input SI.Temperature T;
    output SI.ThermalConductivity lambda "导热系数";
  end thermalConductivity_T;
  replaceable partial function rho_T "返回密度"
    input SI.Temperature T;
    output SI.Density rho "密度";
  end rho_T;
end PartialSolidMedium;
package Graphite "石墨,没有受过辐射"
  extends PartialSolidMedium;
  constant Real c1(unit = "J/(kg.K)") = -143.9883;
  constant Real c2(unit = "J/(kg.K2)") = 3.6677;
  constant Real c3(unit = "J/(kg.K3)") = -0.0022;
  constant Real c4(unit = "J/(kg.K4)") = 4.6251e-7;
  redeclare function extends rho_T  "计算密度"
  algorithm
    rho := 1776.66;
  end rho_T;
  redeclare function extends Cp_T  "计算比热容"
  algorithm
    Cp := c1 + c2 * T + c3 * T ^ 2 + c4 * T ^ 3;
  end Cp_T;
  redeclare function extends thermalConductivity_T  "计算导热系数"
  algorithm
    lambda := 169.245 - 1.24890e-1 * T + 3.28248e-5 * T ^ 2;
  end thermalConductivity_T;
end Graphite;
package B4C "碳化硼"
  extends PartialSolidMedium;
  redeclare function extends rho_T  "计算密度"
  algorithm
    rho := 1800;
  end rho_T;
  redeclare function extends Cp_T  "计算比热容"
  algorithm
    Cp := 713;
  end Cp_T;
  redeclare function extends thermalConductivity_T  "计算导热系数"
  algorithm
    lambda := (-1.873e-10) * T ^ 4 + (5.792e-07) * T ^ 3 + (-0.0005904) * T ^ 2 + 0.1406 * T +
119.7;
  end thermalConductivity_T;
end B4C;
基类模型
模型1
模型2
2.package和function重声明
3. 重声明重用-使用方法
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 31

```text
31
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model Test_packagefunction
  replaceable package solid = Graphite
     constrainedby PartialSolidMedium
      annotation (choicesAllMatching = true);
  Modelica.SIunits.Temperature T = 300 "温度";
  Modelica.SIunits.Density rho;
  Modelica.SIunits.SpecificHeatCapacity Cp;
  Modelica.SIunits.ThermalConductivity lamda;
equation
  rho = solid.rho_T(T);
  Cp = solid.Cp_T(T);
  lamda = solid.thermalConductivity_T(T);
end Test_packagefunction;
应用模型
3. 重声明重用-使用方法
2.package和function重声明
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 32

```text
32
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
典型应用场景：流体系统中，设备模型与介质模型的分离，通过基于package和function的
重申明，实现设备模型中不同类型的介质选择；
典型应用案例：Modelica标准库中Media介质库的开发和调用方式；
3. 重声明重用-使用方法
2.package和function重声明
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 33

```text
33
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model Oil "液压油"
replaceable model Oil = PreDefinedOil.EquationBased.Constant
constrainedby OilMedia.Interfaces.Base "油液类型选择"
annotation (choicesAllMatching = true);
annotation (...);
end Oil;
model Constant "常特性油液"
extends OilMedia.Interfaces.Base(…);
annotation (...);
end Constant;
model MIL_H_5606 "MIL-H-5606牌号油液"
extends OilMedia.Interfaces.Base(…);
annotation (...);
end MIL_H_5606 ;
model Tabular "基于插值表油液模板"
extends OilMedia.Interfaces.Base(…);
annotation (...);
end Tabular;
说明：
•
“constrainedby 基类路径”用来筛选所有继
承此基类的模型
•
“choicesAllMatching = true”表示所有符合
筛选条件的模型均可在参数框中进行选取重声
明
1.重声明约束
3. 重声明重用-注意事项
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 34

```text
34
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
model Oil "液压油"
replaceable model Oil = PreDefined.EquationBased.Constant
constrainedby PreDefinedOil.EquationBased.Constant "油液类型选择"
annotation (choices(
choice(redeclare model Oil = OilMedia.PreDefined.EquationBased.Constant "常特性油液"),
choice(redeclare model Oil = OilMedia.PreDefined.TabularBased.MIL_H_5606 "MIL-H-5606"),
choice(redeclare model Oil = OilMedia.Templates.Tabular "基于插值表油液模板")));
annotation (...);
end Oil;
说明：
•
“constrainby 组件路径”表示默认选择的
模型
•
“choices”作用为增加下拉框选项并赋值，
    详见《注解》章节
2.重声明注解
3. 重声明重用-注意事项
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 35

```text
35
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
目录
1. 继承重用
2. 实例化重用
3. 重声明重用
4. 本章回顾
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 36

```text
36
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
4. 本章回顾
⚫继承重用
使用场景：
➢
继承connector，设计不同的图标和连接线；
➢
继承partial类，完善模型行为方程；
一般结构：
➢
extends + 基类路径(参数/变量变型)
注意事项：
➢
继承保护
➢
继承限制
➢
单一继承
Object-
Oriented
面向对象
extents
继承
multiple
inheritance
多重继承
protected
保护继承
override
继承覆盖
conflict
继承冲突
change
class
类型替换
redeclare
重声明
replaceable
可替代组件
modification
变型
⚫实例化重用
使用场景：
➢
接口实例化；
➢
模型封装；
➢
系统仿真模型构建
一般结构：
➢
父类模型路径+ 实例化名（参数、变量、特殊类变型）
使用方法：
➢
参数变型
➢
数组变型
注意事项：
➢
单一变型
➢
变型合并
⚫重申明重用
使用场景：
➢
架构模型设计；
➢
介质数据库；
使用方法：
➢
model重申明
➢
package和function重声明
注意事项：
➢
重申明约束
➢
重申明注解
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 37

```text
37
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
4. 本章回顾
课堂回顾
1.继承一个模型需要用到的关键词是（）。
   A. partial     B. extends     C. public     D. record
2.下列类中，不能继承record的是（）。
   A. package   B. record   C. connector    D. model
3.对数组变型的时候，用到的关键词是（）。
   A. Real    B. class    C. each    D. change
4.（）关键词定义的元素禁止变型。
   A. public   B. type    C. final    D. partial
5 .下面是重声明的关键词的是（） 。
   A. replaceable   B. pre   C. change    D. edge
6.用于替换类型或组件的关键词是（） 。
A. change   B. record   C. cross    D. redeclare
7 .表明组件可被替换的关键词是（） 。
A. replaceable   B. pre   C. change    D. edge
8.继承保护的关键词是（）。
A. partial    B. public  C.protected
D.change
9. V型继承属于（）继承 。
10. 可以继承package的类是（） 。
11. 重声明的两个关键词分别是（）和（） 。
12. 外层变型可以覆盖（）变型 。
13. 在声明一个对象的同时修改类的属性属于（） 。
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 38

```text
38
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
4. 本章回顾
课后作业
使用可替换重申明（replaceable/ redeclare ） ，
开发一个管道规格数据模型库；开发一个管道质
量计算模型，通过选择不同的管道规格，并在参
数面板中设置管道长度，计算得到该管道的质量。
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```

## Page 39

```text
39
Copyright © 2024 苏州同元软控信息技术有限公司
All rights reserved
谢谢！
建立知识规范，营造协同生态
积累工业模型，发展可控平台
融入中国创新，打造先进软件
苏州同元软控信息技术有限公司版权所有，未经许可不得复制、传播或以其他方式使用；
版权所有，侵权必究。
```
