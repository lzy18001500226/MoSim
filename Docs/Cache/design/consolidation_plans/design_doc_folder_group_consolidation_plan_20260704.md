# MoSim架构文档合并方案：文件夹套文档群

> 日期：2026-07-04
> 性质：重构方案，不代表正式文档已经移动或删除。
> 目标：减少入口歧义，让后续控制器、FAST-LIO、规划、集群、MWORKS/codegen 和展示任务可以按稳定索引推进。

## 1. 结论

建议采用“文件夹套文档群”，但必须限制层级和职责：

```text
根目录只保留入口、需求、赛题、总体架构；
架构/ 下按系统层分 00-04；
controllers/、modules/、planners/ 只作为算法/模块卡片库；
cache 只放历史方案、废弃文档和迁移记录；
任务选择必须从路线图和能力块进入，不能从最长的控制器或规划器文档进入。
```

不建议把所有内容合并成一份大文档。MoSim 不是单一控制器项目，后续还包括状态源、规划、集群、MWORKS 代码生成、真机化和展示平台；压成一份长文档会降低审核效率，也会让 Agent 更容易从局部章节误判当前任务。

也不建议继续无限拆分。算法卡片可以多，但每个一级目录必须有 README 和索引矩阵，告诉读者哪些是当前执行源，哪些只是候选或参考。

## 2. 当前问题

当前 `Docs/Design/` 已经基本形成正式文档树：

```text
Docs/Design/README.md
Docs/Design/需求.md
Docs/Design/赛题.md
Docs/Design/架构.md
Docs/Design/架构/
```

主要问题不是文档数量本身，而是：

```text
1. 根入口、专题入口、路线图之间仍有重复权威；
2. 任务推进和资料索引混在一起；
3. 控制器卡片很多，但需要更明确区分 implemented / accepted / planned；
4. 规划器卡片很多，但当前主线、第二阶段探索、参考资料的边界还要更硬；
5. 旧文档和 cache 文档仍可能被误读为 active source；
6. 后续任务清单需要和 S0-S12 能力块、G9-G12 控制器路线、FAST-LIO 状态源分支统一。
```

因此重构目标是“稳定索引和执行顺序”，不是机械减少文件数量。

## 3. 推荐目标结构

建议保留当前目录骨架，做小幅收口：

```text
Docs/Design/
  README.md                         # 唯一设计入口和读文档顺序
  需求.md                           # 需求、范围、验收口径
  赛题.md                           # 赛题与答辩口径
  架构.md                           # 总体架构、权威边界、当前主线

  架构/
    README.md                       # 专题树入口

    00_架构与任务/
      README.md
      任务路线图.md                 # 唯一任务选择入口
      系统集成接口与编排.md
      ExperimentProfile与兼容性矩阵.md
      系统架构问题与决策矩阵.md

    01_控制器平台/
      README.md
      控制体系总览.md               # 控制器族索引，不直接替代任务路线图
      统一控制接口.md
      单机控制器实现.md
      控制器管理与配置.md
      控制器证据矩阵.md
      控制增强与容错.md
      代码生成与PX4部署.md
      controllers/
      modules/

    02_感知定位与规划集群/
      README.md
      FASTLIO定位闭环.md
      规划与编队控制接口.md
      planners/

    03_测试调参与证据/
      README.md
      测试与评价.md
      调参与参数优化.md
      真机化与C++化.md

    04_展示与实验平台/
      README.md
      展示与实验平台接口.md
      Factory地图导入与全局态势视图.md
      UE渲染镜像桥接方案.md
```

当前结构已经接近这个形态，所以本轮不需要大搬家。更重要的是补强 README、压缩重复入口、建立废弃规则。

## 4. 合并与保留规则

### 4.1 根目录规则

根目录只回答四个问题：

| 文档 | 职责 |
| --- | --- |
| `README.md` | 读文档顺序、active/cache 边界、当前主线摘要 |
| `需求.md` | 需求清单、范围、优先级、验收对象 |
| `赛题.md` | 赛题原始口径、提交/答辩边界 |
| `架构.md` | 系统分层、权威边界、当前执行路线、禁止路线 |

根目录不再新增控制器、规划器、FAST-LIO、UE、调参等专题长文档。

### 4.2 一级专题规则

一级目录只按系统能力分组，不按临时任务或某篇论文分组：

| 目录 | 保留理由 |
| --- | --- |
| `00_架构与任务/` | 防止 Agent 从局部技术文档直接选任务 |
| `01_控制器平台/` | 控制器、接口、增强、管理、代码生成必须统一 |
| `02_感知定位与规划集群/` | FAST-LIO、地图、规划、多机接口强耦合 |
| `03_测试调参与证据/` | 调参、评价、证据包必须绑定 |
| `04_展示与实验平台/` | RViz/Gazebo/UE/Web/QGC 只做显示和实验入口，不拥有控制成功判定 |

一级目录不再继续增加，除非出现完全新的系统域。

### 4.3 卡片库规则

`controllers/`、`modules/`、`planners/` 保留为资料卡片库，不合并进总览长文。

每张卡片必须固定说明：

```text
状态：planned / implemented / accepted 或 BACKLOG / DESIGNED / MEASURED；
链路位置；
输入；
输出层级；
是否复用 PX4 内环；
MWORKS/codegen 路线；
Gazebo/Sunray 验收入口；
禁止声明。
```

卡片存在不代表已实现。进入 `Config/profiles/experiments/` 前，必须有实现和门禁证据；否则只能在 candidates 或文档 backlog 中存在。

## 5. 建议合并项

### 5.1 不做文件级合并，只做内容收口

以下文档暂不建议物理合并，因为它们都承担不同执行职责：

```text
任务路线图.md
系统集成接口与编排.md
ExperimentProfile与兼容性矩阵.md
统一控制接口.md
单机控制器实现.md
代码生成与PX4部署.md
FASTLIO定位闭环.md
规划与编队控制接口.md
测试与评价.md
调参与参数优化.md
```

这些文档可以内部去重，但不应合成一个巨型规范。

### 5.2 可考虑弱合并或强互链

| 文档 | 建议 |
| --- | --- |
| `控制体系总览.md` | 保留，但明确它是控制器族索引，不是任务执行入口 |
| `控制器管理与配置.md` | 保留，和 `ExperimentProfile与兼容性矩阵.md` 建强互链，避免 Profile 规则分裂 |
| `控制器证据矩阵.md` | 保留为短矩阵，避免散落在每个控制器卡片里 |
| `调参与参数优化.md` | 保留，但指标阈值必须以 `测试与评价.md` 为准 |
| `真机化与C++化.md` | 保留，但和 `代码生成与PX4部署.md` 区分：前者管工程可部署形态，后者管生成代码和 PX4/MAVROS 接入 |

### 5.3 应明确废弃或 cache-only

| 文档 | 建议 |
| --- | --- |
| `Docs/Design/架构.md` | 不是废弃文档，应保留为 Level 0 总体架构入口 |
| `Docs/Design/架构/` | 不是废弃目录，是当前正式专题树 |
| `Docs/Cache/design/superseded/MoSim体系.md` | cache-only，不再作为 active source |
| `Docs/Cache/design/superseded/架构历史草案.md` | cache-only，不再作为 active source |
| `Docs/Cache/design/old_architecture/` | 历史追溯，不作为当前执行入口 |
| `Docs/Cache/design/consolidation_plans/` | 迁移方案，不作为当前架构真相 |

如果未来删除废弃文档，只建议删除 active 目录中的重复旧文件；cache 内可保留追溯，不影响当前索引。

## 6. 后续任务清单组织

文档重构后，后续推进应形成一张“主任务表”，而不是靠散落在长文档里的 TODO。

建议主任务表放在：

```text
Docs/Design/架构/00_架构与任务/任务路线图.md
```

任务表至少按 S0-S12 能力块组织：

| 能力块 | 内容 |
| --- | --- |
| S0 | 赛题范围、需求和禁止路线 |
| S1 | Sunray/PX4/MAVROS/Gazebo/RViz 运行基线 |
| S2 | 状态源、MID360、FAST-LIO、truth、定高替身 |
| S3 | 单机控制基准 |
| S4 | 轨迹和任务参考 |
| S5 | 单机规划和局部地图 |
| S6 | 多机和集群 |
| S7 | MWORKS Golden Slice 和代码生成 |
| S8 | 控制器族扩展 |
| S9 | 鲁棒、安全、故障容错 |
| S10 | 真机化与 C++ 化 |
| S11 | UE、前端、可视化 |
| S12 | 自动评估、报告和交付 |

每个任务至少记录：

```text
ID
能力块
目标
前置门禁
输入 profile
输出产物
验收指标
证据路径
当前状态
禁止声明
目标文档
```

这样后续不会再争论“现在该先做控制器、FAST-LIO、EGO 还是 Swarm”，而是先看任务表里的前置门禁和当前主线。

## 7. 执行步骤

建议分四步执行，不一次性大改：

### Step 1：索引收口

更新以下 README 和入口表述：

```text
Docs/Design/README.md
Docs/Design/架构.md
Docs/Design/架构/README.md
Docs/Design/架构/00_架构与任务/README.md
Docs/Design/架构/01_控制器平台/README.md
Docs/Design/架构/02_感知定位与规划集群/README.md
```

目标是让 active source、cache-only、任务入口、专题入口边界更硬。

### Step 2：重复内容收口

不移动文件，先在长文档内部消除重复：

```text
根 架构.md 只保留系统权威和当前主线；
任务路线图.md 只负责任务和门禁；
控制体系总览.md 只负责控制器族索引；
测试与评价.md 负责指标权威；
调参与参数优化.md 只引用指标，不复制一套阈值体系；
FASTLIO定位闭环.md 只负责状态源和定位分支，不承担规划主线；
规划与编队控制接口.md 只负责规划/多机接口，不拥有控制发布权。
```

### Step 3：卡片状态审计

对 `controllers/`、`modules/`、`planners/` 做状态矩阵审计：

```text
planned 只能作为候选或设计；
implemented 必须有代码/配置入口；
accepted 必须有用户审核和冻结证据；
文档卡片的 DESIGNED 不等于 ExperimentProfile 可运行。
```

重点防止把 DFBC、SMC、NMPC、INDI、FUEL、RACER、EGO-Swarm 等候选能力误称为当前闭环能力。

### Step 4：引用扫描和废弃标记

运行扫描，确认正式入口没有把 cache 当 active source：

```powershell
rg -n "MoSim体系\\.md|架构历史草案|Docs/Cache/design|Docs/Design/旧架构|old_architecture" Docs/Design Docs/Workflows Docs/Index -g "*.md"
```

允许命中：

```text
明确写着 cache-only / historical / trace-back 的引用；
迁移方案文件；
废弃说明。
```

非法命中：

```text
正式 README、任务路线图、Workflow 或 Index 把旧文档作为当前执行入口。
```

## 8. 我对“是否拆太多”的判断

当前不是“拆太多”，而是“拆了以后缺少强索引”。文件夹套文档群是合适的，因为 MoSim 的系统域确实多；但必须做到：

```text
入口少；
层级浅；
README 强；
任务表唯一；
卡片库只做索引和规格；
cache 永远不能抢 active source；
每份文档只拥有一个权威职责。
```

如果后续还要继续压缩，优先压缩重复内容，而不是删除专题边界。真正应该删除或归档的是旧入口、历史草案和重复方案，不是当前控制、定位、规划、测试、展示这些系统域文档。

## 9. 推荐下一步

先按本方案做“索引收口”和“状态矩阵审计”，不要马上大规模移动或删除文件。

完成后再决定是否需要物理合并：

```text
如果两个文档长期互相复制同一套规则，再合并；
如果只是互相引用不同权威，保留分离；
如果只是历史解释，降级到 cache；
如果是候选算法，保留卡片但标 planned/backlog。
```

这样重构后的文档既方便人工审核，也能让后续 Agent 稳定按任务路线推进。
