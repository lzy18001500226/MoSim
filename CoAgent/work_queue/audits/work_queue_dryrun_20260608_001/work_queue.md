# MoSim P0 工作队列盘点与运维派发试运行

Request ID: `PMO-COAGENTOPS-WORK-QUEUE-DRYRUN-20260608-001`

生成时间: 2026-06-08 20:36 CST

## 本轮结论

本轮不派发新任务。

原因是 MainPMO 当前已有一个正在进行的派发 turn，并已写出并投递最新一批主线 P0 任务包。UE、ROS2、MWORKS R1 的目标线程已经能读到对应新 turn 和 agent 输出；MWORKS R2 的 025 task packet 已存在且 PMO 声称投递成功，但目标线程当前 read_thread 视图未显示 025 turn，因此需要后续验证，不应由本 dryrun 重复派发。

本轮识别的 P0 队列数: 6
可立即派发数: 0
本轮实际派发数: 0

## P0 主线队列

### 1. MWORKS R1 025 - Dynamics Batch A 静态源迁移

- 目标部门: `MWorksDynamicsControlAgent`
- 目标线程: `019e9be5-334b-76b1-93f9-8b02caebf376`
- 状态: 目标线程已出现 025 新 turn，正在执行。
- 下一步: 等待 `Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025.json` 或对应 blocker。
- 优先级理由: MWORKS R1/R2 是 P0 主线，R1 当前负责把 Dynamics 正式源面继续从 legacy alias 收敛到可审计的 Modelica 源面。
- 阻塞条件: 当前 turn 未回包前不得重复派发；如出现 approval/provider surface 或 completed-without-packet，再按控制面异常处理。
- 需要用户审核的点: 无即时用户判断；等待工程回包后由 PMO 决定是否接受或重派。

### 2. ROS2 R1 074 - Headless live evidence bundle

- 目标部门: `ROS2RuntimeAgent`
- 目标线程: `019e9c72-ee74-79d1-b9fe-621d3c6fc99e`
- 状态: 目标线程已出现 074 新 turn，正在执行。
- 下一步: 等待 `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-HEADLESS-LIVE-EVIDENCE-BUNDLE-20260608-074.json` 或对应 blocker。
- 优先级理由: ROS2 R1 是 P0 主线；074 是 073 静态 validator 后的单次 bounded headless live evidence bundle。
- 阻塞条件: live probe budget、stale process、source window、cleanup、forbidden topic 或 approval/provider surface。
- 需要用户审核的点: 若 074 需要前台 RViz 或额外 live probe，必须由 PMO/用户重新确认，不在本 dryrun 派发。

### 3. UE 032 - Runtime echo receiver capture bundle wiring

- 目标部门: `UEExperimentConsoleAgent`
- 目标线程: `019e9b24-50aa-7cd3-9e7c-4c43b224d993`
- 状态: 目标线程已出现 032 新 turn，正在执行。
- 下一步: 等待 `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-CAPTURE-BUNDLE-WIRING-20260608-032.json` 或对应 blocker。
- 优先级理由: UE gate 是 P0 主线；032 是 source-static wiring/checker，不触碰 UE runtime/editor。
- 阻塞条件: 需要 UE runtime/editor/PIE、live socket/listener/timer、或出现 Codex approval/provider surface。
- 需要用户审核的点: 若后续要进入 runtime echo acceptance，必须另立 gate；032 不能声明 live ack。

### 4. MWORKS R2 025 - Dynamics Batch A 静态审查

- 目标部门: `MWorksGraphicalModelAuditAgent`
- 目标线程: `019e9999-b0d3-7682-bccd-faef08fcf1df`
- 状态: task packet 已存在，PMO 当前 turn 声称四个主线任务均投递成功；但当前目标线程 read_thread 视图尚未显示 025 turn。
- 下一步: PMO/CoAgentOps 后续应验证同线程是否出现 025 turn、agent 输出或 expected packet；验证前不要重复投递。
- 优先级理由: MWORKS R2 是 R1 源迁移后的 P0 静态审查线，防止 R1 自改自验。
- 阻塞条件: R1 025 未回包时 R2 025 可能只能写 dependency blocker；目标线程读面未显示 025 turn时不能把投递声称当执行证据。
- 需要用户审核的点: 无即时用户判断；如 R2 025 未启动，应按 dispatch-surface validation 处理。

### 5. MWORKS R1 027 - ActuatorCommandMapper formal source surface

- 目标部门: `MWorksDynamicsControlAgent`
- 目标线程: `019e9be5-334b-76b1-93f9-8b02caebf376`
- 状态: 早前存在 dispatch-surface failure blocker；当前 R1 已能启动 025 turn，说明执行面可能已由后续 turn 证明恢复，但 027 业务任务本身没有完成。
- 下一步: 等待 025 Batch A 结果后，由 PMO 决定 027 是否仍按原范围重排、合并到后续批次，或写 supersede/替代任务。
- 优先级理由: 属于 MWORKS 源面 P0 后续，但不应与当前 R1 025 并发抢同一模型源面。
- 阻塞条件: 当前 R1 正在执行 025；027 旧 blocker 未有业务 supersede；重复派发可能造成源面冲突。
- 需要用户审核的点: PMO 需要在 025 回包后决定 027 是否仍保留为独立任务。

### 6. MWORKS live check/model/simulation/graphical gate

- 目标部门: `MWorksDynamicsControlAgent` / `MWorksGraphicalModelAuditAgent`
- 目标线程: R1 `019e9be5-334b-76b1-93f9-8b02caebf376`; R2 `019e9999-b0d3-7682-bccd-faef08fcf1df`
- 状态: blocked by live gate。
- 下一步: 等待真实 MWORKS/Sysplorer 主窗口、approved reusable no-start attach route、或 PMO/用户批准的前台/最大化视觉验收路径。
- 优先级理由: MWORKS 是正式仿真源；但 live check_model/SimulateModel/package-browser/graphical review 不能绕过窗口/attach gate。
- 阻塞条件: 当前 canonical docs 和近期 heartbeat blocker 均要求不得把 helper/proxy、后台 JSON、session_manager 新开窗口当作 live proof。
- 需要用户审核的点: 若要恢复 live MWORKS，需用户/PMO确认主窗口/许可/授权/前台验收路径。

## P1 队列

### 1. Context maintenance / new conversation context 审核

- 目标部门: `CodexContextMaintenanceAgent`
- 目标线程: `019e9be0-f6ac-7762-b80c-b1dd18b0d013`
- 状态: 维护队列，不属于 P0 主线。
- 下一步: 按已创建或待创建的定时自动化做上下文恢复包审核和人工 review。
- 优先级理由: 支撑上下文压缩和 resume，但不能压过 MWORKS/ROS2/UE P0。
- 阻塞条件: 自动化/thread 工具不可用或用户未确认大范围重构。
- 需要用户审核的点: 大范围文档重构、文件整理、历史包迁移。

### 2. Agent packet folder organization dryrun

- 目标部门: `CodexContextMaintenanceAgent`
- 目标线程: `019e9be0-f6ac-7762-b80c-b1dd18b0d013`
- 状态: 维护队列，不属于 P0 主线。
- 下一步: 作为自动化任务正文或立即执行验证项派给上下文维护部，而不是由 CoAgentOps 手工执行。
- 优先级理由: 能改善审核效率，但不得掩盖空闲/异常 P0 工程线程。
- 阻塞条件: 用户未确认实际移动计划；邮件工具不可用时只能写 blocker。
- 需要用户审核的点: 所有真实移动/删除/重命名都必须另行确认。

## P2 队列

### 1. Open-source probe / learning 支撑线

- 目标部门: `OpenSourceProbeAgent` / `OpenSourceLearningAgent`
- 目标线程: `019e9be3-94de-7dc3-b067-92a78b678287` / `019e9be4-56d0-7981-b71c-a5ded1c7ec76`
- 状态: 支撑线，不属于 P0 主线。
- 下一步: 只在 PMO 提出明确 source-first 参考问题时执行。
- 优先级理由: 可以支撑 evidence 问题，但不能替代 MWORKS/ROS2/UE 主线调度。
- 阻塞条件: 没有明确 source whitelist 或采用/改造问题。
- 需要用户审核的点: 任何 adopt/adapt 进入项目源面前都要 PMO/用户确认。
