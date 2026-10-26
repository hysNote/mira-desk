"""Hand-modelled details for Mira's existing objects; no extra desk clutter."""
import math
import bpy
from kit import M, MATS, rgb, cyl, ball, torus, plane

def finish_materials(wood,pearl,brown):
    # These colors feed BOTH physical and illustration passes.
    for mat,scale,lo,hi in [(wood,(1.8,22,8),'#aa784b','#d5b27f'),(brown,(100,100,100),'#76503d','#9e6a48')]:
        nt=mat.node_tree; tex=nt.nodes.new('ShaderNodeTexCoord'); mul=nt.nodes.new('ShaderNodeVectorMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=scale
        noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3; noise.inputs['Detail'].default_value=2; noise.inputs['Roughness'].default_value=.65
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=rgb(lo); ramp.color_ramp.elements[1].color=rgb(hi)
        nt.links.new(tex.outputs['Generated'],mul.inputs[0]); nt.links.new(mul.outputs[0],noise.inputs['Vector']); nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        entry=MATS[mat.name]
        nt.links.new(ramp.outputs['Color'],entry['albedo'].inputs['Color']); nt.links.new(ramp.outputs['Color'],entry['beauty'].inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.16; bump.inputs['Distance'].default_value=.003
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs[0],entry['beauty'].inputs['Normal'])
    nt=pearl.node_tree; lw=nt.nodes.new('ShaderNodeLayerWeight'); ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=rgb('#a5adbc'); ramp.color_ramp.elements[1].color=rgb('#dedbd5')
    e=ramp.color_ramp.elements.new(.38); e.color=rgb('#cfc3c4')
    nt.links.new(lw.outputs['Facing'],ramp.inputs[0])
    for mode,sock in [('beauty','Base Color'),('albedo','Color')]: nt.links.new(ramp.outputs[0],MATS[pearl.name][mode].inputs[sock])
    bs=MATS[pearl.name]['beauty']
    for name,value in [('Metallic',.55),('Roughness',.215),('IOR',1.52),('Coat Weight',.55),('Coat Roughness',.12),('Anisotropic IOR Level',.20),('Thin Film Thickness',310),('Thin Film IOR',1.32)]:
        if name in bs.inputs: bs.inputs[name].default_value=value
    # Extremely fine satin surface, well below the size of the sculpted relief.
    tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=260; tex.inputs['Detail'].default_value=2
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.065; bump.inputs['Distance'].default_value=.0005
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs[0],bs.inputs['Normal'])

def carousel(cx,cy,pearl,rounded,rod,curve):
    """Reference-inspired pearl-white photo carousel, with scalloped crown and relief."""
    accent=pearl
    shadow=M('carousel recessed pearl','#b8b9c9',.36,metal=.28)
    def lathe(name,profile,material,scallop=0):
        n=128; verts=[]
        for radius,z in profile:
            for j in range(n):
                a=math.tau*j/n
                dz=scallop*math.cos(8*a) if radius>.25 else 0
                verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z+dz))
        faces=[(r*n+j,r*n+(j+1)%n,(r+1)*n+(j+1)%n,(r+1)*n+j) for r in range(len(profile)-1) for j in range(n)]
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
        ob=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(ob); mesh.materials.append(material); ob['hot']='life'
        for p in mesh.polygons:p.use_smooth=True
        bevel=ob.modifiers.new('soft cast edges','BEVEL'); bevel.width=.0018; bevel.segments=3
        return ob
    lathe('carousel sculpted pedestal',[(0,.762),(.265,.762),(.29,.78),(.295,.80),(.277,.817),(.275,.85),(.25,.867),(0,.867)],pearl)
    for z,r in [(.778,.286),(.809,.28),(.852,.267)]:torus('carousel turned moulding',r,.004,(cx,cy,z),accent,hot='life',seg=96,sub=8)
    for j in range(56):
        a=math.tau*j/56
        ball('carousel base bead',.006,(cx+.29*math.cos(a),cy+.29*math.sin(a),.795),accent,hot='life')
    cyl('carousel central column',.021,.61,(cx,cy,1.15),pearl,hot='life')
    for z in [.885,1.34]:
        cyl('carousel column collar',.039,.018,(cx,cy,z),accent,hot='life')
        torus('carousel column collar ring',.036,.004,(cx,cy,z+.012),pearl,hot='life')
    lathe('carousel swept canopy',[(.018,1.62),(.05,1.59),(.08,1.525),(.16,1.465),(.25,1.425),(.301,1.452),(.31,1.425),(.30,1.365),(.276,1.35)],pearl,.018)
    # Crown edge follows the eight lobes instead of a plain conical roof.
    for z,r in [(1.446,.304),(1.363,.29)]:
        pts=[(cx+r*math.cos(a),cy+r*math.sin(a),z+.018*math.cos(8*a)) for a in [math.tau*j/96 for j in range(97)]]
        curve('carousel scalloped rim',pts,.0055,accent,'life')
    for j in range(8):
        a=math.tau*j/8
        # Radial ribs in the concave roof.
        curve('carousel roof petal',[(cx+r*math.cos(a),cy+r*math.sin(a),z) for r,z in [(.04,1.60),(.10,1.51),(.18,1.46),(.26,1.45),(.302,1.467)]],.004,accent,'life')
        # Pairs of scrolls sculpted onto the vertical crown band.
        for sign in [-1,1]:
            pts=[]
            for k in range(30):
                t=k/29*math.pi*2; rad=.023*(1-k/40)
                u=sign*(.028+rad*math.cos(t)); z=1.401+rad*math.sin(t)
                pts.append((cx+.307*math.cos(a)-u*math.sin(a),cy+.307*math.sin(a)+u*math.cos(a),z))
            curve('carousel acanthus curl',pts,.005,accent,'life')
        # Base garland and a small raised teardrop.
        pts=[]
        for k in range(17):
            t=a-.27+.54*k/16; pts.append((cx+.279*math.cos(t),cy+.279*math.sin(t),.835-.013*math.sin(math.pi*k/16)))
        curve('carousel base garland',pts,.0035,accent,'life')
        ball('carousel base floral relief',.012,(cx+.283*math.cos(a),cy+.283*math.sin(a),.839),accent,scale=(.6,.6,1.2),hot='life')
    for a in [0,math.pi]:
        ball('carousel finial leaf',.039,(cx+.018*math.cos(a),cy,1.635),pearl,scale=(.55,.6,1.35),rot=(0,.3 if a==0 else -.3,0),hot='life')
    for i,a in enumerate([-.62,.83,2.52,4.07]):
        x=cx+.202*math.sin(a); y=cy-.202*math.cos(a)
        rod('carousel hanging rod',(x,y,1.39),(x,y,1.29),.0038,accent,'life')
        torus('carousel photo hook',.011,.0025,(x,y,1.287),accent,rot=(math.pi/2,0,a),hot='life')
        # Photo bodies have thickness, an inset border and a wide Polaroid lower margin.
        rounded('carousel photo frame',(.18,.014,.287),(x,y,1.127),pearl,hot='life',r=.004,rot=(0,0,a))
        plane('carousel photo recess',.163,.231,(x+.008*math.sin(a),y-.008*math.cos(a),1.142),shadow,rot=(0,0,a),hot='life')
        plane('carousel hanging photograph',.151,.215,(x+.009*math.sin(a),y-.009*math.cos(a),1.142),M('carousel photo image '+str(i),image=('carousel.jpg' if i%2 else 'desk.jpg')),rot=(0,0,a),hot='life')
        plane('carousel photo caption',.132,.018,(x+.009*math.sin(a),y-.009*math.cos(a),1.008),M('photo caption '+str(i),image='caption.png'),rot=(0,0,a),hot='life')

def object_details(rounded,rod,curve,dark,silver,gold,brown,pearl):
    # Lens focus barrel and small controls, rather than an unbroken cylinder.
    x,y=1,-.33
    for j in range(36):
        a=math.tau*j/36
        rod('camera lens knurl',(x-.02+.086*math.cos(a),y-.165,.865+.086*math.sin(a)),(x-.02+.086*math.cos(a),y-.12,.865+.086*math.sin(a)),.0017,dark,'photos')
    for r in [.045,.06,.073]:torus('camera optical ring',r,.0018,(x-.02,y-.219,.865),silver,rot=(math.pi/2,0,0),hot='photos')
    ball('camera lens reflection',.025,(x-.04,y-.224,.89),M('lens reflected sky','#739fba',.1,metal=.7),scale=(1,.08,.35),hot='photos')
    for dx in [-.11,.075]:
        cyl('camera control dial',.025,.014,(x+dx,y+.007,.98),silver,hot='photos')
        for j in range(12):
            a=math.tau*j/12
            ball('camera dial groove',.0025,(x+dx+.024*math.cos(a),y+.007+.024*math.sin(a),.983),dark,hot='photos')
    plane('camera maker badge',.10,.024,(x-.065,y-.063,.935),M('camera badge',image='camera-badge.png'),hot='photos')
    # Tangible leather stitching. Each short stitch follows the wallet rotation.
    x,y=1.47,-.45; a=-.15
    def pt(u,v):return (x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a),.811)
    thread=M('wallet thread','#ddbc87',.85)
    for u in [-.125+j*.014 for j in range(19)]:
        for v in [-.084,.084]:rod('wallet stitch',pt(u,v),pt(u+.006,v),.0009,thread,'travel')
    # Small brass clasp on the existing wallet.
    ball('wallet brass button',.009,pt(.11,0),gold,scale=(1,1,.25),hot='travel')
    # Teacup rim, glazed colour and fine tray rings.
    for r in [.195,.208]:torus('tea tray groove',r,.0017,(1.43,.35,.791),brown,seg=72,sub=6)
    # Airpod case seam/charging LED. No new loose objects.
    curve('earbuds case seam',[(.545,-.463,.80),(.59,-.467,.80),(.635,-.463,.80)],.0009,silver)
    ball('earbuds charging light',.0015,(.59,-.468,.79),gold)

