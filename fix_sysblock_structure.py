#!/usr/bin/env python3
"""Fix Sysblock file structure: extends must come BEFORE imports"""

import re

files = [
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_L1ResidualControllerGraphical_Sysblock.mo',
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_INDIControllerGraphical_Sysblock.mo',
    'Models/MoSimQuadrotorModel/Control/Sysblocks/AWFF_LinearMPCControllerGraphical_Sysblock.mo'
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the model declaration line
    model_match = re.search(r'(within .*?;\nmodel \w+.*?".*?")\n', content)
    if not model_match:
        print(f"ERROR: Could not find model declaration in {filepath}")
        continue
    
    model_decl = model_match.group(1)
    
    # Extract the parts after model declaration
    rest = content[model_match.end():]
    
    # Find imports and extends
    import_lines = []
    extends_line = None
    other_lines = []
    
    for line in rest.split('\n'):
        if line.strip().startswith('import '):
            import_lines.append(line)
        elif line.strip().startswith('extends '):
            extends_line = line
        elif line.strip() and not line.strip().startswith('annotation'):
            break
        else:
            other_lines.append(line)
    
    # Reconstruct: model -> extends -> imports -> annotation
    new_header = model_decl + '\n'
    if extends_line:
        new_header += '  ' + extends_line.strip() + '\n'
    for imp in import_lines:
        new_header += '  ' + imp.strip() + '\n'
    
    # Find annotation block
    annot_match = re.search(r'(annotation\(__MWORKS.*?\)\);)', content, re.DOTALL)
    if annot_match:
        new_header += '  ' + annot_match.group(1) + '\n'
    
    # Rebuild file: header + everything after annotation
    annot_end = content.find('\n\n', annot_match.end())
    remaining = content[annot_end:]
    
    new_content = new_header + remaining
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed: {filepath}")

print("\nDone. Files now follow correct Modelica structure:")
print("1. within + model declaration")
print("2. extends ModelWorkspace")
print("3. import statements")
print("4. annotation")
print("5. ports and components")
