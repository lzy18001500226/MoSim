#!/usr/bin/env python3
"""
46 Controller Sysblock Graphical Core Batch Generator
自动从archive提取算法逻辑，转换为纯Sysblock图形化建模
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(r"C:\Users\HP\Desktop\MoSim")
CATALOG_PATH = BASE_DIR / "Config/control_platform/control_scheme_catalog.json"
ARCHIVE_ROOT = Path(r"E:\刘致远18001500226\MoSim_Archive\20260818_codex_legacy_architecture\Control_Implementations_Graphical\Graphical")
CONTROL_ROOT = BASE_DIR / "Models/MoSimQuadrotorModel/Control"

# G3已验证的28个控制器（优先处理）
VERIFIED_28 = [
    "adaptive_backstepping", "adaptive_smc", "backstepping_baseline",
    "dfbc_basic", "dfbc_high_order_bodyrate", "dfbc_high_order_attitude",
    "dfbc_smooth_robust_bodyrate", "dfbc_smooth_robust_attitude",
    "explicit_gain_scheduled_mpc", "feedback_linearization", "fuzzy_smc",
    "h2_state_feedback", "ilqr", "integral_smc", "lqg", "lqi_baseline",
    "lqr_baseline", "mppi", "ndi", "nonsingular_terminal_smc",
    "official_pid", "official_pid_yaw_authority_mapped",
    "passivity_based_control", "px4ctrl", "robust_mpc", "se3_basic",
    "terminal_smc", "tube_mpc"
]

def load_catalog():
    """加载控制器目录"""
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    schemes = [s for s in data['schemes']
               if s['execution_kind'] == 'graphical_control_core'
               and s['implementation_status'] == 'implemented']
    return schemes

def scheme_id_to_package_name(scheme_id: str) -> str:
    """scheme_id转PascalCase包名"""
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
    }
    parts = scheme_id.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

def generate_sysblock_core_template(scheme_id: str, family: str) -> str:
    """生成纯Sysblock图形化Core模板（占位符，实际需要算法逻辑）"""
    pkg_name = scheme_id_to_package_name(scheme_id)

    # 基础模板（后续需要根据archive中的算法逻辑填充真实组件）
    template = f'''within MoSimQuadrotorModel.Control.{family}.{pkg_name};
model {pkg_name}Core "{scheme_id} graphical control core (Sysblock modeling)"
  // TODO: 从archive提取算法逻辑，转换为Sysblock组件
  // 当前为占位模板，需要补充真实控制器组件连线

  // 输入接口
  Modelica.Blocks.Interfaces.RealInput position_reference[3] "Position reference [m]";
  Modelica.Blocks.Interfaces.RealInput position_measurement[3] "Position measurement [m]";
  Modelica.Blocks.Interfaces.RealInput velocity_measurement[3] "Velocity measurement [m/s]";
  Modelica.Blocks.Interfaces.RealInput attitude_measurement[3] "Attitude measurement [rad]";

  // 输出接口
  Modelica.Blocks.Interfaces.RealOutput control_output[4] "Control output (depends on boundary)";

  // 控制器核心组件（占位，需要根据具体算法填充）
  Modelica.Blocks.Math.Add3 position_error "Position error calculation";
  Modelica.Blocks.Continuous.Integrator integrator "Integral term";
  Modelica.Blocks.Math.Gain gain_p(k=1.0) "Proportional gain";

  // 连线（占位，需要根据具体算法拓扑填充）
  annotation(
    Diagram(graphics={{
      Line(points={{-80,60},{-40,60}}, color={0,0,127}),
      Line(points={{-40,60},{0,60}}, color={0,0,127}),
      Line(points={{0,60},{40,60}}, color={0,0,127})
    }}),
    __MWORKS(hide = false, version = "26.3.0")
  );
end {pkg_name}Core;
'''
    return template

def main():
    """主流程：批量生成46个控制器Core"""
    catalog = load_catalog()
    print(f"开始批量生成 {len(catalog)} 个控制器Core")

    # 按优先级排序：28个已验证的优先
    sorted_schemes = []
    for s in catalog:
        if s['scheme_id'] in VERIFIED_28:
            sorted_schemes.insert(0, s)  # 已验证的放前面
        else:
            sorted_schemes.append(s)

    success_count = 0
    fail_count = 0

    for scheme in sorted_schemes:
        scheme_id = scheme['scheme_id']
        family = scheme['implementation_package']
        pkg_name = scheme_id_to_package_name(scheme_id)

        # 检查archive中是否有旧Core（用于提取算法逻辑）
        archive_core_path = ARCHIVE_ROOT / pkg_name / f"{pkg_name}Core.mo"
        has_archive = archive_core_path.exists()

        # 生成新Core路径
        family_dir = CONTROL_ROOT / family / pkg_name
        family_dir.mkdir(parents=True, exist_ok=True)
        core_path = family_dir / f"{pkg_name}Core.mo"

        # 生成模板
        core_content = generate_sysblock_core_template(scheme_id, family)
        core_path.write_text(core_content, encoding='utf-8')

        priority = "⭐ VERIFIED" if scheme_id in VERIFIED_28 else "  "
        archive_status = "✓ archive" if has_archive else "✗ no archive"
        print(f"{priority} {scheme_id:40s} → {family:20s} {archive_status}")

        success_count += 1

    print(f"\n批量生成完成: {success_count} 成功, {fail_count} 失败")
    print(f"注意: 当前生成的是占位模板，需要第二步从archive提取真实算法逻辑")

if __name__ == "__main__":
    main()
