import bpy, json
from pathlib import Path
from mathutils import Vector
BLEND = Path(r'C:/Users/HP/Desktop/MoSim/UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend')
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
rows=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    coords=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn=Vector((min(p.x for p in coords),min(p.y for p in coords),min(p.z for p in coords)))
    mx=Vector((max(p.x for p in coords),max(p.y for p in coords),max(p.z for p in coords)))
    center=(mn+mx)*0.5; size=mx-mn
    if center.y>0.045 or size.x*size.y>0.001 or any(k in obj.name.upper() for k in ['FRONT','RANGING','SENSOR TF','CAMERA','PROTECTIVE','LAND_GEAR','MID360_PROTECT']):
        mats=[]
        for slot in obj.material_slots:
            mat=slot.material
            if not mat: continue
            bsdf = next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'), None) if mat.use_nodes else None
            base=None; alpha=None; rough=None; spec=None; coat=None; trans=None
            if bsdf:
                def val(name):
                    if name in bsdf.inputs:
                        v=bsdf.inputs[name].default_value
                        try: return [round(float(x),3) for x in v]
                        except TypeError: return round(float(v),3)
                    return None
                base=val('Base Color'); alpha=val('Alpha'); rough=val('Roughness'); spec=val('Specular IOR Level') or val('Specular'); coat=val('Coat Weight') or val('Clearcoat'); trans=val('Transmission Weight') or val('Transmission')
            mats.append({'name':mat.name,'diffuse':[round(v,3) for v in mat.diffuse_color],'base':base,'alpha':alpha,'rough':rough,'spec':spec,'coat':coat,'trans':trans,'blend':mat.blend_method})
        rows.append({'object':obj.name,'center':[round(v,4) for v in center],'size':[round(v,4) for v in size],'area_xy':round(size.x*size.y,6),'mats':mats})
rows.sort(key=lambda r: r['area_xy'], reverse=True)
print(json.dumps(rows[:180], ensure_ascii=False, indent=2)[:40000])
