"""A real cutaway room, following upstream build_room/build_desk construction.

Keep Mira's broad rear window. All walls, floor, rug and desk supports are meshes.
The open front is the viewing side of this architectural cutaway.
"""
import bpy
from kit import M, slab, rgb

def build_room(rounded,wood,dark):
    # Scale the reference room's floor distance about the .75 tabletop, too.
    # Otherwise identical camera optics still show short legs and too much floor.
    floor_z=.75*(1-3.8/2.5)
    wall=M('room warm plaster','#dfdbce',.95)
    trim=M('room painted skirting','#ece6d8',.68)
    steel=M('desk support charcoal','#344448',.4,metal=.25)
    # Side returns lie outside the homepage frustum, as in the open reference loft.
    rounded('room floor foundation',(9.34,4.45,.12),(0,-1.15,floor_z-.075),M('floor joint','#867a69',.95),r=.01)
    for j in range(27):
        x=-4.49+j*.346
        for k in range(3):
            length=1.48; y=-2.625+k*1.48
            color=['#bcb09a','#c5b8a2','#c0b39d','#cbbda6'][(j+k*3)%4]
            rounded('room oak floorboard',(.343,length-.003,.025),(x,y,floor_z-.0125),M('floor oak '+str((j+k*3)%4),color,.78),r=.001)
    # Back wall is built around the actual window opening, not a plane behind it.
    rounded('room rear low wall',(9.3,.18,.56-floor_z),(0,1.02,(.56+floor_z)/2),wall,r=.012)
    rounded('room rear header',(9.3,.18,.32),(0,1.02,3.02),wall,r=.012)
    # A broad offset window balances warm plaster against a cooler outdoor view.
    for left,right in [(-4.65,-.85),(3.85,4.65)]:
        rounded('room window pier',(right-left,.18,2.30),((left+right)/2,1.02,1.71),wall,r=.012)
    for x in [-4.65,4.65]:
        rounded('room side wall',(.18,4.45,3.18-floor_z),(x,-1.15,(3.18+floor_z)/2),wall,r=.012)
        rounded('room side skirting',(.025,4.30,.095),(x+(.105 if x<0 else -.105),-1.17,floor_z+.0475),trim,r=.003)
    rounded('room rear skirting',(9.14,.025,.095),(0,.914,floor_z+.0475),trim,r=.003)
    # The recess has a real head and side reveals; existing blue window stays.
    rounded('room window reveal top',(4.75,.20,.055),(1.5,.91,2.87),trim,r=.004)
    for x in [-.875,3.875]:rounded('room window reveal side',(.055,.20,2.31),(x,.91,1.715),trim,r=.004)
    # Low woven rug grounds the four feet, as in the upstream room.
    rugmat=M('room woven rug','#536e80',.98)
    nt=rugmat.node_tree; noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=180
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.001
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs[0],next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
    from flower_rug import build_flower_rug
    build_flower_rug(floor_z)
    # Four feet touch rug top. Top of each leg meets the desk underside at z=.66.
    for x in [-1.67,1.67]:
        for y in [-.65,.54]:
            rounded('desk grounded foot',(.095,.095,.018),(x,y,floor_z+.021),dark,r=.006)
            rounded('desk support leg',(.065,.065,.63-floor_z),(x,y,(.69+floor_z)/2),steel,r=.006)
    for x in [-1.67,1.67]:rounded('desk side apron',(.055,1.25,.075),(x,-.055,.6225),steel,r=.004)
    rounded('desk rear apron',(3.39,.055,.075),(0,.54,.6225),steel,r=.004)
    rounded('desk front apron',(3.39,.045,.045),(0,-.65,.6375),steel,r=.004)
    # Organise the native file for easy inspection rather than a long flat object list.
    return {'floor_z':floor_z,'rug_top_z':floor_z+.012,'feet_bottom_z':floor_z+.012,'leg_top_z':.66,'desktop_underside_z':.66}

