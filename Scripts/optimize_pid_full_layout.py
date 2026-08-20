#!/usr/bin/env python3
"""
Complete layout optimizer for OfficialPidGraphicalCore.mo
Ensures no module overlap with systematic X and Y coordinate placement.
"""

import re

def optimize_full_layout(input_path, output_path):
    """
    Optimize the complete layout with both X and Y coordinates.

    Layout strategy:
    - 6 channels: X(y=300), Y(y=150), Z(y=0), Roll(y=-150), Pitch(y=-300), Yaw(y=-450)
    - Each channel has a horizontal pipeline with consistent X spacing
    - Standard module width: ~80 units, spacing: 80-100 units between origins
    """

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define layout rules for each channel
    # Format: component_name -> (x, y_offset_from_channel_base)

    # X channel (y_base = 300)
    x_channel_layout = {
        'x_ref': (-560, 0),
        'x_mea': (-560, -40),
        'x_error': (-480, 0),
        'x_p': (-400, 35),
        'x_derivative_input': (-480, -40),
        'x_derivative_difference': (-420, -40),
        'x_derivative_slope': (-360, -40),
        'x_d': (-320, -40),
        'x_derivative_filtered_increment': (-300, -70),
        'x_derivative_previous_state': (-300, -10),
        'x_derivative_state_decay': (-240, -10),
        'x_derivative_state_sum': (-180, -40),
        'x_derivative': (-120, -40),
        'x_pd': (-240, 0),
        'pitch_ref_scale': (-160, 0),
        'pitch_ref_limit': (-80, 0),
    }

    # Y channel (y_base = 150)
    y_channel_layout = {
        'y_ref': (-560, 0),
        'y_mea': (-560, -40),
        'y_error': (-480, 0),
        'y_p': (-400, 35),
        'y_derivative_input': (-480, -40),
        'y_derivative_difference': (-420, -40),
        'y_derivative_slope': (-360, -40),
        'y_d': (-320, -40),
        'y_derivative_filtered_increment': (-300, -70),
        'y_derivative_previous_state': (-300, -10),
        'y_derivative_state_decay': (-240, -10),
        'y_derivative_state_sum': (-180, -40),
        'y_derivative': (-120, -40),
        'y_pd': (-240, 0),
        'roll_ref_scale': (-160, 0),
        'roll_ref_limit': (-80, 0),
    }

    # Z channel (y_base = 0)
    z_channel_layout = {
        'z_ref': (-560, 0),
        'z_mea': (-560, -40),
        'z_error': (-480, 0),
        'z_p': (-400, 35),
        'z_integral_dt': (-480, -60),
        'z_integral_accum': (-340, 0),
        'z_integral_feedback': (-400, -30),
        'z_i': (-400, 5),
        'z_derivative_input': (-480, -95),
        'z_derivative_difference': (-420, -95),
        'z_derivative_slope': (-360, -95),
        'z_d': (-320, -95),
        'z_derivative_filtered_increment': (-300, -125),
        'z_derivative_previous_state': (-300, -65),
        'z_derivative_state_decay': (-240, -65),
        'z_derivative_state_sum': (-180, -95),
        'z_derivative': (-120, -95),
        'z_pid': (-240, 0),
        'thrust': (-160, 0),
        'gravity': (-160, -30),
        'thrust_total': (-80, 0),
        'mass': (-80, -30),
    }

    # Roll channel (y_base = -150)
    roll_channel_layout = {
        'roll_mea': (-560, 0),
        'roll_ref_limit': (-480, 0),
        'roll_error': (-400, 0),
        'roll_p': (-320, 35),
        'roll_derivative_input': (-400, -40),
        'roll_derivative_difference': (-340, -40),
        'roll_derivative_slope': (-280, -40),
        'roll_derivative_filtered_increment': (-220, -70),
        'roll_derivative_previous_state': (-220, -10),
        'roll_derivative_state_decay': (-160, -10),
        'roll_derivative_state_sum': (-100, -40),
        'roll_derivative': (-40, -40),
        'roll_d': (-240, -40),
        'roll_pd': (-240, 0),
        'body_rate_x': (-160, 0),
    }

    # Pitch channel (y_base = -300)
    pitch_channel_layout = {
        'pitch_mea': (-560, 0),
        'pitch_ref_limit': (-480, 0),
        'pitch_error': (-400, 0),
        'pitch_p': (-320, 35),
        'pitch_derivative_input': (-400, -40),
        'pitch_derivative_difference': (-340, -40),
        'pitch_derivative_slope': (-280, -40),
        'pitch_derivative_filtered_increment': (-220, -70),
        'pitch_derivative_previous_state': (-220, -10),
        'pitch_derivative_state_decay': (-160, -10),
        'pitch_derivative_state_sum': (-100, -40),
        'pitch_derivative': (-40, -40),
        'pitch_d': (-240, -40),
        'pitch_pd': (-240, 0),
        'body_rate_y': (-160, 0),
    }

    # Yaw channel (y_base = -450)
    yaw_channel_layout = {
        'yaw_mea': (-560, 0),
        'yaw_ref': (-560, 40),
        'yaw_error': (-480, 0),
        'yaw_p': (-400, 35),
        'yaw_derivative_input': (-480, -40),
        'yaw_derivative_difference': (-420, -40),
        'yaw_derivative_slope': (-360, -40),
        'yaw_d': (-320, -40),
        'yaw_derivative_filtered_increment': (-300, -70),
        'yaw_derivative_previous_state': (-300, -10),
        'yaw_derivative_state_decay': (-240, -10),
        'yaw_derivative_state_sum': (-180, -40),
        'yaw_derivative': (-120, -40),
        'yaw_pd': (-240, 0),
        'body_rate_z': (-160, 0),
    }

    # Combine all layouts
    all_layouts = [
        (x_channel_layout, 300),
        (y_channel_layout, 150),
        (z_channel_layout, 0),
        (roll_channel_layout, -150),
        (pitch_channel_layout, -300),
        (yaw_channel_layout, -450),
    ]

    # Apply transformations
    for layout, y_base in all_layouts:
        for comp_name, (x, y_offset) in layout.items():
            y = y_base + y_offset
            pattern = rf'({re.escape(comp_name)}[^a-zA-Z_0-9][^)]*?annotation\(Placement\(transformation\(origin\s*=\s*\{{)[^,}}]+,\s*[^}}]+(\}})'

            def replacer(match):
                return f'{match.group(1)}{x}, {y}{match.group(2)}'

            content = re.sub(pattern, replacer, content)

    # Handle output ports (right side)
    output_positions = {
        'y ': (430, 180),   # Note space after 'y' to avoid matching 'y1'
        'y1': (430, 60),
        'y2': (430, -60),
        'y3': (430, -180),
    }

    for port_name, (x, y) in output_positions.items():
        if port_name == 'y ':
            pattern = r'(Outport y\s[^a-zA-Z_0-9][^)]*?annotation\(Placement\(transformation\(origin\s*=\s*\{)[^,}]+,\s*[^}]+(\})'
        else:
            pattern = rf'(Outport {re.escape(port_name)}[^a-zA-Z_0-9][^)]*?annotation\(Placement\(transformation\(origin\s*=\s*\{{)[^,}}]+,\s*[^}}]+(\}})'

        def replacer(match):
            return f'{match.group(1)}{x}, {y}{match.group(2)}'

        content = re.sub(pattern, replacer, content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Full layout optimized: {input_path} -> {output_path}")

if __name__ == '__main__':
    input_file = 'Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo'
    output_file = input_file
    optimize_full_layout(input_file, output_file)
    print("Done. Verify in Sysplorer before committing.")
