# MoSim 正式文档入口

本目录最终只服务两份交付物：

1. 《四旋翼无人机位姿控制系统技术报告》
2. 《MoSim 软件说明书》

控制器审计、图表清单、公式源和生成脚本是两份交付物的支撑材料，不是第三份
报告，也不能替代任何一份正文。

## 当前写作门槛

在重写 Word 正文前，先以 `审计/控制器证据审计.md` 为准完成控制器图片复核：

- 模型图必须打开到实际内部控制律子模型，不能使用只有接口端口的包装器。
- 走线、反馈方向、关键增益/积分/观测/约束模块和输出分配必须可读；静态 PNG
  不能自动视为布局合格。
- 结果图必须绑定路线、场景和 Run ID；固定输入响应、界面截图和数值摘要不能
  单独写成闭环性能通过。
- 当前目录口径为 48 个活动条目：47 个 MWORKS Control Profile 与 `px4ctrl` 工程/部署
  基线。`pid_awff_linear_eso` 尚未实现，不得以相邻控制器、理论公式或替代截图补齐。
  `px4ctrl` 已完成可审查的 MWORKS 图形化外环和方程桥整机闭环：`ClimbPath` 50 s 的
  `Px4CtrlFormalRunner` 记录有 5001 个有限样本、位置 RMSE `0.276705 m`、终端位置误差
  `0.002734 m`，原始证据在
  `Results/control_platform/px4ctrl_graphical_completion_20260728/`。该记录仅证明 MWORKS
  方程桥闭环可运行，不能替代生成代码、SIL、Gazebo/PX4、MAVROS 或 ROS 运行时证据。

审计脚本：

```powershell
python Scripts/quality/audit_report_controller_assets.py
```

它会检查报告副本是否成对存在、字节级重复、纵向长图、模型源码/数值结果/MSR
覆盖，并生成 `审计/控制器证据审计.md`。它不启动 MWORKS，不会把“有文件”误判为
“走线合格”。

## 正式交付结构

```text
Docs/报告/
  README.md                         # 本入口
  技术报告/                         # 正式技术报告母稿、图表和证据映射
  软件说明书/                       # 正式软件说明书母稿、复现步骤
  图/                               # 报告副本；权威原始证据仍在 Results/
  审计/                             # 可复跑的报告资产审计，不对外单独提交
  公式与推导.md                     # 理论与变量说明源
```

现有 `仿真分析报告_正文骨架.md`、`用户手册_正文骨架.md`、两份临时 `.docx` 和
`build_word_reports.py` 均为初稿/辅助材料，不能直接作为最终报告。后续应以经过审计
的图表、权威 `Results/` 证据和人工复核结论重建正文；不要将历史缩略截图批量插入
文中。

## 证据来源与口径

- 控制器路线上限、源码、截图和数值证据：
  `Results/control_platform/controller_document_evidence_20260720/CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.md`
- 当前 48 项控制器目录、G1 结构验证状态和下一步门限：
  `Docs/Workflows/mainline_operations_board.md`
- 历史 67 条控制器矩阵仅用于追溯，不能补写为当前源代码下的闭环结果：
  `Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`
- 安全、故障容错、三机编队和学习增强专项证据：
  `Results/control_platform/non_frontend_evidence_index_20260718/`

正文只引用与本段结论同层的证据。MWORKS 图形图用于结构说明；结果曲线和指标用于
仿真结论；Gazebo/PX4/MAVROS/RViz 用于运行层结论；QGC、UE、Model Studio 只作为
操作或显示证据，不能替代控制闭环证据。
