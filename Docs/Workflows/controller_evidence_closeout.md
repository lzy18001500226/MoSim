# 控制器证据收尾工作流

> 状态：当前 G1-G7 的控制器证据、模型重构和实验收敛工作流，以及其后的 R1
> 旧模型根退休门。2026-07-16 的旧 G1-G7 收尾编号已在接口规范中改标为历史 H1-H7，
> 不能与本工作流的当前 goal 混用。R1 不重定义赛题实验 goal；它只在 G5-G7 的真实
> 证据完成后负责去除旧兼容根。

## 编号与任务指针（唯一解释）

- 当前任务只由 `Docs/Workflows/mainline_operations_board.md` 选择。
- 当前控制器证据 gate 只使用本文件定义的 G1-G7；它们的顺序和完成条件以本文件为准。
- `Docs/Workflows/g6_controller_experiment_execution.md` 是当前 G6 的执行合同，
  不新建另一套 G 编号，也不选择当前任务。
- `Docs/Design/架构.md` 第 9 节中的 G8-G11、G9.5 和 G9.6 是历史批次标签，
  不代表当前执行顺序，且与当前 G1-G7 没有一一对应关系。
- 2026-07-16 的旧 G1-G7 已改标为历史 H1-H7，只能用于来源追溯。

## 目标与范围

本工作流服务正式技术报告和软件说明书，不是另一份交付报告。它把“模型图存在”
拆成可审阅的内部结构证据，把“结果图存在”拆成可追溯的仿真证据，再按赛题缺口
分批补跑。

- 历史路线矩阵（仅供来源追溯）：`Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`
- 顶层方案目录：`Config/control_platform/control_scheme_catalog.json`
- 当前 G1 可机读清单：`Results/control_platform/g1_control_scheme_execution_inventory_20260722/CONTROL_SCHEME_EXECUTION_INVENTORY.json`
- D2 正式测试壳映射：`Config/control_platform/formal_closed_loop_harness_map.json`
- 当前控制层级与实验矩阵：`Docs/Design/架构/01_控制器平台/控制器证据矩阵.md`
- 报告资产审计：`Docs/报告/审计/控制器证据审计.md`
- 静态证据盘点：`Results/control_platform/controller_document_evidence_20260720/CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.md`
- 赛题与验收：`Docs/Design/赛题.md`、`Docs/Design/需求.md`

历史矩阵有 67 条分层证据路线；`65/67` 仅表示相应路线通过了各自记录的
MWORKS codegen 和 generated-C SIL 门。报告副本中的模型图和结果图属于静态资产，
不等于 65 个完整飞机模型，更不等于 65 条当前可运行图形路线。`mu_synthesis` 与
`neural_smc` 只保留为该历史矩阵中的未实现记录，不是当前活动条目。

当前工程固定为 **48 个活动条目**：**47 个 MWORKS Control Profile** 和 1 条
`px4ctrl` 工程/部署基线。47 个 Profile 的项目源、Adapter/集成链和 Runner 路由
均已登记，`pid_awff_linear_eso` 也已有 50 s FormalRunner 记录；其当前记录未通过
性能门，不能写成性能通过。目录/映射文件中遗留的 `planned/not_runnable` 是冻结元数据，
不是当前“未实现”判定。五条命名整机 Profile 已归入 PID 或最优与预测控制族，不再
作为独立控制器族。G1 清单不会把 `Results/` 中的历史模型副本提升为当前模型库入口。

## 赛题覆盖与项目扩展场景矩阵

赛题要求基础闭环、算法对比和鲁棒性分析，但不要求把每条分层路线机械乘以七个
场景。七场景是项目的统一 A/B 扩展矩阵，用于公平比较和报告收敛，不是既有完成量。

| 场景或能力 | 赛题角色 | 最少报告证据 |
|---|---|---|
| 起飞、悬停、降落 | 基础闭环 | 原始 PID 与一个优化路线的运行/指标 |
| 阶跃 | 动态响应 | 超调、调节时间、稳态误差 |
| 8 字 | 典型轨迹 | 轨迹 RMSE、最大误差、原生结果曲线 |
| 螺旋爬升 | 典型轨迹 | 高度与水平跟踪、原生结果曲线 |
| 风扰 | 鲁棒性 | 注入 profile、前后指标、稳定性观察 |
| 参数摄动 | 鲁棒性 | 摄动定义、前后指标、稳定性观察 |
| 单电机效率故障与安全恢复 | 故障容错 | 故障时间窗、FDI/分配/降落或明确 blocker |
| 三机编队 | 扩展验证 | 三机参考与实际轨迹、机间距、跟踪指标 |

七场景 `hover`、`step`、`figure8`、`spiral`、`wind`、`parameter_mismatch`、
`motor_efficiency_fault` 是当前 A/B 扩展矩阵。它用于 Official PID、已验证的
`px4ctrl` 等效核和各语义族实测胜出者的公平对比；只有控制器完成最小闭环并取得
正式测试壳后，才可扩展到该七场景。

## 当前 G1-G7 顺序

1. G1：以 48 项活动目录、67 路线历史矩阵、Registry、来源模型和证据盘点建立 fail-closed 清单。
2. G2：统一 48/65/67、七个语义控制族、七场景、命名整机 Profile、编队和 `px4ctrl` 的设计边界。
3. G3：核对工作流、索引、检查器、模型入口和证据路径，冻结重构与实验契约。
4. G4：按冻结契约非破坏重构模型库，并把每个活动条目映射到当前入口或状态。已完成：
   `Config/control_platform/current_model_entry_map.json` 保留 46 条历史项目内入口、1 条
   冻结为 planned 的兼容字段和 1 条待实现等效核的 `px4ctrl` 工程/部署基线；这两个状态
   字段不覆盖当前已经落盘的 PID-AWFF-LINEAR-ESO 源/Runner 和运行记录；41 个图形控制器核
   仅作为带来源哈希的正式包副本，不作为完整飞机通过证据。
5. G5：48 个活动条目都保留入口或状态记录。D2 的历史基线冻结为 `46 = 41 + 5`：41 条图形控制器核
   与 5 条已归族的命名整机 Profile。G5 原批次处理 46 条路线的图形处理闭环；后续
   PID-AWFF-LINEAR-ESO、SMC boundary layer 和 NMPC outer 已有补充 FormalRunner 记录，不能再按
   缺失入口处理。G5 的剩余证据仍按类别和性能门判定：打开
   实际内部控制律，修复包装器、不可读布局和模型检查问题，取得当前模型哈希的 `CheckModel`
   与 Windows 原生整窗图，并把每条写成 `graphical_ready`。图形控制器核在本阶段仍只证明内部
    图形实现，不得被改写为整机闭环；命名整机 Profile 也只完成图形/模型检查。PID-AWFF-LINEAR-ESO
    的补充记录应保留其性能失败边界，`px4ctrl` 仍只记录等效核未完成状态，不伪造 MWORKS 图。
6. G6：原始 G6 批次仅在 46 条路线全部完成 G5 图形处理闭环后，才开始任何 `simulate_model`、最小闭环或
   七场景任务。先在七个语义控制族中按当前来源的 ClimbPath RMSE 选择一条实测胜出者。胜出者
   不能借用其他 Profile 或历史结果进入七场景：必须先按 D2 的冠军测试壳晋级契约，在
   `Models/MoSimQuadrotorModel/` 下建立并验证与其核心、Adapter、正式整机植物和最小场景绑定的
   测试壳，更新映射和检查器后，才可与 Official PID 基线完成同参数、同指标的七场景 A/B。
   `px4ctrl` 仅在其 MWORKS 等效核完成行为和接口等效验证后加入同一比较；Official PID 始终是
   非胜出者的固定 A/B 参考基线。
7. G7：补齐安全、故障、固定三机编队、Syslab 指标和后续部署候选交接；不把它们夸大为联合仿真或现场部署成功。

G1-G7 只负责当前模型证据与实验收敛。其后才可进入 R1：确认正式根在真实实验中
不再依赖旧兼容包，并以可逆归档退休三个旧模型根；R1 不是“跑过静态检查即可移动目录”的许可。

## 三轮审查门

G5 前必须依次完成下列三轮审查，并把发现写回本工作流、模型结构索引或对应的
machine-readable manifest；不能以一次静态扫描替代三轮。

1. D1 文档与入口审查：确认当前口径只有 48 个活动条目、47 个 MWORKS Control Profile、
   46 条原始 G6 路线、1 条已物化但性能失败的 ESO Profile 和 1 条待实现等效核的 `px4ctrl`
   工程/部署基线；正式实现和公开入口只指向
   `Models/MoSimQuadrotorModel/`。67 路历史矩阵、旧报告和旧结果必须明确标为历史，
   不能作为当前运行或报告完成证据。
2. D2 证据链审查：每条当前 MWORKS 路线先有内部拓扑审查目标，再由
   `formal_closed_loop_harness_map.json` 明确分类。41 条图形控制器核只能记录
   `internal_graphical_probe` 和 `missing_closed_loop_harness`；5 条命名整机 Profile 已具备
   同一正式根下命名的 `canonical_closed_loop_harness`、接口/Adapter、模型哈希和最小场景。
   不得临时拼接模型来凑最小闭环，也不得把内部固定输入响应改写成整机闭环。七族实测胜出者
   在 G5 筛选后必须走“冠军测试壳晋级”：为选中的核心建立同一正式根下的 public alias、明确
   Adapter、整机 source harness、最小场景和哈希；在 `formal_closed_loop_harness_map.json` 中把
   该路线更新为可复核的正式壳，并同时更新映射构建器/检查器。已有命名整机 Profile 不能替代
   另一语义族胜出者的测试壳。
3. D3 退休预审：明确旧根引用审计范围、允许的历史例外、归档 manifest、恢复位置和
   归档后烟雾门。D3 只冻结 R1 的执行条件，不能提前移动任何旧根文件。

三轮都通过的最低含义是“可以开始逐条取得真实 MWORKS 证据”，不是 46 条路线已经
运行或通过。D1-D3 的输出分别是当前口径、G5 测试壳映射和 R1 审计计划。

## 执行细则

### 2026-07-22 报告截图重建边界

报告目录中原有的 130 张控制器导出图片和 3 份旧说明已经归档到
Docs/报告/图/归档/控制器旧导出资产_20260722/，其哈希清单是
LEGACY_CONTROLLER_EXPORT_ARCHIVE_MANIFEST.json。归档只保留历史可追溯性，不能再作为正文结构图、结果图或图审通过依据。

Docs/报告/图/控制器/ 现在只保留 46 条当前路线的空槽位。每条后续必须补一张内部结构原生整窗截图和一张最小闭环结果原生整窗截图。截图必须由 Windows MCP 的直接整窗/桌面采集获得，保持窗口原生宽高比；禁止 MWORKS 导出画布、报告副本、历史结果图或缩放变形图回写。

规范化前的 25 份 G5 packet 及其本地截图已移入 `Results/control_platform/g5_graphical_structure_review_20260722/historical_reviews_pre_normalization_20260722/`。它们的模型哈希对应规范化前副本，只保留为追溯记录，不是当前报告图片资产，也不计入当前 G5 审查进度。新的 packet 只能写入 `reviews/`，必须绑定当前冻结模型哈希、原生窗口截图和实际 MWORKS 图审。

### E0 静态审计

运行：

```powershell
python Scripts/quality/build_controller_document_evidence_inventory.py
python Scripts/quality/audit_report_controller_assets.py
```

先处理审计表中的字节级重复图、纵向长图和无原生 `Result.msr` 的路线。静态审计
只确认文件和来源，不能写入 `layout_passed` 或 `simulation_passed`。

### E1 / G5 图形结构复核

G4 映射完成后，48 个活动条目都必须有审查记录。`pid_awff_linear_eso` 已有项目源、
Adapter、FormalRunner 和负性能记录，但仍须与其它路线一样按证据类别审核；`px4ctrl`
仍是独立的工程/部署基线，不把它写成已完成 MWORKS 等效核。其余 47 条 MWORKS Profile
按控制器族分批，每批 4 至 6 条。对每条：

1. 先读取 `Config/control_platform/formal_closed_loop_harness_map.json` 中该路线的
   `formal_harness_state`，再用当前 activation/window 证据或一次有界 sentinel/probe 确认 MWORKS 可用；
   遇到登录、许可、未知 GUI 错误立即停止该批。
2. 打开实际控制律内部子模型，不打开 `ExperimentRunner`、`ControllerWrapper` 或只有
   左右端口的接口壳。
3. 读取/导出内部图，检查误差输入、控制律、关键状态、约束/饱和、输出分配和反馈
   走线是否可读。接口壳只能记录“已接入”，不得替代内部算法图。`graphical_ready`
   的最低标准是：内部控制律真实存在，原生整窗图能显示真实组件与连接，当前模型
   `CheckModel` 通过。密集图可以由当前 `.mo` 组件/连接名辅助判读，不要求一屏内每个
   标签都达到报告排版级清晰度；包字段 `layout_passed` 在 G5 表示“内部拓扑已核实”，
   不表示走线已美化。主信号从左到右、输入/输出置边界是优先布局而非美学门槛；单根线
   绕远、轻微交叉或留白不单独构成 `needs_relayout`。只有真实组件/连接不能证实、主链
   缺失/断开，或画面仍是接口壳时才判为 `needs_relayout` 或 `wrapper_only`。
4. 记录 `layout_passed`、`needs_relayout`、`wrapper_only`、`missing_graphical_counterpart`
   或 `blocked`，并保存 Windows 原生整窗截图和证据 manifest。

G5 只处理图形模型，不启动 `simulate_model`。对 41 条 `missing_closed_loop_harness` 图形核，
本阶段只保存内部图形、`CheckModel` 或首个明确模型 blocker；这不是整机、植物耦合或轨迹
跟踪闭环。对 5 条 `resolved_canonical_whole_aircraft_harness` 命名整机 Profile 同样先完成图审和
`CheckModel`，不得因其已有测试壳而抢先进入 E2。

不为排版对已通过模型做无谓重构。只有图形确为包装器、走线缺失、错误连接或不可读时
才修复；不得为了走线美观、对齐或消除无碍阅读的轻微交叉反复调整。仅做布局修复时，
必须保持组件类型、参数和连接端点不变，记录修复前后结构签名，并重新执行 `CheckModel`
与原生整窗复核；不能把“线不穿模块”写成算法或仿真性能改善。

### E2 / G6 最小真实仿真复核

只有 46 条当前路线全部完成 G5 图形处理闭环后，才从 D2 的测试壳映射读取
`canonical_closed_loop_harness`。映射必须
绑定同一正式根下的 controller core、Adapter/接口、整机测试壳和最小场景；命名整机 Profile
可以以自己的正式整机入口作为测试壳。当前冻结映射只有 5 条命名整机 Profile 满足此条件；
将来新增其他整机壳前，必须先更新并复核 D2 映射。只有映射完整的路线才逐条运行
`check_model -> 最小 MWORKS simulate -> 新鲜原生结果与完整时间序列 -> metrics`。结果绑定必须同时确认：本次独立根下的 `Result.msr` 已写入、文件时间不早于本次调用、`time` 序列非空并到达声明终点。仅有变量类型、零值 `GetVarValueAt` 或空数组都不是结果就绪证据。每条至少保存：
核心和测试壳路径/哈希、场景配置、原生结果或可定位结果、时间序列、指标、结果图和
MCP/GUI 观察。失败、发散、接口不匹配和缺测试壳均保留为失败或 blocker 证据，不重复
改写成通过。

结构图和结果图各必须来自一次对应阶段的 Windows 原生整窗采集，并在同一实验目录的
`screenshots/` 与 `logs/screenshot_manifest.json` 中记录窗口标题、原始像素尺寸、采集
时刻、关联模型哈希和阶段。MWORKS 导出画布、缩放图、报告副本或别的运行的截图不能
补足该项。

`mu_synthesis` 与 `neural_smc` 不属于当前 E2 范围；它们只作为历史 67 路线矩阵的来源
记录保留，不以静态图或邻近算法替代为当前 Profile。

### E3 / G6-G7 场景证据补跑

优先顺序：

1. G5 图形门必须已闭合：46 条当前路线均为 `graphical_ready`，不再存在
   `needs_relayout`、`wrapper_only` 或 `model_check_failed`。之后才可进行 41 条图形控制器核的
   `internal_graphical_probe` 或正式冠军测试壳晋级，以及 5 条命名整机 Profile 的真实整机最小闭环；不借用邻近路线结果。
2. 从 PID 与智能 PID、线性与鲁棒状态反馈、非线性与自适应、滑模、最优与预测、几何与微分
   平坦、智能与学习七个语义控制族各选择一条合格胜出者；每条先完成冠军测试壳晋级：正式根内的
   核心、Adapter、整机 source harness、最小场景、模型哈希和 `check_model -> 最小闭环` 记录必须
   同时存在，并写回 D2 映射。只有随后通过这一门的胜出者才与 Official PID 基线完成同参数、同
   指标的七场景 A/B；`px4ctrl` 则需先完成 MWORKS 等效核验证后再加入。
3. 已归入 PID 或最优与预测族的命名整机 Profile 只按其自身的族内位置和最小闭环补测，不把内部
   L1、INDI 或安全模块拆成任意组合。
4. 安全、故障和固定三机编队进入 G7：分别记录触发/恢复链、故障时间窗和每机参考、实际轨迹、最小间距与跟踪指标。

每个单独的候选在其最小闭环失败、接口缺失、模型不稳定或许可证出现阻塞时立即止损，
切换到下一路线；不要让单个失败控制器阻塞整个报告主线。

### E4 / R1 单根模型卫生

正式 Modelica 实现只有一个根：`Models/MoSimQuadrotorModel/package.mo`。此前三个顶层
兼容 facade 不拥有独立实现，已从 `Models/` 退休，不能作为保留旧实验的理由或第二加载
入口。这个目录收敛动作不替代 G5-G7，也不声明任何控制器实验已完成。

R1 的持续门是：

1. `python Scripts/quality/consolidate_mosimquad_model_root.py --check`、
   `python Scripts/quality/build_current_model_entry_map.py --check` 和
   `python Scripts/quality/check_current_model_entry_map.py` 均通过。
2. 任何当前模型、配置、runner、测试和操作文档只引用正式根；历史结果或缓存中记录的旧
   名称只能作为当时 provenance，不能变成新的加载说明。
3. 自动恢复副本位于 `Models/` 之外的 cache，永远不作为 package、source candidate 或
   MWORKS 加载目录。
4. 每次结构调整后，用正式根做一次最小 MWORKS load/check。该检查只证明根可加载/可检查，
   不代替最小闭环、七场景 A/B 或 G7 代表实验。

## 完成条件

G7 交接前必须满足：

- 48 个活动条目均有当前入口或明确状态；47 个 MWORKS Profile 均有源/Runner 路由和对应运行或失败记录。`pid_awff_linear_eso` 的实现与 50 s 记录已存在，但性能门失败；`px4ctrl` 仍保持独立工程/部署等效性边界。`graphical_ready`、CheckModel、整机仿真和性能通过仍按各自证据字段单独判定。
- 41 条 `GraphicalMIL` 核均保留内部固定输入探针或 blocker，且未被写成整机闭环；5 条
  命名整机 Profile 均保留整机最小闭环证据或 blocker，并与 D2 映射中的正式测试壳一致。
- 七族实测胜出者与 Official PID 的核心对比均有正式根内的核心/Adapter/整机测试壳绑定、真实模型、结果、指标和同场景记录；`px4ctrl` 只有在其 MWORKS 等效核完成验证后才加入。任何胜出者都不得由其他 Profile 或历史结果代替。
- 安全、故障和编队各保留至少一条可信代表实验或明确 blocker，不以静态图替代。
- 任何缺失路线、未运行路线、超阈值或失败结果均在审计/矩阵中保留明确状态。

R1 的单根卫生完成只要求所有活动路径已切换到 `MoSimQuadrotorModel`，并在没有第二根的
状态下通过对应静态和最小 MWORKS load/check 验证。它不能以“已迁移”替代 G5-G7 的实验验证。
