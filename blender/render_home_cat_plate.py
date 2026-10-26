"""Remove the old still cat in a bounded native room render; preserve accepted assets."""
import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent))
from kit import MATS
from upstream_render import render_pass,override_mat
s=bpy.context.scene;out=ROOT/'build/home-cat';out.mkdir(exist_ok=True)
for m in bpy.data.materials:
    if not m.use_nodes:continue
    n=m.node_tree.nodes
    if all(n.get(k) for k in ['Principled BSDF','Emission','Emission.001','Material Output']):MATS[m.name]={'mat':m,'out':n['Material Output'],'beauty':n['Principled BSDF'],'albedo':n['Emission'],'emit':n['Emission.001']}
meta=json.loads((ROOT/'site/assets/scene.json').read_text())
x0,y0,x1,y1=meta['hots']['cat']['bbox']
x0=max(0,x0-65);y0=max(0,y0-40);x1=min(1920,x1+110);y1=min(1080,y1+60)
crop=[x0,y0,x1,y1];(out/'crop.json').write_text(json.dumps(crop))
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.use_border=s.render.use_crop_to_border=True
s.render.border_min_x=x0/1920;s.render.border_max_x=x1/1920;s.render.border_min_y=(1080-y1)/1080;s.render.border_max_y=(1080-y0)/1080
try:
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
    for d in p.devices:d.use=d.type=='OPTIX'
    if any(d.type=='OPTIX' for d in p.devices):s.cycles.device='GPU'
except Exception:pass
render_pass(s,'before',str(out),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=48,transform='AgX',denoise=True)
for o in s.objects:
    if o.get('hot')=='cat':o.hide_render=True
render_pass(s,'beauty',str(out),mode='beauty',lights=('sun','sky'),world=('#cfeaff',.12),samples=48,transform='AgX',denoise=True)
render_pass(s,'albedo',str(out),mode='albedo',samples=8)
render_pass(s,'id',str(out),override=override_mat('id'),samples=1,box_filter=True)
render_pass(s,'normal',str(out),override=override_mat('normal'),samples=8,transform='Raw')
render_pass(s,'depth',str(out),override=override_mat('depth'),samples=8,transform='Raw',depth='16')
clay=override_mat('clay')
for group in ['sun','sky']:
    render_pass(s,'light_'+group,str(out),override=clay,lights=(group,),world=('#cfeaff',.12) if group=='sky' else ('#000000',0),samples=24,transform='Raw',fmt='OPEN_EXR',depth='16',denoise=True)
print('HOME_CAT_PLATE_READY',flush=True)
