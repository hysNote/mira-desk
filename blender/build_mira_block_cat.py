"""Original block cat, authored locally. +X faces forward, Z up, metres.
No downloaded meshes, textures, or animation tracks are used.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix, Euler

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/mira-block-cat'; OUT.mkdir(parents=True,exist_ok=True)
ASSETS=ROOT/'site/assets/mira-block-cat'; ASSETS.mkdir(parents=True,exist_ok=True)
FPS=30; DURATION=8; END=241
def ease(t):
    t=max(0,min(1,t)); return t*t*t*(t*(t*6-15)+10)
def ramp(t,a,b): return ease((t-a)/(b-a))
def pulse(t,c,w):return math.cos((t-c)/w*math.pi/2)**2 if abs(t-c)<w else 0
def ik(a,b,l1,l2,groom=0):
    axis=(b-a).normalized(); d=(b-a).length
    along=(l1*l1-l2*l2+d*d)/(2*d)
    side=Vector((-1,-.65*groom,-.7*groom)); side=(side-axis*side.dot(axis)).normalized()
    return a+axis*along+side*math.sqrt(max(0,l1*l1-along*along))
def bm(a,b,name=''):
    if name.startswith(('Arm','Forearm')):
        # Stable elbow plane: prevent a half-turn when a bent leg passes vertical.
        y=(b-a).normalized();x=y.cross(Vector((0,1,0))).normalized();z=x.cross(y).normalized()
        return Matrix.Translation(a)@Matrix((x,y,z)).transposed().to_4x4()
    return Matrix.Translation(a)@(b-a).to_track_quat('Y','Z').to_matrix().to_4x4()
def state(t):
    rise=ramp(t,.45,2.05)*(1-ramp(t,5.85,7.5))
    groom=ramp(t,2.25,3.15)*(1-ramp(t,5.15,5.8))
    lick=sum(pulse(t,c,w) for c,w in [(3.40,.16),(4.07,.18),(4.82,.17)])
    nod=sum(pulse(t,c-.06,w+.13) for c,w in [(3.40,.16),(4.07,.18),(4.82,.17)])
    awake=ramp(t,.05,.4)*(1-ramp(t,7.4,7.9))
    angle=rise*.95
    hip=Vector((-.25,0,.25-.04*rise))
    chest=hip+Vector((math.cos(angle)*.48,0,math.sin(angle)*.48))
    head=chest+Vector((.14,-.028*groom,.035+.075*rise-.009*nod))
    rot=Euler((0,groom*(.42+.035*nod),-.18*groom)).to_matrix()
    pts={}; parents={}
    def add(n,a,b,parent=None):pts[n]=(Vector(a),Vector(b));parents[n]=parent
    add('Hip',hip,hip+Vector((.1,0,0)))
    add('Torso',hip,chest,'Hip')
    add('Neck',chest,head,'Torso')
    add('Head',head,head+rot@Vector((.2,0,0)),'Neck')
    for side,label in [(-1,'L'),(1,'R')]:
        root=hip.lerp(chest,.75)+Vector((.03,side*.105,.025-.055*rise))
        foot=Vector((.22,side*.12,.070))
        if side==-1:foot=foot.lerp(Vector((.30,-.09,.465+.003*nod)),groom)
        assert (foot-root).length < .5, 'Foreleg target beyond reach'
        elbow=ik(root,foot,.255,.245,groom if side==-1 else 0)
        add('Arm'+label,root,elbow,'Torso')
        add('Forearm'+label,elbow,foot,'Arm'+label)
        pawdir=Vector((.13,0,0)).lerp(Vector((.065,0,.10)),groom if side==-1 else 0)
        add('Paw'+label,foot,foot+pawdir,'Forearm'+label)
        h=Vector((-.26,side*.14,.17)); end=Vector((-.19,side*.15,.065))
        add('Haunch'+label,h,h+Vector((.1,0,0)),'Hip')
        add('BackPaw'+label,end,end+Vector((.12,0,0)),'Haunch'+label)
    # Root is buried inside the pelvis and follows its translation throughout.
    tail=[tuple(hip+Vector((-.12,.035,.01))),(-.64,.03,.14),(-.68,-.20,.08),(-.50,-.30,.07),(-.25,-.31,.075)]
    # Low curled tail; the small tip movement settles before the final rest.
    for i in range(1,len(tail)):
        x,y,z=tail[i];tail[i]=(x,y+math.sin(t*2-i*.6)*.012*rise*i/4,z)
    for i in range(4):add('Tail'+str(i),tail[i],tail[i+1],'Hip' if i==0 else 'Tail'+str(i-1))
    for n in ['EyesOpen','EyesClosed']:add(n,head,head+rot@Vector((.1,0,0)),'Head')
    mouth=head+rot@Vector((.211,0,-.079))
    add('Tongue',mouth,mouth+rot@Vector((.08,0,0)),'Head')
    scales={'EyesOpen':max(.001,awake),'EyesClosed':max(.001,1-awake),'Tongue':max(.001,lick*groom)}
    return pts,parents,scales

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=END
rest,parents,_=state(0)
data=bpy.data.armatures.new('Mira block cat skeleton')
rig=bpy.data.objects.new('Mira block cat • rest groom rest',data);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name,(a,b) in rest.items():
    bone=data.edit_bones.new(name);bone.head=a;bone.tail=b
    # Match authored rest frames to the sampled pose frames, including bone roll.
    # Otherwise blended skins twist even at time zero (most visible on the tail).
    bone.align_roll(bm(a,b,name).to_3x3().col[2])
    if parents[name]:bone.parent=data.edit_bones[parents[name]]
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def material(name,color,roughness=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness
    return m
coal=material('soft charcoal',(.055,.072,.083))
slate=material('blue grey cheeks',(.095,.119,.13))
paws=material('charcoal paws',(.07,.085,.093))
ear=material('muted rose inner ears',(.36,.21,.24))
pink=material('nose and tongue',(.61,.30,.34))
eye=material('warm chartreuse eyes',(.63,.73,.32))
dark=material('dark eye pupils',(.014,.022,.024))
teal=material('dusty teal collar',(.13,.30,.28))
tag=material('small brass collar tag',(.58,.45,.21),.5)
meshes=[]
def bind(ob,bone):
    ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    if isinstance(bone,str):
        vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    else:
        groups={n:ob.vertex_groups.new(name=n) for n in rest}
        for v in ob.data.vertices:
            for n,w in bone(v).items():
                if w>0:groups[n].add([v.index],w,'REPLACE')
    mod=ob.modifiers.new('Rigid block articulation','ARMATURE');mod.object=rig
    ob.parent=rig;meshes.append(ob);return ob
def box(name,loc,size,mat,bone,rotation=None,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    if rotation is not None:o.rotation_euler=rotation
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft toy edges','BEVEL');mod.width=bevel;mod.segments=4
        bpy.ops.object.modifier_apply(modifier=mod.name)
        for p in o.data.polygons:p.use_smooth=True
        mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(mat);return bind(o,bone)
def ellipsoid(name,loc,size,mat,bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=size
    for p in ob.data.polygons:p.use_smooth=True
    ob.data.materials.append(mat);bpy.context.view_layer.update();return bind(ob,bone)
def skin(name,verts,faces,weights,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat)
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
    for p in me.polygons:p.use_smooth=True
    return bind(ob,lambda v:weights[v.index])
def segment(name,width,depth,mat):
    a,b=rest[name];q=(b-a).to_track_quat('Z','Y')
    box(name+' block',(a+b)/2,(width,depth,(b-a).length+.026),mat,name,q.to_euler())
# Rounded-square torso with a soft waist and a fixed, weight-bearing pelvis.
rings=[(-.44,.22,.025,.03),(-.39,.24,.15,.15),(-.28,.25,.215,.20),(-.13,.25,.225,.195),(.02,.25,.205,.18),(.16,.26,.18,.16),(.25,.28,.135,.13),(.30,.29,.045,.05)]
verts=[];faces=[];weights=[];N=32
for x,z,ry,rz in rings:
    w=ease((x+.34)/.32)
    for j in range(N):
        a=j/N*math.tau;c=math.cos(a);s=math.sin(a)
        verts.append((x,math.copysign(abs(c)**.63,c)*ry,z+math.copysign(abs(s)**.63,s)*rz))
        weights.append({'Hip':1-w,'Torso':w})
for i in range(len(rings)-1):
    for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
faces.extend([tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))])
skin('Soft block body',verts,faces,weights,coal)
segment('Neck',.25,.25,coal)
for side in ['L','R']:
    # A single continuous skin across shoulder and elbow, not two hinged bars.
    root,knee=rest['Arm'+side];_,wrist=rest['Forearm'+side]
    centers=[root.lerp(knee,t) for t in [0,.25,.55,.80]]+[knee]+[knee.lerp(wrist,t) for t in [.20,.45,.75,1]]
    vv=[];ff=[];ww=[];count=16
    radii=[.025,.073,.072,.066,.063,.064,.062,.060,.055]
    for i,c in enumerate(centers):
        direction=centers[min(i+1,8)]-centers[max(0,i-1)];basis=direction.to_track_quat('Z','Y').to_matrix()
        w=ease((i-2)/4)
        for j in range(count):
            a=j/count*math.tau;vv.append(c+basis@Vector((math.cos(a)*radii[i],math.sin(a)*radii[i],0)))
            ww.append({'Arm'+side:1-w,'Forearm'+side:w})
    for i in range(8):
        for j in range(count):ff.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    ff.extend([tuple(range(count-1,-1,-1)),tuple(8*count+j for j in range(count))])
    skin('Continuous foreleg '+side,vv,ff,ww,coal)
    a,b=rest['Paw'+side];box('Tucked mitten paw '+side,a+Vector((.012,0,-.006)),(.135,.125,.104),paws,'Paw'+side,bevel=.038)
    a,_=rest['Haunch'+side];ellipsoid('Soft haunch '+side,a,(.17,.115,.15),coal,'Haunch'+side)
    a,_=rest['BackPaw'+side];box('Back paw '+side,a-Vector((0,0,.009)),(.17,.12,.11),paws,'BackPaw'+side,bevel=.035)
# A continuous rounded tail, with overlapping bone weights instead of visible blocks.
controls=[rest['Tail0'][0]]+[rest['Tail'+str(i)][1] for i in range(4)]
centers=[];tv=[];tf=[];tw=[];steps=10;count=12
for i in range(4):
    p0=controls[max(0,i-1)];p1=controls[i];p2=controls[i+1];p3=controls[min(4,i+2)]
    for j in range(steps+(1 if i==3 else 0)):
        u=j/steps
        centers.append((p1*2+(-p0+p2)*u+(p0*2-p1*5+p2*4-p3)*u*u+(-p0+p1*3-p2*3+p3)*u*u*u)*.5)
for i,c in enumerate(centers):
    basis=(centers[min(i+1,40)]-centers[max(0,i-1)]).to_track_quat('Z','Y').to_matrix()
    radius=(.048-.026*i/40+.017*(1-ease(i/9)))*(1 if i<38 else [.9,.65,.12][i-38])
    bonepos=max(0,min(3,i/10-.5));lo=int(bonepos);hi=min(3,lo+1);w=ease(bonepos-lo)
    weights={'Tail'+str(lo):1-w};weights['Tail'+str(hi)]=weights.get('Tail'+str(hi),0)+w
    if i<6:
        follow=ease(i/6);weights={n:v*follow for n,v in weights.items()};weights['Hip']=1-follow
    for j in range(count):
        a=j/count*math.tau;tv.append(c+basis@Vector((math.cos(a)*radius,math.sin(a)*radius,0)));tw.append(weights)
for i in range(40):
    for j in range(count):tf.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
tf.extend([tuple(range(count-1,-1,-1)),tuple(40*count+j for j in range(count))])
skin('Soft continuous curled tail',tv,tf,tw,coal)
h=rest['Head'][0]
box('Rounded block head',h,(.37,.40,.32),coal,'Head',bevel=.065)
for side in [-1,1]:
    # Short rounded wedge ears keep the cat silhouette instead of robot antennae.
    points=[]
    for x in [-.025,.015]:
        points += [h+Vector((x,side*.035,.115)),h+Vector((x,side*.210,.105)),h+Vector((x-.010,side*.160,.265))]
    me=bpy.data.meshes.new('Ear');me.from_pydata(points,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.materials.append(coal)
    ob=bpy.data.objects.new('Rounded ear',me);scene.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Soft ear edges','BEVEL');mod.width=.018;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in ob.data.polygons:p.use_smooth=True
    bind(ob,'Head')
    inner=[h+Vector((.018,side*.082,.145)),h+Vector((.018,side*.174,.140)),h+Vector((.011,side*.156,.235))]
    me=bpy.data.meshes.new('Inner ear');me.from_pydata(inner,[],[(0,1,2)]);me.materials.append(ear)
    ob=bpy.data.objects.new('Inset pink ear',me);scene.collection.objects.link(ob);bind(ob,'Head')
    box('Soft cheek',h+Vector((.163,side*.073,-.055)),(.105,.15,.11),slate,'Head',bevel=.045)
    ellipsoid('Open eye',h+Vector((.181,side*.106,.037)),(.012,.041,.046),eye,'EyesOpen')
    ellipsoid('Eye pupil',h+Vector((.192,side*.106-.005,.037)),(.004,.015,.037),dark,'EyesOpen')
    box('Sleep eyelid',h+Vector((.187,side*.106,.015)),(.009,.062,.008),slate,'EyesClosed',bevel=.003)
ellipsoid('Little pink nose',h+Vector((.222,0,-.029)),(.014,.025,.016),pink,'Head')
box('Short mouth line',h+Vector((.220,0,-.076)),(.01,.027,.008),dark,'Head',bevel=0)
m=rest['Tongue'][0];box('Tongue',m+Vector((.023,0,-.007)),(.055,.035,.012),pink,'Tongue',bevel=.003)
chest=rest['Neck'][0]
box('Teal collar',chest+Vector((.045,0,.01)),(.057,.32,.25),teal,'Neck',bevel=.003)
box('Square brass tag',chest+Vector((.079,-.155,-.07)),(.02,.032,.043),tag,'Neck',bevel=.003)

for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
# Full sampled clip keeps browser playback identical to the editable Blender source.
for frame in range(1,END+1):
    pts,_,scales=state((frame-1)/FPS)
    for name,(a,b) in pts.items():
        pb=rig.pose.bones[name];target=bm(a,b,name)
        if name in scales:target=target@Matrix.Scale(scales[name],4)
        pb.matrix=target;bpy.context.view_layer.update()
        for channel in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=channel,frame=frame,group=name)
action=rig.animation_data.action;action.name='Rest • rise • groom • settle'
scene.frame_set(1)
# Export only the authored cat, before adding the presentation studio.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in meshes:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(ASSETS/'mira-block-cat.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_frame_range=True,export_anim_slide_to_zero=True,export_yup=True)

scene.world=bpy.data.worlds.new('Soft grey studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.60,.53,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
floor=material('studio floor',(.58,.62,.55))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.data.materials.append(floor)
for loc,power,size in [((2,-3,4),400,4),((-3,1,3),220,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.8,-2.8,1.45));cam=bpy.context.object;target=Vector((0,0,.40));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.75;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.type=='OPTIX' for d in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
scene.render.resolution_x=720;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mira-block-cat.blend'))
for f in [1,61,106,151,199,241]:
    scene.frame_set(f);scene.render.filepath=str(OUT/f'pose-{f}.png');bpy.ops.render.render(write_still=True)
(ASSETS/'motion.json').write_text(json.dumps({'duration':DURATION,'fps':FPS,'frames':END,'rest':0,'sit':2,'groom':3.5,'settle':6.6,'author':'Original model and animation made for Mira; no downloaded model data used.'},indent=2))
print('MIRA_BLOCK_CAT_READY',flush=True)
