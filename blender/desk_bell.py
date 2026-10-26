"""Mira's yellow/red counter bell, sitting on the right of the monitor riser."""
import math
import bpy
from kit import M, cyl, torus


def build_bell(curve):
    x, y, z = .83, .405, 1.0025
    yellow = M('bell golden yellow enamel', '#ffc21d', .24, metal=.12)
    red = M('bell cherry red enamel', '#ef2424', .29)
    gold = M('bell arches yellow', '#ffd044', .35)
    dark = M('bell underside rubber', '#402e29', .78)
    for material in (yellow, red):
        bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Coat Weight'].default_value = .32
        bsdf.inputs['Coat Roughness'].default_value = .2
    cyl('style bell rubber foot', .108, .007, (x,y,z+.0035), dark, hot='style')
    cyl('style bell red base', .119, .018, (x,y,z+.015), red, hot='style', seg=64)
    torus('style bell rolled red rim', .113, .007, (x,y,z+.022), red, hot='style', seg=64)
    # A revolved profile gives the shallow, round shoulder in the real photo.
    profile=[(.116,.023),(.117,.03),(.115,.045),(.108,.063),(.096,.081),(.08,.098),(.058,.111),(.035,.117),(0,.12)]
    verts=[];faces=[];segments=96
    for radius,height in profile:
        verts.extend((x+radius*math.cos(i*math.tau/segments),y+radius*math.sin(i*math.tau/segments),z+height) for i in range(segments))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    mesh=bpy.data.meshes.new('bell rounded shell');mesh.from_pydata(verts,[],faces);mesh.materials.append(yellow)
    shell=bpy.data.objects.new('style bell yellow dome',mesh);bpy.context.scene.collection.objects.link(shell);shell['hot']='style'
    for face in mesh.polygons:face.use_smooth=True
    cyl('style bell button stem', .017, .016, (x,y,z+.122), red, hot='style')
    cyl('style bell red push button', .045, .012, (x,y,z+.137), red, hot='style', seg=64)
    torus('style bell button rounded lip', .042, .003, (x,y,z+.141), red, hot='style', seg=64)
    # Small golden double arch, on the upward-facing button, facing the visitor.
    points=[(-.027,-.023),(-.023,.013),(-.015,.023),(-.006,.016),(0,-.018),(.006,.016),(.015,.023),(.023,.013),(.027,-.023)]
    curve('style bell golden arches',[(x+a,y+b,z+.144) for a,b in points],.0028,gold,hot='style')
