#!/usr/bin/env python3
"""
重新整理 OfficialPidGraphicalCore.mo 的图形布局
参考 Px4CtrlBaselineCore 的清晰水平分层布局模式

布局策略：
- 输入端口：左侧 x=-560
- X通道：上层 y=260附近（包含误差、PD、导数滤波器）
- Y通道：中上层 y=120附近
- Z通道：中层 y=-20附近
- Roll通道：中下层 y=-160附近
- Pitch通道：下层 y=-300附近
- Yaw通道：底层 y=-440附近
- Motor mixer：右侧 x=200~400
- 输出端口：最右侧 x=430

每个通道的水平分层：
  误差计算 → P/I项 → 导数滤波器 → PD求和 → 限幅 → 输出
  x=-480    x=-400   x=-300~-180   x=-240    x=-160  x=-80
"""

import re

# 新的布局坐标方案（参考Px4CtrlBaselineCore的清晰分层）
NEW_LAYOUT = {
    # ═══ 输入端口（左侧，垂直排列）═══
    'x_ref': '{-560, 260}',
    'y_ref': '{-560, 202}',
    'z_ref': '{-560, 144}',
    'x_mea': '{-560, 86}',
    'y_mea': '{-560, 28}',
    'z_mea': '{-560, -30}',
    'roll_mea': '{-560, -88}',
    'pitch_mea': '{-560, -146}',
    'yaw_mea': '{-560, -204}',

    # ═══ 输出端口（右侧）═══
    'y': '{430, 180}',
    'y1': '{430, 60}',
    'y2': '{430, -60}',
    'y3': '{430, -180}',

    # ═══ X通道（顶层 y≈260）═══
    'x_error': '{-480, 260}',
    'x_p': '{-400, 295}',
    'x_derivative_input': '{-480, 225}',
    'x_derivative_difference': '{-420, 225}',
    'x_derivative_slope': '{-360, 225}',
    'x_d': '{-320, 225}',
    'x_derivative_filtered_increment': '{-300, 195}',
    'x_derivative_previous_state': '{-300, 255}',
    'x_derivative_state_decay': '{-240, 255}',
    'x_derivative_state_sum': '{-180, 225}',
    'x_derivative': '{-120, 225}',
    'x_pd': '{-240, 260}',
    'pitch_ref_scale': '{-160, 260}',
    'pitch_ref_limit': '{-80, 260}',

    # ═══ Y通道（中上层 y≈120）═══
    'y_error': '{-480, 120}',
    'y_p': '{-400, 155}',
    'y_derivative_input': '{-480, 85}',
    'y_derivative_difference': '{-420, 85}',
    'y_derivative_slope': '{-360, 85}',
    'y_d': '{-320, 85}',
    'y_derivative_filtered_increment': '{-300, 55}',
    'y_derivative_previous_state': '{-300, 115}',
    'y_derivative_state_decay': '{-240, 115}',
    'y_derivative_state_sum': '{-180, 85}',
    'y_derivative': '{-120, 85}',
    'y_pd': '{-240, 120}',
    'roll_ref_scale': '{-160, 120}',
    'roll_ref_limit': '{-80, 120}',

    # ═══ Z通道（中层 y≈-20）═══
    'z_error': '{-480, -20}',
    'z_p': '{-400, 25}',
    'z_integral_dt': '{-480, -55}',
    'z_integral_increment': '{-420, -55}',
    'z_integral_previous': '{-420, -85}',
    'z_integral_state_decay': '{-360, -85}',
    'z_integral_state_sum': '{-300, -55}',
    'z_integral': '{-240, -55}',
    'z_i': '{-360, -55}',
    'z_derivative_input': '{-480, -90}',
    'z_derivative_difference': '{-420, -120}',
    'z_derivative_slope': '{-360, -120}',
    'z_d': '{-320, -120}',
    'z_derivative_filtered_increment': '{-300, -150}',
    'z_derivative_previous_state': '{-300, -90}',
    'z_derivative_state_decay': '{-240, -90}',
    'z_derivative_state_sum': '{-180, -120}',
    'z_derivative': '{-120, -120}',
    'z_pid': '{-180, -20}',
    'z_reference': '{-100, -20}',
    'z_gravity_compensation': '{-40, -20}',

    # ═══ Roll通道（中下层 y≈-160）═══
    'roll_error': '{-480, -160}',
    'roll_p': '{-400, -125}',
    'roll_derivative_input': '{-480, -195}',
    'roll_derivative_difference': '{-420, -195}',
    'roll_derivative_slope': '{-360, -195}',
    'roll_d': '{-320, -195}',
    'roll_derivative_filtered_increment': '{-300, -225}',
    'roll_derivative_previous_state': '{-300, -165}',
    'roll_derivative_state_decay': '{-240, -165}',
    'roll_derivative_state_sum': '{-180, -195}',
    'roll_derivative': '{-120, -195}',
    'roll_pd': '{-240, -160}',
    'roll_limit': '{-160, -160}',
    'roll_mix': '{-80, -160}',

    # ═══ Pitch通道（下层 y≈-300）═══
    'pitch_error': '{-480, -300}',
    'pitch_p': '{-400, -265}',
    'pitch_derivative_input': '{-480, -335}',
    'pitch_derivative_difference': '{-420, -335}',
    'pitch_derivative_slope': '{-360, -335}',
    'pitch_d': '{-320, -335}',
    'pitch_derivative_filtered_increment': '{-300, -365}',
    'pitch_derivative_previous_state': '{-300, -305}',
    'pitch_derivative_state_decay': '{-240, -305}',
    'pitch_derivative_state_sum': '{-180, -335}',
    'pitch_derivative': '{-120, -335}',
    'pitch_pd': '{-240, -300}',
    'pitch_limit': '{-160, -300}',
    'pitch_mix': '{-80, -300}',

    # ═══ Yaw通道（底层 y≈-440）═══
    'yaw_error': '{-480, -440}',
    'yaw_p': '{-400, -405}',
    'yaw_derivative_input': '{-480, -475}',
    'yaw_derivative_difference': '{-420, -475}',
    'yaw_derivative_slope': '{-360, -475}',
    'yaw_d': '{-320, -475}',
    'yaw_derivative_filtered_increment': '{-300, -505}',
    'yaw_derivative_previous_state': '{-300, -445}',
    'yaw_derivative_state_decay': '{-240, -445}',
    'yaw_derivative_state_sum': '{-180, -475}',
    'yaw_derivative': '{-120, -475}',
    'yaw_pd': '{-240, -440}',
    'yaw_limit': '{-160, -440}',
    'yaw_mix': '{-80, -440}',

    # ═══ Motor Mixer（右侧）═══
    'mixer_1_roll': '{20, -160}',
    'mixer_1_pitch': '{20, -300}',
    'mixer_1_yaw': '{20, -440}',
    'mixer_1_first': '{100, 180}',
    'mixer_1_second': '{180, 180}',
    'mixer_1': '{260, 180}',
    'amplitude_limit_1': '{340, 180}',

    'mixer_2_roll': '{60, -160}',
    'mixer_2_pitch': '{60, -300}',
    'mixer_2_yaw': '{60, -440}',
    'mixer_2_first': '{100, 60}',
    'mixer_2_second': '{180, 60}',
    'mixer_2': '{260, 60}',
    'amplitude_limit_2': '{340, 60}',

    'mixer_3_roll': '{100, -160}',
    'mixer_3_pitch': '{100, -300}',
    'mixer_3_yaw': '{100, -440}',
    'mixer_3_first': '{100, -60}',
    'mixer_3_second': '{180, -60}',
    'mixer_3': '{260, -60}',
    'amplitude_limit_3': '{340, -60}',

    'mixer_4_roll': '{140, -160}',
    'mixer_4_pitch': '{140, -300}',
    'mixer_4_yaw': '{140, -440}',
    'mixer_4_first': '{100, -180}',
    'mixer_4_second': '{180, -180}',
    'mixer_4': '{260, -180}',
    'amplitude_limit_4': '{340, -180}',
}

def replace_origin(match):
    """替换origin坐标"""
    comp_name = match.group(1)
    if comp_name in NEW_LAYOUT:
        new_origin = NEW_LAYOUT[comp_name]
        # 保持原有的格式，只替换origin值
        return match.group(0).replace(match.group(2), new_origin)
    return match.group(0)

def main():
    input_file = "Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo"
    output_file = input_file

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 component_name ... annotation (Placement(transformation(origin = {...}
    pattern = r'(\w+)(?:\([^)]*\))?\s*annotation\s*\(Placement\(transformation\(origin\s*=\s*(\{[^}]+\})'

    # 替换所有匹配的origin坐标
    new_content = re.sub(pattern, replace_origin, content)

    # 统计修改了多少个组件
    modified_count = sum(1 for name in NEW_LAYOUT if name in content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[OK] Updated {modified_count} component placements")
    print(f"[OK] File saved: {output_file}")
    print("\nLayout layers:")
    print("  X channel (position->pitch): y=260")
    print("  Y channel (position->roll): y=120")
    print("  Z channel (position+integral): y=-20")
    print("  Roll inner loop: y=-160")
    print("  Pitch inner loop: y=-300")
    print("  Yaw inner loop: y=-440")
    print("  Motor Mixer: x=20~340")

if __name__ == "__main__":
    main()
