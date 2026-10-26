"""Check contact targets, cycle closure and the absence of coat image textures."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent))
from cat_model import pose,FPS,END,ORIGIN
s=bpy.context.scene;rig=bpy.data.objects['American shorthair • pet and stretch'];records=[];start={}
for f in [1,20,41,60,80,96,121,145,174]:
    s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();joints,_=pose((f-1)/FPS)
    errors=[]
    for name,(a,b) in joints.items():
        bone=rig.pose.bones[name];errors.extend([(bone.head-a).length,(bone.tail-b).length])
    assert max(errors)<.0001,(f,max(errors),[(n,(rig.pose.bones[n].head-a).length,(rig.pose.bones[n].tail-b).length) for n,(a,b) in joints.items() if (rig.pose.bones[n].head-a).length>.0001 or (rig.pose.bones[n].tail-b).length>.0001])
    lows=[]
    for ob in s.objects:
        if not ob.name.startswith('ASH ') or ob.type!='MESH':continue
        evaluated=ob.evaluated_get(deps);points=[ob.matrix_world@v.co for v in evaluated.data.vertices];lows.append(min(p.z for p in points))
        if f==1:start[ob.name]=[p.copy() for p in points]
        if f==END:assert max((a-b).length for a,b in zip(start[ob.name],points))<.0001,ob.name
        for mat in ob.data.materials:
            assert not any(n.type=='TEX_IMAGE' for n in mat.node_tree.nodes),mat.name
    assert min(lows)>.735,(f,min(lows))
    records.append({'frame':f,'joint_error':max(errors),'mesh_min_z':min(lows),'front_paws':[list(joints[n+'Paw'][0]) for n in ['frontL','frontR']]})
(ROOT/'build/cat-motion/audit.json').write_text(json.dumps({'bone_count':len(rig.pose.bones),'cycle_closes':True,'coat_image_textures':0,'samples':records},indent=2))
print('CAT_AUDIT_PASSED',flush=True)
