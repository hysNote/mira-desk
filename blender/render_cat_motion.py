"""Bake the rig at 12 fps, with native room occlusion and contact shadows."""
import sys,json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent))
from kit import MATS,set_mode
from upstream_render import render_pass,override_mat
from cat_model import END,FPS
s=bpy.context.scene;out=ROOT/'build/cat-motion';frames=list(range(1,END,2))+[END]
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    n=mat.node_tree.nodes
    if all(n.get(k) for k in ['Principled BSDF','Emission','Emission.001','Material Output']):MATS[mat.name]={'mat':mat,'out':n['Material Output'],'beauty':n['Principled BSDF'],'albedo':n['Emission'],'emit':n['Emission.001']}
rig=bpy.data.objects['American shorthair • pet and stretch'];cats=[o for o in s.objects if o.name.startswith('ASH ') and o.type=='MESH']
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
coords=[]
for f in [1,41,80,121,174]:
    s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get()
    for ob in cats:
        evaluated=ob.evaluated_get(deps)
        for p in evaluated.data.vertices:
            v=world_to_camera_view(s,s.camera,ob.matrix_world@p.co);coords.append((v.x*1920,(1-v.y)*1080))
# Include old cat silhouette and contact shadow; crops remain well away from the window.
old=json.loads((ROOT/'site/assets/scene.json').read_text())['hots']['cat']['bbox']
x0=max(0,math.floor(min(min(p[0] for p in coords),old[0]))-35);x1=min(1920,math.ceil(max(max(p[0] for p in coords),old[2]))+35)
y0=max(0,math.floor(min(min(p[1] for p in coords),old[1]))-35);y1=min(1080,math.ceil(max(max(p[1] for p in coords),old[3]))+35)
meta={'frames':len(frames),'source_frames':frames,'duration_ms':(END-1)/FPS*1000,'crop':[x0,y0,x1,y1],'canvas':[1920,1080],'width':x1-x0,'height':y1-y0,'columns':11,'fps':12,'coat':'untextured clay','bone_count':len(rig.pose.bones)}
(out/'manifest.json').write_text(json.dumps(meta,indent=2))
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.use_border=s.render.use_crop_to_border=True;s.render.border_min_x=x0/1920;s.render.border_max_x=x1/1920;s.render.border_min_y=(1080-y1)/1080;s.render.border_max_y=(1080-y0)/1080
desk_camera=s.camera;close_camera=bpy.data.objects['Cat motion close view']
s.frame_set(1);s.render.use_border=s.render.use_crop_to_border=False
render_pass(s,'desk-idle',str(out),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=48,transform='AgX',denoise=True)
s.render.use_border=s.render.use_crop_to_border=True
stamp=hashlib.sha256(Path(bpy.data.filepath).read_bytes()+Path(__file__).read_bytes()).hexdigest()
for index,f in enumerate(frames):
    directory=out/f'{index:03d}';directory.mkdir(exist_ok=True)
    if (directory/'ready').exists() and (directory/'ready').read_text()==stamp:continue
    s.frame_set(f)
    render_pass(s,'beauty',str(directory),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=24,transform='AgX',denoise=True)
    s.camera=close_camera;s.render.use_border=s.render.use_crop_to_border=False;s.render.resolution_x=800;s.render.resolution_y=650
    render_pass(s,'close',str(directory),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=24,transform='AgX',denoise=True)
    s.camera=desk_camera;s.render.use_border=s.render.use_crop_to_border=True;s.render.resolution_x=1920;s.render.resolution_y=1080
    (directory/'ready').write_text(stamp);print('CAT_FRAME',index,'/',len(frames),flush=True)
print('CAT_BAKE_READY',flush=True)
