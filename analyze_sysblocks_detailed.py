#!/usr/bin/env python3
"""Detailed analysis of Sysblocks folder for reorganization"""

import os
from pathlib import Path

sysblocks_dir = Path('Models/MoSimQuadrotorModel/Control/Sysblocks')
files = [f.stem for f in sysblocks_dir.glob('*.mo') if f.stem != 'package']

print("=" * 80)
print("SYSBLOCKS REORGANIZATION PLAN")
print("=" * 80)

# Category 1: Equation versions -> Archive
equation_files = [f for f in files if 'Equation' in f]
print(f"\n[1] ARCHIVE - Equation versions ({len(equation_files)} files)")
print("    These are pure formula implementations, not needed for graphical workflow")
for eq in equation_files:
    print(f"    - {eq}.mo")

# Category 2: Graphical controllers that should move to family folders
graphical_controllers = [
    'AWFF_PidLinearEsoControllerGraphical_Sysblock',  # -> PidFamily or AwffControllers
    'PX4CTRL_Original_OuterLoop_Graphical_Sysblock',  # -> Px4Ctrl family
]
print(f"\n[2] MIGRATE - Graphical controllers ({len(graphical_controllers)} files)")
print("    These should move to their controller family folders")
for gr in graphical_controllers:
    if gr in files:
        print(f"    - {gr}.mo")

# Category 3: Sub-modules used by composite controllers
submodules = [
    'AWFF_AttitudeInnerLoop_Sysblock',
    'AWFF_MotorMixer_Sysblock', 
    'AWFF_PositionOuterLoop_Sysblock',
    'AWFF_InnovationGraphicalControllers',  # Contains L1, PID, INDI, MPC, Mixer modules
]
print(f"\n[3] KEEP AS SHARED - Sub-modules ({len(submodules)} files)")
print("    These are building blocks used by multiple controllers")
for sub in submodules:
    if sub in files:
        print(f"    - {sub}.mo")

# Category 4: Complete composite controllers (reference examples)
composites = [
    'AWFF_FullController_Sysblock',  # Complete 3-layer example
    'AWFF_FullControllerFlatGraphical_Sysblock',  # Flat version
]
print(f"\n[4] KEEP AS REFERENCE - Composite examples ({len(composites)} files)")
print("    These are complete working examples")
for comp in composites:
    if comp in files:
        print(f"    - {comp}.mo")

# Category 5: Special purpose / Testing
special = [
    'AWFF_FullController_Sysblock_SIL_Constant',
    'AWFF_PID_Sysblock_Demo',
    'AWFF_PID_Sysblock_Demo_SIL_Constant',
    'MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL',
    'PX4CTRL_Core_MinimalLinear_Probe_Sysblock',
    'PX4CTRL_TemplateCopy_Probe_Sysblock',
]
print(f"\n[5] REVIEW - Testing/Demo files ({len(special)} files)")
print("    Need to check if still needed")
for sp in special:
    if sp in files:
        print(f"    - {sp}.mo")

# Category 6: Advanced controllers (might have their own families)
advanced = [
    'AWFF_LinearMPCMultiFaultAllocationController_Sysblock',
    'AWFF_LinearMPCOnlineFaultAllocationController_Sysblock',
    'AWFF_QPNMPCSafetyController_Sysblock',
]
print(f"\n[6] MIGRATE - Advanced controllers ({len(advanced)} files)")
print("    Should move to Optimization family or keep in Sysblocks")
for adv in advanced:
    if adv in files:
        print(f"    - {adv}.mo")

# Check references
print("\n" + "=" * 80)
print("ACTIVE REFERENCES (files that ARE being used):")
print("=" * 80)

references = {
    'AWFF_QPNMPCSafetyController_Sysblock': 'Control/IntegratedChains/QpNmpcL1IndiCbf/QpNmpcL1IndiCbfCore.mo',
    'AWFF_PidLinearEsoControllerGraphical_Sysblock': 'Experiment/AwffControllers/PidAwffLinearEsoGraphicalRunner.mo',
    'AWFF_FullController_Sysblock': 'Experiment/Templates/IntegratedChains/FixedAwffPid.mo',
}

for file, ref_location in references.items():
    print(f"\n{file}:")
    print(f"  Referenced by: {ref_location}")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("""
1. Archive all Equation files (11 files) to E:/MoSim_Archive/deprecated_equation_sysblocks/
2. Keep shared sub-modules in Sysblocks temporarily (AWFF_InnovationGraphicalControllers.mo, etc.)
3. Migrate 3 actively-used graphical controllers to their family folders:
   - AWFF_QPNMPCSafetyController -> Optimization/QpNmpcL1IndiCbf/
   - AWFF_PidLinearEsoControllerGraphical -> PidFamily/ or AwffControllers/
   - AWFF_FullController -> Keep as shared reference example
4. Delete or archive Demo/Test files after verification
5. Eventually consolidate shared sub-modules into a SharedComponents folder

Want me to execute this plan?
""")

