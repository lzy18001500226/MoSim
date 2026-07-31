# MoSim 报告与手册入口

本目录的当前证据收敛文本为：

1. `仿真分析报告_正文骨架.md`：四旋翼位姿控制与仿真分析报告；
2. `用户手册_正文骨架.md`：MoSim Studio 与 MWORKS 手动工作流；
3. `公式与推导.md`：活动运行链的逐变量源码映射、参数复核和理论边界附录。

三份文本统一使用
`Docs/Design/报告手册交付证据总账_P0_20260731.md` 的数字、路径和边界。报告
正文引用原始 `Results/`、`Config/` 和 `Models/`；Studio、QGC、RViz、UE 的显示
或窗口状态不是控制闭环成功判据。

全部 48 条控制器的正文公式位于 `仿真分析报告_正文骨架.md` 的第 5、6、8 章；
公共动力学、接口与指标公式位于第 3、4、9 章；FUEL、Diff-Planner 与 FAST-LIO
的支撑模块公式和边界位于第 12 章。`公式与推导.md` 用于回查这些表达所绑定的
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

现有 `.docx` 与 `build_word_reports.py` 是历史辅助材料，尚未由本批次 Markdown
重新导出；它们不得被当作比当前 Markdown 更新的权威正文。需要导出 Word 时，
应以这三份 Markdown、证据总账和发布清单为源重新审校，不能回填旧计划数字或
无原始路径的图表。

## 证据边界

1. 48 为控制器目录冻结条目，46 为有 MWORKS 控制模块，44 为 Studio 可手动打开的
   FormalRunner 路由。执行侧另有三层口径：41 条目录↔执行对齐、38 条跑通
   （产出完整 50 s 数据集）、28 条性能达标（终端位置误差 < 5 m）。这些数字不可
   互换，也不可相加成 48；口径定义与换算见
   `Config/control_platform/climbpath_baseline_count_definition.json`，
   两套 ID 命名的桥接见 `Config/control_platform/scheme_id_alias_map.json`。
2. 七场景为 14 条总记录，其中 12 条有效、2 条无效负样本；灵敏度 24 条为
   17 通过、3 物理门限失败、4 执行阻塞。
3. px4ctrl 的图形模型到 C、构建和 MWORKS 50 s SIL 已有证据；`graphical_c99`
   已在项目本地源码的 Gazebo/PX4 链路完成名义起飞-悬停-降落、风扰注入和转子
   效率故障恢复。该运行记录仅覆盖 px4ctrl，不替代严格性能、故障容错或全控制器
   部署验证。
