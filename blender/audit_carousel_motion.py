import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];s=bpy.context.scene
carrier=s.objects['Carousel rotating photo carrier'];moving=list(carrier.children)
assert len(moving)==24
stationary=[o for o in s.objects if o.name.startswith('carousel') and o not in moving]
fixed={o.name:o.matrix_world.copy() for o in stationary};radii={};samples=[]
for frame in [1,19,37,55,73]:
    s.frame_set(frame);bpy.context.view_layer.update()
    for ob in moving:
        radius=math.hypot(ob.matrix_world.translation.x-carrier.location.x,ob.matrix_world.translation.y-carrier.location.y)
        if frame==1:radii[ob.name]=radius
        assert abs(radius-radii[ob.name])<1e-5,(ob.name,frame,radius)
    for ob in stationary:assert all(abs(ob.matrix_world[i][j]-fixed[ob.name][i][j])<1e-5 for i in range(4) for j in range(4)),ob.name
    samples.append({'frame':frame,'angle':math.degrees(carrier.rotation_euler.z)})
report={'moving_parts':len(moving),'stationary_parts':len(stationary),'constant_radius':True,'samples':samples}
(root/'build/carousel-motion/native-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
