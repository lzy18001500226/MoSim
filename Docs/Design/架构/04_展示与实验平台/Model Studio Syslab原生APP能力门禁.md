# Model Studio Syslab原生APP能力门禁

> 状态：D1通过，2026-07-17。
>
> 文档边界：本文是 2026-07-17 的 D1/D4 历史门禁记录。其原生窗口、
> `native_app/` 源码和 `.slappinstall` 证据不能直接替代当前
> `apps/model_studio/src/app.jl` 的现场加载复核；当前启动路径、交付状态和
> 路径覆盖规则以 `apps/model_studio/README.md` 与
> `Docs/报告/用户手册_正文骨架.md` 为准。

## 1. 结论

MWORKS.Syslab 2026a具备用户自定义原生APP能力。Model Studio冻结采用
`TyAppDesigner`路线，不采用Web页面或独立Qt应用替代。

当时门禁使用的本机证据：

- Syslab版本：`26.3.1.7499`；
- Julia版本：`1.10.10+4`；
- `TyAppDesigner 1.0.9`、`TyAppBundler 1.0.6`已安装；
- 官方文档明确APP设计工具是构建交互式APP的推荐环境；
- 官方支持窗口、下拉框、控件禁用、数值输入、按钮回调、启动回调、坐标区和曲线；
- APP可打包为`.slappinstall`并安装到Syslab“我的APP”。
- D1机器门禁：`Results/ui_platform/model_studio_d1_gate_20260717/GATE.json`；
- 原生运行与正式Orchestrator回调证据：
  `Results/ui_platform/model_studio_native_review_20260717/model_studio_after_clean_f5/`和
  `Results/ui_platform/model_studio_native_review_20260717/model_studio_prepare_run/`；
- 当时安装包：`apps/model_studio/dist/MoSim Model Studio.slappinstall`（历史产物，
  不是当前 `MoSim Studio` 发布包）。

本机还提供Python/C++ `SyslabAppSdk`和曲线拟合示例，但该路线仅保留为外部扩展参考，
不作为Model Studio主体。

## 2. 产品边界

Model Studio原生APP负责：

- 选择实验、控制器、参数集和车辆数量；
- 显示能力门禁、禁用原因和运行摘要；
- 显示少量标准曲线；
- 向Orchestrator写入受审计请求；
- 请求打开Sysplorer模型上下文和MWORKS结果查看器。

它不负责图形化模型编辑、复杂调参、ROS命令拼接、MAVROS setpoint发布或飞行控制。

## 3. 已确认能力

| 能力 | 官方接口/证据 | D1状态 |
| --- | --- | --- |
| 原生窗口 | `TyAppDesigner.uifigure` | 源码已实现 |
| 下拉框 | `uidropdown`, `Items`, `ValueChangedFcn` | 源码已实现 |
| 控件禁用 | `Enable` | 已确认 |
| 单项禁用 | 原生Dropdown未提供per-item Enable | 采用可见选项+请求拒绝+原因提示 |
| 数值参数 | `uinumericeditfield`, `Limits` | 源码已实现 |
| 曲线 | `uiaxes`, `plot`, `title`, `xlabel`, `ylabel` | 源码已实现 |
| 回调 | 组件回调和`startupFcn` | 源码已实现 |
| APP分发 | `.slappinstall` | 已打包通过 |
| Orchestrator接入 | APP回调通过固定客户端提交正式请求并读取响应 | 原生运行门禁已通过 |
| Sysplorer/结果查看器 | 通过Orchestrator请求，不在APP内直启底层命令 | D4边界已联调 |

## 4. D1最小验收

当前源码入口是 `apps/model_studio/src/app.jl`；本节的 D1 结论只约束
2026-07-17 门禁所用的原生 APP 基线，当前源码或布局变更后必须重新做一次
Syslab 加载和窗口级复核。

D1只有完成以下同一轮证据后才通过：

1. 在Syslab中启动APP；
2. 窗口、下拉框、数值输入、曲线和状态区可见；
3. 选择4至9机或未验收控制器后，所有请求按钮拒绝执行并显示原因；
4. `Prepare run`生成项目内请求文件；
5. APP可关闭且不影响现有Sysplorer会话；
6. 形成截图、日志和机器可读门禁结果；
7. 在APP设计工具中保存并打包`.slappinstall`。

上述七项已在同一D1门禁中完成。三机`px4ctrl`请求成功生成，选择5机和
`nmpc_outer`时请求均被拒绝且请求文件数量不增加；安装包已由APP设计工具生成。

2026-07-17补充原生运行复核：Syslab编辑器必须在干净Julia REPL中首次加载
`apps/model_studio/native_app/app.jl`，同一REPL重复定义`@oodef App`会触发
`invalid redefinition of const MoSimModelStudio.App`，不能归类为APP源码或授权失败。
清理旧REPL后，原生窗口正常加载Registry/Profile Catalog。点击`Prepare run`返回
`true / run_prepared`，正式Orchestrator生成
`run-20260717-071006-ec0378d8`和请求
`req-ab01df125aa94e64a54be0c43ec1388c`。回调参数在进入Julia `Cmd`前统一执行
`String.(args)`，避免下拉框值使参数向量推导为`Vector{AbstractString}`。

## 5. APP设计器兼容性结论

当前APP设计工具能保留组件回调引用，但导入`.slapp`后不会可靠地把
`customPrivateFunctions`和`customPrivateProperties`写入生成的`app.jl`。回调若依赖这些
自定义成员，会在按钮调用时静默中止。

D1采用以下兼容策略：

- 请求按钮在生成的`.slapp`回调中内联能力门禁、目录创建、JSON写入和状态更新；
- `src/app.jl`保留结构化`create_request`方法，作为可读源码和后续D3正式IPC入口；
- APP不直接启动Sysplorer、结果查看器或ROS运行时，只生成受审计请求；
- D3接入正式Orchestrator后，必须重新验证请求消费、错误回传和进程解耦。

## 6. 证据边界

D1证明Syslab原生APP技术路线可行，首版控制器/车辆数量门禁可以在界面执行，且正式
Orchestrator能够消费`prepare_run`并返回同一`run_id`。它不证明MWORKS/codegen、Gazebo、
PX4、MAVROS、RViz或UE闭环成功，也不证明4至9机可运行。
