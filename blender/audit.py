import bpy, json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
assert s.camera is not None
assert bpy.context.view_layer.material_override is None
keys={o.get('hot') for o in bpy.data.objects if o.get('hot')}
assert keys=={'about','resume','awards','photos','life','travel','cat','notebook'}
images=[im for im in bpy.data.images if im.source=='FILE']
assert all(im.packed_file for im in images)
report={'hotspots':sorted(keys),'meshes':sum(o.type=='MESH' for o in bpy.data.objects),'packed_images':len(images),'camera':s.camera.name,'material_override':None}
def z_bounds(ob):
    z=[(ob.matrix_world@Vector(v)).z for v in ob.bound_box]
    return min(z),max(z)
feet=[o for o in s.objects if o.name.startswith('desk grounded foot')]
legs=[o for o in s.objects if o.name.startswith('desk support leg')]
assert len(feet)==len(legs)==4,'Four physical supports are required'
rug_top=z_bounds(bpy.data.objects['room woven rug'])[1]
underside=z_bounds(bpy.data.objects['desktop'])[0]
for foot,leg in zip(sorted(feet,key=lambda o:o.name),sorted(legs,key=lambda o:o.name)):
    assert abs(z_bounds(foot)[0]-rug_top)<.0001,'Floating desk foot'
    assert abs(z_bounds(foot)[1]-z_bounds(leg)[0])<.0001,'Gap above foot'
    assert abs(z_bounds(leg)[1]-underside)<.0001,'Leg does not meet desktop'
assert len([o for o in s.objects if o.name.startswith('room side wall')])==2
assert bpy.data.objects.get('Room overview') is not None
report['room']={'feet':4,'rug_top':round(rug_top,4),'desktop_underside':round(underside,4),'support_contacts_verified':True}
Path(bpy.data.filepath).with_name('model-audit.json').write_text(json.dumps(report,indent=2))
print('MODEL_AUDIT',json.dumps(report))
