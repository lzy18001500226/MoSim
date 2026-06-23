可以。LIO 这一组应该放在刚才那些规划器的**前一层**来讲。

先用一句话确定位置：

> **FAST-LIO2、FAST-LIVO2 等算法负责回答“无人机现在在哪里、怎么运动、周围障碍物在世界坐标系哪里”；Fast-Planner、EGO、SUPER 等规划器负责回答“接下来应该怎么飞”。**

完整链路是：

```text
MID360 / Camera / IMU
          │
          ▼
FAST-LIO2 / FAST-LIVO2
状态估计 + 点云配准 + 局部建图
          │
          ├─ 无人机位姿
          ├─ 速度
          ├─ IMU偏置
          ├─ 世界坐标点云
          └─ 局部地图
          │
          ▼
SUPER / EGO / Fast-Planner
          │
          ▼
轨迹跟踪控制器
          │
          ▼
PX4
```

---

# 16. 项目概述：LIO / LIVO 算法体系

## 16.1 定位

LIO，全称：

```text
LiDAR-Inertial Odometry
激光雷达—惯性里程计
```

它融合：

```text
LiDAR：
    测量周围环境几何结构

IMU：
    测量角速度和线加速度
```

输出机器人连续运动状态：

```text
位置
姿态
速度
IMU零偏
局部地图
```

LIVO则是在 LIO 基础上再加入相机：

```text
LiDAR-Inertial-Visual Odometry
激光雷达—惯性—视觉里程计
```

三种传感器分别擅长：

| 传感器    | 优势                 | 主要问题             |
| ------ | ------------------ | ---------------- |
| IMU    | 高频、延迟低、能感知快速运动     | 积分后迅速漂移          |
| LiDAR  | 有绝对尺度、几何稳定、受光照影响较小 | 频率较低，走廊和平面环境可能退化 |
| Camera | 纹理丰富、信息量大、设备轻      | 受光照、模糊、曝光和弱纹理影响  |

因此融合的核心不是“数据越多越好”，而是：

> **让高频但会漂移的 IMU负责短时间预测，让 LiDAR 和相机不断把预测结果拉回正确位置。**

---

## 16.2 Odometry 和 SLAM 不是完全一回事

里程计主要解决：

```text
从上一时刻到当前时刻
机器人移动了多少？
```

SLAM还要解决：

```text
长期地图如何保持一致？
机器人重新回到旧位置时
能不能识别出来并消除累计漂移？
```

因此：

```text
FAST-LIO2：
    强项是高频、实时、局部连续的里程计和建图

LIO-SAM：
    除了局部里程计
    还强调因子图、GPS和闭环约束

FAST-LIVO2：
    在LiDAR和IMU基础上加入视觉直接法

R3LIVE：
    更强调彩色地图和辐射信息重建
```

FAST-LIO2本身重点是高速 LiDAR—IMU 前端，而不是完整的全局闭环图优化系统；LIO-SAM则明确使用因子图融合 LiDAR、IMU、GPS和闭环等约束。([arXiv][1])

---

# 16.3 LIO 算法谱系

可以先建立这张知识地图：

```text
LOAM
激光里程计与建图分线程
 │
 ├─────────────── 优化 / 因子图路线
 │
 │             LIO-SAM
 │     IMU预积分 + LiDAR因子
 │     GPS + 闭环 + 因子图平滑
 │
 └─────────────── 滤波路线
               FAST-LIO
          迭代扩展卡尔曼滤波
                    │
                    ▼
               FAST-LIO2
        原始点直接配准 + ikd-Tree
             │              │
             │              ├── Point-LIO
             │              │   逐点更新、高带宽
             │              │
             │              ├── Swarm-LIO2
             │              │   多无人机相对状态估计
             │              │
             ▼              ▼
          FAST-LIVO       R3LIVE
       加入相机直接法    几何+彩色地图
             │
             ▼
         FAST-LIVO2
  统一体素地图 + LiDAR/视觉顺序更新
```

另外还有：

```text
LVI-SAM：
    LIO-SAM + VINS-Mono
    属于因子图式LiDAR-视觉-惯性融合路线
```

LVI-SAM官方实现将 LIO-SAM 与 VINS-Mono 在系统层面组合，利用 LiDAR 和视觉惯性两个子系统互相提供约束。([GitHub][2])

---

# 16.4 系统设计逻辑

## 16.4.1 第一性原理：为什么 LiDAR 单独工作不够？

LiDAR的一帧点云并不是同一瞬间拍下来的。

例如 MID360 扫描一帧过程中，无人机一直在运动：

```text
扫描第一个点时：
    无人机在位置A

扫描最后一个点时：
    无人机已经移动到位置B
```

如果直接把这一帧所有点当成同一时刻，就会产生：

```text
墙变弯
柱子被拉长
边缘错位
点云重影
```

这叫：

```text
Motion Distortion
运动畸变
```

IMU频率高，可以估计扫描过程中每个时刻的姿态和位移，因此可以将不同时间采集的点转换到统一参考时刻：

```text
原始点云
    ↓
根据点时间戳和IMU轨迹
    ↓
逐点补偿
    ↓
去畸变点云
```

所以对 FAST-LIO2 来说，**每个激光点的时间信息非常重要**。官方仓库特别指出，Livox消息需要提供逐点时间戳，才能正确进行运动去畸变。([GitHub][3])

---

## 16.4.2 第二性原理：为什么 IMU 不能单独定位？

IMU测量：

```text
角速度 ω
加速度 a
```

通过积分可以得到：

```text
角速度积分 → 姿态
加速度积分 → 速度
速度积分 → 位置
```

但IMU存在：

```text
零偏
噪声
比例误差
温漂
安装误差
```

很小的加速度偏差经过两次积分后，会迅速变成巨大的位置误差。

可以类比为：

```text
IMU：
    一个反应很快但容易越走越偏的人

LiDAR：
    一个反应稍慢，但能看清周围墙壁位置的人
```

LIO让：

```text
IMU负责快速预测
LiDAR负责纠正漂移
```

---

## 16.4.3 第三性原理：什么叫紧耦合？

### 松耦合

```text
LiDAR先独立算一个位姿
IMU也独立算一个位姿
最后再融合两个位姿结果
```

融合对象是：

```text
已经计算好的结果
```

### 紧耦合

```text
IMU原始测量
LiDAR点到平面残差
相机像素光度残差
```

直接进入同一个状态估计器。

融合对象是：

```text
底层原始测量残差
```

紧耦合可以更充分地利用：

```text
传感器不确定性
IMU偏置
外参
几何约束
传感器之间的相关关系
```

FAST-LIO系列采用迭代卡尔曼滤波紧耦合 LiDAR 和 IMU；FAST-LIVO2进一步将 LiDAR、IMU和图像测量放入同一误差状态迭代卡尔曼滤波框架。([GitHub][3])

---

## 16.4.4 第四性原理：滤波和因子图有什么区别？

### 滤波路线

代表：

```text
FAST-LIO2
Point-LIO
FAST-LIVO2
```

处理方式：

```text
上一时刻状态
    +
当前新测量
    ↓
更新当前状态
```

特点：

```text
实时性强
延迟低
适合机载控制
通常重点维护当前状态和局部地图
```

### 平滑 / 因子图路线

代表：

```text
LIO-SAM
LVI-SAM
```

处理方式：

```text
保留一段历史关键帧
将IMU、LiDAR、GPS、闭环写成因子
统一优化一组历史状态
```

特点：

```text
容易加入闭环
容易加入GPS
长期全局一致性更强
计算和系统复杂度更高
```

可以类比：

```text
滤波：
    每写一句就立即修正当前句子

因子图：
    写完一段后回头同时修改前面多句话
```

---

# 17. 项目概述：FAST-LIO2

## 17.1 定位

FAST-LIO2 是香港大学 MaRS 实验室提出的一套高效、鲁棒的 LiDAR—IMU紧耦合里程计与建图框架。

它最核心的两个改进是：

```text
1. 不再依赖人工提取边缘点和平面点
   直接使用原始LiDAR点进行scan-to-map配准

2. 使用ikd-Tree维护增量点云地图
   支持插入、删除、重平衡和局部下采样
```

FAST-LIO2论文报告其可适配旋转式和固态 LiDAR，并面向无人机、手持设备以及 Intel、ARM 等平台；论文实验中展示了最高约100 Hz的里程计与建图处理能力，但这属于作者特定硬件、数据和参数条件下的结果。([arXiv][1])

---

## 17.2 核心设计理念

| 设计原则     | 说明                 |
| -------- | ------------------ |
| IMU高频传播  | 在两次LiDAR更新之间连续预测状态 |
| 紧耦合滤波    | LiDAR点到地图残差直接更新状态  |
| 原始点直接配准  | 不强制提取边缘和平面特征       |
| 迭代更新     | 重复线性化，提高强非线性场景精度   |
| 增量地图     | 新点持续加入，旧点按局部窗口删除   |
| ikd-Tree | 为最近邻搜索、增量更新和下采样服务  |
| 机载实时性    | 优先保证低延迟和较低计算开销     |

---

# 17.3 系统设计逻辑

## 17.3.1 第一性原理：为什么不再提取特征？

传统 LOAM 类算法会将点云分为：

```text
边缘点
平面点
```

然后只使用这些特征点配准。

优点是：

```text
点数少
几何意义明确
```

但问题是：

```text
不同LiDAR扫描模式差异大
固态LiDAR没有传统旋转线束结构
人工阈值依赖较强
一些细微几何信息会被丢弃
```

FAST-LIO2直接使用原始点与地图局部平面进行配准，从而减少对特定扫描线结构和手工特征提取规则的依赖。这也是它更容易适配不同 LiDAR扫描模式的重要原因。([arXiv][1])

---

## 17.3.2 第二性原理：点到平面残差是什么？

对于当前激光点：

```text
p
```

先在地图中寻找附近点，并拟合局部平面：

```text
nᵀx + d = 0
```

将当前点根据预测位姿变换到世界坐标系后，计算它到平面的距离：

```text
r = nᵀ(Rp + t) + d
```

其中：

```text
R：
    当前姿态

t：
    当前位置

n：
    地图局部平面的法向量
```

如果位姿正确：

```text
新扫描到的墙面点
应该落在旧地图墙面上
```

所以残差应接近0。

滤波器不断调整：

```text
位置
姿态
速度
IMU偏置
```

让大量点到平面的残差同时减小。

---

## 17.3.3 第三性原理：为什么是迭代卡尔曼滤波？

普通 EKF 每次测量只线性化一次。

但 LiDAR配准残差与姿态之间高度非线性。

如果初始预测稍有偏差，一次线性化可能不够准确。

迭代方式是：

```text
第一次：
    根据当前预测计算残差
    更新状态

第二次：
    根据更新后的状态重新计算残差
    再次更新

重复若干次
    直到变化足够小
```

因此：

```text
普通EKF：
    只朝估计方向走一步

迭代EKF：
    每走一步重新观察目标方向
```

FAST-LIO和FAST-LIO2的核心正是高效的紧耦合迭代卡尔曼滤波框架。([GitHub][3])

---

# 17.4 FAST-LIO2 的主要架构

```text
IMU数据
   │
   ▼
IMU初始化
├─ 重力方向
├─ 陀螺仪零偏
└─ 初始姿态
   │
   ▼
IMU状态传播
├─ 姿态
├─ 速度
└─ 位置
   │
   ├─────────────────────┐
   │                     │
LiDAR逐点时间戳      状态传播轨迹
   │                     │
   └──────────┬──────────┘
              ▼
        点云运动去畸变
              │
              ▼
       原始点Scan-to-Map
              │
              ▼
      点到局部平面残差
              │
              ▼
            ESIKF
        反复迭代更新
              │
              ▼
       当前位姿和IMU偏置
              │
              ▼
          ikd-Tree地图
      插入 / 删除 / 下采样
```

---

# 17.5 FAST-LIO2 的状态包含什么？

可以抽象成：

```text
EstimatorState
├─ position
├─ orientation
├─ velocity
├─ gyro_bias
├─ accel_bias
├─ gravity
├─ lidar_to_imu_rotation
└─ lidar_to_imu_translation
```

具体是否在线估计外参，取决于配置和实现方式。

这里最重要的是：

> **LIO不仅在估计位置，还同时估计速度、姿态、IMU偏置和重力方向。**

否则IMU误差无法长期被正确纠正。

---

# 17.6 ikd-Tree 是什么？

普通 KD-Tree适合：

```text
地图建好后
进行大量最近邻查询
```

但实时建图时地图不断变化：

```text
新点加入
旧区域删除
局部地图滑动
点云下采样
树结构失衡
```

如果每次都重新构建整棵 KD-Tree，计算开销会很大。

ikd-Tree支持：

```text
增量插入
点删除
动态重平衡
盒状区域删除
树内下采样
最近邻搜索
```

它是FAST-LIO2能够持续维护大型增量点云地图的重要组成部分。([GitHub][4])

---

# 17.7 FAST-LIO2 与 MID360 的关系

FAST-LIO2非常适合固态或非传统扫描模式 LiDAR，但接 MID360 时，真正关键的不是只改一个 `lidar_type` 参数，而是保证：

```text
1. 每个激光点具有正确时间戳
2. LiDAR和IMU时间基准一致
3. 点云字段格式正确
4. IMU坐标系和LiDAR坐标系定义正确
5. 外参正确
6. 驱动没有重复补偿运动
7. 点云发布频率和分包方式正确
```

对于你们的 Sunray-150 + MID360，最容易出问题的地方通常不是滤波数学，而是：

```text
时间同步
外参方向
坐标轴定义
Livox消息格式
IMU噪声参数
```

---

# 17.8 FAST-LIO2 与 PX4 的关系

PX4内部通常也有自己的状态估计器，例如 EKF2。

这就出现两个估计系统：

```text
PX4 EKF：
    服务飞控内部闭环

FAST-LIO2：
    服务外部自主导航和地图
```

常见架构有两种。

## 方案一：FAST-LIO2只给规划器使用

```text
FAST-LIO2
    ↓
ROS2 odometry
    ↓
规划器

PX4继续使用自己的EKF
```

优点：

```text
系统边界清晰
容易调试
不会立即改动飞控内部估计
```

问题：

```text
规划器坐标和PX4坐标可能缓慢不一致
```

## 方案二：FAST-LIO2作为外部视觉里程计送入PX4

```text
FAST-LIO2
    ↓
MAVLink ODOMETRY / VISION_POSITION_ESTIMATE
    ↓
PX4 EKF2
    ↓
飞控内部融合
```

这样可以让PX4利用LIO定位，但必须正确处理：

```text
ENU与NED
FLU与FRD
时间戳
协方差
坐标系
重置计数
```

第一阶段建议先采用方案一，等LIO稳定后再测试外部里程计融合。

---

# 17.9 FAST-LIO2 与规划器的关系

规划器需要两类数据：

```text
无人机当前状态
周围障碍物地图
```

FAST-LIO2可以提供：

```text
Odometry
├─ position
├─ orientation
├─ velocity
└─ covariance

Registered Cloud
    已经转换到世界坐标系的点云

Local Map
    增量点云地图
```

但是要注意：

```text
FAST-LIO2的点云地图
不一定等于规划器直接需要的占据地图
```

通常还需要：

```text
FAST-LIO2点云
    ↓
ROG-Map / Voxel Map / OctoMap
    ↓
障碍物膨胀
    ↓
规划地图
```

所以不应让规划器直接依赖 ikd-Tree内部结构。

---

# 17.10 我们应该吸收 FAST-LIO2 哪些设计？

## 吸收一：状态估计和地图数据结构分离

```text
Estimator：
    计算状态

Map：
    提供最近邻和增量更新
```

---

## 吸收二：传感器预处理独立

统一定义：

```text
LidarPreprocessor
├─ parseFields()
├─ assignPointTime()
├─ filterInvalidPoints()
├─ removeBlindZone()
└─ convertCoordinate()
```

---

## 吸收三：逐点时间戳是一等数据

MoSim的仿真 LiDAR不能只输出：

```text
一帧点云一个时间戳
```

还应支持：

```text
每个点相对于扫描起点的时间
```

否则无法真实验证运动去畸变。

---

## 吸收四：状态协方差

规划和控制不应该只接收一个“绝对正确”的位置。

应该同时获得：

```text
position covariance
orientation covariance
velocity covariance
```

以后可以做：

```text
不确定性感知规划
定位退化降速
定位失效悬停
```

---

# 17.11 我们不应该照搬什么？

## 不照搬一：不要让 FAST-LIO2 内部地图成为平台公共接口

平台公共接口应该是：

```text
PointCloud
OccupancyMap
LocalMapQuery
```

而不是：

```text
ikd-Tree指针
```

---

## 不照搬二：不要忽略闭环和长期漂移

FAST-LIO2局部性能很强，但长距离运行仍可能累计漂移。

需要可选后端：

```text
Pose Graph
Loop Closure
GPS
UWB
AprilTag
已知地图定位
```

---

## 不照搬三：不要默认仿真真值IMU等于真实IMU

必须支持：

```text
白噪声
零偏随机游走
温漂
比例因子
轴不正交
时间延迟
丢帧
饱和
```

否则仿真中LIO太容易成功。

---

# 17.12 在 MoSim 中的位置

```text
MID360 + IMU
      │
      ▼
Sensor Synchronizer
      │
      ▼
FastLio2Adapter
├─ IMU propagation
├─ Deskew
├─ ESIKF
└─ ikd-Tree
      │
      ├─ EstimatorState
      ├─ RegisteredCloud
      └─ LocalPointMap
      │
      ▼
ROG-Map / Planning Map
      │
      ▼
SUPER / EGO
```

---

# 17.13 最小研究任务

```text
1. 跑通官方数据集
2. 理清IMU初始化过程
3. 理清每个激光点时间戳
4. 理清点云去畸变
5. 理清ESIKF状态变量
6. 理清点到平面残差
7. 理清迭代更新过程
8. 理清ikd-Tree插入和删除
9. 记录每帧匹配点数量
10. 记录残差和协方差变化
11. 接入MID360真实数据
12. 接入Gazebo模拟点云和IMU
13. 注入时间偏移和外参误差
14. 将输出接入ROG-Map
15. 将里程计接入SUPER
16. 写 FAST-LIO2 REVIEW.md
```

---

# 17.14 对 FAST-LIO2 的最终判断

```text
是否进入长期项目：
    是

是否作为第一阶段默认LIO：
    是

进入哪一层：
    实时状态估计
    点云去畸变
    局部几何建图

主要吸收：
    ESIKF
    原始点直接配准
    ikd-Tree
    逐点时间戳
    高频机载估计

不承担：
    完整闭环SLAM
    彩色地图
    全局任务规划
    飞行控制
```

一句话：

> **FAST-LIO2最适合作为我们当前MID360无人机的第一版主状态估计器：结构相对直接、实时性强、适合固态LiDAR，而且与SUPER同属一套技术生态。**

---

# 18. 项目概述：FAST-LIVO2

## 18.1 定位

FAST-LIVO2 是一套直接法 LiDAR—IMU—视觉融合里程计与建图系统。

它在FAST-LIO2的几何定位基础上增加相机，使系统同时利用：

```text
LiDAR：
    三维几何约束

IMU：
    高频运动约束

Camera：
    图像纹理和光度约束
```

FAST-LIVO2通过误差状态迭代卡尔曼滤波融合三种传感器，并采用顺序更新方式处理 LiDAR和视觉测量维度差异；LiDAR侧直接配准原始点，视觉侧直接最小化图像光度误差，两者共享统一体素地图。([arXiv][5])

官方代码于2025年1月公开，官方仓库当前主要列出 Ubuntu 18.04至20.04和ROS环境；ROS2版本主要由社区移植维护，因此接入我们的ROS2主干时需要独立评估。([GitHub][6])

---

## 18.2 核心设计理念

| 设计原则      | 说明                       |
| --------- | ------------------------ |
| 三传感器紧耦合   | LiDAR、IMU、Camera共同更新状态   |
| 双直接法      | LiDAR不提几何特征，相机不提ORB等视觉特征 |
| 顺序滤波更新    | LiDAR和视觉测量依次进入同一滤波器      |
| 统一体素地图    | 地图点同时携带几何和图像信息           |
| LiDAR平面先验 | 利用点云平面帮助图像块对齐            |
| 动态参考图像块   | 根据新观测更新地图点的视觉参考          |
| 在线曝光估计    | 减少相机曝光变化造成的光度误差          |
| 按需光线投射    | 只为当前视觉匹配需要的区域执行raycast   |

---

# 18.3 系统设计逻辑

## 18.3.1 第一性原理：FAST-LIO2 已经能定位，为什么还要相机？

LiDAR可能在某些环境退化。

例如长直走廊：

```text
左右两侧都是平行墙面
前后方向几何变化很少
```

点云可能很难约束：

```text
沿走廊方向的位移
```

相机如果能看到：

```text
门
标识
纹理
灯具
墙面图案
```

就能提供额外约束。

反过来，相机也会退化：

```text
黑暗
强光
运动模糊
纯白墙面
重复纹理
```

此时LiDAR仍能提供稳定尺度和三维结构。

因此三传感器融合是：

```text
LiDAR退化时：
    视觉补充纹理

视觉退化时：
    LiDAR补充几何

短时间快速运动：
    IMU维持连续预测
```

---

## 18.3.2 第二性原理：什么是视觉直接法？

特征法会执行：

```text
检测角点
    ↓
计算描述子
    ↓
匹配特征
    ↓
最小化重投影误差
```

直接法则使用像素亮度：

```text
地图点在参考图像中的小图像块
    ↓
投影到当前图像
    ↓
比较像素亮度差异
```

光度残差可以写成：

```text
r = I_current(u') - I_reference(u)
```

优化器调整位姿，让同一个三维点在两张图像中的局部图像块尽可能一致。

FAST-LIVO和FAST-LIVO2都采用稀疏直接视觉方法，不依赖ORB或FAST角点描述子。([arXiv][7])

---

## 18.3.3 第三性原理：为什么要统一地图？

简单做法是：

```text
LiDAR维护一张点云地图
Camera维护另一张视觉地图
最后再融合两个位姿
```

但这会产生：

```text
地图重复
数据关联复杂
几何和视觉信息分离
```

FAST-LIVO2让地图中的几何点同时关联：

```text
三维位置
局部平面
图像块
可见性
参考帧
```

于是：

```text
LiDAR模块：
    使用地图点几何结构

视觉模块：
    使用同一地图点上的图像块
```

统一地图是FAST-LIVO2区别于简单“FAST-LIO2加一个VIO”的重要设计。([arXiv][5])

---

# 18.4 FAST-LIVO2 的主要架构

```text
                IMU
                 │
                 ▼
          状态传播与去畸变
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
   LiDAR点云             Camera图像
       │                   │
       ▼                   ▼
原始点几何配准       稀疏直接光度配准
       │                   │
       └─────────┬─────────┘
                 ▼
              ESIKF
          顺序执行两类更新
                 │
                 ▼
          统一Voxel Map
├─ 三维地图点
├─ 局部平面
├─ 图像patch
├─ 可见性
└─ 动态参考patch
                 │
                 ▼
         位姿 + 彩色几何地图
```

---

# 18.5 为什么使用顺序更新？

LiDAR可能提供：

```text
数千到数万个几何残差
```

相机可能提供：

```text
大量像素光度残差
```

如果全部一次性组成一个巨大测量矩阵：

```text
内存开销大
计算复杂
不同测量维度难统一管理
```

顺序更新方式是：

```text
先用LiDAR更新一次状态
    ↓
再以更新后的状态为起点
使用视觉测量继续更新
```

它们共享同一个状态和协方差，但不必构建一个超大的联合测量矩阵。FAST-LIVO2论文将此作为处理异构传感器测量维数差异的重要设计。([arXiv][5])

---

# 18.6 FAST-LIVO2 的工程难点

相比FAST-LIO2，它额外增加了：

```text
相机内参
相机畸变
LiDAR—Camera外参
IMU—Camera外参
曝光时间
硬件时间同步
滚动快门问题
图像模糊
光度标定
```

尤其是时间同步。

如果相机时间比LiDAR慢20毫秒：

```text
无人机高速飞行时
图像和点云看到的已经不是同一姿态
```

所以LIVO系统往往比纯LIO更依赖：

```text
硬触发
统一时钟
准确外参
稳定曝光
```

FAST-LIVO2官方不仅开源算法，还提供了同步设备、传感器驱动和标定工具相关资源，这说明硬件同步本身就是系统的重要组成部分。([GitHub][6])

---

# 18.7 FAST-LIVO2 适合我们的什么阶段？

如果当前 Sunray-150 只有：

```text
MID360 + IMU
```

第一阶段没有必要直接上FAST-LIVO2。

如果后续加入：

```text
前视广角相机
鱼眼相机
双目相机
```

并且任务包括：

```text
走廊
室内弱几何环境
复杂城市纹理
彩色地图
视觉目标识别
NeRF或三维重建
```

FAST-LIVO2价值会明显提高。

---

# 18.8 我们应该吸收哪些设计？

## 吸收一：统一几何—视觉地图

```text
MapPoint
├─ position
├─ normal
├─ covariance
├─ color
├─ image_patch
└─ observations
```

---

## 吸收二：异构传感器顺序更新

适合未来接入：

```text
LiDAR
Camera
UWB
GPS
Radar
```

---

## 吸收三：传感器退化感知

系统应估计当前：

```text
LiDAR geometry quality
Visual texture quality
IMU excitation quality
```

然后动态选择更新来源。

---

## 吸收四：标定和算法必须成套设计

不能只有估计算法，没有：

```text
内参标定
外参标定
时间标定
数据质量诊断
```

---

# 18.9 我们不应该照搬什么？

## 不照搬一：不要一开始就把三传感器全接上

系统出现问题时，很难判断来自：

```text
LiDAR
Camera
IMU
同步
外参
曝光
```

应该先：

```text
FAST-LIO2稳定
    ↓
单独验证相机
    ↓
验证标定和同步
    ↓
再接FAST-LIVO2
```

---

## 不照搬二：不要认为相机一定提高定位

如果：

```text
曝光不稳定
运动模糊严重
镜头被遮挡
时间不同步
```

视觉更新反而可能把状态拉错。

---

# 18.10 在 MoSim 中的位置

```text
MID360 + IMU + Camera
          │
          ▼
Hardware Sync / Sim Clock
          │
          ▼
FastLivo2Adapter
├─ LiDAR direct update
├─ Visual direct update
├─ Sequential ESIKF
└─ Unified Voxel Map
          │
          ├─ Odometry
          ├─ Registered Cloud
          ├─ Colored Map
          └─ Degeneration Status
          │
          ▼
Planning / Perception / Rendering
```

---

# 18.11 最小研究任务

```text
1. 先跑通FAST-LIO2
2. 跑通FAST-LIVO2官方数据集
3. 理清统一体素地图
4. 理清视觉patch选择
5. 理清直接光度残差
6. 理清LiDAR和视觉顺序更新
7. 理清LiDAR平面先验
8. 理清动态参考patch
9. 理清曝光时间估计
10. 完成LiDAR—Camera外参标定
11. 完成硬件时间同步
12. 在Gazebo/UE生成同步点云和图像
13. 构造LiDAR退化走廊
14. 构造视觉弱纹理和暗光场景
15. 对比FAST-LIO2和FAST-LIVO2
16. 写 FAST-LIVO2 REVIEW.md
```

---

# 18.12 对 FAST-LIVO2 的最终判断

```text
是否进入长期项目：
    是

是否第一阶段直接使用：
    否

进入哪一层：
    高级多模态状态估计
    彩色几何地图
    弱几何环境增强定位

主要吸收：
    统一LiDAR视觉地图
    双直接法
    顺序ESIKF更新
    曝光估计
    平面先验视觉对齐

主要风险：
    标定复杂
    时间同步要求高
    ROS2需要适配
    计算量和调参复杂度高于FAST-LIO2
```

一句话：

> **FAST-LIVO2不是简单地给FAST-LIO2加一个相机，而是让LiDAR几何、视觉纹理和IMU运动在同一个地图和滤波框架中共同工作。**

---

# 19. 项目概述：LIO-SAM

## 19.1 定位

LIO-SAM是一套基于因子图平滑与建图的 LiDAR—IMU里程计系统。

它的核心特点是：

```text
IMU预积分
LiDAR里程计因子
GPS因子
闭环因子
关键帧
因子图优化
```

LIO-SAM通过IMU预积分为点云去畸变和LiDAR配准提供初值，再将LiDAR里程计结果用于估计IMU偏置；系统还可将GPS和闭环约束作为因子加入全局图中。([arXiv][8])

---

## 19.2 核心设计理念

| 设计原则   | 说明                        |
| ------ | ------------------------- |
| 因子图    | 将不同传感器约束表示成统一图结构          |
| IMU预积分 | 避免每次优化都重新积分所有IMU数据        |
| 关键帧    | 只保存有代表性的LiDAR帧            |
| 局部子地图  | 当前帧与固定数量附近关键帧匹配           |
| 双图结构   | 一个图负责地图优化，一个图负责IMU偏置和高频状态 |
| GPS可选  | 大尺度户外可加入绝对位置              |
| 闭环可选   | 回到旧地点时修正累计漂移              |

官方仓库说明其维护两个因子图：地图优化图持续融合LiDAR和GPS等因子，IMU预积分图则融合IMU和LiDAR里程计，用于估计IMU偏置和实时状态。([GitHub][9])

---

# 19.3 系统设计逻辑

## 19.3.1 什么是因子图？

状态节点：

```text
X0, X1, X2, X3...
```

分别代表不同时间的：

```text
位置
姿态
速度
IMU偏置
```

因子表示约束：

```text
IMU因子：
    X1应该根据IMU运动到X2

LiDAR因子：
    X2与地图配准结果应一致

GPS因子：
    X3应接近某个绝对坐标

闭环因子：
    X100和X10实际上位于同一地点
```

优化器寻找一组状态，使所有约束总体误差最小。

---

## 19.3.2 为什么适合长期地图？

滤波器重点回答：

```text
我现在在哪里？
```

因子图可以回头修改历史：

```text
以前估计的位置可能有偏差
现在发现闭环后
把整段历史轨迹一起调整
```

所以 LIO-SAM 更适合：

```text
长距离测绘
车辆导航
室外大范围地图
需要GPS或闭环的任务
```

---

# 19.4 LIO-SAM 的主要架构

```text
IMU
 │
 ▼
IMU预积分
 │
 ├─ 点云去畸变
 └─ LiDAR配准初值
          │
LiDAR点云 │
    │     │
    └──┬──┘
       ▼
特征提取 / Scan-to-Map
       │
       ▼
LiDAR里程计因子
       │
       ├──────── GPS因子
       ├──────── 闭环因子
       ▼
      因子图
       │
       ▼
优化后的关键帧轨迹和地图
```

---

# 19.5 LIO-SAM 与 FAST-LIO2 的区别

| 维度      | FAST-LIO2    | LIO-SAM    |
| ------- | ------------ | ---------- |
| 核心后端    | 迭代卡尔曼滤波      | 因子图平滑      |
| LiDAR处理 | 原始点直接配准      | 传统实现包含特征提取 |
| 地图结构    | ikd-Tree增量地图 | 关键帧和局部子地图  |
| 闭环      | 非核心          | 原生支持加入闭环因子 |
| GPS     | 需外部扩展        | 原生支持GPS因子  |
| 实时状态    | 延迟低、适合机载     | 结构更复杂      |
| 全局一致性   | 需要额外后端       | 更容易实现      |

---

# 19.6 我们应该吸收哪些设计？

```text
前端与后端分离：

FAST-LIO2式前端
    负责高速局部里程计

Pose Graph Backend
    负责闭环、GPS和全局一致性
```

MoSim不一定非要原样使用LIO-SAM前端，但应该吸收它的：

```text
关键帧管理
因子图接口
GPS因子
闭环因子
map→odom校正
```

---

# 19.7 最终判断

```text
是否进入长期项目：
    是

进入哪一层：
    全局SLAM后端参考
    长期地图和闭环基线

是否替代FAST-LIO2：
    不建议直接替代
    更适合成为另一套基线或全局后端

主要吸收：
    因子图
    IMU预积分
    GPS
    闭环
    关键帧
```

一句话：

> **FAST-LIO2更像高速局部定位器，LIO-SAM更像能够回头修改历史、加入GPS和闭环的全局账本。**

---

# 20. 项目概述：Point-LIO

## 20.1 定位

Point-LIO 是面向高速、强振动和高动态运动的高带宽 LiDAR—IMU里程计。

与按完整 LiDAR帧更新的系统不同，它强调：

```text
以点为粒度
持续传播和更新状态
```

官方论文与仓库将其定位为高带宽、可处理激烈运动的LIO，并报告里程计输出可达到约4至8 kHz；该数字同样属于作者实现和实验条件，而不是所有硬件上的固定指标。([GitHub][10])

---

## 20.2 为什么逐点更新？

传统方式：

```text
等待一整帧LiDAR点云
    ↓
去畸变
    ↓
配准
    ↓
更新一次位姿
```

Point-LIO：

```text
激光点不断到达
    ↓
结合临近IMU
    ↓
逐点处理和更新
```

优点是：

```text
输出延迟低
状态更新频率高
适合快速旋转和振动
```

尤其适合：

```text
高速无人机
激烈机动
高频控制反馈
机械振动环境
```

---

# 20.3 Point-LIO 与 FAST-LIO2 的关系

可以理解为：

```text
FAST-LIO2：
    以扫描帧为主要处理单位

Point-LIO：
    将处理粒度进一步缩小到单个点
```

但高频输出不代表所有下游模块都要以几千赫兹运行。

规划器可能只需要：

```text
20～100 Hz
```

控制器可能需要：

```text
100～500 Hz
```

Point-LIO的高带宽更适合：

```text
状态传播
高频控制
快速运动补偿
```

---

# 20.4 在 MoSim 中的位置

```text
MID360 + High-rate IMU
          │
          ▼
PointLioAdapter
          │
          ├─ HighRateState
          └─ MappingState
          │
          ├────────→ 控制器
          │
          └────────→ 规划器降采样状态
```

---

# 20.5 最终判断

```text
是否进入长期项目：
    是，作为高动态研究分支

是否第一阶段使用：
    否

主要用途：
    高速机动
    振动环境
    高频控制反馈
    Point-wise LIO研究

主要风险：
    系统复杂度高
    逐点时间和同步要求更严格
    下游未必需要如此高的输出频率
```

一句话：

> **Point-LIO的价值不只是“频率高”，而是将LiDAR从一帧一帧的传感器，变成持续不断到达的异步测量流。**

---

# 21. 其他相关算法

## 21.1 FAST-LIO

FAST-LIO是FAST-LIO2的前代，核心已经采用紧耦合迭代卡尔曼滤波，但更依赖特征点和传统地图查询；FAST-LIO2进一步加入原始点直接配准和ikd-Tree增量地图。([GitHub][3])

对我们来说：

```text
FAST-LIO：
    用于理解算法演化

FAST-LIO2：
    实际优先研究版本
```

---

## 21.2 FAST-LIVO

FAST-LIVO是FAST-LIVO2的前代，使用两个紧耦合的直接法子系统：

```text
直接LIO
+
稀疏直接VIO
```

地图点附加图像patch，通过光度误差完成图像对齐。FAST-LIVO2则进一步统一地图结构、顺序更新、平面先验、参考patch更新和曝光估计。([arXiv][7])

---

## 21.3 R3LIVE / R3LIVE++

R3LIVE包含：

```text
LIO子系统：
    建立三维几何结构

VIO子系统：
    为几何地图恢复颜色和辐射信息
```

它不仅关注定位，也关注：

```text
实时RGB点云
彩色三维地图
网格重建
纹理映射
```

R3LIVE建立在FAST-LIO等工作基础上，R3LIVE++进一步考虑相机光度响应、暗角和曝光时间等问题。([GitHub][11])

在MoSim里，它更适合：

```text
高质量三维建图
数字孪生
UE场景重建
彩色地图展示
```

而不是当前最低延迟飞控定位主线。

---

## 21.4 LVI-SAM

LVI-SAM结合：

```text
LIO-SAM
+
VINS-Mono
```

它更偏向：

```text
因子图
视觉惯性
LiDAR惯性
长期平滑和闭环
```

适合研究另一条不同于FAST-LIVO2滤波框架的LiDAR—视觉—惯性融合路线。([GitHub][2])

---

## 21.5 Swarm-LIO2

Swarm-LIO2面向无人机集群状态估计。

每架无人机不仅估计自身状态，还通过：

```text
机间观测
无线通信
相对状态
```

估计其他无人机相对自己的位置。

官方项目将其描述为完全去中心化、即插即用、计算和通信高效的无人机集群LIO；公开实现基于Ubuntu 20.04和ROS Noetic，并提供了Livox MID360相关启动配置。([GitHub][12])

它与EGO-Swarm的关系是：

```text
Swarm-LIO2：
    解决多架无人机彼此在哪里

EGO-Swarm：
    解决多架无人机接下来怎么避让
```

完整链路：

```text
Swarm-LIO2
    ↓
多机相对状态
    ↓
EGO-Swarm
    ↓
多机轨迹去冲突
```

---

# 22. 主要算法横向对比

| 算法         | 传感器              | 核心方法          | 地图结构        | 闭环/GPS | 主要优势            | 适合我们的位置   |
| ---------- | ---------------- | ------------- | ----------- | ------ | --------------- | --------- |
| FAST-LIO2  | LiDAR+IMU        | ESIKF、原始点直接配准 | ikd-Tree    | 非核心    | 轻量、实时、适合固态LiDAR | 第一阶段默认LIO |
| FAST-LIVO2 | LiDAR+IMU+Camera | 顺序ESIKF、双直接法  | 统一Voxel Map | 非核心    | 几何和视觉互补         | 高级多模态估计   |
| LIO-SAM    | LiDAR+IMU，可加GPS  | 因子图、IMU预积分    | 关键帧子地图      | 强      | 长期一致性、闭环        | 全局SLAM基线  |
| Point-LIO  | LiDAR+IMU        | 逐点滤波更新        | 增量点云地图      | 非核心    | 高带宽、高动态         | 高速控制研究    |
| R3LIVE++   | LiDAR+IMU+Camera | LIO+VIO、辐射重建  | 彩色/辐射地图     | 非核心    | 彩色建图和重建         | 数字孪生与展示   |
| LVI-SAM    | LiDAR+IMU+Camera | 因子图、LIO+VIO   | 关键帧地图       | 强      | 全局多传感器SLAM      | 研究对照      |
| Swarm-LIO2 | 多机LiDAR+IMU      | 分布式自身及相对估计    | 多机局部地图      | 多机约束   | 无人机集群状态估计       | 多机系统      |

---

# 23. MoSim 应该如何设计状态估计层

不能让所有算法直接发布各自不同的ROS消息，然后让规划器逐个适配。

应该定义统一接口：

```text
EstimatorInput
├─ ImuMeasurement
├─ LidarScan
├─ CameraFrame
├─ GnssMeasurement
└─ InterRobotMeasurement
```

输出：

```text
EstimatorOutput
├─ timestamp
├─ position
├─ orientation
├─ velocity
├─ angular_velocity
├─ gyro_bias
├─ accel_bias
├─ covariance
├─ tracking_status
├─ degeneration_status
└─ reset_counter
```

地图输出：

```text
MappingOutput
├─ registered_cloud
├─ local_point_map
├─ colored_point_map
├─ map_update_region
└─ map_frame
```

目录可以设计为：

```text
StateEstimation/
├─ Interfaces/
│  ├─ IStateEstimator
│  ├─ IMapProvider
│  ├─ ISensorSynchronizer
│  └─ ICalibrationProvider
│
├─ LIO/
│  ├─ FastLio2Adapter
│  ├─ PointLioAdapter
│  └─ LioSamAdapter
│
├─ LIVO/
│  ├─ FastLivo2Adapter
│  ├─ R3LiveAdapter
│  └─ LviSamAdapter
│
├─ Swarm/
│  └─ SwarmLio2Adapter
│
├─ Backend/
│  ├─ PoseGraph
│  ├─ LoopClosure
│  └─ GnssFusion
│
└─ Calibration/
   ├─ TimeCalibration
   ├─ LidarImuCalibration
   └─ LidarCameraCalibration
```

---

# 24. 坐标系必须提前统一

至少明确：

```text
map
    全局地图坐标系
    允许因闭环而修正

odom
    局部连续坐标系
    不应该突然跳变

base_link
    无人机机体坐标系，通常FLU

base_link_frd
    PX4机体坐标系，通常FRD

imu_link
    IMU坐标系

lidar_link
    MID360坐标系

camera_link
    相机坐标系
```

推荐：

```text
map → odom
    由闭环/GPS后端维护
    可能缓慢或突然修正

odom → base_link
    由FAST-LIO2等实时里程计维护
    必须连续平滑
```

规划器局部控制通常应优先使用连续的：

```text
odom
```

而全局任务和地图管理使用：

```text
map
```

否则闭环发生时，无人机当前位置可能在控制器看来突然跳动。

---

# 25. 对我们当前系统的选型结论

## 第一阶段：FAST-LIO2

```text
MID360 + IMU
    ↓
FAST-LIO2
    ↓
世界坐标点云 + 里程计
    ↓
ROG-Map
    ↓
SUPER
```

原因：

```text
传感器数量少
系统容易排错
适合固态LiDAR
与SUPER生态接近
计算量相对可控
```

---

## 第二阶段：FAST-LIVO2

当加入相机，并完成：

```text
硬件同步
相机内参
LiDAR—Camera外参
曝光控制
```

再接入FAST-LIVO2。

主要目标：

```text
LiDAR退化环境增强
彩色地图
视觉感知
三维重建
```

---

## 第三阶段：全局后端

在FAST-LIO2之上增加：

```text
Pose Graph
Loop Closure
GNSS / UWB
```

不一定必须直接更换为LIO-SAM，也可以采用：

```text
FAST-LIO2前端
    +
独立闭环和因子图后端
```

---

## 第四阶段：专项算法

```text
Point-LIO：
    高速、高振动、高频控制

Swarm-LIO2：
    多无人机相对状态估计

R3LIVE：
    彩色地图和数字孪生

LVI-SAM：
    因子图式LIVO对照实验
```

---

# 26. 最终研究顺序

```text
1. LiDAR、IMU、点时间戳和坐标系基础
2. FAST-LIO2
3. ikd-Tree
4. MID360真实数据接入
5. Gazebo模拟MID360与IMU
6. FAST-LIO2 → ROG-Map → SUPER
7. 时间同步与外参误差测试
8. LIO-SAM和闭环后端
9. Camera标定与同步
10. FAST-LIVO2
11. Point-LIO
12. R3LIVE / LVI-SAM
13. Swarm-LIO2
```

整个系统最终应该形成：

```text
传感器层
MID360 / Camera / IMU
          │
          ▼
时间同步与标定层
          │
          ▼
状态估计层
FAST-LIO2 / FAST-LIVO2 / Point-LIO
          │
          ├─ 实时odom
          ├─ 世界坐标点云
          └─ 状态协方差
          │
          ▼
全局SLAM后端
Loop Closure / GPS / Pose Graph
          │
          ▼
地图层
ROG-Map / Occupancy / ESDF
          │
          ▼
规划层
FAR / SUPER / EGO
          │
          ▼
控制层
Controller / PX4
```

最核心的结论是：

> **当前先把FAST-LIO2做成MoSim的默认实时状态估计器；FAST-LIVO2作为加入相机后的高级版本；LIO-SAM负责研究闭环和全局一致性；Point-LIO负责高动态、高带宽；Swarm-LIO2负责多机相对定位。LIO层稳定以后，再谈SUPER、EGO等规划器才真正有工程意义。**

[1]: https://arxiv.org/abs/2107.06829?utm_source=chatgpt.com "FAST-LIO2: Fast Direct LiDAR-inertial Odometry"
[2]: https://github.com/TixiaoShan/LVI-SAM?utm_source=chatgpt.com "GitHub - TixiaoShan/LVI-SAM: LVI-SAM: Tightly-coupled Lidar-Visual-Inertial Odometry via Smoothing and Mapping · GitHub"
[3]: https://github.com/hku-mars/FAST_LIO?utm_source=chatgpt.com "GitHub - hku-mars/FAST_LIO: A computationally efficient and robust LiDAR-inertial odometry (LIO) package · GitHub"
[4]: https://github.com/hku-mars/ikd-Tree?utm_source=chatgpt.com "GitHub - hku-mars/ikd-Tree: This repository provides implementation of an incremental k-d tree for robotic applications. · GitHub"
[5]: https://arxiv.org/abs/2408.14035?utm_source=chatgpt.com "FAST-LIVO2: Fast, Direct LiDAR-Inertial-Visual Odometry"
[6]: https://github.com/hku-mars/fast-livo2?utm_source=chatgpt.com "GitHub - hku-mars/FAST-LIVO2: FAST-LIVO2: Fast, Direct LiDAR-Inertial-Visual Odometry · GitHub"
[7]: https://arxiv.org/abs/2203.00893?utm_source=chatgpt.com "FAST-LIVO: Fast and Tightly-coupled Sparse-Direct LiDAR-Inertial-Visual Odometry"
[8]: https://arxiv.org/abs/2007.00258?utm_source=chatgpt.com "LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping"
[9]: https://github.com/TixiaoShan/LIO-SAM?utm_source=chatgpt.com "GitHub - TixiaoShan/LIO-SAM: LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping · GitHub"
[10]: https://github.com/hku-mars/Point-LIO?utm_source=chatgpt.com "GitHub - hku-mars/Point-LIO · GitHub"
[11]: https://github.com/hku-mars/r3live?utm_source=chatgpt.com "GitHub - hku-mars/r3live: A Robust, Real-time, RGB-colored, LiDAR-Inertial-Visual tightly-coupled state Estimation and mapping package · GitHub"
[12]: https://github.com/hku-mars/Swarm-LIO2?utm_source=chatgpt.com "GitHub - hku-mars/Swarm-LIO2: [T-RO 24] Swarm-LIO2: Decentralized, Efficient LiDAR-inertial Odometry for UAV Swarms · GitHub"
