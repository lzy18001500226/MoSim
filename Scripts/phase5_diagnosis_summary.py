"""
Phase 5 失败控制器诊断汇总表格生成脚本

生成用于答辩的失败原因分类统计表
"""

import json
import sys
from pathlib import Path

# 设置UTF-8输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 12个失败控制器的诊断结果
controllers = [
    {
        "rank": 1,
        "name": "dfbc_smooth_robust_attitude",
        "error": 5.30,
        "category": "设计参数不匹配",
        "detail": "控制器设计假设±8 m/s²，平台限制±3.0 m/s²",
        "fixable": "需重新设计"
    },
    {
        "rank": 2,
        "name": "trained_neural_residual",
        "error": 6.93,
        "category": "架构不完整",
        "detail": "神经网络权重未加载或基线控制器参数不匹配",
        "fixable": "需补全实现"
    },
    {
        "rank": 3,
        "name": "rl_gain_scheduler",
        "error": 7.33,
        "category": "架构不完整",
        "detail": "强化学习策略未正确配置",
        "fixable": "需补全实现"
    },
    {
        "rank": 4,
        "name": "explicit_gain_scheduled_mpc",
        "error": 7.45,
        "category": "适配器架构不完整",
        "detail": "GraphicalAccelerationRotorPreview: collective_thrust=0, k=1无单位转换",
        "fixable": "需重新设计适配器"
    },
    {
        "rank": 5,
        "name": "tube_mpc",
        "error": 7.68,
        "category": "适配器架构不完整",
        "detail": "GraphicalAccelerationRotorPreview: collective_thrust=0, k=1无单位转换",
        "fixable": "需重新设计适配器"
    },
    {
        "rank": 6,
        "name": "official_pid",
        "error": 8.90,
        "category": "参数传递/配置问题",
        "detail": "scenario_mode或参数传递问题",
        "fixable": "可能可修复"
    },
    {
        "rank": 7,
        "name": "adaptive_smc",
        "error": 11.08,
        "category": "适配器架构不完整",
        "detail": "GraphicalAccelerationRotorPreview: collective_thrust=0, k=1无单位转换",
        "fixable": "需重新设计适配器"
    },
    {
        "rank": 8,
        "name": "fixed_awff_pid",
        "error": 11.18,
        "category": "遗留模板不兼容",
        "detail": "使用QuadChassis+ClimbPath遗留架构",
        "fixable": "需重新适配"
    },
    {
        "rank": 9,
        "name": "gain_scheduled_pid",
        "error": 11.53,
        "category": "适配器架构缺陷",
        "detail": "GraphicalScalarRotorPreview: 4个电机转速恒定相同，无法控制姿态",
        "fixable": "根本性缺陷"
    },
    {
        "rank": 10,
        "name": "fopid",
        "error": 14.12,
        "error_measured": 8.35,
        "category": "参考轨迹配置问题",
        "detail": "z_ref=5.2m(应为15.0m), 控制器本身性能良好",
        "fixable": "可能可修复"
    },
    {
        "rank": 11,
        "name": "fuzzy_pid",
        "error": 14.51,
        "category": "适配器架构缺陷",
        "detail": "GraphicalScalarRotorPreview: 4个电机转速恒定相同，无法控制姿态",
        "fixable": "根本性缺陷"
    },
    {
        "rank": 12,
        "name": "mrac",
        "error": 14.99,
        "error_measured": 1907.51,
        "category": "自适应律发散",
        "detail": "自适应增益设置不当，电机饱和110 rad/s",
        "fixable": "需调参或重新设计"
    }
]

# 按类别分组统计
category_stats = {}
for ctrl in controllers:
    cat = ctrl["category"]
    if cat not in category_stats:
        category_stats[cat] = []
    category_stats[cat].append(ctrl)

# 输出统计表
print("=" * 80)
print("Phase 5 失败控制器诊断汇总")
print("=" * 80)
print(f"\n总失败控制器数: {len(controllers)}")
print(f"总通过控制器数: 26")
print(f"Phase 5 成功率: 26/38 = 68.4%\n")

print("-" * 80)
print("按失败原因分类:")
print("-" * 80)

for i, (category, ctrls) in enumerate(sorted(category_stats.items(), key=lambda x: -len(x[1])), 1):
    print(f"\n{i}. {category} ({len(ctrls)}个)")
    for ctrl in ctrls:
        err_str = f"{ctrl['error']:.2f}m"
        if "error_measured" in ctrl:
            err_str += f" (实测{ctrl['error_measured']:.2f}m)"
        print(f"   - {ctrl['name']}: {err_str}")
        print(f"     问题: {ctrl['detail']}")
        print(f"     可修复性: {ctrl['fixable']}")

# 可修复性统计
print("\n" + "=" * 80)
print("可修复性分析:")
print("=" * 80)

fixable_groups = {
    "短期无法修复 (适配器/模板架构问题)": [],
    "需要较大改动 (重新设计/调参)": [],
    "可能通过调参修复 (配置问题)": []
}

for ctrl in controllers:
    if ctrl["fixable"] in ["根本性缺陷", "需重新设计适配器", "需重新适配"]:
        fixable_groups["短期无法修复 (适配器/模板架构问题)"].append(ctrl)
    elif ctrl["fixable"] in ["需重新设计", "需调参或重新设计", "需补全实现"]:
        fixable_groups["需要较大改动 (重新设计/调参)"].append(ctrl)
    else:
        fixable_groups["可能通过调参修复 (配置问题)"].append(ctrl)

for group_name, ctrls in fixable_groups.items():
    print(f"\n{group_name}: {len(ctrls)}个")
    for ctrl in ctrls:
        print(f"   - {ctrl['name']} ({ctrl['error']:.2f}m)")

# 适配器问题占比
adapter_issue_count = sum(1 for c in controllers if "适配器" in c["category"])
print(f"\n适配器架构问题占比: {adapter_issue_count}/12 = {adapter_issue_count/12*100:.1f}%")
print(f"排除适配器问题后的有效成功率: 26/(38-{adapter_issue_count}) = {26/(38-adapter_issue_count)*100:.1f}%")

print("\n" + "=" * 80)
print("诊断完成 (2026-08-19)")
print("=" * 80)

# 保存到JSON
output = {
    "summary": {
        "total_controllers": 38,
        "passed": 26,
        "failed": 12,
        "success_rate": 68.4,
        "adapter_issue_count": adapter_issue_count,
        "effective_success_rate": round(26/(38-adapter_issue_count)*100, 1)
    },
    "failed_controllers": controllers,
    "category_stats": {cat: len(ctrls) for cat, ctrls in category_stats.items()},
    "fixable_stats": {k: len(v) for k, v in fixable_groups.items()}
}

output_path = Path(__file__).parent.parent.parent / "Results" / "control_platform" / "phase5_failed_controllers_diagnosis.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n诊断结果已保存到: {output_path}")
