"""Compare normalized homepage framing to the upstream 23 mm reference camera."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

s=bpy.context.scene
actual=s.camera
reference_data=bpy.data.cameras.new('audit reference')
reference=bpy.data.objects.new('audit reference',reference_data)
s.collection.objects.link(reference)
reference.location=(0,-1.70,2.56)
target=Vector((.05,.14,1.06))
reference.rotation_euler=(target-reference.location).to_track_quat('-Z','Y').to_euler()
reference_data.lens=23
reference_data.sensor_width=36
bpy.context.view_layer.update()
scale=3.8/2.5
anchors=[]
for name,x,y,z in [('rear left',-1.25,.52,.75),('rear right',1.25,.52,.75),
                    ('front left',-1.25,-.52,.75),('front right',1.25,-.52,.75),
                    ('floor center',0,-.1,0)]:
    p=Vector((x,y,z))
    mapped=Vector((0,-.02,.75))+scale*(p-Vector((0,0,.75)))
    a=world_to_camera_view(s,reference,p)
    b=world_to_camera_view(s,actual,mapped)
    error=math.hypot((a.x-b.x)*s.render.resolution_x,(a.y-b.y)*s.render.resolution_y)
    anchors.append({'name':name,'reference_uv':[a.x,1-a.y],
                    'mira_uv':[b.x,1-b.y],'error_pixels':error})
assert max(a['error_pixels'] for a in anchors)<.02
assert abs(actual.data.lens-23)<1e-6
assert abs(actual.data.sensor_width-36)<1e-6
assert s.render.resolution_x*9==s.render.resolution_y*16
delta=target-reference.location
report={'reference':'../blender/layout.py:build_lights_and_camera',
        'lens_mm':actual.data.lens,'pitch_down_degrees':math.degrees(math.atan2(-delta.z,math.hypot(delta.x,delta.y))),
        'desk_scale':scale,'render_size':[s.render.resolution_x,s.render.resolution_y],
        'camera_position':list(actual.location),'anchors':anchors}
Path(bpy.data.filepath).with_name('camera-audit.json').write_text(json.dumps(report,indent=2))
bpy.data.objects.remove(reference,do_unlink=True)
bpy.data.cameras.remove(reference_data)
print('CAMERA_AUDIT',json.dumps(report))
