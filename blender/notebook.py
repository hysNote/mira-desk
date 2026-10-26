"""A small handwritten AI journal, real paper edges, ribbon and fountain pen."""
import math
import bpy
from mathutils import Matrix, Vector
from kit import M, slab, plane, cyl, ball

def build_notebook(rounded,rod,curve):
    x,y=.65,.13
    cloth=M('journal sage cloth','#657360',.91)
    paper=M('journal paper edges','#e9e0c8',.91)
    ink=M('journal fountain pen','#273e3d',.27)
    brass=M('journal pen brass','#c9a362',.28,metal=.65)
    slab('journal back cover',.45,.515,.005,.016,(x,y,.754),cloth,hot='notebook')
    slab('journal paper block',.428,.493,.022,.012,(x+.003,y,.7675),paper,hot='notebook')
    for z in [.760,.764,.768,.772,.776]:
        curve('journal page edge',[(x-.203,y-.246,z),(x+.12,y-.246,z),(x+.215,y-.235,z)],.00045,M('journal page line','#b9ad92',1),'notebook')
    slab('journal front cover',.45,.515,.005,.016,(x,y,.781),cloth,hot='notebook')
    plane('journal handwritten cover',.425,.488,(x+.005,y,.784),M('journal cover print',image='notebook-cover.png',rough=.9),rot=(-math.pi/2,0,0),hot='notebook')
    rounded('journal spine',(.024,.51,.032),(x-.213,y,.768),cloth,hot='notebook',r=.008)
    curve('journal bookmark',[(x+.13,y-.18,.779),(x+.13,y-.26,.757),(x+.145,y-.32,.753)],.006,M('journal ribbon','#aa7554',.9),'notebook')
    # Pen is beside the book, with a cap, clip and nib rather than a loose stick.
    a=Vector((x+.28,y-.18,.764)); b=Vector((x+.29,y+.18,.764))
    rod('journal pen body',a,b,.006,ink,'notebook')
    rod('journal pen cap',b,b+Vector((.003,.09,0)),.008,ink,'notebook')
    rod('journal pen clip',b+Vector((.008,0,.006)),b+Vector((.01,.075,.006)),.0015,brass,'notebook')
    rod('journal pen nib',a,a-Vector((0,.024,0)),.003,brass,'notebook')
    pivot=Vector((x,y,.75));transform=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-11),4,'Z')@Matrix.Translation(-pivot)
    bpy.context.view_layer.update()
    for ob in bpy.data.objects:
        if ob.get('hot')=='notebook':ob.matrix_world=transform@ob.matrix_world
    old=bpy.data.objects.get('pen')
    if old:bpy.data.objects.remove(old,do_unlink=True)
