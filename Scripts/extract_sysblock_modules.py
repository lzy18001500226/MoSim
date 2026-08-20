#!/usr/bin/env python3
"""Extract complete sub-module definitions from AWFF_InnovationGraphicalControllers.mo"""

import re

def extract_module(source_file, module_name, start_pattern, end_pattern):
    """Extract a complete module definition from source file"""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find module start
    start_match = re.search(start_pattern, content)
    if not start_match:
        raise ValueError(f"Could not find start pattern for {module_name}")

    start_pos = start_match.start()

    # Find module end - look for "end ModuleName;"
    end_match = re.search(end_pattern, content[start_pos:])
    if not end_match:
        raise ValueError(f"Could not find end pattern for {module_name}")

    end_pos = start_pos + end_match.end()

    return content[start_pos:end_pos]

# Source file
source = 'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_InnovationGraphicalControllers.mo'

# Extract L1ResidualOuterLoopBlock
l1_module = extract_module(
    source,
    'L1ResidualOuterLoopBlock',
    r'  model L1ResidualOuterLoopBlock\n',
    r'  end L1ResidualOuterLoopBlock;'
)

# Extract PIDAttitudeInnerLoopBlock
pid_module = extract_module(
    source,
    'PIDAttitudeInnerLoopBlock',
    r'  model PIDAttitudeInnerLoopBlock\n',
    r'  end PIDAttitudeInnerLoopBlock;'
)

# Extract INDIAttitudeInnerLoopBlock
indi_module = extract_module(
    source,
    'INDIAttitudeInnerLoopBlock',
    r'  model INDIAttitudeInnerLoopBlock\n',
    r'  end INDIAttitudeInnerLoopBlock;'
)

# Extract MotorMixerBlock
mixer_module = extract_module(
    source,
    'MotorMixerBlock',
    r'  model MotorMixerBlock\n',
    r'  end MotorMixerBlock;'
)

# Extract LinearMPCOuterLoopBlock
mpc_module = extract_module(
    source,
    'LinearMPCOuterLoopBlock',
    r'  model LinearMPCOuterLoopBlock\n',
    r'  end LinearMPCOuterLoopBlock;'
)

print("Successfully extracted all modules")
print(f"L1ResidualOuterLoopBlock: {len(l1_module)} chars")
print(f"PIDAttitudeInnerLoopBlock: {len(pid_module)} chars")
print(f"INDIAttitudeInnerLoopBlock: {len(indi_module)} chars")
print(f"MotorMixerBlock: {len(mixer_module)} chars")
print(f"LinearMPCOuterLoopBlock: {len(mpc_module)} chars")

# Save extracted modules
with open('Scripts/extracted_l1_module.txt', 'w', encoding='utf-8') as f:
    f.write(l1_module)
with open('Scripts/extracted_pid_module.txt', 'w', encoding='utf-8') as f:
    f.write(pid_module)
with open('Scripts/extracted_indi_module.txt', 'w', encoding='utf-8') as f:
    f.write(indi_module)
with open('Scripts/extracted_mixer_module.txt', 'w', encoding='utf-8') as f:
    f.write(mixer_module)
with open('Scripts/extracted_mpc_module.txt', 'w', encoding='utf-8') as f:
    f.write(mpc_module)
