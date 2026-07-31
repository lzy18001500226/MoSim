> 【已废止】本文含旧口径数字，权威版本为
> Docs/Design/报告手册交付证据总账_P0_20260731.md。
> 本文仅保留历史追溯，不得引用其数字。

# MoSim 证据总账（2026-07-31）

> **用途**：冻结当前所有可审计证据，作为报告和手册改写的唯一权威数据源
> **更新规则**：每次批次完成后更新，旧版本归档到 `Docs/Cache/`
> **引用规则**：报告中所有数字、图表、结论必须回链到本文档对应章节

---

## 1. 权威数字汇总

### 1.1 控制器实现统计

| 统计维度 | 数值 | 证据来源 | 说明 |
|---------|------|---------|------|
| **控制器目录条目** | 48 | `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json` | 包含所有设计路线，不等于全部通过性能验证 |
| **已实现MWORKS控制模块** | 46 | `Models/MoSimQuadrotorModel/Control/` 目录 | 有对应Modelica源文件的控制器 |
| **Studio可打开的Formal Runner入口** | 44 | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/` | 49个.mo文件减去package.mo |
| **G2 ClimbPath50s通过（17/48）** | 17 | G3_STATUS.json `g2_baseline_passed_count` | 同条件最小闭环筛查，终端误差<5m |
| **G3有效通过（28/48）** | 28 | G3_STATUS.json `effective_passed_count` | 包含G2通过+G3修复后通过 |
| **G3有效失败（20/48）** | 20 | G3_STATUS.json `effective_failed_count` | 性能失败、API失败、超时、CheckModel失败 |

**关键术语定义**：
- **目录条目（48）**：控制器设计清单，包含所有候选路线
- **已实现模块（46）**：有Modelica源码的控制器，但不保证性能通过
- **可手动打开入口（44）**：Studio可写入配置并打开的FormalRunner
- **G2通过（17）**：第一轮筛查通过基线
- **G3有效通过（28）**：包含G2冻结通过+G3修复后新增通过
- **有效失败（20）**：已尝试但未达到性能门限或执行受阻

### 1.2 七场景鲁棒性测试统计

| 统计维度 | 数值 | 证据来源 | 说明 |
|---------|------|---------|------|
| **七场景批次** | v2 | `Results/control_platform/seven_scenario_ab_v2/` | 当前权威批次 |
| **测试控制器数量** | 2 | official_pid + px4ctrl | 仅测试代表性基线和自研控制器 |
| **场景数量** | 7 | hover/step_response/figure8/spiral/wind_disturbance/parameter_mismatch/motor_efficiency_fault | 标准化场景配置 |
| **有效Result.msr数量** | 15 | `find ... -name "Result.msr" \| wc -l` | 实际生成的仿真结果文件 |
| **预期数量** | 14 (2×7) | - | 存在1个额外结果或重跑记录 |

**七场景清单**：
1. `hover` - 悬停保持
2. `step_response` - 阶跃响应
3. `figure8` - 8字轨迹
4. `spiral` - 螺旋上升
5. `wind_disturbance` - 0.25N风扰注入
6. `parameter_mismatch` - 质量/惯量+20%摄动
7. `motor_efficiency_fault` - 15s单电机效率下降

### 1.3 灵敏度分析统计

| 统计维度 | 数值 | 证据来源 | 说明 |
|---------|------|---------|------|
| **风扰灵敏度批次** | v1 | `Results/control_platform/sensitivity_wind_v1/` | 风力大小扫描 |
| **记录总数** | 24 | SENSITIVITY_BATCH_STATUS.json | 包含通过、物理失败、执行阻塞 |
| **通过数量** | 17 | - | 满足性能门限 |
| **物理门限失败** | 3 | - | 超出物理可行边界 |
| **执行阻塞** | 4 | - | MCP超时、API失败等 |

### 1.4 代码生成与SIL统计

| 统计维度 | 数值 | 证据来源 | 说明 |
|---------|------|---------|------|
| **已完成C代码生成** | px4ctrl | `src/control/codegen/px4ctrl/` | 外环位置/速度控制器 |
| **SIL一致性验证** | 已完成 | 生成C代码与Modelica模型数值对比 | 证明生成链路正确 |
| **Gazebo/PX4/MAVROS部署** | 待独立验证 | - | 需要独立运行时证据链 |

---

## 2. 失败分类详细统计

### 2.1 G3有效失败的20条路线分类

基于 `G3_STATUS.json` 中的 `failure_class` 字段：

| 失败类型 | 数量 | 典型控制器 | 原因分析 |
|---------|------|-----------|---------|
| `terminal_position_error_exceeds_5m` | 9 | awff, cascade_pid, dfbc_cascade等 | 终端位置误差>5m，未达性能门限 |
| `simulation_timeout` | 8 | cbf_qp, distributed_formation_mpc等 | MCP执行超时，可能是求解器问题 |
| `simulate_failed` | 2 | adaptive_mpc, fuzzy_gain_scheduling_pid | Sysplorer仿真API报告失败 |
| `check_model_failed` | 1 | (具体控制器名) | CheckModel阶段发现模型错误 |

**关键结论**：
- 失败不等于"设计错误"，可能是：性能参数未调优、求解器超时、执行链阻塞
- 报告中必须如实说明失败类型，不能笼统说"没跑"或"跑不通"
- 保留失败记录体现科学严谨性，符合赛题"透明复现"要求

---

## 3. 参数辨识与建模口径修正

### 3.1 ❌ 错误表述（必须避免）

- "已完成真机参数辨识"
- "基于云纵150实测数据建模"
- "通过飞行数据拟合获得惯量参数"

### 3.2 ✅ 正确表述（报告统一用语）

**建模基础**：
> "项目以云纵150实物结构和安装关系为参考，建立了可追溯的多领域虚拟机体与参数Profile。几何参数（机架尺寸、旋翼位置、MID360安装位姿）来源于实物测量与装配图纸；动力学参数（质量、惯量、推力系数、电机时间常数）采用有来源标注的工程种子参数。"

**参数来源分层**：
1. **几何参数**：实物测量 + 装配图纸（可追溯）
2. **质量参数**：整机称重 + 部件质量累加（可追溯）
3. **惯量参数**：CAD模型估算 + 工程经验值（标注来源）
4. **推力/扭矩系数**：电机厂商数据 + 文献典型值（标注来源）
5. **电机动态**：一阶惯性环节种子参数（标注来源）

**后续改进边界**：
> "当前参数Profile为初始工程配置，后续可通过动力台测试、悬停数据拟合或系统辨识方法替换单项参数，而不破坏模型接口和控制器验证框架。"

---

## 4. px4ctrl定位修正

### 4.1 ❌ 错误表述（必须避免）

- "自主设计的新型控制律"
- "提出了px4ctrl控制算法"
- "创新性地实现了px4ctrl控制器"

### 4.2 ✅ 正确表述（报告统一用语）

**px4ctrl定位**：
> "px4ctrl是本团队自研的MWORKS图形化工程复现、统一接口、代码生成与SIL闭环实现。其位置/速度外环控制律参考PX4开源飞控的几何控制思路，在MWORKS中以Sysblock图形化建模，通过EquationBridge接入PX4姿态环、角速度环与控制分配，形成可审查的全机仿真闭环。"

**技术特点**（不夸大为"创新"）：
1. **统一坐标转换**：ENU/FLU ↔ NED/FRD双向转换逻辑
2. **接口标准化**：符合ATTITUDE_THRUST输出边界
3. **代码生成链路**：Modelica → C代码 → 编译.so → SIL验证
4. **工程复现目标**：为后续Gazebo/PX4/MAVROS部署建立MWORKS参考

**当前完成证据**：
- ✅ MWORKS图形模型 (`MoSimQuadrotorModel.Control.Px4ctrl`)
- ✅ ClimbPath50s整机闭环通过
- ✅ 七场景鲁棒性测试完成
- ✅ C代码生成与SIL一致性验证
- ⏳ Gazebo/PX4运行时部署（需独立证据链）

---

## 5. 报告章节与证据对应关系

### 5.1 第10章：ClimbPath50s基线性能分析

**数据源**：
- `Results/control_platform/phase2_full_48_climbpath/`
- G2: 17条通过，31条失败
- G3: 28条有效通过，20条有效失败

**必须生成的图表**：
- **图10-1a/b/c/d**：代表性控制器的轨迹xy、高度z、位置误差、控制输入（4×4=16个子图）
  - 数据来源：28条通过控制器的CSV文件
  - 对比基准：Official PID
- **图10-2a**：28条控制器RMSE柱状图
  - 横轴：控制器ID（按族分组）
  - 纵轴：位置RMSE (m)
  - 门限线：5m终端误差
- **图10-2b**：多控制器轨迹xy叠加图
  - 选取：Official PID + px4ctrl + 性能最好的6条
- **图10-5a**：48×7状态矩阵（通过/失败/未跑）
- **图10-5b**：28条通过控制器的性能热力图
- **图10-5c**：代表性控制器雷达图（6维指标）

**叙事要点**：
- 48个控制器目录，28个通过G3筛查
- 17个在G2基线通过，11个在G3修复后通过
- 20个未通过：9个性能失败，8个超时，2个API失败，1个CheckModel失败
- 如实保留失败记录，不掩盖问题

### 5.2 第11章：七场景鲁棒性与灵敏度分析

**数据源**：
- `Results/control_platform/seven_scenario_ab_v2/`
- Official PID: 7场景完整
- px4ctrl: 7场景完整

**必须生成的图表**：
- **图11-1**：风扰场景轨迹偏差对比（Official PID vs px4ctrl）
- **图11-2**：电机故障响应曲线（高度z vs 时间，故障注入点标注）
- **图11-3**：参数摄动场景轨迹误差
- **图11-4**：七场景RMSE雷达图对比（Official PID vs px4ctrl）
- **图11-5**：灵敏度扫描曲线（风力大小 vs 终端误差）

**叙事要点**：
- 选择Official PID和px4ctrl作为代表性控制器
- 不是因为只有2个能跑，而是"深度分析优先于广度覆盖"
- 七场景数据用于验证鲁棒性，不等于其他26个控制器无鲁棒性

### 5.3 第15章：AI Agent工具链

**数据源**：
- Agent实现完成后的Demo视频截图
- MCP工具调用日志
- 测试用例通过率

**必须生成的图表**：
- **图15-1**：Model Studio集成Agent界面截图（4栏布局）
- **图15-2**：Agent引导式对话流程示例
- **图15-3**：30个MCP工具分类图
- **表15-1**：工作量统计表（100+能力点分解）

**工作量展示**：
| 类别 | 数量 | 说明 |
|------|------|------|
| MWORKS文档索引 | 19篇，150+章节 | ~1.2M tokens |
| MCP工具 | 30个 | 8仿真+6可视化+5文档+5配置+4工作流+2系统 |
| Skills封装 | 8个 | 32个子函数 |
| Workflows知识库 | 50个 | 覆盖常见分析任务 |
| 测试用例 | 50个 | Claude生成，>90%通过率要求 |

---

## 6. 用户手册关键修正点

### 6.1 启动命令修正

**❌ 错误**（当前手册2.3节）：
```powershell
julia --project=. src\app.jl
```

**✅ 正确**：
```powershell
# 方式1：从apps/model_studio目录启动
cd C:\Users\HP\Desktop\MoSim\apps\model_studio
julia --project=. src\app.jl

# 方式2：从项目根目录启动（如果配置支持）
julia --project=apps/model_studio apps/model_studio/src/app.jl
```

**说明**：Studio依赖MWORKS Syslab/TyAppDesigner，不是普通Julia项目

### 6.2 配置文件权威来源修正

**问题**：手册混用两个配置来源
- `Config/control_platform/mworks_app_entrypoints.json`（旧）
- `Config/control_platform/model_studio_task_routes_v1.toml`（新）

**修正**：
- 删除所有对`mworks_app_entrypoints.json`的引用
- 统一使用`model_studio_task_routes_v1.toml`作为权威配置
- 如果两者都存在，归档旧文件到`Docs/Cache/`

### 6.3 可打开模型数量修正

**❌ 错误**（当前手册1.2节）：
> "当前只有Official PID和px4ctrl可打开"

**✅ 正确**：
> "当前提供44条FormalRunner手动仿真入口，覆盖PID族、线性/鲁棒族、非线性/自适应族、滑模族、优化/预测族、几何/微分平坦族、智能增强族和工程基线。"

### 6.4 绝对路径消除

**问题**：手册中多处使用`C:\Users\HP\Desktop\MoSim\`

**修正规则**：
1. 定义项目根变量：`$MOSIM_ROOT`
2. 所有路径改为：`$MOSIM_ROOT\Models\...`
3. 在第2章说明：
   ```powershell
   $env:MOSIM_ROOT = "C:\Users\HP\Desktop\MoSim"
   # 或Linux/WSL
   export MOSIM_ROOT="/path/to/MoSim"
   ```

---

## 7. 代码生成与构建证据补充清单

### 7.1 px4ctrl代码生成证据

**当前已有**：
- ✅ `src/control/codegen/px4ctrl/` 目录存在
- ✅ 生成的C源文件
- ✅ Linux .so构建记录

**必须补充**：
1. **独立README**
   - 文件路径：`src/control/codegen/px4ctrl/README.md`
   - 内容：生成命令、构建步骤、依赖项、测试方法
2. **CMakeLists.txt或Makefile**
   - 独立构建脚本，不依赖全局环境
3. **哈希校验文件**
   - `px4ctrl_codegen_manifest.json`
   - 包含：Modelica源码哈希、生成时间戳、C文件哈希、.so哈希
4. **最小C测试程序**
   - `test_px4ctrl_c.c`
   - 调用生成函数，验证输入输出
5. **Windows/WSL差异说明**
   - 当前.so是Linux构建，Windows需要.dll
   - 说明跨平台构建步骤

### 7.2 SIL验证证据

**必须包含**：
- 对比脚本：`Scripts/codegen/compare_mil_sil.py`
- 对比结果：`Results/codegen/px4ctrl_sil_validation.json`
- 误差容限：数值精度、时间步长、边界条件

---

## 8. 收尾任务优先级排序

### P0（阻塞提交）

1. **冻结证据总账**（本文档）
   - [x] 已创建框架
   - [ ] 补充失败控制器详细清单
   - [ ] 补充七场景CSV路径清单
   - [ ] 补充灵敏度扫描详细记录

2. **修正报告正文关键表述**
   - [ ] 摘要：改为"48项控制器目录，28项通过验证"
   - [ ] 第1.4节：改为可追溯参数Profile，删除"真机辨识"
   - [ ] 第8章：改为px4ctrl的MWORKS工程复现定位
   - [ ] 第10-11章：补充G3失败分类说明

3. **修正用户手册关键错误**
   - [ ] 2.3节：启动命令路径修正
   - [ ] 1.2节：可打开模型数量修正（44条）
   - [ ] 全文：绝对路径改为$MOSIM_ROOT变量
   - [ ] 配置来源：统一为model_studio_task_routes_v1.toml

4. **补充代码生成证据**
   - [ ] px4ctrl/README.md
   - [ ] CMakeLists.txt
   - [ ] 哈希校验manifest
   - [ ] 最小C测试

### P1（提升质量）

5. **Syslab图表生成**（等Codex完成）
   - [ ] 验证生成的图表质量
   - [ ] 插入报告对应章节
   - [ ] 补充图表说明和观察结论

6. **Agent Demo完成**（等Codex完成）
   - [ ] 测试引导式对话
   - [ ] 录制Demo视频
   - [ ] 截图插入第15章

7. **建立发布清单**
   - [ ] MWORKS版本记录
   - [ ] 依赖清单
   - [ ] 模型入口索引
   - [ ] 源码哈希表

### P2（锦上添花）

8. **干净复现检查**
   - [ ] 全新目录解压
   - [ ] 按手册步骤：加载包根 → Studio写入配置 → 打开模型 → CheckModel → 仿真
   - [ ] 记录复现日志

9. **公式到代码映射表**
   - [ ] 旋翼编号对应关系
   - [ ] 正反转与力矩符号
   - [ ] 控制分配矩阵
   - [ ] 实际Modelica类名

---

## 9. 文档维护规则

### 9.1 唯一正文源

**决定**：选择Markdown作为唯一正文源
- 报告正文：`Docs/报告/仿真分析报告_正文骨架.md`
- 用户手册：`Docs/报告/用户手册_正文骨架.md`
- Word/PDF：从Markdown最终转换生成，不单独维护

### 9.2 旧版本归档

**规则**：
- 旧Markdown → `Docs/Cache/仿真分析报告_正文骨架_20260730.md`
- 旧Word → `Docs/Cache/仿真分析报告_20260725.docx`
- 归档前标注日期和版本号

### 9.3 引用本文档规则

**报告中引用证据**：
> "系统当前包含48项控制器目录条目，其中28项通过G3 ClimbPath50s性能验证（详见《MoSim证据总账》第1.1节）。"

**不允许的表述**：
> "系统实现了26个控制器" （旧计划数字，无证据）
> "43个控制器全部跑通" （混淆目录、实现、通过三个概念）

---

## 10. 质量检查清单

### 10.1 报告自查

- [ ] 所有控制器数量引用已改为48/46/44/28/17/20
- [ ] 所有"真机辨识"改为"可追溯参数Profile"
- [ ] px4ctrl定位已改为"MWORKS工程复现"
- [ ] 所有图表占位已补充数据来源路径
- [ ] 失败控制器已分类说明，未写成"没跑"
- [ ] 公式推导已分层：正文保留运行链，理论放附录
- [ ] 旧计划语句（"后续将"、"拟"）已删除或改为完成时态

### 10.2 手册自查

- [ ] 启动命令路径正确
- [ ] 配置文件来源统一
- [ ] 绝对路径已改为变量
- [ ] 可打开模型数量正确（44）
- [ ] 不从显示界面推断控制成功
- [ ] 每个操作步骤有对应检查点

### 10.3 代码自查

- [ ] px4ctrl代码生成目录有README
- [ ] 有独立构建脚本
- [ ] 有哈希校验文件
- [ ] 有最小测试程序
- [ ] 配置文件无绝对路径

---

## 附录A：G3失败控制器详细清单

### 20条失败控制器分类

#### A.1 性能失败（9条）- terminal_position_error_exceeds_5m

终端位置误差>5m，未达性能门限：

1. `awff` - AWFF自适应前馈控制器
2. `fault_compensation` - 故障补偿控制器
3. `fopid` - 分数阶PID
4. `hinf_hover_wrench` - H∞悬停力矩控制
5. `indi` - 增量非线性动态逆
6. `l_1` - L1自适应控制
7. `linear_mpc_rotor` - 线性MPC旋翼级
8. `mrac` - 模型参考自适应
9. `official_pid_yaw_corrected` - 官方PID偏航修正版

#### A.2 执行超时（8条）- simulation_timeout

MCP执行超时，可能是求解器、优化问题或执行链阻塞：

1. `cascade_pid` - 级联PID
2. `fuzzy_pid` - 模糊PID
3. `gain_scheduled_pid` - 增益调度PID
4. `linear_mpc` - 线性MPC
5. `neural_pid` - 神经网络PID
6. `rl_gain_scheduler` - 强化学习增益调度
7. `super_twisting_smc` - Super-Twisting滑模
8. `trained_neural_residual` - 训练神经残差补偿

#### A.3 仿真API失败（2条）- simulate_failed

Sysplorer仿真API报告失败，模型执行中断：

1. `adaptive_mpc` - 自适应MPC
2. `improved_pid` - 改进PID

#### A.4 模型检查失败（1条）- check_model_failed

CheckModel阶段发现模型错误，未进入仿真：

1. `pole_placement_luenberger` - 极点配置+Luenberger观测器

### 关键说明

**失败不等于设计错误**，可能原因包括：
- 控制参数未针对Sunray150调优（如增益、权重矩阵）
- 求解器超时设置不足（如MPC、优化类控制器）
- 执行链兼容性问题（如特定API调用、边界条件）
- 性能裕度不足（如风扰、参数摄动下失稳）

**保留失败记录的价值**：
- 体现科学严谨性，符合"可复核验证"理念
- 为后续改进提供明确边界和排查方向
- 避免"只报喜不报忧"的不透明做法

---

## 附录B：七场景Result.msr路径清单

### B.1 Official PID（7场景+1重跑）

1. `hover` - `Results/.../official_pid/hover/native_result/.../Result.msr`
2. `step_response` - `Results/.../official_pid/step_response/native_result/.../Result.msr`
3. `figure8` - `Results/.../official_pid/figure8/native_result/.../Result.msr`
4. `spiral` - `Results/.../official_pid/spiral/native_result/.../Result.msr`
5. `spiral_retry` - `Results/.../official_pid/spiral/native_result_retry_01/.../Result.msr` ⚠️重跑记录
6. `wind_disturbance` - `Results/.../official_pid/wind_disturbance/native_result/.../Result.msr`
7. `parameter_mismatch` - `Results/.../official_pid/parameter_mismatch/native_result/.../Result.msr`
8. `motor_efficiency_fault` - `Results/.../official_pid/motor_efficiency_fault/native_result/Result.msr`

### B.2 px4ctrl（7场景）

1. `hover` - `Results/.../px4ctrl/hover/native_result/.../Result.msr`
2. `step_response` - `Results/.../px4ctrl/step_response/native_result/.../Result.msr`
3. `figure8` - `Results/.../px4ctrl/figure8/native_result/.../Result.msr`
4. `spiral` - `Results/.../px4ctrl/spiral/native_result/.../Result.msr`
5. `wind_disturbance` - `Results/.../px4ctrl/wind_disturbance/native_result/.../Result.msr`
6. `parameter_mismatch` - `Results/.../px4ctrl/parameter_mismatch/native_result/.../Result.msr`
7. `motor_efficiency_fault` - `Results/.../px4ctrl/motor_efficiency_fault/native_result/.../Result.msr`

### B.3 统计汇总

- **有效场景记录**：14条（2控制器×7场景）
- **重跑记录**：1条（official_pid/spiral重试）
- **Result.msr总数**：15个文件
- **CSV导出**：待验证每条是否都有`raw/result.csv`和`metrics/metrics.json`

### B.4 数据完整性检查命令

```bash
# 检查CSV是否全部导出
find Results/control_platform/seven_scenario_ab_v2 -name "result.csv" | wc -l
# 预期：14

# 检查metrics是否全部生成
find Results/control_platform/seven_scenario_ab_v2 -name "metrics.json" | wc -l
# 预期：14
```

## 附录C：Syslab图表生成状态

（待Codex任务完成后补充）

## 附录D：Agent测试用例通过率

（待Codex任务完成后补充）
