# Syslab与Sysplorer双向集成_2025b

- Source: `MWORKS高校星火计划资料包/培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/Syslab与Sysplorer双向集成.pdf`
- Converted by: `MinerU precise API`
- Conversion date: `2026-05-08`
- Review status: `MinerU converted; spot check recommended`
- Priority: `P0`
- Source SHA1: `22616e83b3dc`
- MinerU batch id: `702ffa8d-4239-4d3f-b385-1a3ff1197d59`
- Images: `158`
- Notes: 较新版本的 Syslab/Sysplorer 集成材料。

# MWORKS.Syslab和  
MWORKS.Sysplorer双向集成

# CONTENTS

# 目录 $\rightarrow$

01 背景-使用前的准备  
02 ToWorkspace   
03 FromWorkspace   
04 Syslab Block   
05 Sysplorer API   
06 工作区同步  
07 模型调试

# PART 01 $\rightarrow$

# 背景

使用前的准备

![](Syslab与Sysplorer双向集成_2025b_images/15364bb13da55624e0207325547849602f22b7d36da4c04a68b6b763a72a7c15.jpg)

# 1.1 信息物理融合系统(CPS)

![](Syslab与Sysplorer双向集成_2025b_images/650537f0846873713f260a8a8a09b17ec49954ebad04af78277bcd85efeffafc.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/8c0fad05787db8f828b54e80b549bd3fb594668668400cd0797578f6fbcfea3e.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/1713077f7f2471f51bc9e87ee65fbe3b839e271b2fdda5c83600cedcfdea1010.jpg)

Syslab

![](Syslab与Sysplorer双向集成_2025b_images/682c4a5e6bd48125ce88744620e9530e4de562c8e0a837a619414a24e71d83b4.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/cb4d33243e741bf2e43f1482e69243faa92fdce5d9f9dfef2fd7d8bd0f124c5c.jpg)

Sysplorer

# 1.1 信息物理融合系统(CPS)

Radar Tracking Using Syslab Function Block   
![](Syslab与Sysplorer双向集成_2025b_images/5140a543d46f7e7e02a2de8772d2f04bd9d9166e7bd2c6ae88c1b1752f242c79.jpg)  
操作步骤：  
(1) 在Syslab中打开示例并运行：Examples/08 SyslabWorkspace/Demo_SyslabFunction_RadarTracking.jl

示例详见：Sysplorer内置模型库SyslabWorkspace/Examples/Demo_SyslabFunction_RadarTracking/RadarTracking

![](Syslab与Sysplorer双向集成_2025b_images/fa1d301714e6dce257a3cae8de67291e5dd232d3a659f0e353c26db405fcbee3.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/bb157ff7fee0503f276a54ece41dbdbc7e9c97cfcabd1cf47cc41203b28560a3.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/b58573c35660bd360ce986b1ea55f4a48383c80c50c6feaaae3bb6ccd6362c85.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/9f4a2735f74f543e19f46598d7e58114bd4680836164b8a25e4dd940e72895be.jpg)

# 1.2 使用前的准备

在 Syslab 菜单栏中点击 Sysplorer 图标，自动打开 Sysplorer 软件并加载 SyslabWorkspace 模型库

![](Syslab与Sysplorer双向集成_2025b_images/04a8798c15b64e32fbfca2bc07276f549ece5f557178f1ec4de57d222c8d5867.jpg)

# 使用须知:

1. 如不能打开Sysplorer软件，则需要确认Syslab首选项中 Sysplorer可执行文件路径是否正确  
2. Syslab和Sysplorer均需2022版以上  
3. Sysplorer软件编译器为64位

![](Syslab与Sysplorer双向集成_2025b_images/b87ef75d01c161b910cb859d0da8242141631b9929e36d4f0beed5f7d986f336.jpg)

# 02

# PART 02

# To Workspace

将数据写入 Syslab 工作区

# 2. To Workspace

# 将Sysplorer/Sysblock的仿真结果发送至Syslab工作空间中

![](Syslab与Sysplorer双向集成_2025b_images/b437d42807f1cc7b0ddd267c65f28a32842d2cf9a602fb19e979ebdb4c02ba0f.jpg)  
Syslab

![](Syslab与Sysplorer双向集成_2025b_images/6038fb2f2fc14975be4dbf246264b6508360ff83dd816aaaebcc420f2ed8e3d5.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/b659d2d08652b1448cc4f58ca407ec232742f17518e7eb63b49dca59bcb5eaf1.jpg)  
Sysplorer

![](Syslab与Sysplorer双向集成_2025b_images/d1b16d817da055020053e395e1e9d53c83c6e64a20ad3cf705b6bb9a52f7e7a5.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/31126abd9aa41dc5e9e6b052c0613f485ddbb2410b03b79e8f0ba5ac42b3d5d8.jpg)

To Workspace子库中包含4个组件，分别为：

- ToWorkspace_Scale: 输出为标量数据   
- ToWorkspace Vector: 输出为一维数组   
- ToWorkspace Matrix: 输出为数组  
- ToWorkspace_3D_Array: 输出为三维数组

模型组件路径：Sysblock. Utilities.ToWorkspace

# 2. To Workspace

![](Syslab与Sysplorer双向集成_2025b_images/47fd841a832315bd429df93015a31a7e0f02b3d577e932ecb71faa96ea67b122.jpg)  
示例详见：Sysplorer内置模型库

SyslabWorkspace/Examples/Demo_ToWorkspace_PID/stretcher

![](Syslab与Sysplorer双向集成_2025b_images/9f34ede3a2783d97fc35ca98d02c883767d9bfcc2fa3abdb3e55432b4c310062.jpg)

# 仿真

![](Syslab与Sysplorer双向集成_2025b_images/13502cfa29dbc214057c9fc41804c80a8aacc6644dd96be205ba15b3904c2682.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/e2d63527a5bc512d926eecaa98a0b1b0fc5b5d4fda654227137a77f73f7234ab.jpg)  
使用Syslab对仿真结果进行处理分析

![](Syslab与Sysplorer双向集成_2025b_images/c9bdae0e9465d35ef76fadaf127e06f701380abd849e136eeee7b4cd93bbc430.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/5f3e32e93968a3d7cd6674e1ab4d4e9e30b8c28844d71900d88758772338d06e.jpg)

using TyPlot

t = out.tout

w = out.w

plot(t, w)

在Syslab中进行输出变量的后处理

# 2. To Workspace

![](Syslab与Sysplorer双向集成_2025b_images/87fda4df72fd761e90e0a499b5fa344fce9d734de92f7e4d394718c363cf00c9.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/de199b8cbe3f5ca99909a7cdac425f23438a04f51449e365213d341e021ac824.jpg)

# 打开模型

![](Syslab与Sysplorer双向集成_2025b_images/ce7cef243dc9ac53fca6e2669ee5e067031c73932062ec1710b93d1974ca5e76.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/62d9239b18f97231a45f2cfda484695e2841224d4c848f913bedee647729c8cc.jpg)

使用Syslab对仿真结果进行处理分析

![](Syslab与Sysplorer双向集成_2025b_images/17c2ff1811585df6ec46d36f27e6223ae53a220925b3851e22bea901c79bedc6.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/7a105af5f74f63a2f87b9075c099b5419d7b52b5c5f2456dc570955ab3f65049.jpg)

using TyPlot

$$
t = \text {o u t}. \text {t o u t}
$$

$$
\text {s i m o u t} = \text {o u t . s i m o u t}
$$

$$
\text {p l o t} (t, \text {s i m o u t})
$$

在Syslab中进行输出变量的后处理

# 03

# PART 03

# From Workspace

从 Syslab 工作区加载数据

# 3. From Workspace

# Sysplorer/Sysblock从Syslab工作空间中读取数据并作为输入

![](Syslab与Sysplorer双向集成_2025b_images/c5c0e330f37a6c4eded70bd337cefe595b1a2556d756f109089140c89cf6ae9f.jpg)

Syslab

![](Syslab与Sysplorer双向集成_2025b_images/3a8e5be0bf16e08f9d284df4ad309c9d639ea71ec3597057260cf23439845fc6.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/e7e8dc0b9c014196e950983a50fc0ab9f144e593f47dde7c6ed94f8c37fb02f7.jpg)

Sysplorer

![](Syslab与Sysplorer双向集成_2025b_images/1d4cea09984356e2b9b301882ab854263abea2f69b432393165626809a1ba33b.jpg)

FromWorkspace子库中包含5个组件，分别为：

- FromWorkspace_Scale: 获取标量数据   
- FromWorkspace_Vector: 获取一维数组   
- FromWorkspace Matrix: 获取二维数组  
- FromWorkspace_3D_Array: 获取三维数组  
- FromWorkspace_TimeTable: 获取表格矩阵，并通过线性插值生成信号

注：FromWorkspace传递的量均为变量，不能直接作为组件参数。

![](Syslab与Sysplorer双向集成_2025b_images/54bddf957d0b41323dc66573b9c72703d700647049b0aff335cfbebf3584fe6a.jpg)

Constant

模型路径：Sysblock SOURCES Constant

功能：读取Syslab工作区标量或者向量数据

FromWorkspace

模型组件路径：Sysblock SOURCES.FromWorkspace

功能：读取Syslab工作区矩阵数据，且把第一列作为时间列

# 3. From Workspace

Julia代码

$$
\text {t a b l e} = \left[ \begin{array}{l l l} 0 & 1 & 0 & 0 \end{array} \right.
$$

1 1 0 0

2020

3020]

```java
combiTimeTableX = table[, [1,2]] #取1,2两列

```c
combiTimeTableY = table(:, [1,3]) #取1,3两列

```c
combTimeTableZ = table(:, [1,4]) #取1,4两列

![](Syslab与Sysplorer双向集成_2025b_images/b0d3c104a3017152351c49103da2f87c615521835bf709b44479f59ac7dead36.jpg)

# 代码运行

![](Syslab与Sysplorer双向集成_2025b_images/2a5b505ee721644ae70d4182acfe887f86b43aa5c4ca67fea67bb9861a8a80ea.jpg)

若结果不一致，可点击清空工作区再重新运行代码

# 使用FromWorkspace组件

![](Syslab与Sysplorer双向集成_2025b_images/f85d3471363a18dab5b3cae3cb32e6abbeea7f1d011a6391d8588ee309bb3120.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/3f2615fe25f98a0fdfb32317e2c54e4c2d1884ecfae841a4067e6c9a1210d84f.jpg)

# 设定参数

名与工作空间变量名需完全一致

![](Syslab与Sysplorer双向集成_2025b_images/96f03dbf350580b7ecaea09ff442de6c5c0a85cf1d1f77e65659f159bec3917e.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/765ddd3d03b989b245fc5b2940b55d20b5654a5e5ee9a38cb46703c96b449d8b.jpg)  
结果展示.mp4

示例详见：Sysplorer内置模型库

SyslabWorkspace/Examples/Demo_FromWorkspace_RollingWheelSetPulling

# 3. From Workspace

From Workspace Functions 以函数的形式从 Syslab 工作区中读取数据，因此可以直接将获取的数据作为其他组件的参数值。

![](Syslab与Sysplorer双向集成_2025b_images/371a77915ec8581bbae3503f11f2a99b2a90750bb1333ead61597b2390004cb4.jpg)

# 操作步骤

Syslab编辑并运行以下Syslab脚本  
- Sysplorer编辑并运行SubModel模型  
- 查看仿真结果

```matlab
Syslab脚本：  
# 标量  
i_val = 5  
f_val = 7.5  
b_val = true# 向量  
i_vec = [1, 2, 3]  
f_vec = [1, 2.5, 3.5]  
b_vec = [true, false, true]# 矩阵  
i_mtx = [1 2 3; 4 5 6]  
f_mtx = [1 2.5 3.5; 4 5.5 6.5]  
b_mtx = [true false true; false true]# 三维数组  
i.arr = fill(1, (2, 3, 4))  
i.arr[2, 1, 3] = 17  
f.arr = fill(2.5, (2, 3, 4))  
f.arr[2, 1, 3] = 17  
b.arr = fill(true, (2, 3, 4))  
b.arr[2, 1, 3] = false 
```

# Syslab中计算出结果

```verilog
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
parameter Integer int_mtx[(:, :, ] = FwIntMatrix("i_mtx", 2, 3) "整型矩阵";  
parameter Real real_mtx[(:, :, ] = FwRealMatrix("f_mtx", 2, 3) "实型矩阵";  
parameter Boolean bool_mtx[(:, :, ] = FwBoolMatrix("b_mtx", 2, 3) "布尔型矩阵";  
//三维数组  
parameter Integer int.arr[(:, :, ] = FwInt3DArray("i.arr", 2, 3, 4) "整型三维数组";  
parameter Real real carr[(:, :, ] = FwReal3DArray("f carr", 2, 3, 4) "实型三维数组";  
parameter Boolean bool carr[(:, :, ] = FwBool3DArray("b carr", 2, 3, 4) "布尔型三维数组";  
end SubModel; 
```

# Sysplorer中模型通过函数读取工作空间值作为参数

注：函数调用见：Modelica语法-函数；参数定义见Modelica语法-类与内置类型

# 3. From Workspace

# 结果查看

Syslab脚本：

标量

$$
i \quad v a l = 5
$$

$$
f _ {\text {v a l}} = 7. 5
$$

$$
b _ {\text {v a l}} = \text {t r u e} \# \text {向 量}
$$

$$
i _ {\text {v e c}} = [ 1, 2, 3 ]
$$

$$
f _ {\text {v e c}} = [ 1, 2. 5, 3. 5 ]
$$

$$
b _ {\text {v e c}} = [ \text {t r u e}, \text {f a l s e}, \text {t r u e} ] \# \text {矩 阵}
$$

$$
i _ {-} m t x = [ 1 2 3; 4 5 6 ]
$$

$$
f _ {m t x} = [ 1 2. 5 3. 5; 4 5. 5 6. 5 ]
$$

$$
b _ {m t x} = [ \text {t r u e f a l s e t r u e}; \text {f a l s e t r u e}
$$

$$
f a l s e ] \# \text {三 维 数 组}
$$

$$
i _ {-} a r r = f i l l (1, (2, 3, 4))
$$

$$
i _ {-} a r r [ 2, 1, 3 ] = 1 7
$$

$$
f _ {\text {a r r}} = \operatorname {f i l l} (2. 5, (2, 3, 4))
$$

$$
f _ {\text {a r r}} [ 2, 1, 3 ] = 1 7
$$

$$
b _ {-} a r r = f i l l (\text {t r u e}, (2, 3, 4))
$$

$$
b _ {-} a r r [ 2, 1, 3 ] = \text {f a l s e}
$$

通过From Workspace Functions，将Syslab工作区中的数据直接设置为模型的参数

<table><tr><td colspan="3">组件参数</td></tr><tr><td colspan="3">常规</td></tr><tr><td colspan="3">参数</td></tr><tr><td>int_x</td><td>FwInt(&quot;i_val&quot;)</td><td>整型标量</td></tr><tr><td>real x</td><td>FwReal(&quot;f_val&quot;)</td><td>实型标量</td></tr><tr><td>bool x</td><td>FwBool(&quot;b_val&quot;)</td><td>布尔型标量</td></tr><tr><td>int_vec</td><td>FwIntVector(&quot;i_vec&quot;, 3)</td><td>整型向量</td></tr><tr><td>real_vec</td><td>FwRealVector(&quot;f_vec&quot;, 3)</td><td>实型向量</td></tr><tr><td>bool_vec</td><td>FwBoolVector(&quot;b_vec&quot;, 3)</td><td>布尔型向量</td></tr><tr><td>int_mtx</td><td>FwIntMatrix(&quot;i_mtx&quot;, 2, 3)</td><td>整型矩阵</td></tr><tr><td>real_mtx</td><td>FwRealMatrix(&quot;f_mtx&quot;, 2, 3)</td><td>实型矩阵</td></tr><tr><td>bool_mtx</td><td>FwBoolMatrix(&quot;b_mtx&quot;, 2, 3)</td><td>布尔型矩阵</td></tr><tr><td>int.arr</td><td>FwInt3DArray(&quot;i.arr&quot;, 2, 3, 4)</td><td>整型三维数组</td></tr><tr><td>real carr</td><td>FwReal3DArray(&quot;f carr&quot;, 2, 3, 4)</td><td>实型三维数组</td></tr><tr><td>bool carr</td><td>FwBool3DArray(&quot;b carr&quot;, 2, 3, 4)</td><td>布尔型三维数组</td></tr></table>

![](Syslab与Sysplorer双向集成_2025b_images/1cb926ea9fa088a1bb75ae0ae3845079fbf3f89b4a992495afdac991b432f9da.jpg)

# 3. From Workspace

simin = [0.1 1 1

0.2 2 4   
0.3 3 3   
0.4 4 1]

![](Syslab与Sysplorer双向集成_2025b_images/e41bce0b822f1a249643936765d597770bc061e58b569a10fa32e6be3acd9009.jpg)

# 代码运行

![](Syslab与Sysplorer双向集成_2025b_images/ac8671c6adc19a31d88ad8e6a7acf825c105af518a9e06965209fecdc4c898a8.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/2a6802112804347576fdccf815e2ba2395493485c3049502d1d1f95c4a8fd4f9.jpg)

# 使用FromWorkspace组件

![](Syslab与Sysplorer双向集成_2025b_images/2d1dcbf0f435a51142574b5906a1eb246bc30c1824defdb64c8e0c70e1041409.jpg)  
注：可直接在帮助文档中打开该模型

![](Syslab与Sysplorer双向集成_2025b_images/dd82e4ed93059458509442a835cb2f79b437e55a54ce11c25b166f17648c2abe.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/69a51e0b993b524d421c1a2043153140b80cc53a02f5740c87e711c27b0f6c91.jpg)

# 参数设置

数据：名称与工作空间变量名需完全一致

维度：以示例模型为例，其列数为 3，第 1 列为时间列，因此信号列为 2，维度填写为 [2]。

# 3. From Workspace

$$
1 = [ 1, 2, 3, 4, 5, 6 ];
$$

![](Syslab与Sysplorer双向集成_2025b_images/f9369f953c876b5215563eff43ee2e247f61219b8605e0fa6526beb1df2d92ae.jpg)  
代码运行

![](Syslab与Sysplorer双向集成_2025b_images/027d5885d32ec5d2b0d13695862f3d6427ab8ff6cd6bc05188993bccfe0f6e38.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/bee8fcc841c6e4eb750cd02b50f45083ff074bdcd1166307cec23ebd183a2411.jpg)  
使用 Constant 组件

![](Syslab与Sysplorer双向集成_2025b_images/5052631aaff2a3c1fa0d65d3d055fc91fc718772b7b52e5ff1b64b0d48152d94.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/1c1ea57a6761f252a0d1bff6b03f8a0921e3634303c521152da4bd68fc8ba3cf.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/3ff3294ecce6e9491a47b10e817f0d5039918f34e75938a74c7814b9b14f1198.jpg)

# 参数设置

数据：名称与工作空间变量名需完全一致

![](Syslab与Sysplorer双向集成_2025b_images/a1ad1b711f0d3498ec1189bef94ccd96e0986518939ec87550d2f34e7c658b53.jpg)

# PART 04②

# Syslab Block

使用 Syslab 实现新算法

# 04

# 4.1 Syslab Function

将Syslab中构建的Julia复杂算法封装至Sysplorer中

![](Syslab与Sysplorer双向集成_2025b_images/aa24a9189660e43a356412e6f6337c2030c230172b54d735fb6d76d8581d85c7.jpg)

Syslab

![](Syslab与Sysplorer双向集成_2025b_images/2eff88293b306127d826120cc69d91a40c78c8b53f9865af5956d825f62cce83.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/438560b5978be39bf32d73f93093f8764f4d7992b64f6667f97178203df1125a.jpg)

Sysplorer

![](Syslab与Sysplorer双向集成_2025b_images/06c56121d470fcf4e7f0dca871db86cc8864b718b6f20050d06880ce203e6014.jpg)  
拖拽式建模

Function API中包含2个组件:

- SyslabGlobalConfig：用于全局声明，包括导入包及全局变量声明等。  
- SyslabFunction: 用于嵌入 Julia函数, 并将Syslab Function模块的输入和输出数据指定为参数和返回值。

![](Syslab与Sysplorer双向集成_2025b_images/431e9f09c278848ae02bf3c1c885fefad4283d0f7326279d1d742fe205821ddc.jpg)  
示例详见：Sysplorer内置模型库  
SyslabWorkspace/Examples/Demo_SyslabFunction_RadarTracking/RadarTracking

# 4.1 Syslab Function

右击SyslabGlobalConfig模型，选择Syslab初始化配置，即可转到Syslab中的全局声明代码

![](Syslab与Sysplorer双向集成_2025b_images/a85b4ca8486a5d7a490abdffc03974d75e01f2df398b7d5bba3b89ca2b7c1d12.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/07d85ae2d53f9c859cf82995fd2331af578f7a3fc493921f154bb6a408eb064b.jpg)

using LinearAlgebra

定义全局变量,命名以 g_ 为前缀

g_P = zeros(4, 4)

g_xhat = [0.001; 0.01; 0.001; 400; ];

4x1矩阵

示例详见：Sysplorer内置模型库

SyslabWorkspace/Examples/Demo_SyslabFunction_RadarTracking/RadarTracking

# 4.1 Syslab Function

右击SyslabFunction模型，选择编辑Syslab函数脚本，即可转到Syslab中的算法函数代码

![](Syslab与Sysplorer双向集成_2025b_images/2e095a0083d97c8c93b1ae85cb848058f3d39f77eb8dafb816688dbeba039f76.jpg)

示例详见：Sysplorer内置模型库SyslabWorkspace/Examples/Demo_SyslabFunction_RadarTracking/RadarTracking

# Julia算法

```txt
function EXTKALMAN(meas, deltat, time) # 声明全局变量 global g_P global g_xhat
```

```hcl
Initialize  
residual = []  
xhatOut = [] 
```

```txt
Radar update time deltat is inherited from model workspace #1. Compute Phi, Q, and R Phi = [1 deltat 0 0; 0 1 0 0; 0 0 1 deltat; 0 0 1] Q = Diagonal([0, 0.005, 0, 0.005]) #对应 Matlab的diag R = Diagonal([300^2, 0.001^2]) #2. Propagate the covariance matrix: g_P = Phi * g_P * Phi' + Q 
```

# 注意:

SyslabFunction组件认为脚本中的第一个函数为本组件的主函数，其他函数均为服务于主函数的辅助函数。

# 4.1 Syslab Function

此示例主要介绍如何使用SyslabFunction对输入的向量求取平均值和标准差

# 操作步骤

- 新建模型，拖入realExpression和syslabFunction组件  
- 点击realExpression，右键选择“属性”，修改模型名称为“realExpression[4]”；  
修改realExpression组件参数为“{4,5,6,2}”；

![](Syslab与Sysplorer双向集成_2025b_images/5b960f1109333888522643f45d26841f33d2d6a530c8b6b455690cd267fda885.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/86dbb710fb1b13c6bcb337adbd63a4b84fd7e0a717dd71713424bbdba0d4b09e.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/6ddef9465182d51326ef297d79a36c44deed8a25c833cd166551c18b5f3fa887.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/3bfcc66363c70ccfd59bfe111177affac79df5bf90caad7c4d877c024ae256dc.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/99f707ad7a55d3ab27728ce8988b648c84764fa93530b6a7d252f674d127b3ae.jpg)

realExpression路径：Modelica Blocks. Sources. RealExpression

![](Syslab与Sysplorer双向集成_2025b_images/013839efd2d82c995d2e04943edd13f25cccd35ec30baa10391b332ce5e49cbe.jpg)

示例详见附件：CalNumMean

# 4.1 Syslab Function

# 操作步骤

- 点击syslabFunction1_1，右键选择“编辑Syslab函数脚本”  
- 在Syslab脚本编辑界面输入右侧代码  
- 点击syslabFunction1_1，右键选择“设置Syslab函数端口”将维度设置为[4];

![](Syslab与Sysplorer双向集成_2025b_images/0adf5ac2b67645c1bd500b6da031012e3eff965daa050483bc1f47afc138a562.jpg)

function stats(vals) # 计算平均值与标准差 len = length(vals); mean = avg(vals, len); stdev = sqrt(sum((vals. - avg(vals, len)).^2)) / len); return mean, stdev end

求平均值 function avg(array,size) mean $=$ sum(array)/size;

end

![](Syslab与Sysplorer双向集成_2025b_images/528ff21980f042aa6d58eea8a39349b5f4630f0309dbf26b7d05c7bb78767376.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/8380a456601b806de10259ec158c4db78dc16d1745b991a1910cda5da58e5f49.jpg)

# 4.1 Syslab Function

操作步骤：完成连线，进行仿真，查看结果

![](Syslab与Sysplorer双向集成_2025b_images/227dbbbf05ed52d50e11af3c20fccbf215c9d16fb2a3883e65a9f6e88ca23d3d.jpg)  
组件连线.mp4

![](Syslab与Sysplorer双向集成_2025b_images/9e37fa357730ad9ef54aa87ba0d7feae937544d7d7cbdf14d5121bee71fd6a73.jpg)

# 4.1 Syslab Function

Sysplorer 支持将调用 SyslabFunction 组件的物理模型生成半物理仿真代码，以及导入/导出 FMU。

![](Syslab与Sysplorer双向集成_2025b_images/2e29c4b85428a005b9c997f07a8ce1d736b2f76ed511a45e3bc01d380d783b95.jpg)  
物理模型代码生成流程

![](Syslab与Sysplorer双向集成_2025b_images/200220542bf4f864ae9f01f56c236e95fc87898f62f8fbd122f26632b49b567d.jpg)

# 4.2 Syslab Object

# 使用 Syslab 中的 Julia 对象进行动态系统建模和处理流式数据

![](Syslab与Sysplorer双向集成_2025b_images/71bf96e0b756fbad3290844292a9fee89622338097739cfa93b794b27831fd9a.jpg)

Syslab

![](Syslab与Sysplorer双向集成_2025b_images/4eb77f99bea1125c65811cb5e9646de87c52844ba3f88db0439efba76a8a40de.jpg)

Sysplorer

syslabObject

![](Syslab与Sysplorer双向集成_2025b_images/238981a762d89cbde657ae3b58a50d7d5fba47b922c88c0e05fb948d71335e37.jpg)

拖拽组件

![](Syslab与Sysplorer双向集成_2025b_images/63e0d1ba2e64b5ba28d337a5681fb84357f20c326e88c8bbff0619a0d7f67c1f.jpg)

打开组件类型

在新标签页打开组件类型

![](Syslab与Sysplorer双向集成_2025b_images/446878b7c7fc2183c9b3d86d4d0ebb7105c43a8bcaaaf010e7b388f0348ae79b.jpg)

进入组件

创建子系统

Ctrl+G

拆分一维数组端口

选择Syslab对象文件...

设置Syslab对象端口...

转到模型浏览器

剪切

自 复制

克隆

删除

改变组件类...

重命名...

注释

取消注销

显示端口名标签

显示组件注解

置于顶层

置于底层

旋转 ${90}^{ \circ  }$

旋转-90

水平翻转

竖直翻转

查看文档

编辑参数

属性...

Ctrl+G

$\frac{1}{2} =$

#

Ctrl+X

Ctrl+C

Ctrl+D

Del

X

F2

$\therefore m - 1 \neq  0$ ;

$\frac{1 + u}{1} - \frac{u}{1} = \frac{\left( {1 + u}\right) u}{1} < \frac{u}{1} = u$

(1)

$\therefore m = \frac{3}{11}$

Ctrl+R

Ctrl+S

Alt+F1

Alt+En

![](Syslab与Sysplorer双向集成_2025b_images/6babe000f1c21d2307fa1d1cd19f9a8ff7e4e075f0dcde2fcaba2509de2fb3f4.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/fc978671641ac7bb44d12854d60885b96d073b61a2d0f74137613cb9f4c7b9fa.jpg)  
点击“新建”

![](Syslab与Sysplorer双向集成_2025b_images/de10a0849ffd355d09fbb1446ebc37cfeda5a010895086359b87573b97ab07e9.jpg)

using ObjectOriented

@oodef mutable struct SyslabObject

Description（用于生成Modelica组件描述）

Template for syslab object block.

Parameter（用于生成Modelica组件参数，包括名称、类型、描述）

格式：参数名::参数类型 = 参数值 # 参数注释

例如：

gain::Real = 1.0

#增益

Private (Julia内部变量)

格式：变量名::类型 $=$ 值 #变量说明

例如：

_count::Integer = -1

![](Syslab与Sysplorer双向集成_2025b_images/368104ff2065514ca7f357099b71be69955437b6bbb83e3b39b82dcd358162de.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/e70d431b0a3f2aea39d15877c57d432589ae9b18a0c621c78ee4f44d5789673e.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/a77fec78d68bd5d523dcbcce996fd83d3a00e137c040d5c98831d3f5e42ebac0.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/ea6d7a8509371dddcb08f944fdbdcc5db9566a56440629caa302088f3b1d5397.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/95f700df86aeade62bbb1ce75b5007fbdb78b65f3d899cec4edf2f8f2514bd21.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/f2c19d46ca500c964f6d1cd684b3eac1150c7ea9e5779fa9b0065592ab55b001.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/d520e78770fb84a1db5dca8ff7358938e3ce7f74dae1c34104cf40239df60095.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/2ac5305b65320a3a32c140adb0efdc63df001c542a226b09bf95fed28873a2b3.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/fb13f4086e6eec5f93577a29d2bd5d7e92967e0642ae1ed5181de7a70d6bcdc4.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/4b74988c6d90979a6fb925afd617be9e7586a7f9dd512490c72bad4f027dc9cd.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/c6dbd0121b510968f30c3ab475ea191e3d5620ff25c4293fd4395ba497a93621.jpg)

Methods（主要调用算法，包括setupImpl，stepImpl，releaseImpl）

初始化函数：函数名固定，函数形参与stepImpl函数形参一致

function setupImpl(self, u)

$$
\text {c o u n t} = 0
$$

$$

$$

$$
n o t h i n g
$$

end #setupImpl

单步计算函数：函数名固定，第一个函数形参必须是self,

其余函数形参将作为Modelica组件的输入端口，函数返回值作为输出端口

$$
f u n c t i o n \quad s t e p I m p l (\text {s e l f}, u)
$$

$$
\text {s e l f .} \_ \text {c o u n t} + = 1
$$

$$
\# \dots
$$

$$
y = u * \text {s e l f . g a i n}
$$

$$
\text {r e t u r n} \mathcal {Y}
$$

end #stepImpl

释放资源函数：函数名固定，且只能有一个函数参数self

$$
f u n c t i o n \quad r e l a s e I m p l (s e l f)
$$

$$
\# \dots
$$

$$
\text {r e t u r n}
$$

end #releaseImpl

其它自定义函数，第一个函数形参数必须是self

$$
\begin{array}{l} \# \text {f u n c t i o n} x x (\text {s e l f}) \\ \begin{array}{c c c} \# & \dots \\ & \dots \end{array} \\ \# \text {e n d} \\ \end{array}
$$

end

Syslab脚本界面

# 4.2 Syslab Object

![](Syslab与Sysplorer双向集成_2025b_images/01b1e77fa2ef936d44aab7ecd0073371286a08ee8d1b9174acd11f39e3f82897.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/f5afb5b8c1dc303df19c3d486c70965e9cb884bbd788c3c70d28c9ac163e9517.jpg)  
示例详见：Sysplorer内置模型库SyslabWorkspace/Examples/Demo_SyslabObject_AncalogModulationDemodulation

![](Syslab与Sysplorer双向集成_2025b_images/845ebbdc7d11149cdfee2330ea27866e08c5bd0e297589d20054e9bc229ce53f.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/8d146fbd2dbac6a0dd1705e99f34f7864dc2dbeb6134a9100d803a3be7085ffe.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/d81f809a17e2d55b8d16987206b4a69365de2b9266911c822327c82560748799.jpg)

using TyCommunication

using TyBase

using TyMath

using TySignalProcessing

using ObjectOriented

@oodef mutable struct DSBAmplitudeDemodulator

Description

Parameter

InputSignalOffset::Float64 = 1

CarrierFrequency::Float64 = 100

InitialPhase::Float64 = 0

SampleFrequency::Float64 = 1000

FilterOrder::Int64 = 4

CutoffFrequency::Float64 = 100

PassbandRipple::Float64 = 0.1

StopbandAttenuation::F1cat64 = 50

LowPassFilterMethod::String = "Butterworth"

Private

Samplepoint $= 0$

[b = 0\text{.}]

[a = {10}]

[{z}_{1} = 0]

Methods

function setupImpl(self, data)

#

if selfSAMPLEFrequency $<  = 0$

throw(ArgumentError("Fs must be a real, positive scalar."))

end

check that Fs must be greater than $2^{*}Fc$

if selfSAMPLEFrequency $< 2$ * self.CarrierFrequency

throw(ArgumentError("Fs must be at least 2*Fc."))

end

if self.LowPassFilterMethod == "Butterworth"

··

end

self.zi = zeros Float64, (max(length(self.a), length(self.b)) - 1))

return nothing

end #setupImpl

function stepImpl(self, data)

#...

temp = data .* cos(2 * pi * self.CarrierFrequency * self_SAMPLEpoint / self_SAMPLEFrequency + self.InitialPhase)

···

return out

end #stepImpl

function releaseImpl(self)

#...

return nothing

end #releaseImpl

end

<table><tr><td colspan="4">组件参数
常规</td></tr><tr><td colspan="4">参数</td></tr><tr><td>startTime</td><td>0</td><td>s</td><td>sample start time</td></tr><tr><td>period</td><td>0.0001</td><td>s</td><td>sample period</td></tr><tr><td>InputSignalOffset</td><td>1</td><td></td><td></td></tr><tr><td>CarrierFrequency</td><td>100</td><td></td><td></td></tr><tr><td>InitialPhase</td><td>0</td><td></td><td></td></tr><tr><td>SampleFrequency</td><td>10000</td><td></td><td></td></tr><tr><td>FilterOrder</td><td>4</td><td></td><td></td></tr><tr><td>CutoffFrequency</td><td>20</td><td></td><td></td></tr><tr><td>PassbandRipple</td><td>0.1</td><td></td><td></td></tr><tr><td>StopbandAttenuati...</td><td>50</td><td></td><td></td></tr><tr><td>LowPassFilterMethod</td><td>&quot;Butterworth&quot;</td><td></td><td></td></tr></table>

# 4.2 Syslab Object

此示例说明如何使用 Syslab Object 实现移动平均滤波器

# 操作步骤

拖拽组件timeTable、Syslab Object  
- 点击Syslab Object，右键点击“选择Syslab对象文件”  
- 在弹出对象参数中点击“新建”，打开脚本编辑界面；  
- 在编辑界面输入右侧代码，点击保存，保存在所选文件夹中；  
- 组件timeTable、Syslab Object进行连线

TimeTable的Modelica模型路径

Modelica Blocks. Sources. TimeTable

![](Syslab与Sysplorer双向集成_2025b_images/d0b9a427d5f07668fecfa0570a6697fb1da75c8ee2989b12207f673170304dfd.jpg)

示例详见：Sysplorer内置模型库

SyslabWorkspace/Examples/Demo_SyslabObject_MovingAverageFilter

using ObjectOriented   
using TyMath   
using Base   
@oodef mutable struct MovingAverageFilter # Description（用于生成Modelica组件描述） #Moving average filter # Parameter（用于生成Modelica组件参数，包括类型、名称、描述) WindowLength::Int64 $= 0$ #窗口长度 #Private（内部变量，不对用户展示） pNumChannels::Int64 $= -1$ pCoefficients $\equiv$ [] State $= []$ #Methods（主要调用算法，包括setupImpl，stepImpl，releaseImpl)

```txt
初始化函数：函数名固定，函数形参与stepImpl函数形参一致  
function setupImpl(self, u)  
# Perform one-time calculations, such as computing constants  
self.NumChannels = size(u, 2)  
self.pCoefficients = ones(1, self.WindowLength) / self.WindowLength  
self.State = zeros(self.WindowLength - 1, self.NumChannels)  
return nothing  
end #setupImpl 
```

```txt
# 单步计算函数: 函数名固定, 第一个函数形参数必须是self, 其余函数形参将作为Modelica 组件的输入端口, 函数返回值作为输出端口 function stepImpl(self, u) # Implement algorithm. Calculate y as a function of input u and states. # @info "$(now())" step simulation input parameter u = $u" y, self.State = filter1(self.pCoefficients, 1, u, self.State) return y end #stepImpl
```

```txt
释放资源函数：函数名固定，且只有一个参数，第一个函数形参必须是self function releaseImpl(self) #... return nothing end #releaseImpl
```

```txt
# 其它自定义函数
# function xx(self) {
#     ...
# end
end
```

# 4.2 Syslab Object

# 操作步骤

- 将文件MovingAverage.csv中的数据复制到timeTable组件中  
设置movingAverageFilter_1参数  
- 点击仿真，仿真终止时间为250s，查看movingAverageFilter结果

1. 复制选中csv中参数（注意，不选择表头行）

![](Syslab与Sysplorer双向集成_2025b_images/d556c833ed0d02a2652a16cebac1ff0688f441865d2e5abc6d1483414c9cc55e.jpg)  
注：MovingAverage_此csv文件见附件

2.点击timeTable组件，选择组件参数的table设置行数251行，将csv中参数粘贴进去，点击确定

![](Syslab与Sysplorer双向集成_2025b_images/2f535fafa1e8dd161167f0f9c58fc90f38c8b503494f2cb1fa51e963fe711afe.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/cbc3ebe273056122c940941bc2ac53409adef95128b3f0d424dfde376d1ab132.jpg)

<table><tr><td>组件参数
常规</td><td colspan="3">3.设置movingAverageFilter_1参数</td></tr><tr><td>参数</td><td></td><td></td><td></td></tr><tr><td>startTime</td><td>0</td><td>s</td><td>sample start time</td></tr><tr><td>period</td><td>1</td><td>s</td><td>sample period</td></tr><tr><td>WindowLength</td><td>10</td><td></td><td>窗口长度</td></tr></table>

# 4. 查看仿真结果

![](Syslab与Sysplorer双向集成_2025b_images/e16b8a8c069e522268303f9e504255569d16428252483b5cc71e7ceea061e84b.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/194e29b61d5bf6367a9605bdab5bbb875d3ccad27ab61ce12a1db94a0689f48a.jpg)

# 4.3 Julia Function

将Syslab中构建的Julia复杂算法封装至Sysblock中使用方式及参数设置与 SyslabFunction 一致

![](Syslab与Sysplorer双向集成_2025b_images/d2948c34b61cdf560de5b0810e581fc6e9ddd36e5ba6839f41e519e493d8718a.jpg)

Sysblock. Utilities.JuliaFunction

示例详见附件：JuliaFunctionDemo

```lua
function fcn(u1, u2)  
    y = u1 + u2  
    return y  
end 
```

![](Syslab与Sysplorer双向集成_2025b_images/57c28cff34cd4bc9e552f90fa5d3b8e03f09286270ace71c67e837de6a0903f3.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/10dfb8fad902d88a1f12e5924107cc85876b20653461ae305c7b631914bb87dd.jpg)

# 4.4 Julia Object

使用 Syslab 中的 Julia 对象进行动态系统建模和处理流式数据。

使用方式与 Syslab Object 基本一致

![](Syslab与Sysplorer双向集成_2025b_images/2648ad114c599ec11f5d0ac04a85e0b094b176408aba5fefc0d00e60ae96c82c.jpg)  
Sysblock. Utilities.JuliaObject

![](Syslab与Sysplorer双向集成_2025b_images/43e98550639135028770cfe8072e52281851dffe6c1a5334f842397c854e737c.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/ccd977460bbb4c3dc44f556339b1304c6215d6446d7b2e219218ce6ce25a01a0.jpg)  
注：可直接在帮助文档中打开该示例模型

# 05

# PART 05②

# Sysplorer API

建模仿真语言和科学计算语言之间支持互相调用

# 5. Sysplorer API

Sysplorer API 是具备 Sysplorer 部分功能模块的 API，支持用户对 Sysplorer 进行自动化脚本或专业 APP 开发。用于在 Syslab 使用 Julia 语言调用 Sysplorer，实现物理建模与框图建模，同时可支持模型检查、翻译、仿真模型等一系列操作。

各个函数的使用方式可前往帮助中心查阅。

![](Syslab与Sysplorer双向集成_2025b_images/12832baeaa0b3113a02e172d2fa0be05361ba517271803d1ca513cd631003337.jpg)  
API列表

![](Syslab与Sysplorer双向集成_2025b_images/ef68efe840f5099a40639ea54adbe25f17e414a6337d5f6e4473fa0fd2190e6e.jpg)

![](Syslab与Sysplorer双向集成_2025b_images/212f44ca66d3b4f4e666b5b13d12c31c2415bfdc884c860b7b1da102ac799590.jpg)  
入门案例

# 06

# PART 06

# 工作区同步

Sysplorer 基础工作区和 Syslab 的 Julia 工作区互通数据

# 6. 工作区同步

通过 Syslab 打开 Sysplorer 时，Sysplorer 基础工作区和 Syslab 的 Julia 工作区将互通数据。

包括Syslab数据同步到Sysplorer与Sysplorer数据同步到Syslab。

Syslab 数据同步到 Sysplorer: 当 Syslab 工作区数据修改后, 可以通过手动或自动的方式在 Sysplorer 中同步 Syslab 工作区数据。

## Parameter 类型

VP3 = SysplorerParam();

VP3.Value = [1,2,3,4,5,6];

VP3.Description = "Sysplorer参数，向量类型";

VP3.DataType = "Float64"

VP3.Dimensions = [6]

## Scalar 数值类型

s1 = Float64(64.1)

## Vector 数值类型

v1 = Bool[1,0,1,0,1,1,0,0]

v2 = Float32[32.1, 32.2, 32.3, 32.4, 36.0]

## 2维矩阵

m1 = Bool[1,0,1,0,1,0,1,0,0,0];

m2 = reshape(m1, 2, 5)

![](Syslab与Sysplorer双向集成_2025b_images/78529cb9bbb55313cd2d2d71b5c037359e6e883785319e6a10415b9f6e8e6485.jpg)  
Syslab 数据同步到 Sysplorer.mp4

# 6. 工作区同步

Sysplorer 数据同步到 Syslab：在 Sysplorer 基础工作区中，任何变量或参数的变更，都将实时同步到 Syslab 的 Julia 工作区中。

![](Syslab与Sysplorer双向集成_2025b_images/4ca939bb3b062330765a050a05fda7268154e7f5e9f0f4ab1e8ef39303197a44.jpg)

# PART 07 $\rightarrow$

# Syslab 调试

调试 Sysplorer 模型中 Syslab Block 模块与 Sysblock 模型中 Julia 模块中的 Julia 代码

# 7. Syslab 调试

调试 Sysplorer 模型中 Syslab Block 模块与Sysblock模型中 Julia 模块中的 Julia 代码。 Syslab 调试工作流有两种方式：①常规调试工作流；②指定时刻调试工作流。

![](Syslab与Sysplorer双向集成_2025b_images/bc4aa600ff9af1e987ab17198d5663c476055bae0079cbcae81f62b5db597633.jpg)  
常规调试工作流.mp4

![](Syslab与Sysplorer双向集成_2025b_images/6a6eaca89d7d00b4073eb93891a635519c8939c2a11ea34aef1464985988c73e.jpg)  
指定时刻调试工作流.mp4

![](Syslab与Sysplorer双向集成_2025b_images/e1486f44c6ca18e9295d94b4385ef2bac25a552734c13d0158e55eb219bc5812.jpg)  
https://tongyuanrk.mikecrm.com

# MWORKS软件学习资源需求调研问卷

为更好地解决用户在使用MWORKS软件过程中的学习痛点，优化软件学习资源供给，我们特开展此次调研。本次调研聚焦于用户的线上学习习惯与资源需求，调研结果仅用于学习资源优化，所有数据将严格保密，请您放心填写。感谢您的支持！

一、基本信息

1.您所处的学习/工作阶段是？（单选）

本科在读

硕士在读

博士在读

已工作

2.您所在的专业方向是？（单选）

电气工程

自动控制（自动化/控制工程）

# Thanks.

建立知识规范，营造协同生态

积累工业模型，发展可控平台

融入工业创新，共创先进软件

![](Syslab与Sysplorer双向集成_2025b_images/7c81c0f7d3ae3beec929d751142a6c21a347fdccb3a703d666c0211e044b0ed0.jpg)
