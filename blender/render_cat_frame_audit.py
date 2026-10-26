"""Render every authored frame and additional rear views for visual inspection."""
import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'build/mira-block-cat/frame-audit';out.mkdir(exist_ok=True)
s=bpy.context.scene;s.render.resolution_x=480;s.render.resolution_y=400;s.render.resolution_percentage=100;s.cycles.samples=8
try:
    p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
    for d in p.devices:d.use=d.type=='OPTIX'
    if any(d.type=='OPTIX' for d in p.devices):s.cycles.device='GPU'
except Exception:pass
for f in range(1,242):
    s.frame_set(f);s.render.filepath=str(out/f'{f:03d}.png');bpy.ops.render.render(write_still=True)
    if f%30==0:print('AUDIT_RENDER_FRAME',f,flush=True)
s.camera.location=(-1.7,-2.5,1.1);s.camera.rotation_euler=(Vector((-.10,0,.30))-s.camera.location).to_track_quat('-Z','Y').to_euler()
for f in [1,31,61,91,103,123,145,175,199,223,241]:
    s.frame_set(f);s.render.filepath=str(out/f'rear-{f:03d}.png');bpy.ops.render.render(write_still=True)
print('EVERY_FRAME_RENDERED',flush=True)
