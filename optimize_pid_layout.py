#!/usr/bin/env python3
"""
Optimize OfficialPidGraphicalCore layout for uniform vertical spacing.
"""

import re
import sys

# Define target Y coordinates for each channel (uniform 150-unit spacing)
CHANNEL_Y_COORDS = {
    'x_': 300,       # X channel
    'y_': 150,       # Y channel
    'z_': 0,         # Z channel
    'roll_': -150,   # Roll channel
    'pitch_': -300,  # Pitch channel
    'yaw_': -450,    # Yaw channel
}

def get_channel_from_name(component_name):
    """Extract channel prefix from component name."""
    for prefix in CHANNEL_Y_COORDS.keys():
        if component_name.startswith(prefix):
            return prefix
    return None

def update_placement_y(line, new_y):
    """Update the Y coordinate in a Placement annotation."""
    # Pattern: origin = {x, y}
    pattern = r'(origin\s*=\s*\{)([^,]+),\s*([^}]+)(\})'

    def replacer(match):
        return f'{match.group(1)}{match.group(2)}, {new_y}{match.group(4)}'

    return re.sub(pattern, replacer, line)

def process_file(input_path, output_path):
    """Process the .mo file and update Y coordinates."""
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_lines = []
    current_component = None
    component_pattern = r'^\s*SysplorerEmbeddedCoder\.\S+\s+(\w+)'

    for line in lines:
        # Check if this line declares a new component
        match = re.match(component_pattern, line)
        if match:
            current_component = match.group(1)

        # Check if this line contains a Placement with origin
        if current_component and 'origin' in line and '{' in line:
            channel = get_channel_from_name(current_component)
            if channel:
                target_y = CHANNEL_Y_COORDS[channel]
                line = update_placement_y(line, target_y)

        modified_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

    print(f"Layout optimized: {input_path} -> {output_path}")

if __name__ == '__main__':
    input_file = 'Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo'
    output_file = input_file  # Overwrite in place

    process_file(input_file, output_file)
    print("Done. Commit the changes after verifying in Sysplorer.")
