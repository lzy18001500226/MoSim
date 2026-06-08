import bpy, json, math
from pathlib import Path
from mathutils import Vector
PROJECT_ROOT = Path(r'C:/Users/HP/Desktop/MoSim')
BLEND = PROJECT_ROOT / 'UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
rows=[]
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    mats=[]
    for slot in obj.material_slots:
        mat=slot.material
        if not mat:
            continue
        color=list(mat.diffuse_color)
        r,g,b,a=color
        mx=max(r,g,b); mn=min(r,g,b)
        sat=0.0 if mx <= 1e-9 else (mx-mn)/mx
        lum=0.2126*r+0.7152*g+0.0722*b
        mats.append({'name':mat.name,'diffuse':[round(v,4) for v in color],'sat':round(sat,4),'lum':round(lum,4),'alpha':round(a,4),'blend':mat.blend_method})
    if mats:
        greyish=any(m['sat'] < 0.12 and 0.18 < m['lum'] < 0.82 and m['alpha'] > 0.85 for m in mats)
        rows.append({'object':obj.name,'materials':mats,'greyish_risk':greyish})
summary={
 'mesh_count':len(rows),
 'greyish_risk_count':sum(1 for r in rows if r['greyish_risk']),
 'material_names':sorted({m['name'] for r in rows for m in r['materials']})[:300],
 'focus':[]
}
keys=['MID360','FRONT_CAMERA','BOTTOM_CAMERA','Sensor TF Mini','TF Mini','PROTECTIVE_RING','LAND_GEAR','TriBlade','BATTERY','YUNDRONE_4S1P','N150','ESC_SPEEDYBEE','CABLE','WIRE','A_USB','HDMI','NGFF','PJ311']
for r in rows:
    upper=r['object'].upper()
    if any(k.upper() in upper for k in keys):
        summary['focus'].append(r)
print(json.dumps(summary, ensure_ascii=False, indent=2)[:16000])
