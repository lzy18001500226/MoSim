# MoSim 发布与干净复现清单

> 版本：2026-07-31 P0 证据收敛批次。本文是交付前检查表，不替代原始结果。
> 共同数字总账见 `Docs/Design/报告手册交付证据总账_P0_20260731.md`。

## 1. 环境核对

| 组件 | 当前交付依据/最低需要 | 核对方法 |
|---|---|---|
| MWORKS、Sysplorer、Sysblock、Syslab | 活动模型注解为 `26.3.0`；目标机器需安装、授权且版本兼容 | 在 MWORKS “帮助/关于”中逐项记录版本；打开 `Models/MoSimQuadrotorModel/package.mo` 后执行 CheckModel |
| Julia / Syslab | 不使用独立 `Project.toml`；必须由 Syslab 提供 `ObjectOriented`、`TyAppDesigner` | 在 Syslab 执行 `VERSION`，再 `using ObjectOriented; using TyAppDesigner` |
| Python | 用于部分指标和辅助脚本 | `python --version` |
| Windows CMake | 当前机器检查到 `cmake version 4.3.2` | `cmake --version` |
| WSL gcc | 本批次构建验证：Ubuntu-20.04 WSL，`gcc 9.4.0` | `gcc --version` |
| WSL CMake | 本批次构建验证：`cmake version 3.16.3` | `cmake --version` |

### 1.1 Codex CLI 构建（可选，用于 AI 辅助功能）

Model Studio 第四栏的 AI 助手功能需要 Codex CLI。该功能为**可选**，跳过不影响核心仿真。

| 平台 | 构建命令 | 产物路径 |
|---|---|---|
| Windows | `cd src\Agent; .\build_codex.ps1` | `src\Agent\codex-main\codex-rs\target\release\codex.exe` |
| Linux / macOS | `cd src/Agent && ./build_codex.sh` | `src/Agent/codex-main/codex-rs/target/release/codex` |

**依赖检查：**

```bash
# 验证 Rust
cargo --version
# 预期：cargo 1.x.x 或更高
# Windows 验证 Codex
src\Agent\codex-main\codex-rs\target\release\codex.exe --version
# Linux/macOS 验证 Codex
src/Agent/codex-main/codex-rs/target/release/codex --version
```

**首次启用 GPT：** 将 `src/Agent/codex.config.example.toml` 的非密钥配置合并到
用户自己的 `CODEX_HOME/config.toml`，然后使用本节产物执行 `login` 并以 `login status`
核对。认证状态由 Codex 的用户配置保存，不写入 `MOSIM_ROOT`；
AI 助手无法使用不影响 MWORKS 核心仿真、结果复核或 px4ctrl 代码生成。

源码快照身份、许可证和树指纹见 `src/Agent/CODEX_SOURCE_MANIFEST.json`。导入快照
未携带可验证的上游 Git revision，因此发布时必须同时保留该清单和 MoSim 的发布提交。

Windows 上当前普通 PowerShell 未暴露 `gcc`、`clang` 或 `cl`，因此本批次没有宣称
Windows DLL 已构建。已安装 Visual Studio Build Tools 的机器仍应在 Developer
PowerShell/VS Native Tools 提示符中重新构建，或显式配置 LLVM/Clang。
导入的 Codex 源码将 Windows 11 + WSL2 列为其文档化系统路径；`build_codex.ps1`
是为 Studio 提供原生 `.exe` 的项目入口，只有目标机实际通过 `--version` 后才可
视为可用。首次 `cargo build --locked` 仍可能下载锁定依赖，除非 Cargo 缓存已就绪。
本机 2026-07-31 复核到 `D:\Dev\cargo\bin\cargo.exe`，但 Rustup 尚未配置默认
工具链，`cargo --version` 会提示执行 `rustup default stable`；因此当前不能把
“Cargo 已在 PATH”写成“可从零重编译”。现有
`src\Agent\codex-main\codex-rs\target\release\codex.exe --version` 能输出
`codex-cli 0.0.0`，这只证明该本机可执行文件可启动，不等同于目标机已构建、已登录
或已完成 GPT 请求。

## 2. 正式模型包根

唯一正式模型包根：

```text
Models/MoSimQuadrotorModel/package.mo
```

其余 `package.mo` 不得作为第二个项目根加载。加载多个根会改变类解析和依赖边界，
不属于本清单支持的干净复现流程。

## 3. 配置权威源

Studio 实际读取的唯一任务路由权威源为：

```text
Config/control_platform/model_studio_task_routes_v1.toml
```

`Config/control_platform/mworks_app_entrypoints.json` 是历史设计文件，仅保留追溯
价值；不用于决定当前可打开入口、任务路由或代码生成状态。此结论由
`apps/model_studio/src/app.jl` 和 `Scripts/ui/model_studio_task_config.py` 的实际
读取路径确认。

## 4. 44 条 FormalRunner 手动入口索引

下表来自权威 TOML 的 `available=true` 路由。它们的含义是“可以写配置并手动
打开”，不表示每条已经通过性能门限、七场景或代码生成。

46 条 MWORKS 实现模块的逐项 `current_model_file` 存在性清单见
`Docs/Design/控制器实现和Studio入口计数依据_P0_20260731.md`。

| 控制器 ID | Runner 全类名 | 文件相对路径 | 输出边界 |
|---|---|---|---|
| `official_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidFormalRunner.mo` | `ROTOR_COMMAND` |
| `cascade_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.CascadePidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/CascadePidFormalRunner.mo` | `ATTITUDE_THRUST` |
| `gain_scheduled_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.GainScheduledPidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/GainScheduledPidFormalRunner.mo` | `ATTITUDE_THRUST` |
| `fuzzy_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.FuzzyPidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/FuzzyPidFormalRunner.mo` | `ATTITUDE_THRUST` |
| `neural_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.NeuralPidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/NeuralPidFormalRunner.mo` | `ATTITUDE_THRUST` |
| `fopid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.FopidFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/FopidFormalRunner.mo` | `ATTITUDE_THRUST` |
| `fixed_awff_pid` | `MoSimQuadrotorModel.Experiment.Runners.Formal.AwffFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/AwffFormalRunner.mo` | `ROTOR_COMMAND` |
| `fixed_awff_l1_residual` | `MoSimQuadrotorModel.Experiment.Runners.Formal.L1FormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/L1FormalRunner.mo` | `ROTOR_COMMAND` |
| `fixed_awff_l1_indi` | `MoSimQuadrotorModel.Experiment.Runners.Formal.IndiFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/IndiFormalRunner.mo` | `ROTOR_COMMAND` |
| `lqr_baseline` | `MoSimQuadrotorModel.Experiment.Runners.Formal.LqrBaselineFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LqrBaselineFormalRunner.mo` | `ATTITUDE_THRUST` |
| `lqi_baseline` | `MoSimQuadrotorModel.Experiment.Runners.Formal.LqiFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LqiFormalRunner.mo` | `ATTITUDE_THRUST` |
| `lqg` | `MoSimQuadrotorModel.Experiment.Runners.Formal.LqgFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LqgFormalRunner.mo` | `ATTITUDE_THRUST` |
| `h2_state_feedback` | `MoSimQuadrotorModel.Experiment.Runners.Formal.H2StateFeedbackFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/H2StateFeedbackFormalRunner.mo` | `ATTITUDE_THRUST` |
| `hinf_hover_wrench` | `MoSimQuadrotorModel.Experiment.Runners.Formal.HinfHoverWrenchFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/HinfHoverWrenchFormalRunner.mo` | `WRENCH` |
| `pole_placement_luenberger` | `MoSimQuadrotorModel.Experiment.Runners.Formal.PolePlacementLuenbergerFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/PolePlacementLuenbergerFormalRunner.mo` | `ATTITUDE_THRUST` |
| `backstepping_baseline` | `MoSimQuadrotorModel.Experiment.Runners.Formal.BacksteppingBaselineFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/BacksteppingBaselineFormalRunner.mo` | `ATTITUDE_THRUST` |
| `adaptive_backstepping` | `MoSimQuadrotorModel.Experiment.Runners.Formal.AdaptiveBacksteppingFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/AdaptiveBacksteppingFormalRunner.mo` | `ATTITUDE_THRUST` |
| `feedback_linearization` | `MoSimQuadrotorModel.Experiment.Runners.Formal.FeedbackLinearizationFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/FeedbackLinearizationFormalRunner.mo` | `ATTITUDE_THRUST` |
| `mrac` | `MoSimQuadrotorModel.Experiment.Runners.Formal.MracFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/MracFormalRunner.mo` | `ATTITUDE_THRUST` |
| `ndi` | `MoSimQuadrotorModel.Experiment.Runners.Formal.NdiFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/NdiFormalRunner.mo` | `ATTITUDE_THRUST` |
| `passivity_based_control` | `MoSimQuadrotorModel.Experiment.Runners.Formal.PassivityBasedControlFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/PassivityBasedControlFormalRunner.mo` | `ATTITUDE_THRUST` |
| `integral_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.IntegralSmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/IntegralSmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `terminal_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.TerminalSmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/TerminalSmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `nonsingular_terminal_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.NonsingularTerminalSmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/NonsingularTerminalSmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `super_twisting_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.SuperTwistingSmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/SuperTwistingSmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `adaptive_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.AdaptiveSmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/AdaptiveSmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `fuzzy_smc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.FuzzySmcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/FuzzySmcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `linear_mpc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.LinearMpcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LinearMpcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `robust_mpc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.RobustMpcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/RobustMpcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `adaptive_mpc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.AdaptiveMpcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/AdaptiveMpcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `tube_mpc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.TubeMpcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/TubeMpcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `explicit_gain_scheduled_mpc` | `MoSimQuadrotorModel.Experiment.Runners.Formal.ExplicitGainScheduledMpcFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/ExplicitGainScheduledMpcFormalRunner.mo` | `ATTITUDE_THRUST` |
| `ilqr` | `MoSimQuadrotorModel.Experiment.Runners.Formal.IlqrFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/IlqrFormalRunner.mo` | `ATTITUDE_THRUST` |
| `mppi` | `MoSimQuadrotorModel.Experiment.Runners.Formal.MppiFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/MppiFormalRunner.mo` | `ATTITUDE_THRUST` |
| `fixed_linear_mpc_l1_indi` | `MoSimQuadrotorModel.Experiment.Runners.Formal.LinearMpcRotorFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/LinearMpcRotorFormalRunner.mo` | `ROTOR_COMMAND` |
| `se3_basic` | `MoSimQuadrotorModel.Experiment.Runners.Formal.Se3BasicFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/Se3BasicFormalRunner.mo` | `ATTITUDE_THRUST` |
| `dfbc_basic` | `MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcBasicFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcBasicFormalRunner.mo` | `ATTITUDE_THRUST` |
| `dfbc_high_order_attitude` | `MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcHighOrderFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcHighOrderFormalRunner.mo` | `ATTITUDE_THRUST` |
| `dfbc_high_order_bodyrate` | `MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcHighOrderBodyRateFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcHighOrderBodyRateFormalRunner.mo` | `BODY_RATE_THRUST` |
| `dfbc_smooth_robust_attitude` | `MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcSmoothRobustFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcSmoothRobustFormalRunner.mo` | `ATTITUDE_THRUST` |
| `dfbc_smooth_robust_bodyrate` | `MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcSmoothRobustBodyRateFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/DfbcSmoothRobustBodyRateFormalRunner.mo` | `BODY_RATE_THRUST` |
| `trained_neural_residual` | `MoSimQuadrotorModel.Experiment.Runners.Formal.TrainedNeuralResidualFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/TrainedNeuralResidualFormalRunner.mo` | `ATTITUDE_THRUST` |
| `rl_gain_scheduler` | `MoSimQuadrotorModel.Experiment.Runners.Formal.RlGainSchedulerFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/RlGainSchedulerFormalRunner.mo` | `ATTITUDE_THRUST` |
| `px4ctrl` | `MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner` | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/Px4CtrlFormalRunner.mo` | `ATTITUDE_THRUST` |

## 5. 关键源码与证据哈希

| 对象 | 相对路径 | SHA256 |
|---|---|---|
| 云纵150装配 | `Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo` | `fb863a0077f5d7306bfb97f85eee49ea72c7c6b9373098fb5447ceb1a385f0f6` |
| 虚拟参数 Profile | `Models/MoSimQuadrotorModel/Parameters/Sunray150VirtualPx4Classic.mo` | `158f90336df9e22a86aa16b1c837442c2bea99134f1878aeabf6a4831d05c805` |
| 旋翼/故障动力学 | `Models/MoSimQuadrotorModel/Vehicle/Dynamics/RotorActuatorCore.mo` | `149587298855446369e0fc7a77e93b2c3b0ae8615476562185abd0fba030e538` |
| 物理力矩适配 | `Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo` | `8dcd99a7115be813e3c50035085461e6c312db3546f880330d269887e4ed6222` |
| px4ctrl 图形外环 | `Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/PX4CTRL_Original_OuterLoop_Graphical_Sysblock.mo` | `86dc0be78490e87ed7bf487406b49531330ee5379d042cf0e44c8a4b718307d6` |
| px4ctrl Adapter | `Models/MoSimQuadrotorModel/Control/Adapters/Px4CtrlAttitudeThrustAdapter.mo` | `e3c97cd09041c2e53e744c74c49dec69383b462cdbe916fac3f5cb777f58e057` |
| ATTITUDE_THRUST Runner 基类 | `Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalAttitudeThrustRunnerBase.mo` | `c822c96d94a365b9f94788e85a05ea017a63ae9a6a593d372815c12cc5f99aaf` |
| ROTOR_COMMAND Runner 基类 | `Models/MoSimQuadrotorModel/Experiment/Runners/Base/FormalRotorCommandRunnerBase.mo` | `ce7a121dbf051aa84f71f7d6f2a19dec9bae59f07828c9d663e856a1b35d0ffe` |
| Studio 权威路由 | `Config/control_platform/model_studio_task_routes_v1.toml` | `ddb26b07629b479b1c73d2a93d7cd1eaec279810ee7f549847c163e34fb53478` |
| 路由接口合同 | `Config/control_platform/controller_route_interface_matrix.json` | `64fa2b6f4ea8bb95fc9c47964fc74d09e852d37494628cb47c9084f2486ed021` |
| G3 状态总账 | `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json` | `080573fdf7a5b63b76cff81d2eed787deae8604a03662df00974d3835131e130` |
| 24 条灵敏度总账 | `Results/control_platform/sensitivity_analysis_long_v1/SENSITIVITY_LONG_V1_CLOSEOUT.json` | `de106345b724aeb0d71f74e9ec2bc0f5d578c0ab485d86d7d10d708e261183a3` |
| 七场景矩阵 | `Results/control_platform/seven_scenario_ab_v2/SCENARIO_RMSE_MATRIX.pending_syslab.json` | `8accf3088bd1f77d0790f7b3c5a2dfad1e9b8a9de4d16b35ec0b2ee87bfb1d76` |
| 50 s SIL 状态 | `Results/control_platform/px4ctrl_codegen_sil_v1/logs/CLOSED_LOOP_SIL_RESULT.json` | `2e7e438d0d54f6369dc75d7a51821296895547b1579981f45fa0c13c583a0570` |
| Codex CLI Cargo 工作区 | `src/Agent/codex-main/codex-rs/Cargo.toml` | `dfc44a70b284492377e9c04084fd1a9f4ee074d608399921e4b06423ecff667f` |
| Codex CLI 锁定依赖 | `src/Agent/codex-main/codex-rs/Cargo.lock` | `76ee8398f430b10fc79041af8c106fbc296a834cfe90afba359284176cc3b669` |
| Codex Windows 构建脚本 | `src/Agent/build_codex.ps1` | `5805ac0fd744aab1e386083d76f799a0ebfd07eaf0e9f7818aad97b8f966925f` |
| Codex Unix 构建脚本 | `src/Agent/build_codex.sh` | `68b120e91ddc3566768f01425b8de7237361eadb83cacb1831ab6526847f1ba2` |
| Codex 源码清单 | `src/Agent/CODEX_SOURCE_MANIFEST.json` | 源码树 `ca332f08f756c1380e6f2ffa11ed6d21d9f1eaf38b8ad8b20d92e00ff55c0bb4` |

px4ctrl C 源、构建文件与共享库证据的完整哈希清单位于
`src/control/codegen/px4ctrl/codegen_manifest.json`。

## 6. 干净复现步骤

1. 解压/克隆仓库，并设置项目根：

   ```powershell
   $MOSIM_ROOT = (Resolve-Path '<解压目录>\MoSim').Path
   $env:MOSIM_ROOT = $MOSIM_ROOT
   ```

   Linux/WSL：

   ```bash
   export MOSIM_ROOT="/path/to/MoSim"
   ```

2. 可选启用 Studio AI 助手时，先在 `src/Agent` 运行本清单第 1.1 节对应平台的
   构建脚本，再以该产物完成 `login` 与 `login status`。凭据和 `CODEX_HOME` 必须
   位于用户目录，不能置于项目根。
3. 在授权的 MWORKS 中仅加载
   `$MOSIM_ROOT\Models\MoSimQuadrotorModel\package.mo`。
4. 在 Syslab 中启动 Studio：

   ```julia
   include(joinpath(ENV["MOSIM_ROOT"], "apps", "model_studio", "src", "app.jl"))
   ```

5. 在 Studio 根据
   `Config/control_platform/model_studio_task_routes_v1.toml` 选择有效任务和
   控制器，点击“写入配置”，再点击“打开仿真模型”。
6. 在 MWORKS 内确认 Runner、执行 CheckModel，并由用户人工开始仿真。
7. 在结果查看器读取 Result.msr，或读取该运行记录的 `metrics/METRICS.json`。
   不把 Studio 窗口、截图或打开操作写作仿真成功。
8. 需要重新导出 px4ctrl 时，在 MWORKS 中打开图形 Sysblock，使用
   GenerateModelCode；随后更新生成文件哈希并按以下命令构建。
9. Linux/WSL 构建与 C 测试：

   ```bash
   cmake -S "${MOSIM_ROOT}/src/control/codegen/px4ctrl" \
     -B "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl"
   cmake --build "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl" --parallel
   (cd "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl" && ctest --output-on-failure)
   bash "${MOSIM_ROOT}/src/control/codegen/px4ctrl/hash_check.sh"
   ```

10. Windows 使用已安装的 Visual Studio Build Tools 或 LLVM/Clang 重新执行
   `CMakeLists.txt` 的构建；不要复用 Linux `.so` 作为 Windows DLL。
11. 需要验证图形模型到 CFunction 的整机一致性时，使用相同的 ClimbPath、
    初始条件和求解器复核 50 s SIL。现有 SIL 的证明范围到此为止，不跨越到
    Gazebo/PX4 运行时。

## 7. 路径校验报告

以下报告/手册/交付物引用路径已在 2026-07-31 执行静态存在性检查，均存在：

| 路径 | 用途 | 存在性 |
|---|---|---|
| `Models/MoSimQuadrotorModel/package.mo` | 唯一正式模型包根 | 通过 |
| `Config/control_platform/model_studio_task_routes_v1.toml` | Studio 权威路由 | 通过 |
| `Config/control_platform/controller_route_interface_matrix.json` | 接口合同 | 通过 |
| `Config/control_platform/seven_scenario_experiment_profiles_v2.json` | 七场景 Profile | 通过 |
| `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json` | G2/G3 状态 | 通过 |
| `Results/control_platform/seven_scenario_ab_v2/` | 七场景记录根 | 通过 |
| `Results/control_platform/sensitivity_analysis_long_v1/SENSITIVITY_LONG_V1_CLOSEOUT.json` | 24 条灵敏度总账 | 通过 |
| `Results/control_platform/sensitivity_wind_v1/SENSITIVITY_BATCH_STATUS.json` | 8 条风扰批次 | 通过 |
| `Results/control_platform/px4ctrl_codegen_sil_v1/logs/CLOSED_LOOP_SIL_RESULT.json` | 50 s SIL | 通过 |
| `src/control/codegen/px4ctrl/` | C 生成交付目录 | 通过 |
| `src/Agent/codex-main/` | 可选 Codex CLI 源码快照（Apache-2.0） | 通过 |
| `src/Agent/CODEX_SOURCE_MANIFEST.json` | Codex 源码树指纹与安全扫描基线 | 通过 |
| `src/Agent/build_codex.ps1` | Windows 锁定构建入口 | 通过 |
| `src/Agent/build_codex.sh` | Linux/macOS 锁定构建入口 | 通过 |
| `Config/control_platform/model_studio_codex_cli_v1.toml` | Studio Codex CLI 权威配置 | 通过 |
| `Scripts/agent/codex_cli_agent_server.py` | Studio loopback Codex Bridge | 通过 |

## 8. 已知限制与必须随交付保留的状态

1. G3 有效失败共 20 条：
   - `terminal_position_error_exceeds_5m`（9）：awff、fault_compensation、
     fopid、hinf_hover_wrench、indi、l_1、linear_mpc_rotor、mrac、
     official_pid_yaw_corrected；
   - `simulation_timeout`（8）：cascade_pid、fuzzy_pid、gain_scheduled_pid、
     linear_mpc、neural_pid、rl_gain_scheduler、super_twisting_smc、
     trained_neural_residual；
   - `simulate_failed`（2）：adaptive_mpc、improved_pid；
   - `check_model_failed`（1）：pole_placement_luenberger。
2. 七场景是 14 条总记录、12 条有效、2 条无效电机效率故障负样本；不是 14 条
   全部有效记录。
3. 灵敏度 24 条中有 3 条物理门限失败与 4 条执行阻塞；`sensitivity_wind_v1`
   的 8 条通过不替代总账。
4. 固定三角队形 Figure8 仅为离线参考接入，未证明在线自主避障或可重构编队。
5. px4ctrl 已完成 MWORKS 图形模型到生成 C、共享库和 50 s CFunction SIL；
   尚未证明该生成 C 已接入 Gazebo/PX4 运行时。

## 9. Config / Results 打包与归档边界

源代码包与证据包必须分开制作：根 `.gitignore` 排除了 `Results/`，因此克隆仓库
不能替代证据交付。当前的非破坏性分类、保留路径和归档前置条件见
`Docs/Design/config_results_packaging_archive_audit_20260731.md`；机器可读清单为
`Docs/Design/config_results_packaging_archive_manifest_20260731.json`。

打包前运行：

```powershell
python Scripts/quality/validate_config_results_packaging_archive.py `
  --output Results/final_submission/config_results_packaging_archive_audit_20260731.json
```

该检查只验证路径和分类，不移动或删除任何 `Config/`、`Results/` 文件。`Results/robustness/`
及其配套旧配置是可追溯的历史归档候选，不属于当前 P0 证据包；ROS/Gazebo/PX4/QGC/UE
路径由其运行时所有者锁定，不能在 MWORKS 交付打包时擅自处理。
