#!/usr/bin/env python3
"""Restructure: move Graphical Sysblocks to family folders and flatten runner structure"""

import os
import shutil

# Step 1: Move files to correct locations and update within declarations
moves = [
    {
        'src': 'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_L1ResidualControllerGraphical_Sysblock.mo',
        'dst': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Residual/AwffL1ResidualGraphicalController.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Sysblocks;',
        'new_within': 'within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual;',
        'old_model': 'model AWFF_L1ResidualControllerGraphical_Sysblock',
        'new_model': 'model AwffL1ResidualGraphicalController'
    },
    {
        'src': 'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_INDIControllerGraphical_Sysblock.mo',
        'dst': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Indi/AwffL1IndiGraphicalController.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Sysblocks;',
        'new_within': 'within MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi;',
        'old_model': 'model AWFF_INDIControllerGraphical_Sysblock',
        'new_model': 'model AwffL1IndiGraphicalController'
    },
    {
        'src': 'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_LinearMPCControllerGraphical_Sysblock.mo',
        'dst': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/LinearMpcL1Indi/LinearMpcL1IndiGraphicalController.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Sysblocks;',
        'new_within': 'within MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi;',
        'old_model': 'model AWFF_LinearMPCControllerGraphical_Sysblock',
        'new_model': 'model LinearMpcL1IndiGraphicalController'
    }
]

for move in moves:
    with open(move['src'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update within and model name
    content = content.replace(move['old_within'], move['new_within'])
    content = content.replace(move['old_model'], move['new_model'])
    # Also update the end statement
    old_end = 'end ' + move['old_model'].split()[1] + ';'
    new_end = 'end ' + move['new_model'].split()[1] + ';'
    content = content.replace(old_end, new_end)
    
    with open(move['dst'], 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Moved and updated: {os.path.basename(move['dst'])}")

print("\nStep 1 complete: Files moved to family folders")
