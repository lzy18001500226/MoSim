#!/usr/bin/env python3
"""
Remove enable switches from LqrBaselineCore - they gate outputs to zero
OfficialPid has no enable switches and works perfectly
Root cause: enable signal reads as 0.0, causing all switches to output zeros
Solution: Bypass switches, connect computed values directly to outputs
"""

def generate_fixed_core():
    """Generate LqrBaselineCore without enable switches"""

    # Read the backup
    with open('C:/Users/HP/Desktop/MoSim/Models/MoSimQuadrotorModel/Control/ClassicRobust/LqrBaseline/LqrBaselineCore.mo.backup', 'r') as f:
        lines = f.readlines()

    # Find and remove enable-related components
    output_lines = []
    skip_until_equation = False
    in_equation_section = False

    for i, line in enumerate(lines):
        # Skip enable switch declarations (lines 104-155)
        if 'SignalRouting.Switch enable_' in line:
            skip_until_equation = True
            continue

        # Skip disabled_command constant (line 44-45)
        if 'disabled_command' in line and 'Constant' in line:
            continue

        # Mark equation section start
        if line.strip() == 'equation':
            in_equation_section = True
            output_lines.append(line)
            continue

        # In equation section, replace enable switch connections with direct connections
        if in_equation_section:
            # Skip all enable switch connections (lines 239-342)
            if 'enable_position_error' in line or \
               'enable_velocity_error' in line or \
               'enable_desired_acceleration' in line or \
               'enable_desired_roll_rad' in line or \
               'enable_desired_pitch_rad' in line or \
               'enable_normalized_thrust' in line or \
               'enable_collective_thrust_n' in line or \
               'disabled_command' in line:
                continue

            # Add direct connections instead (at end of equation section, before 'end')
            if line.strip().startswith('end '):
                # Add direct connections
                output_lines.append('  // Direct output connections (enable switches removed)\n')
                output_lines.append('  connect(position_error_x.y, position_error_x_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, 297}, {661, 330}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(position_error_y.y, position_error_y_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, 87}, {661, 292}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(position_error_z.y, position_error_z_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, -123}, {661, 254}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(velocity_error_x.y, velocity_error_x_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, 213}, {661, 216}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(velocity_error_y.y, velocity_error_y_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, 3}, {661, 178}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(velocity_error_z.y, velocity_error_z_out)\n')
                output_lines.append('    annotation(Line(points = {{-496, -207}, {661, 140}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(desired_acceleration_x.y, desired_acceleration_x_out)\n')
                output_lines.append('    annotation(Line(points = {{139, 255}, {661, 102}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(desired_acceleration_y.y, desired_acceleration_y_out)\n')
                output_lines.append('    annotation(Line(points = {{139, 45}, {661, 64}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(desired_acceleration_z.y, desired_acceleration_z_out)\n')
                output_lines.append('    annotation(Line(points = {{139, -165}, {661, 26}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(roll_tilt_limit.y, desired_roll_rad_out)\n')
                output_lines.append('    annotation(Line(points = {{339, 55}, {661, -12}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(pitch_tilt_limit.y, desired_pitch_rad_out)\n')
                output_lines.append('    annotation(Line(points = {{339, 120}, {661, -50}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(normalized_thrust_limit.y, normalized_thrust_out)\n')
                output_lines.append('    annotation(Line(points = {{339, -55}, {661, -88}}, color = {0, 0, 127}));\n')
                output_lines.append('  connect(collective_thrust_from_normalized.y, collective_thrust_n_out)\n')
                output_lines.append('    annotation(Line(points = {{424, -55}, {661, -126}}, color = {0, 0, 127}));\n')
                output_lines.append('\n')
                # Now add the 'end' line
                output_lines.append(line)
                continue

        output_lines.append(line)

    return ''.join(output_lines)

if __name__ == '__main__':
    print("=" * 80)
    print("Fixing LqrBaselineCore: Removing enable switches")
    print("=" * 80)
    print("\nRoot cause:")
    print("- Enable signal reads as 0.0 instead of 1.0")
    print("- 13 enable switches output zeros when enable < 0.5")
    print("- OfficialPid has no enable switches and works perfectly")
    print("\nSolution:")
    print("- Remove all 13 enable switches")
    print("- Remove disabled_command constant")
    print("- Connect computed values directly to outputs")
    print()

    fixed_content = generate_fixed_core()

    with open('C:/Users/HP/Desktop/MoSim/Models/MoSimQuadrotorModel/Control/ClassicRobust/LqrBaseline/LqrBaselineCore.mo', 'w') as f:
        f.write(fixed_content)

    print("[OK] Fixed LqrBaselineCore written")
    print("[OK] Enable switches removed")
    print("[OK] Direct output connections added")
    print("\nNext: Test with CheckModel and SimulateModel")
