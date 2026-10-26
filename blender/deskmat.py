"""Mira's reference-derived orange tiger mat: shaped mesh, textile top, bound edge."""
import json
import bpy
from kit import M, MATS

def build_deskmat(root):
    data=json.loads((root/'build/textures/tiger-deskmat-outline.json').read_text())
    width=1.85; depth=width*data['height']/data['width']
    points=data['points']; n=len(points)
    verts=[((u-.5)*width,(v-.5)*depth,z) for z in [.755,.750] for u,v in points]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    faces += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    mesh=bpy.data.meshes.new('tiger mat silhouette');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new('tiger deskmat textile',mesh);bpy.context.scene.collection.objects.link(ob)
    ob.location=(.28,-.48,0)
    top=M('tiger textile',rough=.91,image='tiger-deskmat.png')
    edge=M('tiger bound edge','#bd5a1b',.9)
    mesh.materials.append(top);mesh.materials.append(edge)
    uv=mesh.uv_layers.new(name='Reference top view')
    for poly in mesh.polygons:
        poly.material_index=0 if poly.index==0 else 1
        for li in poly.loop_indices:uv.data[li].uv=points[mesh.loops[li].vertex_index%n]
    bevel=ob.modifiers.new('soft fabric edge','BEVEL');bevel.width=.0008;bevel.segments=2;bevel.material=1
    nt=top.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=450
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00025
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],MATS[top.name]['beauty'].inputs['Normal'])
    return ob
