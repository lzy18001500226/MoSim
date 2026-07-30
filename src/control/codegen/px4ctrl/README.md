# px4ctrl MWORKS 生成 C 交付物

## 范围

本目录保存下列 MWORKS 图形类的 C99 导出物及其独立构建材料：

```text
MoSimQuadrotorModel.Control.Implementations.Sysblocks.
PX4CTRL_Original_OuterLoop_Graphical_Sysblock
```

它是 px4ctrl 位置/速度外环的图形化工程复现导出，不是 PX4/ROS C++ 源码副本。
生成 C 已在 MWORKS 全机 CFunction 50 s SIL 中与图形基线比较通过；该事实不等于
Gazebo/PX4 运行时已接入或已部署。

## 目录说明

| 文件 | 用途 |
|---|---|
| `PX4CTRL_Original_OuterLoop_Graphical_Sysblock.*` | MWORKS GenerateModelCode 生成的核心源码和头文件；不要手工修改 |
| `mwb_types.h`、`mwb_runtime.h`、`mwb_main.c` | MWORKS 生成的类型、运行时头和独立示例入口 |
| `px4ctrl_graphical_generated_shared.c` | 标量 C ABI 包装；在单个编译单元中包含生成核心以避免符号重复 |
| `px4ctrl_graphical_generated_shared.h` | 面向 C/C++ 调用方的 ABI 声明 |
| `CMakeLists.txt` | 静态库、共享库和最小 C 测试构建定义 |
| `test_px4ctrl_c.c` | 四步固定输入序列与参考输出断言 |
| `codegen_manifest.json` | 源类、生成时间、文件及二进制哈希 |
| `hash_check.ps1`、`hash_check.sh` | 对 manifest 中所有受管文件重新计算 SHA256 |

`mwb_main.c` 是生成器的独立示例 `main`，不加入 CMake 库目标，避免与测试
可执行文件的 `main` 冲突。当前生成核心不依赖额外 MWORKS 运行时库；若以后
GenerateModelCode 产生外部资源或运行时库依赖，应在 CMake 和 manifest 中显式
登记，不能假定现有构建仍成立。

## 从 MWORKS 重新导出

1. 仅加载正式模型包根 `Models/MoSimQuadrotorModel/package.mo`。
2. 打开上述图形 Sysblock 全类名，并先执行 CheckModel。
3. 在 MWORKS “代码生成”中选择 GenerateModelCode；活动模型注解要求 C99、
   双精度实数和 0.01 s 采样。
4. 将生成目录内的核心 `.c/.h`、`mwb_types.h`、`mwb_runtime.h`、`mwb_main.c`
   与本目录比较。保留生成器原文件，不用手写文件覆盖它们。
5. 更新 `codegen_manifest.json` 中的真实 SHA256，并重新构建、运行固定向量测试
   和 MWORKS SIL。

历史生成操作、原始模型哈希和整机 SIL 证据位于：

```text
Results/control_platform/px4ctrl_codegen_sil_v1/
```

## C ABI

`MosimPx4ctrlGeneratedGraphStepScalar` 接收 17 个标量输入，输出 8 个标量：

```c
void MosimPx4ctrlGeneratedGraphStepScalar(
    double ref_px, double px, double ref_vx, double vx, double ref_ax,
    double ref_py, double py, double ref_vy, double vy, double ref_ay,
    double ref_pz, double pz, double ref_vz, double vz, double ref_az,
    double yaw_mea, double ref_yaw,
    double *desired_acc_x, double *desired_acc_y, double *desired_acc_z,
    double *roll_cmd, double *pitch_cmd, double *yaw_cmd,
    double *collective_thrust_n, double *normalized_thrust);
```

该函数在本进程第一次调用时执行 `Init()`，之后每次调用执行一次 `Step()`。
调用方必须按 0.01 s 节拍调用，提供八个非空且可写的输出指针。固定向量测试的
状态顺序来自 `raw/runtime_schema.json`，因而每次测试必须从新的进程开始。

## 构建与测试

### Linux/WSL

```bash
cmake -S "${MOSIM_ROOT}/src/control/codegen/px4ctrl" \
  -B "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl"
cmake --build "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl" --parallel
(cd "${MOSIM_ROOT}/src/control/codegen/px4ctrl/build-wsl" && ctest --output-on-failure)
bash "${MOSIM_ROOT}/src/control/codegen/px4ctrl/hash_check.sh"
```

### Windows

安装 Visual Studio Build Tools 或 LLVM/Clang 后，在已设置 `MOSIM_ROOT` 的
PowerShell 中执行：

```powershell
cmake -S "$MOSIM_ROOT\src\control\codegen\px4ctrl" `
  -B "$MOSIM_ROOT\src\control\codegen\px4ctrl\build-win"
cmake --build "$MOSIM_ROOT\src\control\codegen\px4ctrl\build-win" --config Release
Push-Location "$MOSIM_ROOT\src\control\codegen\px4ctrl\build-win"
ctest -C Release --output-on-failure
Pop-Location
& "$MOSIM_ROOT\src\control\codegen\px4ctrl\hash_check.ps1"
```

Windows 与 WSL 的静态库、共享库扩展名和 ABI 不同，必须在目标平台重新编译。
`Results/control_platform/px4ctrl_codegen_sil_v1/native/` 中的 Linux `.so` 仅
证明当时的 WSL Linux 构建成功，不能表述为任意机器可直接运行。

## SIL 复核

1. 先运行本目录的固定向量 C 测试，验证源级 C ABI 与生成逻辑没有漂移。
2. 在 MWORKS 中使用图形基线 Runner 与生成 CFunction Runner，保持相同的
   ClimbPath、初始条件、Dassl、50 s、`Tolerance=1e-4` 和 `Interval=0.01`。
3. 用 `CLOSED_LOOP_SIL_RESULT.json` 的门限比较位置、姿态和旋翼指令差异。
4. 记录图形模型、生成 C、Adapter、Runner 和共享库哈希。

当前通过记录为：位置 RMSE 差 `1.1481051588325626e-13 m`，姿态最大差
`3.2070318622956506e-12 rad`，旋翼指令最大差
`7.354117315117037e-11 rad/s`。这些数字只覆盖 MWORKS 内的图形模型到 CFunction
整机 SIL；Gazebo/PX4 运行时仍需要独立运行证据。
