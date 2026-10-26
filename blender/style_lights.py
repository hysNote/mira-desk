"""Extra isolated lighting passes for the style family; leaves the saved model intact."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from upstream_render import override_mat,render_pass
root=Path(__file__).resolve().parents[1]
s=bpy.context.scene
out=root/'build/style-lights';out.mkdir(exist_ok=True)
def area(name,group,loc,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o['group']=group
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for name,power in [('resume screen',18),('intro screen',8)]:
    ob=bpy.data.objects[name];p=sum((ob.matrix_world@Vector(v) for v in ob.bound_box),Vector())/8
    area('style '+name,'screen',p+Vector((0,-.03,.03)),(p.x,-.6,.75),power,(.52,.78,1),.55)
area('style magenta bounce','rgb',(-1,.5,1.05),(-1,-.3,.75),12,(1,.05,.44),.55)
area('style cyan bounce','rgb',(1.1,.5,1.05),(1.1,-.3,.75),12,(.04,.8,1),.55)
area('style lamp wash','lamp',(-1.92,.65,2.04),(-1.7,.91,2.6),35,(1,.7,.34),.28)
clay=override_mat('clay')
for group in ['screen','rgb','lamp']:
    render_pass(s,'light_'+group,str(out),override=clay,mode='beauty',lights=(group,),samples=32,transform='Raw',fmt='OPEN_EXR',depth='16',denoise=True)
print('STYLE_LIGHTS_READY')
