# 灵敏度分析执行计划

## 目标
评估 px4ctrl 和 official_pid 在不同故障/扰动强度下的性能边界，为报告 §8.6 和 §10.1/10.2 提供证据。

## 实验设计

### 因子 1：电机效率故障（motor_efficiency_fault 场景）
- **基线场景**：Figure8 轨迹（50s），故障注入时刻 t=15s
- **扫描参数**：`fault_rotor_effectiveness ∈ {0.85, 0.75, 0.65, 0.55}`
  - 0.85：轻度故障（15% 效率损失）
  - 0.75：中度故障（25% 效率损失）
  - 0.65：重度故障（35% 效率损失）
  - 0.55：极端故障（45% 效率损失）
- **预期结果**：找到"可恢复边界"（px4ctrl 和 official_pid 能维持稳定的最大故障强度）

### 因子 2：风扰强度（wind_disturbance 场景）
- **基线场景**：Figure8 轨迹（50s），风扰时段 t=15-50s
- **扫描参数**：`gust_force ∈ {[0.1,0,0], [0.25,0,0], [0.5,0,0], [1.0,0,0]}` N
  - 0.1 N：微风（~5% 额外推力需求）
  - 0.25 N：中等风（~12.5%，七场景 v2 基线）
  - 0.5 N：强风（~25%）
  - 1.0 N：极端风（~50%）
- **预期结果**：验证 px4ctrl 在高风速下的抗扰性能优势

### 实验矩阵
- 总实验数：4（故障强度）+ 4（风扰强度）= **8 组**
- 每组跑 **2 个控制器**（px4ctrl + official_pid）
- 总运行次数：**16 次 MWORKS 仿真**
- 预计机时：16 × 50s × 2（求解器开销）≈ **30 分钟**

---

## 配置文件

### 文件 1：`seven_scenario_experiment_profiles_sensitivity_motor_v1.json`

```json
{
  "schema": "mosim.seven_scenario_experiment_profiles.v2",
  "profiles": [
    {
      "profile_id": "sensitivity_motor_fault_0p85_v1",
      "scenario_id": "motor_efficiency_fault",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.0, 0.0, 0.0],
        "gust_start_s": 0.0,
        "gust_duration_s": 0.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 15.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 0.85
      }
    },
    {
      "profile_id": "sensitivity_motor_fault_0p75_v1",
      "scenario_id": "motor_efficiency_fault",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.0, 0.0, 0.0],
        "gust_start_s": 0.0,
        "gust_duration_s": 0.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 15.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 0.75
      }
    },
    {
      "profile_id": "sensitivity_motor_fault_0p65_v1",
      "scenario_id": "motor_efficiency_fault",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.0, 0.0, 0.0],
        "gust_start_s": 0.0,
        "gust_duration_s": 0.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 15.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 0.65
      }
    },
    {
      "profile_id": "sensitivity_motor_fault_0p55_v1",
      "scenario_id": "motor_efficiency_fault",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.0, 0.0, 0.0],
        "gust_start_s": 0.0,
        "gust_duration_s": 0.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 15.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 0.55
      }
    }
  ]
}
```

### 文件 2：`seven_scenario_experiment_profiles_sensitivity_wind_v1.json`

```json
{
  "schema": "mosim.seven_scenario_experiment_profiles.v2",
  "profiles": [
    {
      "profile_id": "sensitivity_wind_0p1_v1",
      "scenario_id": "wind_disturbance",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.1, 0.0, 0.0],
        "gust_start_s": 15.0,
        "gust_duration_s": 35.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 1000000000.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 1.0
      }
    },
    {
      "profile_id": "sensitivity_wind_0p25_v1",
      "scenario_id": "wind_disturbance",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.25, 0.0, 0.0],
        "gust_start_s": 15.0,
        "gust_duration_s": 35.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 1000000000.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 1.0
      }
    },
    {
      "profile_id": "sensitivity_wind_0p5_v1",
      "scenario_id": "wind_disturbance",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [0.5, 0.0, 0.0],
        "gust_start_s": 15.0,
        "gust_duration_s": 35.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 1000000000.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 1.0
      }
    },
    {
      "profile_id": "sensitivity_wind_1p0_v1",
      "scenario_id": "wind_disturbance",
      "trajectory_class": "MoSimQuadrotorModel.Guidance.Trajectories.Figure8",
      "duration_s": 50.0,
      "trajectory_parameter_overrides": {
        "altitude_m": 2.0,
        "takeoff_duration_s": 5.0,
        "x_amplitude_m": 2.0,
        "y_amplitude_m": 1.0,
        "angular_rate_rad_s": 0.35
      },
      "runner_parameter_overrides": {
        "gust_force": [1.0, 0.0, 0.0],
        "gust_start_s": 15.0,
        "gust_duration_s": 35.0,
        "mass_scale": 1.0,
        "inertia_scale": [1.0, 1.0, 1.0],
        "rotor_effectiveness": [1.0, 1.0, 1.0, 1.0],
        "fault_start_s": 1000000000.0,
        "fault_rotor_index": 1,
        "fault_rotor_effectiveness": 1.0
      }
    }
  ]
}
```

---

## 执行步骤

### Step 1：创建配置文件
```bash
# 已由上面的 Write 工具生成 SENSITIVITY_ANALYSIS_PLAN.md
# 需要手动创建两个 JSON 配置文件（见上面内容）
```

### Step 2：运行实验（license 恢复后）
```bash
# 电机故障灵敏度
python Scripts/control_platform/run_seven_scenario_batch.py \
  --profile Config/control_platform/seven_scenario_experiment_profiles_sensitivity_motor_v1.json \
  --controllers px4ctrl official_pid \
  --output Results/control_platform/sensitivity_motor_v1

# 风扰灵敏度
python Scripts/control_platform/run_seven_scenario_batch.py \
  --profile Config/control_platform/seven_scenario_experiment_profiles_sensitivity_wind_v1.json \
  --controllers px4ctrl official_pid \
  --output Results/control_platform/sensitivity_wind_v1
```

### Step 3：生成分析报告
```python
# 脚本：Scripts/analysis/plot_sensitivity_curves.py
# 输出：
#   - sensitivity_motor_rmse_vs_fault.png（RMSE vs 故障强度曲线）
#   - sensitivity_wind_rmse_vs_gust.png（RMSE vs 风扰强度曲线）
#   - SENSITIVITY_ANALYSIS_REPORT.md（数值表格 + 边界分析）
```

---

## 预期结果示例

### 电机故障边界
| Controller   | 0.85 eff | 0.75 eff | 0.65 eff | 0.55 eff |
|--------------|----------|----------|----------|----------|
| px4ctrl      | 0.12m    | 0.28m    | 0.65m    | **FAIL** |
| official_pid | 0.35m    | 0.71m    | **FAIL** | **FAIL** |

**结论**：px4ctrl 的故障容忍边界在 0.65（35% 效率损失），official_pid 在 0.75（25% 效率损失）。

### 风扰鲁棒性
| Controller   | 0.1N  | 0.25N | 0.5N  | 1.0N  |
|--------------|-------|-------|-------|-------|
| px4ctrl      | 0.09m | 0.16m | 0.35m | 0.82m |
| official_pid | 0.21m | 0.34m | 0.68m | 1.45m |

**结论**：px4ctrl 在所有风扰强度下 RMSE 均低于 official_pid 约 50-60%。

---

## 报告章节映射

- **§8.6 实验设计 — 灵敏度分析**：描述上述实验矩阵和参数选择依据
- **§10.1 电机故障容忍边界**：展示故障强度曲线和边界判据
- **§10.2 风扰鲁棒性对比**：展示风扰强度曲线和控制能量分析

---

## 时间估算
- 配置文件创建：10 分钟
- 16 次仿真运行：30 分钟（后台跑）
- 数据分析 + 绘图：20 分钟
- **总计：1 小时**
