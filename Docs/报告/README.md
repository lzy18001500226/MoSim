# MoSim 报告与手册入口

本目录的当前证据收敛文本为：

(1) `仿真分析报告_正文骨架.md`：四旋翼位姿控制与仿真分析报告；
(2) `用户手册_正文骨架.md`：MoSim Studio、MWORKS 手动工作流与 C99 单机运行时复现；
(3) `公式与推导.md`：活动运行链的逐变量源码映射、参数复核和理论边界复核索引；它不替代正文，也不是附录式的唯一公式载体。

三份文本统一使用
`Docs/Design/报告手册交付证据总账_P0_20260731.md` 的数字、路径和边界。报告
正文引用原始 `Results/`、`Config/` 和 `Models/`；Studio、QGC、RViz、UE 的显示
或窗口状态不是控制闭环成功判据。

全部 48 条控制器的正文公式位于 `仿真分析报告_正文骨架.md` 的第 5、6、8 章；
公共动力学、接口与指标公式位于第 3、4、9 章；FUEL、Diff-Planner 与 FAST-LIO
的支撑模块公式和边界位于第 11 章。`公式与推导.md` 用于回查这些表达所绑定的
活动 MWORKS 变量、类和文件路径。

## 归档与交付

本批次改写前的三份正文已归档到 `Docs/Cache/`：

```text
仿真分析报告_正文骨架_archived_20260731.md
公式与推导_archived_20260731.md
用户手册_正文骨架_archived_20260731.md
```

根目录的 `RELEASE_CHECKLIST.md` 提供环境核对、44 条 Studio 手动入口索引、
关键哈希、代码生成构建命令、复现步骤和已知限制。

历史 `build_word_reports.py` 与旧版 `.docx` 仍是辅助材料，不得被当作比当前
Markdown 更新的权威正文。当前国赛版 Word 由
`build_competition_report_docx.py` 从 `仿真分析报告_正文骨架.md` 与
`国赛论文模版.docx` 生成：

```powershell
python Docs/报告/build_competition_report_docx.py --export-pdf
```

默认输出为 `MoSim_仿真分析报告_国赛版.docx`。脚本保留模板的页面、页眉页脚和
标题样式，生成原生 Word 表格与 Office Math；图片按原文件嵌入且显式关闭 Word
图片压缩。图、表题注使用 Word 的 `SEQ` 域，按一级标题自动形成 `图 12-20`、
`表 12-20` 这类章节内编号。构建清单与 PDF 核查产物位于
`Results/docx_build/competition_report_20260802/`。

该国赛版 Word 可能超过 GitHub 的单文件限制；不要为了提交而压缩或降采样图件。
若需将成品发布到远端，应使用经审核的 Git LFS 或发布附件渠道，Markdown、构建
脚本和证据总账仍是可审计源。

## 证据边界

(1) 当前固定 48 条目录的名义 ClimbPath 对账为 **30 通过、18 完成失败、0 未运行**，
   权威源为
   `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`。
   冻结历史 `G3_STATUS.json` 的 28/20 是旧 G3 执行快照及现有 28 条图集的来源，
   不能改写成当前目录状态。48 为目录冻结条目，46 为有 MWORKS 控制模块，44 为
   Studio 可手动打开的 FormalRunner 路由，53 为 FormalRunner 源文件；这些分母均
   不可互换。完整口径见
   `Config/control_platform/climbpath_baseline_count_definition.json` 与
   `Docs/报告/审计/当前目录48条ClimbPath口径对齐_20260801.md`。
(2) 七场景为 14 条总记录，其中 12 条有效、2 条无效负样本；灵敏度 24 条为
   17 通过、3 物理门限失败、4 执行阻塞。
(3) px4ctrl 的图形模型到 C、构建和 MWORKS 50 s SIL 已有证据；`graphical_c99`
   已在项目本地源码的 Gazebo/PX4 链路完成名义起飞-悬停-降落、风扰注入和转子
   效率故障恢复。该运行记录仅覆盖 px4ctrl，不替代严格性能、故障容错或全控制器
   部署验证。
