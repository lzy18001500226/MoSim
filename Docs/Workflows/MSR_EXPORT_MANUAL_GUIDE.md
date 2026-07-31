# MSR导出CSV人工操作指南

## 背景
28个G3通过的控制器需要从MSR格式导出为CSV，供Julia脚本生成报告图表。

## 28个通过控制器清单
```
adaptive_backstepping, adaptive_smc, backstepping_baseline, dfbc_basic, 
dfbc_high_order_body_rate, dfbc_high_order, dfbc_smooth_robust_body_rate, 
dfbc_smooth_robust, explicit_gain_scheduled_mpc, feedback_linearization, 
fuzzy_smc, h_2_state_feedback, ilqr, integral_smc, lqg, lqi, lqr_baseline, 
mppi, ndi, nonsingular_terminal_smc, official_pid, official_pid_yaw_authority_mapped, 
passivity_based_control, px4ctrl, robust_mpc, se_3_basic, terminal_smc, tube_mpc
```

## 方案A：批量导出（推荐）- 使用Julia脚本

在MWORKS Syslab中运行以下Julia代码：

```julia
using Glob

# 28个通过控制器列表
controllers = [
    "adaptive_backstepping", "adaptive_smc", "backstepping_baseline", "dfbc_basic",
    "dfbc_high_order_body_rate", "dfbc_high_order", "dfbc_smooth_robust_body_rate",
    "dfbc_smooth_robust", "explicit_gain_scheduled_mpc", "feedback_linearization",
    "fuzzy_smc", "h_2_state_feedback", "ilqr", "integral_smc", "lqg", "lqi",
    "lqr_baseline", "mppi", "ndi", "nonsingular_terminal_smc", "official_pid",
    "official_pid_yaw_authority_mapped", "passivity_based_control", "px4ctrl",
    "robust_mpc", "se_3_basic", "terminal_smc", "tube_mpc"
]

base_path = raw"C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath"

for controller_id in controllers
    println("Processing: $controller_id")
    
    # 定位MSR文件（选择最新的native_result_g6目录）
    msr_pattern = joinpath(base_path, controller_id, "native_result_g6_*", "*", "Result.msr")
    msr_files = glob(msr_pattern)
    
    if isempty(msr_files)
        println("  ERROR: No MSR file found")
        continue
    end
    
    # 选择最新的MSR
    latest_msr = sort(msr_files, by=mtime, rev=true)[1]
    println("  MSR: $latest_msr")
    
    # 创建输出目录
    output_dir = joinpath(base_path, controller_id, "raw")
    mkpath(output_dir)
    output_csv = joinpath(output_dir, "climbpath50s.csv")
    
    # 使用MWORKS API导出CSV
    # 注意：以下API调用需要根据实际MWORKS版本调整
    try
        # 方法1：如果有直接的MSR→CSV导出函数
        # MWORKS.export_msr_to_csv(latest_msr, output_csv, 
        #     columns=["time", "x", "y", "z", "x_ref", "y_ref", "z_ref", 
        #              "vx", "vy", "vz", "roll", "pitch", "yaw", 
        #              "u1", "u2", "u3", "u4"])
        
        # 方法2：通过Result Viewer命令行接口（如果可用）
        # run(`mworks-result-viewer --export-csv $latest_msr --output $output_csv`)
        
        # 方法3：手动打开Result Viewer导出（见下面的"方案B"）
        
        println("  SUCCESS: Exported to $output_csv")
    catch e
        println("  ERROR: $e")
    end
end

println("\nBatch export complete!")
```

**注意：** 上述代码中的MWORKS API调用需要根据你的MWORKS版本调整。如果不确定API，使用方案B手动导出。

---

## 方案B：手动导出（通过Result Viewer）

如果批量脚本不可用，对每个控制器执行以下步骤：

### 步骤1：定位MSR文件
对于每个控制器，找到其最新的MSR文件：
```
Results/control_platform/phase2_full_48_climbpath/{controller}/native_result_g6_*/*/Result.msr
```

例如：
- `adaptive_backstepping` → `Results/.../adaptive_backstepping/native_result_g6_20260729_.../AdaptiveBacksteppingFormalRunner/Result.msr`

### 步骤2：打开Result Viewer
1. 启动MWORKS Syslab
2. 打开Result Viewer
3. `File → Open` → 选择MSR文件

### 步骤3：导出CSV
1. 在Result Viewer中，选择需要导出的变量（列）：
   - `time` - 时间戳
   - `x`, `y`, `z` - 实际位置
   - `x_ref`, `y_ref`, `z_ref` - 参考位置
   - `vx`, `vy`, `vz` - 速度（如果有）
   - `roll`, `pitch`, `yaw` - 姿态角（如果有）
   - `u1`, `u2`, `u3`, `u4` - 控制输入（如果有）

2. `Export → CSV`
3. 保存为：`Results/control_platform/phase2_full_48_climbpath/{controller}/raw/climbpath50s.csv`

### 步骤4：重复28次
对全部28个控制器重复步骤1-3。

---

## 验证导出结果

导出完成后，运行以下命令验证：

```bash
cd C:/Users/HP/Desktop/MoSim

# 检查CSV文件数量
find Results/control_platform/phase2_full_48_climbpath -name "climbpath50s.csv" | wc -l
# 应该输出：28

# 检查每个CSV的行数（ClimbPath 50s @ 100Hz ≈ 5000行）
find Results/control_platform/phase2_full_48_climbpath -name "climbpath50s.csv" -exec wc -l {} \;
```

---

## 导出完成后的下一步

CSV导出完成后，运行Julia脚本生成图表：

```bash
# 1. 生成28个控制器详细轨迹图（112张SVG）
julia Scripts/syslab/generate_controller_trajectories.jl

# 2. 更新族内对比图（24张SVG，新字体标准）
julia Scripts/syslab/compare_controllers.jl --climbpath {各族控制器CSV路径} --output-dir Docs/figures/第10章/{族名}_family_comparison
```

具体命令我会在CSV导出完成后提供。
