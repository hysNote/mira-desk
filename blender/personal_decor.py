"""Reference-based felt photo board, uplighter, plant, fabric wallet and mini bin."""
import math, random
import bpy
from mathutils import Vector
from kit import M, MATS, box, plane, cyl, ball, torus, rgb

def lathe(name,profile,mat,xy=(0,0),lobes=0):
    n=80; verts=[]
    for r,z in profile:
        for j in range(n):
            a=j*math.tau/n; rr=r*(1+lobes*math.sin(10*a))
            verts.append((xy[0]+rr*math.cos(a),xy[1]+rr*math.sin(a),z))
    faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(profile)-1) for j in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    return ob

def fabric(mat,scale=230):
    nt=mat.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.0005
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],MATS[mat.name]['beauty'].inputs['Normal'])

def replace_wallet(rounded):
    for ob in list(bpy.data.objects):
        if ob.get('hot')=='travel':bpy.data.objects.remove(ob,do_unlink=True)
    ink=M('wallet black fabric','#15181b',.96);blue=M('wallet blue fabric','#8dc8d3',.94)
    yellow=M('wallet yellow fabric','#f6d82b',.94);lime=M('wallet lime fabric','#afc52c',.94)
    for m in [ink,blue,yellow,lime]:fabric(m)
    x,y=1.47,-.45
    def patch(name,size,offset,mat,r=.02):
        return rounded('wallet '+name,size,(x+offset[0],y+offset[1],offset[2]),mat,hot='travel',r=r)
    patch('black binding',(.35,.29,.032),(0,0,.774),ink,.03)
    patch('lime side panel',(.318,.254,.005),(.005,0,.793),lime,.025)
    patch('front black piping',(.302,.268,.008),(-.017,0,.797),ink,.025)
    patch('cyan front',(.269,.234,.005),(-.02,0,.802),blue,.023)
    patch('strap black piping',(.18,.103,.010),(.082,0,.811),ink,.038)
    patch('yellow strap',(.146,.065,.006),(.089,0,.819),yellow,.027)
    for yy in [-.083,.083]:
        for i in range(6):patch('dash stitch',(.013,.005,.001),(-.118+i*.032,yy,.806),ink,.001)

def photo_board(rounded,variant):
    x=-1.45+(.11 if variant=='b' else 0);z=1.85;w=.72;h=1.075
    backing=M('felt board frame','#392a27',.7)
    rounded('felt board thick backing',(w+.024,.038,h+.024),(x,.900,z),backing,r=.005)
    mat=M('felt board real photographs',image='felt-board-reference.jpg',rough=.86)
    ob=plane('felt board photo collage',w,h,(x,.875,z),mat)
    # Preserve the user's real photographs. UV coordinates rectify just the board;
    # no generated faces or replacement memories are introduced.
    uv=[(134/1080,1-181/1440),(124/1080,1-1346/1440),(910/1080,1-1335/1440),(893/1080,1-181/1440)]
    for loop,t in zip(ob.data.uv_layers.active.data,uv):loop.uv=t
    # A few physical pins catch the light over the photographed collage.
    pin=M('felt board pink pins','#d7a1bf',.42)
    for u,v in [(.35,.98),(.69,.98),(.80,.62),(.09,.30),(.62,.16)]:
        ball('felt board pin',.008,(x+(u-.5)*w,.866,z+(v-.5)*h),pin,scale=(1,.48,1))

def floor_lamp(rounded,variant):
    if variant=='c':return
    x,y,top=(2.02,.65,2.13) if variant=='a' else (-1.92,.65,2.03)
    floor=-.39
    dark=M('uplighter charcoal','#24272b',.44,metal=.35)
    white=M('uplighter frosted glass','#fff3d9',.36,emit=.45)
    cyl('uplighter weighted base',.17,.045,(x,y,floor+.0225),dark,r2=.155)
    cyl('uplighter slim pole',.012,top-floor-.36,(x,y,(floor+top-.36)/2),dark)
    for z in [.45,1.04]:cyl('uplighter pole collar',.015,.042,(x,y,z),dark)
    lathe('uplighter black socket',[(0,top-.37),(.017,top-.37),(.070,top-.25),(.075,top-.24)],dark,(x,y))
    lathe('uplighter frosted bowl',[(.072,top-.24),(.22,top-.012),(.221,top),(.211,top+.002),(.064,top-.21),(.035,top-.23)],white,(x,y))
    bulb=M('uplighter bulb','#fff4d8',.4,emit=2.0)
    ball('uplighter warm bulb',.042,(x,y,top-.12),bulb,scale=(1,1,.8))
    ld=bpy.data.lights.new('uplighter warm light','POINT');ld.energy=12;ld.color=(1,.82,.59);ld.shadow_soft_size=.12
    lo=bpy.data.objects.new('uplighter warm light',ld);bpy.context.scene.collection.objects.link(lo);lo.location=(x,y,top-.08);lo['group']='sky'

def plant(rod,curve,variant):
    x,y=(-2.18,.28) if variant=='a' else (2.16,.24)
    floor=-.39;pot_top=-.04
    pot=M('plant sand ceramic','#c1b294',.9);soil=M('plant soil','#342a22',1)
    lathe('plant ceramic pot',[(0,floor),(.145,floor),(.19,pot_top-.025),(.191,pot_top),(.175,pot_top),(.16,pot_top-.06)],pot,(x,y))
    cyl('plant soil',.167,.012,(x,y,pot_top-.04),soil)
    torus('plant rolled pot rim',.182,.008,(x,y,pot_top-.005),pot)
    stem=M('plant stems','#455e38',.85)
    leafm=[M('plant leaf '+str(i),c,.55) for i,c in enumerate(['#426d43','#668952','#33563d'])]
    rng=random.Random(24)
    for i in range(10):
        a=i*2.4; height=.60+(i%4)*.14+( .12 if variant=='c' else 0)
        tip=Vector((x+math.cos(a)*(.18+.04*(i%3)),y+math.sin(a)*.20,height))
        start=Vector((x,y,pot_top-.02))
        mid=start.lerp(tip,.6)+Vector((math.cos(a)*.04,math.sin(a)*.04,.02))
        curve('plant leaf stem',[tuple(start),tuple(mid),tuple(tip)],.0035,stem)
        direction=Vector((math.cos(a)*.30,math.sin(a)*.25,.02));side=Vector((-math.sin(a),math.cos(a),0))
        verts=[];rows=12
        for j in range(rows+1):
            t=j/rows;center=tip+direction*t+Vector((0,0,.10*math.sin(math.pi*t)-.08*t))
            width=.125*math.sin(math.pi*t)**.6
            if i%3==0 and j in [3,6,9]:width*=.48
            for sign in [-1,0,1]:verts.append(tuple(center+side*width*sign+Vector((0,0,-.018*abs(sign)*math.sin(math.pi*t)))))
        faces=[(j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k) for j in range(rows) for k in range(2)]
        me=bpy.data.meshes.new('plant curved leaf');me.from_pydata(verts,[],faces);me.update()
        ob=bpy.data.objects.new('plant curved leaf',me);bpy.context.scene.collection.objects.link(ob);me.materials.append(leafm[i%3])
        for p in me.polygons:p.use_smooth=True
        ob.modifiers.new('leaf thickness','SOLIDIFY').thickness=.001
        rib=[verts[j*3+1] for j in range(0,rows+1,2)]
        curve('plant midrib',[(vx,vy,vz+.001) for vx,vy,vz in rib],.0012,stem)

def miniature_bin(rounded,rod,curve):
    x,y=1.46,.59
    metal=M('mini bin brushed pewter','#858d94',.38,metal=.65);inside=M('mini bin inside','#424b50',.6,metal=.3)
    red=M('mini bin red letters','#c9332a',.5);yellow=M('mini bin yellow door','#efbc29',.55)
    lathe('mini bin barrel',[(0,.751),(.087,.751),(.093,.77),(.109,1.00),(.115,1.012),(.101,1.012),(.086,.79),(0,.79)],metal,(x,y))
    for z,r in [(.77,.091),(.995,.111), (1.012,.111)]:torus('mini bin rim',r,.006,(x,y,z),metal)
    cyl('mini bin dark cavity',.086,.004,(x,y,.80),inside)
    curve('mini bin carrying handle',[(x-.12,y,.98),(x-.135,y,1.10),(x-.11,y,1.145),(x+.11,y,1.145),(x+.135,y,1.10),(x+.12,y,.98)],.009,metal)
    for text,z,size in [('CHUM',.916,.046),('BUCKET',.865,.037)]:
        cu=bpy.data.curves.new('mini bin lettering','FONT');cu.body=text;cu.align_x='CENTER';cu.size=size;cu.extrude=.0014;cu.bevel_depth=.0003
        ob=bpy.data.objects.new('mini bin '+text,cu);bpy.context.scene.collection.objects.link(ob);ob.data.materials.append(red);ob.location=(x,y-.108,z);ob.rotation_euler=(math.pi/2,0,0)
        bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
    for dx in [-.024,.024]:
        rounded('mini bin yellow door',(.046,.008,.066),(x+dx,y-.092,.789),yellow,r=.003)
        ball('mini bin door window',.009,(x+dx,y-.098,.797),M('mini bin teal windows','#409d9d',.3),scale=(1,.25,1))
    green=M('mini bin sculpted green hand','#3d9b83',.36,metal=.4)
    nt=green.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=38
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=rgb('#287775');ramp.color_ramp.elements[1].color=rgb('#c4b85c')
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
    for mode,sock in [('beauty','Base Color'),('albedo','Color')]:nt.links.new(ramp.outputs[0],MATS[green.name][mode].inputs[sock])
    for i in range(4):
        xx=x-.069+i*.045
        ball('mini bin curled finger',.031,(xx,y-.012,1.15),green,scale=(.75,1.1,1.35))
        ball('mini bin knuckle',.023,(xx,y-.030,1.177),green)
    ball('mini bin thumb',.038,(x+.09,y+.008,1.18),green,scale=(.7,1.25,.75))
    lathe('mini bin scalloped cuff',[(.05,1.175),(.065,1.22),(.078,1.245),(.068,1.249),(.055,1.21)],green,(x,y+.018),lobes=.12)

def build_decor(rounded,rod,curve,variant):
    photo_board(rounded,variant);floor_lamp(rounded,variant);bird_of_paradise(rod,curve,variant);miniature_bin(rounded,rod,curve);pineapple_cup(rounded,rod,curve)

def pineapple_cup(rounded,rod,curve):
    x,y=-.80,-.035
    orange=M('pineapple orange ceramic','#f19115',.48);groove=M('pineapple amber relief','#d16c12',.64)
    metal=M('pineapple pewter','#9ca4a5',.32,metal=.72);blue=M('pineapple blue window','#356eac',.32)
    lathe('pineapple pen cup',[(0,.751),(.071,.751),(.088,.775),(.101,.855),(.096,.94),(.089,.971),(.079,.971),(.079,.805),(0,.805)],orange,(x,y))
    for direction in [-1,1]:
        for i in range(7):
            pts=[]
            for j in range(30):
                t=j/29;z=.77+t*.20;r=.088+.013*math.sin(math.pi*t)
                a=i*math.tau/7+direction*t*1.8;pts.append((x+r*math.cos(a),y+r*math.sin(a),z))
            curve('pineapple diamond seam',pts,.0014,groove)
    rounded('pineapple silver door',(.067,.012,.095),(x,y-.095,.807),metal,r=.022)
    rounded('pineapple inset door',(.051,.005,.079),(x,y-.104,.807),M('pineapple door inset','#667176',.45,metal=.5),r=.017)
    torus('pineapple door valve',.012,.002,(x,y-.109,.805),metal,rot=(math.pi/2,0,0))
    for a in [j*math.tau/6 for j in range(6)]:rod('pineapple valve spoke',(x,y-.110,.805),(x+.020*math.cos(a),y-.110,.805+.020*math.sin(a)),.0013,metal)
    for dx,z in [(-.05,.918),(.068,.855)]:
        yy=y-math.sqrt(.10**2-dx**2)
        cyl('pineapple window frame',.020,.006,(x+dx,yy-.003,z),metal,rot=(math.pi/2,0,0))
        cyl('pineapple blue porthole',.015,.007,(x+dx,yy-.006,z),blue,rot=(math.pi/2,0,0))
    for i,(dx,dy,height,color) in enumerate([(-.03,0,.19,'#c94e63'),(.018,.02,.23,'#314d84'),(.044,-.01,.17,'#eab83f')]):
        a=Vector((x+dx,y+dy,.86));b=a+Vector((dx*.5,dy*.4,height+.10))
        mat=M('pineapple pen '+str(i),color,.45);rod('pineapple coloured pen',a,b,.007,mat)
        rod('pineapple pen cap',b-Vector((0,0,.035)),b+Vector((0,0,.012)),.008,mat)
    a=Vector((x-.025,y+.035,.85));b=Vector((x-.065,y+.04,1.22))
    rod('pineapple brush handle',a,b,.006,M('pineapple brush sage','#a4bd81',.6))
    rod('pineapple brush ferrule',b,b+Vector((-.007,0,.045)),.007,metal)
    ball('pineapple brush bristles',.014,b+Vector((-.009,0,.063)),M('pineapple brush hair','#aa6f32',.8),scale=(.7,.6,1.8))

def bird_of_paradise(rod,curve,variant):
    x,y=(-2.16,.38) if variant=='a' else (2.16,.38)
    sign=-1 if variant=='a' else 1
    pot=M('bird plant ceramic','#c0ad8e',.88);stem=M('bird plant stems','#576f35',.65)
    leaves=[M('bird plant leaf '+str(i),c,.42) for i,c in enumerate(['#416b37','#668548','#355c37'])]
    lathe('plant ceramic pot',[(0,-.39),(.16,-.39),(.205,-.03),(.207,0),(.19,0),(.175,-.06)],pot,(x,y))
    cyl('plant soil',.181,.012,(x,y,-.04),M('bird plant soil','#352a21',1))
    # Upright petioles and broad banana-like blades, rather than small ivy leaves.
    for i,(dx,dy,z,lift) in enumerate([(-.18,.05,1.20,.52),(.05,.05,1.35,.60),(.19,-.05,1.05,.54),(-.14,-.10,.88,.48),(.16,.12,1.22,.56),(-.03,-.12,1.10,.47),(.02,.2,.92,.54)]):
        start=Vector((x,y,-.035));base=Vector((x+dx*sign,y+dy,z))
        curve('bird plant petiole',[tuple(start),tuple(start.lerp(base,.6)+Vector((dx*.3,dy*.4,.03))),tuple(base)],.006,stem)
        direction=Vector((dx*1.5*sign,dy*1.4,lift));side=Vector((1,.35 if i%2 else -.25,0)).normalized()
        vertices=[];rib=[];rows=20
        for j in range(rows+1):
            t=j/rows;center=base+direction*t+Vector((-.025*sign*math.sin(math.pi*t),-.08*math.sin(math.pi*t),.02*math.sin(t*math.pi)))
            width=(.12+(i%3)*.014)*math.sin(math.pi*t)**.56
            if i in [0,3] and j in [7,13]:width*=.64
            rib.append(tuple(center+Vector((0,-.002,.002))))
            for edge in [-1,0,1]:vertices.append(tuple(center+side*width*edge+Vector((0,.025*abs(edge)*math.sin(math.pi*t),-.012*abs(edge)))))
        faces=[(j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k) for j in range(rows) for k in range(2)]
        me=bpy.data.meshes.new('bird long leaf');me.from_pydata(vertices,[],faces);me.update()
        ob=bpy.data.objects.new('plant bird of paradise broad leaf',me);bpy.context.scene.collection.objects.link(ob);me.materials.append(leaves[i%3])
        for poly in me.polygons:poly.use_smooth=True
        ob.modifiers.new('leaf thickness','SOLIDIFY').thickness=.0013
        curve('bird plant leaf vein',rib[::2],.0015,stem)
    orange=M('bird flower orange','#ef8d24',.42);blue=M('bird flower blue','#426ca8',.4);bract=M('bird flower green bract','#6b7942',.58)
    for i,(dx,z) in enumerate([(-.20,1.36),(.08,1.66)]):
        p=Vector((x+dx*sign,y-.14,z))
        curve('bird flower stem',[(x,y,-.03),(x+dx*.5*sign,y-.07,z*.65),tuple(p)],.006,stem)
        direction=Vector((-.19*sign,-.035,.016))
        rod('bird flower beak',p,p+direction,.017,bract)
        for j in range(3):
            start=p+direction*(.2+j*.18)
            end=start+Vector(((-.035+j*.025)*sign,-.015,.12+j*.025))
            ob=cyl('bird flower orange petal',.013,(end-start).length,(start+end)/2,orange,r2=.001,seg=12)
            ob.rotation_euler=(end-start).to_track_quat('Z','Y').to_euler()
        rod('bird flower blue tongue',p+direction*.4,p+direction*1.12+Vector((0,0,.06)),.009,blue)
