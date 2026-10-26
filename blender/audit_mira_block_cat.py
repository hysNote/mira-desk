import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/mira-block-cat'
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');meshes=[o for o in s.objects if o.parent==rig and o.type=='MESH']
minimum=1;worst=None;support=[];first=None;last=None;length_error=0
tail_outside=[];tail_root_clearance=10;max_step=0;step_at=None;previous={};joint_gap=0
def inside(tree,point):
    direction=Vector((.812,.317,.49)).normalized();origin=point.copy();hits=0
    for _ in range(20):
        pos,normal,index,distance=tree.ray_cast(origin,direction)
        if pos is None:break
        hits+=1;origin=pos+direction*.00001
    return hits%2==1
for f in range(1,242):
    s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    matrices=[list(v for row in p.matrix for v in row) for p in rig.pose.bones]
    if f==1:first=matrices
    if f==241:last=matrices
    support.append(tuple(rig.pose.bones['PawR'].head))
    body=bpy.data.objects['Soft block body'].evaluated_get(deps)
    tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
    tail=bpy.data.objects['Soft continuous curled tail'].evaluated_get(deps)
    root=[tail.matrix_world@v.co for v in list(tail.data.vertices)[:12]]
    if not all(inside(tree,p) for p in root):tail_outside.append(f)
    tail_root_clearance=min(tail_root_clearance,min(tree.find_nearest(p)[3] for p in root))
    for side in ['L','R']:
        joint_gap=max(joint_gap,(rig.pose.bones['Arm'+side].tail-rig.pose.bones['Forearm'+side].head).length,(rig.pose.bones['Forearm'+side].tail-rig.pose.bones['Paw'+side].head).length)
    for name in ['ArmL','ArmR','ForearmL','ForearmR']:
        p=rig.pose.bones[name];length_error=max(length_error,abs((p.tail-p.head).length-p.bone.length))
    for o in meshes:
        ev=o.evaluated_get(deps)
        low=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
        if low<minimum:minimum=low;worst=(f,o.name)
        if o.name in ['Soft block body','Soft continuous curled tail','Continuous foreleg L','Continuous foreleg R']:
            points=[ev.matrix_world@v.co for v in ev.data.vertices]
            if o.name in previous:
                step=max((a-b).length for a,b in zip(points,previous[o.name]))
                if step>max_step:max_step=step;step_at=[f,o.name]
            previous[o.name]=points
end_error=max(abs(a-b) for ra,rb in zip(first,last) for a,b in zip(ra,rb))
support_drift=max(max(abs(p[i]-support[0][i]) for i in range(3)) for p in support)
report={'frames':241,'min_vertex_z':minimum,'lowest':worst,'right_support_paw_drift':support_drift,'forelimb_length_error':length_error,'rest_endpoint_matrix_error':end_error,'tail_root_outside_frames':tail_outside,'tail_root_min_burial':tail_root_clearance,'max_adjacent_vertex_step':max_step,'max_step_at':step_at,'foreleg_joint_gap':joint_gap}
(out/('audit-before-tail.json' if '--baseline' in sys.argv else 'audit.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
assert minimum>-.01
assert support_drift<.0001 and length_error<.0001 and end_error<.0001
assert not tail_outside, 'Tail root must remain buried in the pelvis on every frame'
assert tail_root_clearance>.005
assert joint_gap<.0001 and max_step<.06
