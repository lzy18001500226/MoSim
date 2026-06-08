import bpy, json
from pathlib import Path
BLEND = Path(r'C:/Users/HP/Desktop/MoSim/UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend')
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
rows=[]
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for slot in obj.material_slots:
        mat=slot.material
        if not mat: continue
        r,g,b,a=mat.diffuse_color
        lum=0.2126*r+0.7152*g+0.0722*b
        mx=max(r,g,b); mn=min(r,g,b); sat=0 if mx<=1e-9 else (mx-mn)/mx
        if lum > 0.70 and a > 0.85:
            rows.append({'object':obj.name,'material':mat.name,'diffuse':[round(v,3) for v in mat.diffuse_color],'lum':round(lum,3),'sat':round(sat,3)})
print(json.dumps({'high_luminance_count':len(rows),'sample':rows[:200]}, ensure_ascii=False, indent=2))
