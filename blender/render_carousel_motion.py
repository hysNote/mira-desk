"""Render the actual rotating photo carrier, leaving crown/pedestal stationary."""
import bpy,sys,json,math,os,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent))
from kit import MATS
from upstream_render import render_pass,override_mat
s=bpy.context.scene;out=ROOT/'build/carousel-motion';out.mkdir(exist_ok=True)
source_key=hashlib.sha256(Path(bpy.data.filepath).read_bytes()+Path(__file__).read_bytes()).hexdigest()
# Reconnect the three registered material outputs from the saved native scene.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    nodes=mat.node_tree.nodes
    if all(nodes.get(name) for name in ['Principled BSDF','Emission','Emission.001','Material Output']):
        MATS[mat.name]={'mat':mat,'out':nodes['Material Output'],'beauty':nodes['Principled BSDF'],'albedo':nodes['Emission'],'emit':nodes['Emission.001']}
prefixes=('carousel hanging rod','carousel photo hook','carousel photo frame','carousel photo recess','carousel hanging photograph','carousel photo caption')
moving=[o for o in s.objects if o.name.startswith(prefixes)]
assert len(moving)==24,len(moving)
pivot=Vector((-1.435,.31,.75));initial={o.name:o.matrix_world.copy() for o in moving}
frames=25
# Keep every changing photo, its occlusion and nearby shadow within one patch.
coords=[]
for angle in [0,math.pi/4,math.pi/2]:
    transform=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)
    for ob in moving:
        for corner in ob.bound_box:
            p=world_to_camera_view(s,s.camera,transform@initial[ob.name]@Vector(corner));coords.append((p.x*1920,(1-p.y)*1080))
x0=max(0,math.floor(min(p[0] for p in coords))-28);x1=min(1920,math.ceil(max(p[0] for p in coords))+28)
y0=max(0,math.floor(min(p[1] for p in coords))-28);y1=min(1080,math.ceil(max(p[1] for p in coords))+28)
# Pixel-aligned crop; upper bound is exclusive.
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/1920;s.render.border_max_x=x1/1920
s.render.border_min_y=(1080-y1)/1080;s.render.border_max_y=(1080-y0)/1080
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
meta={'frames':frames,'angle_degrees':90,'duration_ms':2900,'crop':[x0,y0,x1,y1],'canvas':[1920,1080],'moving_objects':[o.name for o in moving],'pivot':list(pivot),'stationary':['canopy','finial','central column','pedestal']}
(out/'manifest.json').write_text(json.dumps(meta,indent=2))
clay=override_mat('clay');normal=override_mat('normal');depth=override_mat('depth');ids=override_mat('id')
for f in range(frames):
    directory=out/f'{f:02d}';directory.mkdir(exist_ok=True)
    if (directory/'ready').exists() and (directory/'ready').read_text()==source_key:continue
    angle=f/(frames-1)*math.pi/2
    transform=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot)
    for ob in moving:ob.matrix_world=transform@initial[ob.name]
    bpy.context.view_layer.update()
    render_pass(s,'beauty',str(directory),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=48,transform='AgX',denoise=True)
    render_pass(s,'albedo',str(directory),mode='albedo',samples=8)
    render_pass(s,'id',str(directory),override=ids,samples=1,box_filter=True)
    render_pass(s,'normal',str(directory),override=normal,samples=8,transform='Raw')
    render_pass(s,'depth',str(directory),override=depth,samples=8,transform='Raw',depth='16')
    for group in ['sun','sky']:
        render_pass(s,'light_'+group,str(directory),mode='beauty',override=clay,lights=(group,),world=('#cfeaff',.12) if group=='sky' else ('#000000',0),samples=24,transform='Raw',fmt='OPEN_EXR',depth='16',denoise=True)
    (directory/'ready').write_text(source_key)
    print('CAROUSEL_FRAME',f,flush=True)
# Save a separate inspectable native animation; do not overwrite the still room.
carrier=bpy.data.objects.new('Carousel rotating photo carrier',None)
s.collection.objects.link(carrier);carrier.location=pivot
bpy.context.view_layer.update()
for ob in moving:
    ob.animation_data_clear();ob.parent=carrier
    ob.matrix_parent_inverse=carrier.matrix_world.inverted()
    ob.matrix_world=initial[ob.name]
carrier.rotation_euler.z=0;carrier.keyframe_insert('rotation_euler',frame=1)
carrier.rotation_euler.z=math.pi/2;carrier.keyframe_insert('rotation_euler',frame=73)
s.frame_start=1;s.frame_end=73;s.render.fps=25;s.frame_set(1)
s.render.use_border=False;s.render.use_crop_to_border=False
bpy.context.view_layer.material_override=None
from kit import set_mode
set_mode('beauty')
for ob in s.objects:
    if ob.type=='LIGHT':ob.hide_render=False
s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'carousel-motion.blend'))
print('CAROUSEL_MOTION_READY',flush=True)
