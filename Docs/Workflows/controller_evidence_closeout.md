# 控制器证据收尾工作流

> 状态：当前 G1-G7 的控制器证据、模型重构和实验收敛工作流，以及其后的 R1
> 旧模型根退休门。2026-07-16 的旧 G1-G7 收尾编号已在接口规范中改标为历史 H1-H7，
> 不能与本工作流的当前 goal 混用。R1 不重定义赛题实验 goal；它只在 G5-G7 的真实
> 证据完成后负责去除旧兼容根。

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
不等于 65 个完整飞机模型，更不等于 65 条当前可运行图形路线。`mu_synthesis`、
`neural_smc` 保持明确实现阻塞。

当前工程的完整控制方案数固定为 49：43 条名义路线、1 条 `px4ctrl` 工程基线和
5 条固定集成链。G1 清单只登记源候选和阻塞，不会把 `Results/` 中的历史模型副本
提升为当前模型库入口；G4 完成映射前，所有条目的 `mworks_run_eligible=false`。

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
`motor_efficiency_fault` 是当前 A/B 扩展矩阵。先用于“原始 PID + 选定优化路线”
的公平对比；只有某控制器被列为正文核心候选、且最小闭环通过后，才扩展到该七场景。

## 当前 G1-G7 顺序

1. G1：以 49 方案目录、67 路线矩阵、Registry、来源模型和证据盘点建立 fail-closed 清单。
2. G2：统一 49/65/67、六个名义控制族、七场景、固定集成链、编队和 `px4ctrl` 的设计边界。
3. G3：核对工作流、索引、检查器、模型入口和证据路径，冻结重构与实验契约。
4. G4：按冻结契约非破坏重构模型库，并把每个顶层方案映射到当前入口或 blocker。已完成：
   `Config/control_platform/current_model_entry_map.json` 固定 46 条项目内入口、2 条
   真正缺实现 blocker 和 `px4ctrl` runtime baseline；41 个历史图形控制器核仅作为
   带来源哈希的正式包副本，不作为完整飞机通过证据。
5. G5：49 条方案都保留入口或状态记录。D2 已冻结为 `46 = 41 + 5`：41 条名义 `GraphicalMIL` 核只能进入 `internal_graphical_probe`，并明确保留 `missing_closed_loop_harness`；5 条固定集成链才解析为 `resolved_canonical_whole_aircraft_harness`，可进入真实整机最小闭环。mu_synthesis、neural_smc 保持实现 blocker，px4ctrl 保持 ROS1/PX4 运行时基线，不伪造 MWORKS 图。
6. G6：先对 46 条当前路线做最小筛选；再由 PID、经典鲁棒、滑模、优化、几何平坦、学习六个名义控制族各选择一条冠军。冠军不能直接借用五条固定集成链或历史结果进入七场景：必须先按 D2 的冠军测试壳晋级契约，在 `Models/MoSimQuadrotorModel/` 下建立并验证与其核心、Adapter、正式整机植物和最小场景绑定的测试壳，更新映射和检查器后，才可与 Official PID 基线完成同参数、同指标的七场景 A/B。PID 族冠军若就是 Official PID，可复用同一已验证基线壳而不重复计数。固定集成链只在自身最小闭环合格后保留为整机对照，不与六族冠军重复计数。
7. G7：补齐安全、故障、固定三机编队、Syslab 指标和后续部署候选交接；不把它们夸大为联合仿真或现场部署成功。

G1-G7 只负责当前模型证据与实验收敛。其后才可进入 R1：确认正式根在真实实验中
不再依赖旧兼容包，并以可逆归档退休三个旧模型根；R1 不是“跑过静态检查即可移动目录”的许可。

## 三轮审查门

G5 前必须依次完成下列三轮审查，并把发现写回本工作流、模型结构索引或对应的
machine-readable manifest；不能以一次静态扫描替代三轮。

1. D1 文档与入口审查：确认当前口径只有 49 个方案、46 条 MWORKS 候选、2 个实现
   blocker 和 1 条 `px4ctrl` runtime baseline；正式实现和公开入口只指向
   `Models/MoSimQuadrotorModel/`。67 路历史矩阵、旧报告和旧结果必须明确标为历史，
   不能作为当前运行或报告完成证据。
2. D2 证据链审查：每条当前 MWORKS 路线先有内部拓扑审查目标，再由
   `formal_closed_loop_harness_map.json` 明确分类。41 条 `GraphicalMIL` 核只能记录
   `internal_graphical_probe` 和 `missing_closed_loop_harness`；只有 5 条固定集成链具备
   同一正式根下命名的 `canonical_closed_loop_harness`、接口/Adapter、模型哈希和最小场景。
   不得临时拼接模型来凑最小闭环，也不得把内部固定输入响应改写成整机闭环。六族冠军在 G5 筛选后必须走“冠军测试壳晋级”：为选中的核心建立同一正式根下的 public alias、明确 Adapter、整机 source harness、最小场景和哈希；在 `formal_closed_loop_harness_map.json` 中把该路线更新为可复核的正式壳，并同时更新映射构建器/检查器。五条既有固定集成链不自动满足这一步，也不能替代其他名义族冠军。
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

G4 映射完成后，49 个顶层方案都必须有审查记录。`px4ctrl` 是 ROS1/PX4 工程
基线，不存在 MWORKS 图形模型时应记录为 `not_applicable_runtime_baseline`，而不是
伪造或寻找替代图。mu_synthesis、neural_smc 保持 blocked_before_live_review；其余 46 条当前 MWORKS 路线按控制器族分批，每批 4 至 6 条。对每条：

1. 先读取 `Config/control_platform/formal_closed_loop_harness_map.json` 中该路线的
   `formal_harness_state`，再用当前 activation/window 证据或一次有界 sentinel/probe 确认 MWORKS 可用；
   遇到登录、许可、未知 GUI 错误立即停止该批。
2. 打开实际控制律内部子模型，不打开 `ExperimentRunner`、`ControllerWrapper` 或只有
   左右端口的接口壳。
3. 读取/导出内部图，检查误差输入、控制律、关键状态、约束/饱和、输出分配和反馈
   走线是否可读。接口壳只能记录“已接入”，不得替代内部算法图。
4. 记录 `layout_passed`、`needs_relayout`、`wrapper_only`、`missing_graphical_counterpart`
   或 `blocked`，并保存 Windows 原生整窗截图和证据 manifest。

对 41 条 `missing_closed_loop_harness` 图形核，可在其自身固定输入合同下运行
`internal_graphical_probe`，并保存内部响应、首个 blocker 或模型检查结果；这不是整机、植物耦合
或轨迹跟踪闭环。它们不得进入 E2 的 `check_model -> 最小 MWORKS simulate -> metrics` 整机链。
对 5 条 `resolved_canonical_whole_aircraft_harness` 固定集成链，E1 图审完成后才进入 E2。

不为排版对已通过模型做无谓重构。只有图形确为包装器、走线缺失、错误连接或不可读时
才修复，并先对该路线运行最小 smoke。

### E2 / G5 最小真实仿真复核

完成 E1 后，先从 D2 的 G5 测试壳映射读取 `canonical_closed_loop_harness`。映射必须
绑定同一正式根下的 controller core、Adapter/接口、整机测试壳和最小场景；固定集成链
可以以自己的正式整机入口作为测试壳。当前冻结映射只有 5 条固定集成链满足此条件；
将来新增其他整机壳前，必须先更新并复核 D2 映射。只有映射完整的路线才逐条运行
`check_model -> 最小 MWORKS simulate -> result variables -> metrics`。每条至少保存：
核心和测试壳路径/哈希、场景配置、原生结果或可定位结果、时间序列、指标、结果图和
MCP/GUI 观察。失败、发散、接口不匹配和缺测试壳均保留为失败或 blocker 证据，不重复
改写成通过。

结构图和结果图各必须来自一次对应阶段的 Windows 原生整窗采集，并在同一实验目录的
`screenshots/` 与 `logs/screenshot_manifest.json` 中记录窗口标题、原始像素尺寸、采集
时刻、关联模型哈希和阶段。MWORKS 导出画布、缩放图、报告副本或别的运行的截图不能
补足该项。

`mu_synthesis` 和 `neural_smc` 先走 E2 的“实现前置条件”分支：确认动态综合或训练集、
冻结权重、定长推理、回退测试是否真实存在。缺任一项时记录 blocker，不以静态图或
邻近算法替代。

### E3 / G6-G7 场景证据补跑

优先顺序：

1. 46 条当前路线先按 G5 的分层门完成筛选：41 条名义图形控制器核各自保留
   `internal_graphical_probe` 证据或首个 blocker，5 条固定集成链各自保留真实整机最小闭环证据或首个 blocker；不借用邻近路线结果。
2. 从 PID、经典鲁棒、滑模、优化、几何平坦、学习六个名义控制族各选择一条合格冠军；每条先完成冠军测试壳晋级：正式根内的核心、Adapter、整机 source harness、最小场景、模型哈希和 `check_model -> 最小闭环` 记录必须同时存在，并写回 D2 映射。只有随后通过这一门的冠军才与 Official PID 基线完成同参数、同指标的七场景 A/B。Official PID 基线也必须有同版本的正式根测试壳；只有它同时是 PID 族冠军时才可复用该壳而不重复计数。
3. 固定集成链只在其自身 G5 最小闭环通过后作为命名方案补测，不把内部 L1、INDI 或安全模块拆成任意组合。
4. 安全、故障和固定三机编队进入 G7：分别记录触发/恢复链、故障时间窗和每机参考、实际轨迹、最小间距与跟踪指标。

每个单独的候选在其最小闭环失败、接口缺失、模型不稳定或许可证出现阻塞时立即止损，
切换到下一路线；不要让单个失败控制器阻塞整个报告主线。

### E4 / R1 旧模型根退休与归档

R1 只能在 G5-G7 已产生终态证据后执行，不能为了整理目录跳过实验。退休对象仅为：
`Models/QuadrotorExperiments/`、`Models/QuadrotorControllerBlocks/` 和
`Models/MworksLive/`；正式实现根始终是 `Models/MoSimQuadrotorModel/`。

R1 的前置门：

1. 41 条图形核均已有 `internal_graphical_probe` 终态证据或明确 blocker，5 条固定集成链
   均已有真实整机最小闭环证据或明确 blocker；六族冠军场景和 G7 代表实验也均从正式根
   产生终态记录。
2. `python Scripts/quality/consolidate_mosimquad_model_root.py --check`、
   `python Scripts/quality/build_current_model_entry_map.py --check` 和
   `python Scripts/quality/check_current_model_entry_map.py` 均通过。
3. 对 `Models/`、`Config/`、`Scripts/`、活跃 `Docs/` 和测试执行路径做引用审计；
   旧根只能出现在历史 cache、已归档证据或明确的迁移清单中，不能仍是可执行导入、
   runner、配置或正式模型依赖。审计同时覆盖 `.mo` 的 `within`/`extends`/引用、
   `package.order`、配置模型类、Python/PowerShell runner 和测试；不能只搜索文档。
4. 使用正式根完成一次真实 MWORKS `check_model` 与最小闭环复核；静态检查、旧截图、
   旧 `Result.msr` 或迁移映射都不能替代该门。

归档操作必须先写入旧根文件清单、SHA-256、迁移映射和恢复位置，再将三个旧根整体
移入 `Docs/Cache/model_legacy/retired_model_roots_<date>/`。归档后立即在旧根缺席的
状态下重跑正式根的静态检查与最小 MWORKS 烟雾；任一活动引用或正式根加载失败即恢复，
保留 blocker，不宣称退休完成。

## 完成条件

G7 交接前必须满足：

- 49 条方案均有当前入口或明确 blocker；46 条当前 MWORKS 路线均有 layout_passed、needs_relayout、wrapper_only、missing_graphical_counterpart 或 blocked 状态；两条实现 blocker 与 px4ctrl 保持各自非运行状态。
- 41 条 `GraphicalMIL` 核均保留内部固定输入探针或 blocker，且未被写成整机闭环；5 条
  固定集成链均保留整机最小闭环证据或 blocker，并与 D2 映射中的正式测试壳一致。
- 六族冠军与 Official PID 的核心对比均有正式根内的核心/Adapter/整机测试壳绑定、真实模型、结果、指标和同场景记录；任何冠军都不得由五条既有固定集成链或历史结果代替。
- 安全、故障和编队各保留至少一条可信代表实验或明确 blocker，不以静态图替代。
- 任何缺失路线、未运行路线、超阈值或失败结果均在审计/矩阵中保留明确状态。

R1 退休完成还必须满足：旧根归档前后都有可追溯 manifest，所有活动路径已切换到
`MoSimQuadrotorModel`，正式根在旧根缺席时通过对应烟雾验证；否则旧根继续作为隐藏
兼容 facade 保留，不能以“已迁移”替代验证。
