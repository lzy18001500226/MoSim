import bpy, json
from pathlib import Path
BLEND = Path(r'C:/Users/HP/Desktop/MoSim/UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend')
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
keys=['PROTECTIVE_RING','LAND_GEAR','MID360_PROTECT_ARC','MAIN_STRUCTURE','TOP_PANNEL','TriBlade','FRONT_CAMERA','RANGING_LIDAR']
rows=[]
for obj in bpy.context.scene.objects:
    up=obj.name.upper()
    if obj.type=='MESH' and any(k in up for k in keys):
        mats=[]
        for slot in obj.material_slots:
            mat=slot.material
            if not mat: continue
            bsdf = next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'), None) if mat.use_nodes else None
            inputs={}
            if bsdf:
                for name in ['Base Color','Alpha','Roughness','Metallic','Specular IOR Level','Specular','Coat Weight','Clearcoat','Transmission Weight','Transmission']:
                    if name in bsdf.inputs:
                        val=bsdf.inputs[name].default_value
                        try:
                            val=list(val)
                        except TypeError:
                            pass
                        inputs[name]=val
            mats.append({'name':mat.name,'diffuse':[round(v,3) for v in mat.diffuse_color],'blend':mat.blend_method,'use_screen_refraction':getattr(mat,'use_screen_refraction',None),'inputs':inputs})
        rows.append({'object':obj.name,'materials':mats})
print(json.dumps(rows[:250], ensure_ascii=False, indent=2)[:24000])
