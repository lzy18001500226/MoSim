#!/usr/bin/env python3
"""
Complete layout optimizer for OfficialPidGraphicalCore.mo with large spacing.
Reference: Px4CtrlBaselineCore uses ~100 unit vertical spacing between channels.
This script uses 200+ unit vertical spacing and 60-80 unit horizontal spacing.
"""

import re

def optimize_full_layout(input_path, output_path):
    """
    Optimize with large spacing to match Px4Ctrl reference layout.

    Strategy:
    - 6 channels with 250-unit vertical spacing between channel bases
    - X channel: y_base=600
    - Y channel: y_base=350
    - Z channel: y_base=100
    - Roll channel: y_base=-150
    - Pitch channel: y_base=-400
    - Yaw channel: y_base=-650
    - Horizontal spacing: 60-80 units between module origins
    """

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Component layout rules: {component_name: (x, y_offset_from_channel_base)}

    # X channel (y_base = 600) - Position/Attitude control
    x_channel = {
        'x_ref': (-560, 0),
        'x_mea': (-560, -60),
        'x_error': (-480, -30),
        'x_p': (-400, 20),
        'x_derivative_input': (-480, -90),
        'x_derivative_difference': (-410, -90),
        'x_derivative_slope': (-340, -90),
        'x_d': (-270, -90),
        'x_derivative_filtered_increment': (-200, -120),
        'x_derivative_previous_state': (-200, -60),
        'x_derivative_state_decay': (-130, -60),
        'x_derivative_state_sum': (-60, -90),
        'x_derivative': (10, -90),
        'x_pd': (-200, -30),
        'pitch_ref_scale': (-120, -30),
        'pitch_ref_limit': (-40, -30),
    }

    # Y channel (y_base = 350)
    y_channel = {
        'y_ref': (-560, 0),
        'y_mea': (-560, -60),
        'y_error': (-480, -30),
        'y_p': (-400, 20),
        'y_derivative_input': (-480, -90),
        'y_derivative_difference': (-410, -90),
        'y_derivative_slope': (-340, -90),
        'y_d': (-270, -90),
        'y_derivative_filtered_increment': (-200, -120),
        'y_derivative_previous_state': (-200, -60),
        'y_derivative_state_decay': (-130, -60),
        'y_derivative_state_sum': (-60, -90),
        'y_derivative': (10, -90),
        'y_pd': (-200, -30),
        'roll_ref_scale': (-120, -30),
        'roll_ref_limit': (-40, -30),
    }

    # Z channel (y_base = 100) - Has PID (with I term)
    z_channel = {
        'z_ref': (-560, 0),
        'z_mea': (-560, -60),
        'z_error': (-480, -30),
        'z_p': (-400, 40),
        'z_integral_dt': (-480, -90),
        'z_integral_accum': (-410, -60),
        'z_integral_state': (-340, -60),
        'z_i': (-270, -90),
        'z_derivative_input': (-480, -150),
        'z_derivative_difference': (-410, -150),
        'z_derivative_slope': (-340, -150),
        'z_d': (-270, -150),
        'z_derivative_filtered_increment': (-200, -180),
        'z_derivative_previous_state': (-200, -120),
        'z_derivative_state_decay': (-130, -120),
        'z_derivative_state_sum': (-60, -150),
        'z_derivative': (10, -150),
        'z_pi': (-340, -30),
        'z_pid': (-200, -30),
        'thrust': (-130, -30),
        'gravity': (-130, -90),
        'thrust_total': (-60, -60),
        'mass': (-60, -120),
    }

    # Roll channel (y_base = -150) - Body rate control
    roll_channel = {
        'roll_mea': (-560, 0),
        'roll_mea_sign': (-490, 0),
        'roll_ref_limit': (-420, 0),
        'roll_error': (-350, 0),
        'roll_p': (-280, 30),
        'roll_derivative_input': (-350, -60),
        'roll_derivative_difference': (-280, -60),
        'roll_derivative_slope': (-210, -60),
        'roll_derivative_filtered_increment': (-140, -90),
        'roll_derivative_previous_state': (-140, -30),
        'roll_derivative_state_decay': (-70, -30),
        'roll_derivative_state_sum': (0, -60),
        'roll_derivative': (70, -60),
        'roll_d': (-210, -60),
        'roll_pd': (-140, 0),
        'roll_limit': (-70, 0),
        'roll_mix': (0, 0),
        'body_rate_x': (70, 0),
    }

    # Pitch channel (y_base = -400)
    pitch_channel = {
        'pitch_mea': (-560, 0),
        'pitch_ref_limit': (-490, 0),
        'yaw_reference': (-560, -60),
        'pitch_error': (-420, 0),
        'pitch_p': (-350, 30),
        'pitch_derivative_input': (-420, -60),
        'pitch_derivative_difference': (-350, -60),
        'pitch_derivative_slope': (-280, -60),
        'pitch_derivative_filtered_increment': (-210, -90),
        'pitch_derivative_previous_state': (-210, -30),
        'pitch_derivative_state_decay': (-140, -30),
        'pitch_derivative_state_sum': (-70, -60),
        'pitch_derivative': (0, -60),
        'pitch_d': (-280, -60),
        'pitch_pd': (-210, 0),
        'pitch_limit': (-140, 0),
        'pitch_mix': (-70, 0),
        'body_rate_y': (0, 0),
    }

    # Yaw channel (y_base = -650)
    yaw_channel = {
        'yaw_mea': (-560, 0),
        'yaw_ref': (-560, 60),
        'yaw_error': (-480, 30),
        'yaw_p': (-410, 60),
        'yaw_derivative_input': (-480, -30),
        'yaw_derivative_difference': (-410, -30),
        'yaw_derivative_slope': (-340, -30),
        'yaw_d': (-270, -30),
        'yaw_derivative_filtered_increment': (-200, -60),
        'yaw_derivative_previous_state': (-200, 0),
        'yaw_derivative_state_decay': (-130, 0),
        'yaw_derivative_state_sum': (-60, -30),
        'yaw_derivative': (10, -30),
        'yaw_pd': (-200, 30),
        'yaw_limit': (-130, 30),
        'yaw_mix': (-60, 30),
        'body_rate_z': (10, 30),
    }

    # Combine all layouts with their y_base
    all_layouts = [
        (x_channel, 600, "X"),
        (y_channel, 350, "Y"),
        (z_channel, 100, "Z"),
        (roll_channel, -150, "Roll"),
        (pitch_channel, -400, "Pitch"),
        (yaw_channel, -650, "Yaw"),
    ]

    # Apply transformations
    updated_count = 0
    for layout, y_base, channel_name in all_layouts:
        for comp_name, (x, y_offset) in layout.items():
            y = y_base + y_offset

            # Pattern to match component annotation
            pattern = rf'({re.escape(comp_name)}(?:[^a-zA-Z_0-9]|\s)[^)]*?annotation\(Placement\(transformation\(origin\s*=\s*\{{)[^,}}]+,\s*[^}}]+(\}})'

            def replacer(match):
                nonlocal updated_count
                updated_count += 1
                return f'{match.group(1)}{x}, {y}{match.group(2)}'

            new_content = re.sub(pattern, replacer, content, count=1)
            if new_content != content:
                print(f"  {channel_name}: {comp_name} -> ({x}, {y})")
            content = new_content

    # Handle output ports (right side)
    output_positions = {
        ('y ', 'Outport y\\s'): (430, 200),
        ('y1', 'Outport y1'): (430, 80),
        ('y2', 'Outport y2'): (430, -40),
        ('y3', 'Outport y3'): (430, -160),
    }

    for (port_name, pattern_str), (x, y) in output_positions.items():
        pattern = rf'({pattern_str}[^a-zA-Z_0-9][^)]*?annotation\(Placement\(transformation\(origin\s*=\s*\{{)[^,}}]+,\s*[^}}]+(\}})'

        def replacer(match):
            nonlocal updated_count
            updated_count += 1
            return f'{match.group(1)}{x}, {y}{match.group(2)}'

        content = re.sub(pattern, replacer, content, count=1)
        print(f"  Output: {port_name.strip()} -> ({x}, {y})")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nLayout optimized: {updated_count} components updated")
    print(f"Output: {output_path}")

if __name__ == '__main__':
    input_file = 'Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo'
    output_file = input_file

    print("Optimizing PID layout with large spacing (no overlap)...")
    optimize_full_layout(input_file, output_file)
    print("\nDone. Verify in Sysplorer before committing.")
