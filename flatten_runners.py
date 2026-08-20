#!/usr/bin/env python3
"""Flatten runner structure: remove Core layer, directly instantiate Graphical Controller"""

import re

runners = [
    {
        'path': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1IndiGraphicalRunner.mo',
        'old_import': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi.AwffL1IndiCore core',
        'new_import': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi.AwffL1IndiGraphicalController controller',
        'old_var': 'core',
        'new_var': 'controller'
    },
    {
        'path': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1ResidualGraphicalRunner.mo',
        'old_import': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual.AwffL1ResidualCore core',
        'new_import': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual.AwffL1ResidualGraphicalController controller',
        'old_var': 'core',
        'new_var': 'controller'
    },
    {
        'path': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/LinearMpcL1IndiGraphicalRunner.mo',
        'old_import': 'MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi.LinearMpcL1IndiCore core',
        'new_import': 'MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi.LinearMpcL1IndiGraphicalController controller',
        'old_var': 'core',
        'new_var': 'controller'
    }
]

for runner in runners:
    with open(runner['path'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the import line
    content = content.replace(runner['old_import'], runner['new_import'])
    
    # Replace all occurrences of old_var with new_var (e.g., core.x_error -> controller.x_error)
    content = re.sub(r'\b' + runner['old_var'] + r'\.', runner['new_var'] + '.', content)
    
    with open(runner['path'], 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Flattened: {runner['path'].split('/')[-1]}")

print("\nStep 2 complete: Runners now directly instantiate Graphical Controllers")
