"""Untextured American shorthair study: editable quadruped rig and clay meshes.
Coordinates are local metres, +X is the nose, Z is up. No coat markings.
"""
import math
import bpy
from mathutils import Vector, Matrix
from kit import M, ball

def curve(name,points,r,mat):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=r;data.bevel_resolution=3
    spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);data.materials.append(mat);return ob

DURATION=7.2
FPS=24
END=174
SCALE=.54
ORIGIN=Vector((-1.37,-.455,.753))
YAW=math.radians(-8)

def ease(v):
    v=max(0,min(1,v));return v*v*(3-2*v)

def blend(a,b,v):return Vector(a).lerp(Vector(b),v)

def ik(a,b,l1,l2,bend):
    d=b-a;length=d.length;axis=d.normalized()
    along=(l1*l1-l2*l2+length*length)/(2*length)
    h=math.sqrt(max(.000001,l1*l1-along*along))
    side=Vector(bend)-axis*Vector(bend).dot(axis);side.normalize()
    return a+axis*along+side*h

def pose(t):
    # Deliberate pauses give the cat time to wake, stretch, then settle.
    keys=[(0,0,0),(.65,0,0),(1.65,1,0),(2.9,1,1),(4.0,1,1),(4.9,1,0),(6.5,0,0),(7.2,0,0)]
    for i in range(len(keys)-1):
        if t<=keys[i+1][0]:
            a,b=keys[i],keys[i+1];u=ease((t-a[0])/(b[0]-a[0]));rise=a[1]+(b[1]-a[1])*u;stretch=a[2]+(b[2]-a[2])*u;break
    else:rise=stretch=0
    hip=blend((-.32,0,.245),(-.32,0,.56),rise)+Vector((-.055*stretch,0,.055*stretch))
    chest=blend((.25,0,.235),(.28,0,.56),rise)+Vector((.045*stretch,0,-.28*stretch))
    neck=chest+Vector((.105,0,.07))
    head=neck+Vector((.15,0,.105-.055*stretch))
    pts={};parents={}
    def add(n,a,b,p=None):pts[n]=(Vector(a),Vector(b));parents[n]=p
    spine=[hip,hip.lerp(chest,.32)+Vector((0,0,-.04*stretch)),hip.lerp(chest,.68)+Vector((0,0,-.06*stretch)),chest,neck]
    for i in range(4):add('spine'+str(i),spine[i],spine[i+1],'spine'+str(i-1) if i else None)
    # A subtle head turn toward the person, without moving the jaw independently.
    yaw=-.38-.2*(1-rise);forward=Vector((math.cos(yaw),math.sin(yaw),-.12*stretch))*.2
    add('head',head,head+forward,'spine3')
    for side in [-1,1]:
        suffix='L' if side<0 else 'R';y=side*.155
        for front in [True,False]:
            root=(chest if front else hip)+Vector((0,y,0))
            if front:
                foot=Vector((.34+.43*stretch,y,.065));knee=ik(root,foot,.29,.28,(-1,0,0));label='front'
            else:
                foot=Vector((-.38-.08*stretch,y,.065));knee=ik(root,foot,.33,.31,(1,0,0));label='rear'
            add(label+suffix+'Upper',root,knee,'spine2' if front else 'spine0')
            add(label+suffix+'Lower',knee,foot,label+suffix+'Upper')
            add(label+suffix+'Paw',foot,foot+Vector((.13,0,0)),label+suffix+'Lower')
    # Curl beside the loaf; lift from the base during the stretch, with delayed tip.
    curl=[(-.46,.03,.24),(-.62,.02,.15),(-.66,-.13,.08),(-.54,-.27,.07),(-.35,-.30,.07),(-.15,-.30,.07),(.02,-.27,.075),(.15,-.23,.085)]
    raised=[(-.45,.03,.57),(-.60,.025,.65),(-.72,.025,.82),(-.76,.025,1.0),(-.73,.025,1.14),(-.63,.025,1.18),(-.54,.025,1.15),(-.52,.025,1.08)]
    tail=[blend(a,b,rise*.72+stretch*.28) for a,b in zip(curl,raised)]
    for i in range(7):
        tail[i].y+=math.sin(t*1.3-i*.4)*.025*rise
        add('tail'+str(i),tail[i],tail[i+1],'spine0' if i==0 else 'tail'+str(i-1))
    return pts,parents

def bone_matrix(a,b):
    return Matrix.Translation(a)@(b-a).to_track_quat('Y','Z').to_matrix().to_4x4()

def build_cat():
    clay=M('ASH untextured warm grey clay','#b8b6b1',.78)
    detail=M('ASH sculpt recess','#797b7b',.85)
    rigdata=bpy.data.armatures.new('American shorthair skeleton');rig=bpy.data.objects.new('American shorthair • pet and stretch',rigdata);bpy.context.scene.collection.objects.link(rig)
    rig.location=ORIGIN;rig.rotation_euler.z=YAW;rig.scale=(SCALE,)*3;rig.show_in_front=True
    rest,parents=pose(1.65)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for name,(a,b) in rest.items():
        bone=rigdata.edit_bones.new(name);bone.head=a;bone.tail=b;bone.inherit_scale='NONE'
        if parents[name]:bone.parent=rigdata.edit_bones[parents[name]]
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    meshes=[]
    def bind(ob,weights):
        bpy.context.view_layer.update()
        if ob.type=='CURVE':
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
        # Vertices must be in the common rig-local coordinate system.
        ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
        ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);bpy.context.view_layer.update()
        mod=ob.modifiers.new('Shared quadruped skeleton','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
        if isinstance(weights,str):ob.vertex_groups.new(name=weights).add(list(range(len(ob.data.vertices))),1,'REPLACE')
        else:
            groups={n:ob.vertex_groups.new(name=n) for n in rest}
            for v in ob.data.vertices:
                for name,w in weights(v.co).items():
                    if w>0:groups[name].add([v.index],w,'REPLACE')
        ob['hot']='cat';meshes.append(ob);return ob
    def ell(name,loc,size,bone):return bind(ball('ASH '+name,1,loc,clay,scale=size),bone)
    # Continuous soft torso, weighted along the spinal chain rather than separate balls.
    rings=[(-.53,.56,.025,.04),(-.46,.56,.15,.16),(-.32,.56,.215,.205),(-.12,.56,.22,.19),(.10,.56,.205,.185),(.28,.56,.18,.19),(.385,.60,.115,.14),(.43,.63,.025,.035)]
    verts=[];faces=[];count=32
    for x,z,ry,rz in rings:
        for j in range(count):
            a=j/count*math.tau;verts.append((x,math.cos(a)*ry,z+math.sin(a)*rz))
    for i in range(len(rings)-1):
        for j in range(count):faces.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    faces.extend([tuple(range(count-1,-1,-1)),tuple((len(rings)-1)*count+j for j in range(count))])
    me=bpy.data.meshes.new('ASH continuous torso');me.from_pydata(verts,[],faces);me.materials.append(clay)
    body=bpy.data.objects.new('ASH continuous torso',me);bpy.context.scene.collection.objects.link(body)
    for p in me.polygons:p.use_smooth=True
    def weights(v):
        centers=[-.32,-.10,.15,.34];raw=[math.exp(-((v.x-x)/.15)**2) for x in centers];total=sum(raw)
        return {'spine'+str(i):w/total for i,w in enumerate(raw)}
    bind(body,weights);sub=body.modifiers.new('Smooth body silhouette','SUBSURF');sub.levels=2
    # Short, sturdy legs. Overlapping rounded joints are tucked inside the body.
    for side in ['L','R']:
        for label in ['front','rear']:
            for segment in ['Upper','Lower']:
                name=label+side+segment;a,b=rest[name];r=.085 if segment=='Upper' else .057
                if label=='rear' and segment=='Upper':r=.115
                ob=ball('ASH '+name,1,(a+b)/2,clay,scale=(r,r,(b-a).length*.58));ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();bind(ob,name)
            name=label+side+'Paw';a,b=rest[name];ell(label+side+' rounded paw',a+Vector((.045,0,-.005)),(.115,.075,.06),name)
    # Broad cheeks and short muzzle, fused into one sculpt, including rounded ears.
    h=rest['head'][0];forward=(rest['head'][1]-h).normalized();right=Vector((-forward.y,forward.x,0));up=Vector((0,0,1));parts=[]
    def facepoint(x,y,z):return h+forward*x+right*y+up*z
    for name,xyz,size in [('head',(0,0,.02),(.19,.185,.18)),('cheek L',(.065,-.105,-.035),(.105,.095,.10)),('cheek R',(.065,.105,-.035),(.105,.095,.10)),('muzzle L',(.155,-.05,-.045),(.072,.066,.055)),('muzzle R',(.155,.05,-.045),(.072,.066,.055)),('chin',(.135,0,-.092),(.08,.08,.04))]:
        parts.append(ball('ASH sculpt '+name,1,facepoint(*xyz),clay,scale=size))
    for side in [-1,1]:
        # Rounded triangular shells; modest ears for the breed, not long pointed fox ears.
        coords=[facepoint(-.07,side*.065,.12),facepoint(.045,side*.065,.12),facepoint(-.055,side*.215,.105),facepoint(.035,side*.215,.105),facepoint(-.035,side*.17,.265),facepoint(.015,side*.17,.265)]
        me=bpy.data.meshes.new('ear sculpt');me.from_pydata(coords,[],[(0,2,4),(1,5,3),(0,4,5,1),(2,3,5,4),(0,1,3,2)]);me.materials.append(clay);ob=bpy.data.objects.new('ASH short rounded ear',me);bpy.context.scene.collection.objects.link(ob);parts.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();head=parts[0]
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    rem=head.modifiers.new('Unified clay sculpt','REMESH');rem.mode='VOXEL';rem.voxel_size=.009;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=head.modifiers.new('Relax sculpt','SMOOTH');sm.factor=1;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
    bind(head,'head')
    # Sculpted facial recesses, no image textures, whisker lines or coat stripes.
    for side in [-1,1]:
        coords=[facepoint(.156,side*.092-.032,.035),facepoint(.174,side*.092,.020),facepoint(.156,side*.092+.032,.035)]
        bind(curve('ASH sleepy eyelid',coords,.006,detail),'head')
    nose=ball('ASH nose',1,facepoint(.217,0,-.018),detail,scale=(.02,.032,.019));bind(nose,'head')
    bind(curve('ASH mouth groove',[facepoint(.214,0,-.038),facepoint(.218,0,-.062),facepoint(.201,-.028,-.074)],.003,detail),'head')
    bind(curve('ASH mouth groove',[facepoint(.218,0,-.062),facepoint(.201,.028,-.074)],.003,detail),'head')
    # Smooth continuous tail tube with blended weights across seven vertebrae.
    vv=[];ff=[];tailpoints=[rest['tail'+str(i)][0] for i in range(7)]+[rest['tail6'][1]]
    for i,p in enumerate(tailpoints):
        direction=(tailpoints[min(i+1,7)]-tailpoints[max(0,i-1)]).normalized();basis=direction.to_track_quat('Z','Y').to_matrix();r=.053*(1-.72*(i/7)**1.6)
        for j in range(16):vv.append(p+basis@Vector((math.cos(j/16*math.tau)*r,math.sin(j/16*math.tau)*r,0)))
    for i in range(7):
        for j in range(16):ff.append((i*16+j,i*16+(j+1)%16,(i+1)*16+(j+1)%16,(i+1)*16+j))
    ff.extend([tuple(range(15,-1,-1)),tuple(112+j for j in range(16))]);me=bpy.data.meshes.new('tail skin');me.from_pydata(vv,[],ff);me.materials.append(clay)
    tail=bpy.data.objects.new('ASH continuous curled tail',me);bpy.context.scene.collection.objects.link(tail)
    for p in me.polygons:p.use_smooth=True
    bind(tail,lambda v:{'tail'+str(min(6,min(range(8),key=lambda i:(v-tailpoints[i]).length))):1})
    sub=tail.modifiers.new('Soft tail','SUBSURF');sub.levels=2
    # Union the torso and limbs into a continuous skin; transfer their authored weights.
    from mathutils.kdtree import KDTree
    skin=[o for o in meshes if o==body or any(o.name.startswith('ASH '+prefix) for prefix in ['frontL','frontR','rearL','rearR'])]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in skin:
        bpy.context.view_layer.objects.active=ob
        for modifier in list(ob.modifiers):
            if modifier.type=='ARMATURE':ob.modifiers.remove(modifier)
            else:bpy.ops.object.modifier_apply(modifier=modifier.name)
        ob.select_set(True)
    bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
    groupnames={g.index:g.name for g in body.vertex_groups}
    authored=[{groupnames[g.group]:g.weight for g in v.groups} for v in body.data.vertices]
    kd=KDTree(len(body.data.vertices))
    for v in body.data.vertices:kd.insert(v.co,v.index)
    kd.balance()
    rem=body.modifiers.new('Continuous shoulder and haunch sculpt','REMESH');rem.mode='VOXEL';rem.voxel_size=.012;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
    smooth=body.modifiers.new('Relax limb joins','SMOOTH');smooth.factor=.7;smooth.iterations=4;bpy.ops.object.modifier_apply(modifier=smooth.name)
    import numpy as np
    body.vertex_groups.clear();groups={n:body.vertex_groups.new(name=n) for n in rest};names=list(rest);weightmap=np.zeros((len(body.data.vertices),len(names)),dtype=np.float64)
    for v in body.data.vertices:
        weights={}
        for _,index,d in kd.find_n(v.co,3):
            for name,w in authored[index].items():weights[name]=weights.get(name,0)+w/max(d,.002)**2
        total=sum(weights.values())
        for name,w in weights.items():weightmap[v.index,names.index(name)]=w/total
    edges=np.array([tuple(e.vertices) for e in body.data.edges]);a,b=edges[:,0],edges[:,1];degree=np.bincount(np.concatenate((a,b)),minlength=len(weightmap))
    for _ in range(32):
        average=np.zeros_like(weightmap);np.add.at(average,a,weightmap[b]);np.add.at(average,b,weightmap[a]);weightmap=.25*weightmap+.75*average/np.maximum(degree[:,None],1)
    for index,row in enumerate(weightmap):
        for j,w in enumerate(row):
            if w>.0001:groups[names[j]].add([index],float(w),'REPLACE')
    mod=body.modifiers.new('Shared quadruped skeleton','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    meshes=[o for o in bpy.context.scene.objects if o.name.startswith('ASH ') and o.type=='MESH']
    for frame in range(1,END+1):
        current,_=pose((frame-1)/FPS)
        for name,(a,b) in current.items():
            bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION';bone.matrix=bone_matrix(a,b)@Matrix.Diagonal(Vector((1,(b-a).length/rigdata.bones[name].length,1,1)))
            bpy.context.view_layer.update()
            bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame);bone.keyframe_insert('scale',frame=frame)
        bpy.context.view_layer.update()
    rig['motion']='loaf → wake → rise → chest low / hips high stretch → settle → loaf'
    rig['coat']='Neutral untextured clay; owner reference pending'
    return rig,meshes
