#!/usr/bin/env python3
"""Verify the restructuring is complete"""

import os

print("=" * 60)
print("RESTRUCTURING VERIFICATION")
print("=" * 60)

# Check new controller files exist
controllers = [
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Residual/AwffL1ResidualGraphicalController.mo',
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Indi/AwffL1IndiGraphicalController.mo',
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/LinearMpcL1Indi/LinearMpcL1IndiGraphicalController.mo'
]

print("\n✓ New Graphical Controllers in family folders:")
for ctrl in controllers:
    size = os.path.getsize(ctrl) // 1024
    print(f"  - {ctrl.split('/')[-1]} ({size}KB)")

# Check runners are updated
runners = [
    'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1IndiGraphicalRunner.mo',
    'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1ResidualGraphicalRunner.mo',
    'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/LinearMpcL1IndiGraphicalRunner.mo'
]

print("\n✓ Flattened Runners (Core layer removed):")
for runner in runners:
    with open(runner, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'controller' in content and 'Core core' not in content:
            print(f"  - {runner.split('/')[-1]} → now uses 'controller' directly")
        else:
            print(f"  ✗ {runner.split('/')[-1]} → ERROR: still references Core")

# Check old files are deleted
old_files = [
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_L1ResidualControllerGraphical_Sysblock.mo',
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_INDIControllerGraphical_Sysblock.mo',
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_LinearMPCControllerGraphical_Sysblock.mo',
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Residual/AwffL1ResidualCore.mo',
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Indi/AwffL1IndiCore.mo',
    'Models/MoSimQuadrotorModel/Control/IntegratedChains/LinearMpcL1Indi/LinearMpcL1IndiCore.mo'
]

print("\n✓ Obsolete files deleted:")
all_deleted = True
for old in old_files:
    if not os.path.exists(old):
        print(f"  - {old.split('/')[-1]} (deleted)")
    else:
        print(f"  ✗ {old.split('/')[-1]} (still exists)")
        all_deleted = False

print("\n" + "=" * 60)
if all_deleted:
    print("✓ RESTRUCTURING COMPLETE")
    print("\nNext steps:")
    print("1. Reload MoSimQuadrotorModel package in Sysplorer")
    print("2. Open any runner: AwffL1IndiGraphicalRunner")
    print("3. Double-click 'controller' block (not 'core')")
    print("4. You should see: position_loop → attitude_loop → motor_mixer")
else:
    print("⚠ RESTRUCTURING INCOMPLETE - check errors above")
print("=" * 60)
