"""Reference-inspired tufted meadow rug with a soft, asymmetric cream outline."""
import math,random
import bpy
from kit import M,MATS,ball

def build_flower_rug(floor_z):
    colors=['#e4d8aa','#8eaa55','#52682f']
    materials=[]
    for i,c in enumerate(colors):
        mat=M('flower rug wool '+str(i),c,.99);nt=mat.node_tree
        noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=170;noise.inputs['Detail'].default_value=3
        bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.6;bump.inputs['Distance'].default_value=.004
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],MATS[mat.name]['beauty'].inputs['Normal']);materials.append(mat)
    n=160;verts=[];cy=-.20
    for scale,z in [(1,floor_z), (1,floor_z+.012),(.94,floor_z+.012),(.85,floor_z+.012)]:
        for j in range(n):
            a=math.tau*j/n;c=math.cos(a);s=math.sin(a)
            wobble=1+.025*math.sin(5*a+.5)+.018*math.sin(9*a)
            verts.append((2.82*math.copysign(abs(c)**.55,c)*scale*wobble,cy+1.64*math.copysign(abs(s)**.55,s)*scale*wobble,z))
    faces=[];mi=[]
    for ring in range(3):
        for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j));mi.append(0 if ring<2 else 1)
    faces.append(tuple(range(3*n,4*n)));mi.append(2)
    mesh=bpy.data.meshes.new('flower rug organic outline');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new('room woven rug',mesh);bpy.context.scene.collection.objects.link(ob)
    for mat in materials:mesh.materials.append(mat)
    for poly,i in zip(mesh.polygons,mi):poly.material_index=i
    flowers=[M('flower rug petals '+str(i),c,.98) for i,c in enumerate(['#d99d9c','#d5bd66','#83a6ae','#e09b42','#e8c5a0'])]
    rng=random.Random(34)
    # Keep the raised tufts away from all four feet. Flowers continue under the
    # desk, with several visible at its front and sides in the homepage crop.
    positions=[(-2.30,-.55),(-2.10,-1.04),(-2.25,.32),(-1.85,-1.35),(-1.15,-1.36),(-.42,-1.25),(.3,-1.38),(1,-1.28),(1.75,-1.24),(2.25,-.75),(2.32,-.05),(2.20,.56),(-.55,.83),(.40,.9),(-1.20,-.35),(-.50,-.47),(.30,-.32),(1.0,-.45),(1.70,-.35),(-2.15,.06),(2.20,0)]
    for i,(x,y) in enumerate(positions):
        radius=rng.uniform(.065,.11);mat=flowers[i%len(flowers)]
        for j in range(5):
            a=j*math.tau/5+.2
            ball('room rug flower petal',radius,(x+radius*.65*math.cos(a),y+radius*.65*math.sin(a),floor_z+.014),mat,scale=(.85,.85,.075))
        ball('room rug flower center',radius*.33,(x,y,floor_z+.022),flowers[(i+2)%len(flowers)],scale=(1,1,.14))
    return ob
