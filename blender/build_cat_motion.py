"""Build a separate editable cat study in the existing room; never overwrite the desk."""
import sys,json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent))
from kit import MATS,set_mode,lin
from upstream_render import render_pass
from cat_model import build_cat,ORIGIN,SCALE,FPS,END
out=ROOT/'build/cat-motion';out.mkdir(exist_ok=True)
s=bpy.context.scene
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    nodes=mat.node_tree.nodes
    if all(nodes.get(n) for n in ['Principled BSDF','Emission','Emission.001','Material Output']):MATS[mat.name]={'mat':mat,'out':nodes['Material Output'],'beauty':nodes['Principled BSDF'],'albedo':nodes['Emission'],'emit':nodes['Emission.001']}
old=[o for o in s.objects if o.get('hot')=='cat']
for ob in old:ob.hide_render=True;ob.hide_set(True)
rig,meshes=build_cat()
# Preserve existing object IDs; append cat names to the compositor lookup.
meta=json.loads((ROOT/'build/passes/scene.json').read_text())
for i,ob in enumerate(meshes):
    color=[16+(i%15)*16,80,80];ob.color=tuple(lin(v/255) for v in color)+(1,)
    meta['ids'].append({'object':ob.name,'color':color,'hot':'cat'})
(out/'scene.json').write_text(json.dumps(meta))
s.frame_start=1;s.frame_end=END;s.render.fps=FPS;s.frame_set(1)
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
s.render.resolution_x=1920;s.render.resolution_y=1080
set_mode('beauty');bpy.context.view_layer.material_override=None
for ob in s.objects:
    if ob.type=='LIGHT':ob.hide_render=False
s.view_settings.view_transform='AgX'
# A dedicated close camera makes the untextured sculpt and back line reviewable.
camd=bpy.data.cameras.new('Cat motion close view');cam=bpy.data.objects.new('Cat motion close view',camd);s.collection.objects.link(cam)
target=ORIGIN+Vector((.02,0,.28));cam.location=ORIGIN+Vector((1.25,-1.95,1.12));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=1.32
desk_camera=s.camera
bpy.ops.wm.save_as_mainfile(filepath=str(out/'american-shorthair-motion.blend'))
s.camera=cam;s.render.resolution_x=800;s.render.resolution_y=650
for f in [1,41,80,121,174]:
    s.frame_set(f);render_pass(s,f'pose-{f:03d}',str(out),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=32,transform='AgX',denoise=True)
print('CAT_STUDY_READY',flush=True)
