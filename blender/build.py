"""Mira desk using the upstream MIT geometry kit and comic render pipeline."""
import os, sys, math, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['DESK_TEXTURE_DIR']=str(ROOT/'build/textures')
sys.path.insert(0,str(Path(__file__).parent))
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
from kit import M, MATS, SURFACES, box, slab, plane, cyl, ball, torus, rgb, lin, set_mode

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
def rounded(name,size,loc,mat,hot=None,r=.012,rot=(0,0,0)):
    ob=box(name,size,loc,mat,hot=hot,rot=rot)
    mod=ob.modifiers.new('soft edges','BEVEL'); mod.width=r; mod.segments=3
    ob.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return ob
def rod(name,a,b,r,mat,hot=None):
    a,b=Vector(a),Vector(b)
    return cyl(name,r,(b-a).length,(a+b)/2,mat,rot=(b-a).to_track_quat('Z','Y').to_euler(),hot=hot)
def curve(name,pts,r,mat,hot=None):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); s.collection.objects.link(ob); ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    if hot: ob['hot']=hot
    return ob
cream=M('warm porcelain','#eee7d9',.6); wood=M('pale oak','#c9a274',.6)
dark=M('charcoal','#222c2d',.4); silver=M('aluminium','#b9c6c8',.3,metal=.65)
pearl=M('pearl','#f4eddf',.32,metal=.18); gold=M('gold','#d4a34f',.25,metal=.7)
glass=M('crystal','#b3d8d7',.22,metal=.4); brown=M('leather','#8c5536',.85)
fur=M('cat taupe','#998777',.95); white=M('ivory fur','#ede6dc',.95)
pink=M('ear pink','#c49b93',.85); green=M('sage','#617964',.8)
# Large clean window and simple sky, intentionally no city, cables, lamp or board.
from room import build_room
room_dimensions=build_room(rounded,wood,dark)
sky=plane('sky',8,5,(1.5,1.3,2.0),M('sky',image='sky.png',emit=0))
sky.visible_shadow=False
windowmat=M('painted blue window','#547780',.7)
for x in [-.85,.72,2.28,3.85]: rounded('window mullion',(.028,.07,2.26),(x,.88,1.71),windowmat)
for z in [.60,2.82]: rounded('window rail',(4.75,.07,.028),(1.5,.88,z),windowmat)
rounded('window sill',(4.8,.22,.065),(1.5,.80,.69),cream)
slab('desktop',3.8,1.04*(3.8/2.5),.09,.07,(0,-.02,.705),wood)
# Riser with readable legs and storage void.
rounded('riser top',(2.24,.4,.055),(0,.36,.975),wood)
for x in [-1,1]: rounded('riser leg',(.055,.36,.19),(x,.36,.86),wood)
rounded('riser lower lip',(2.0,.36,.025),(0,.36,.767),wood)
# Main monitor / resume, central and above laptop.
rounded('monitor foot',(.40,.22,.026),(0,.38,1.017),dark,hot='resume')
rounded('monitor neck',(.08,.065,.25),(0,.43,1.12),dark,hot='resume')
rounded('monitor bezel',(1.40,.055,.85),(0,.43,1.62),dark,hot='resume',r=.025)
plane('resume screen',1.34,.754,(0,.399,1.645),M('resume pixels',image='monitor.png',emit=0),hot='resume',surface='resume')
# Laptop lower front, built-in keyboard only.
slab('laptop base',.88,.49,.028,.024,(0,-.39,.776),silver,hot='about')
rounded('laptop lid',(.87,.028,.55),(0,-.12,1.052),silver,hot='about',r=.016)
plane('intro screen',.81,.506,(0,-.138,1.055),M('intro pixels',image='laptop.png',emit=0),hot='about',surface='about')
rounded('trackpad',(.29,.11,.002),(0,-.54,.792),M('trackpad','#aab7b9',.4),hot='about',r=.008)
for row in range(4):
    for col in range(13): rounded('laptop key',(.047,.031,.006),(-.344+col*.057,-.25-row*.043,.795),dark,hot='about',r=.004)
rounded('spacebar',(.25,.026,.006),(0,-.425,.795),dark,hot='about',r=.004)
# Three small award shapes on left end of raised shelf.
for i,x in enumerate([-.91,-.74,-.56]):
    cyl('award base',.058,.035,(x,.32,1.025),dark,hot='awards')
    cyl('award stem',.014,.10,(x,.32,1.09),gold,hot='awards')
    if i==0:
        # Star extruded in XZ plane.
        vs=[]
        for y in [.305,.335]:
            for j in range(10):
                a=math.pi/2+j*math.pi/5; r=.073 if j%2==0 else .035
                vs.append((x+r*math.cos(a),y,1.21+r*math.sin(a)))
        faces=[tuple(range(9,-1,-1)),tuple(range(10,20))]+[(j,(j+1)%10,(j+1)%10+10,j+10) for j in range(10)]
        me=bpy.data.meshes.new('star'); me.from_pydata(vs,[],faces); ob=bpy.data.objects.new('star award',me); s.collection.objects.link(ob); ob.data.materials.append(gold); ob['hot']='awards'
    elif i==1: cyl('crystal prize',.055,.23,(x,.32,1.15),glass,r2=0,seg=5,hot='awards')
    else: torus('round prize',.055,.013,(x,.32,1.19),gold,rot=(math.pi/2,0,0),hot='awards')
# Reference-inspired sculpted carousel with suspended photo frames.
from refinement import carousel, finish_materials, object_details
finish_materials(wood,pearl,brown)
carousel(-1.42,.35,pearl,rounded,rod,curve)
# Stylized resting cat, placeholder likeness, curled tail and closed eyes.
cx,cy=-1.34,-.42
ball('cat body',.27,(cx,cy,.87),fur,scale=(1.32,.8,.55),hot='cat')
ball('white flank',.22,(cx-.07,cy-.015,.9),white,scale=(1,.75,.45),hot='cat')
ball('cat head',.135,(cx+.23,cy-.07,.89),fur,scale=(1,.9,.88),hot='cat')
ball('muzzle',.075,(cx+.23,cy-.17,.865),white,scale=(1,.55,.55),hot='cat')
for dx in [.15,.31]:
    cyl('cat ear',.06,.12,(cx+dx,cy-.03,1.025),fur,r2=.005,seg=3,hot='cat')
    ball('ear inner',.026,(cx+dx,cy-.064,1.028),pink,scale=(.7,.2,1),hot='cat')
for dx in [.18,.28]: curve('sleeping eye',[(cx+dx-.022,cy-.172,.922),(cx+dx,cy-.18,.913),(cx+dx+.022,cy-.172,.922)],.003,dark,'cat')
ball('nose',.011,(cx+.23,cy-.211,.87),pink,hot='cat')
curve('curled tail',[(cx-.30,cy+.04,.84),(cx-.29,cy-.18,.80),(cx-.09,cy-.23,.80),(cx+.10,cy-.20,.81)],.048,fur,'cat')
ball('rounded tail tip',.048,(cx+.10,cy-.20,.81),fur,hot='cat')
for dx in [.18,.27]:ball('resting paw',.041,(cx+dx,cy-.16,.787),white,scale=(1.12,.9,.5),hot='cat')
for i in range(4): curve('fur marking',[(cx-.18+i*.09,cy+.10,.96),(cx-.15+i*.09,cy+.01,1.00),(cx-.13+i*.09,cy-.05,.97)],.014,fur,'cat')
# Camera at right, lens toward viewer.
x,y=1.0,-.33
rounded('camera body',(.30,.12,.20),(x,y,.87),dark,hot='photos',r=.025)
rounded('camera grip',(.07,.145,.22),(x+.13,y-.01,.87),dark,hot='photos')
rounded('camera viewfinder',(.10,.10,.05),(x-.01,y,.989),dark,hot='photos')
for r,h,yy,mat in [(.092,.09,y-.09,dark),(.087,.07,y-.16,silver),(.079,.018,y-.203,dark),(.067,.004,y-.215,M('lens glass','#234c55',.12,metal=.6))]:
    cyl('lens',r,h,(x-.02,yy,.865),mat,rot=(math.pi/2,0,0),hot='photos')
torus('lens ring',.074,.004,(x-.02,y-.22,.865),dark,rot=(math.pi/2,0,0),hot='photos')
cyl('shutter',.022,.009,(x+.10,y,.99),silver,hot='photos')
curve('camera strap',[(x+.15,y,.82),(x+.24,y-.05,.76),(x+.19,y-.25,.76),(x+.10,y-.28,.76)],.012,brown,'photos')
# Wallet remains visible to the right of computer, banknotes are blank placeholders.
rounded('wallet',(.30,.21,.045),(1.47,-.45,.783),brown,hot='travel',rot=(0,0,-.15),r=.015)
rounded('wallet seam',(.276,.19,.003),(1.47,-.45,.808),M('leather inset','#a37450',.9),hot='travel',rot=(0,0,-.15),r=.01)
for i,col in enumerate(['#b9cbb1','#d6bcaa']): rounded('blank note',(.25,.12,.001),(1.49,-.42+i*.025,.81+i*.002),M('note'+str(i),col),hot='travel',rot=(0,0,-.13+i*.08),r=.002)
# Tea is static decor for this MVP. No weather controls.
tx,ty=1.43,.35
glaze=M('celadon tea glaze','#6b9f9b',.2,metal=.15)
cyl('tea tray',.245,.028,(tx,ty,.775),wood)
torus('tray rim',.23,.012,(tx,ty,.795),wood)
ball('teapot',.095,(tx-.09,ty+.015,.88),glaze,scale=(1,1,.8))
cyl('pot lid',.065,.012,(tx-.09,ty+.015,.96),glaze)
ball('lid knob',.017,(tx-.09,ty+.015,.979),wood)
rod('spout',(tx-.17,ty,.88),(tx-.22,ty,.94),.023,glaze)
torus('pot handle',.065,.012,(tx-.005,ty+.015,.88),glaze,rot=(math.pi/2,0,0))
cyl('teacup',.052,.065,(tx+.105,ty-.06,.835),glaze,r2=.063)
cyl('tea surface',.056,.002,(tx+.105,ty-.06,.869),M('tea','#82512d',.2))
torus('cup lip',.06,.004,(tx+.105,ty-.06,.870),glaze)
torus('cup handle',.023,.006,(tx+.167,ty-.06,.835),glaze,rot=(math.pi/2,0,0))
# Small everyday objects: earbuds and pen, purely decorative.
rounded('earbuds case',(.10,.075,.045),(.59,-.43,.784),pearl,r=.02)
for i in range(2):
    ball('earbud',.015,(.59+i*.045,-.53,.766),pearl)
    cyl('earbud stem',.006,.04,(.60+i*.045,-.54,.765),pearl,rot=(0,math.pi/2,0))
rod('pen',(1.10,-.66,.758),(1.38,-.64,.758),.006,gold)
object_details(rounded,rod,curve,dark,silver,gold,brown,pearl)
from personal_decor import replace_wallet, build_decor
replace_wallet(rounded)
# Arrange complete objects around their own pivots, including surface metadata.
# Deliberate modest asymmetry: someone's desk in use, not a centered product display.
def arrange(selector,pivot,yaw,offset=(0,0,0)):
    p=Vector(pivot); transform=Matrix.Translation(p+Vector(offset))@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Translation(-p)
    bpy.context.view_layer.update()
    for ob in list(bpy.data.objects):
        if selector(ob): ob.matrix_world=transform@ob.matrix_world
arrange(lambda o:o.get('hot')=='about',(0,-.3,.75),-6,(-.20,.28,0))
arrange(lambda o:o.name.startswith('riser'),(0,.36,.75),0,(0,.06,0))
arrange(lambda o:o.get('hot')=='resume',(0,.43,1.0),7,(.10,.015,0))
arrange(lambda o:o.get('hot')=='awards',(-.74,.32,1.0),0,(-.12,.10,0))
arrange(lambda o:o.get('hot')=='photos',(1,-.33,.75),24,(-.02,.05,0))
arrange(lambda o:o.get('hot')=='travel',(1.47,-.45,.75),-22,(-.05,.06,0))
arrange(lambda o:o.get('hot')=='life',(-1.42,.35,.75),-9,(-.015,-.04,0))
arrange(lambda o:o.get('hot')=='cat',(-1.34,-.42,.75),12,(-.03,-.035,0))
arrange(lambda o:o.name.startswith('earbud'),(.59,-.43,.75),-23,(.11,.065,0))
from deskmat import build_deskmat
build_deskmat(ROOT)
layout_variant=os.environ.get('MIRA_LAYOUT','b').lower()
assert layout_variant in {'a','b','c'}
build_decor(rounded,rod,curve,layout_variant)
# Bring the bin inward and slide the complete tea set forward to leave clearance.
tea_prefixes=('tea tray','tray rim','teapot','pot lid','lid knob','spout','pot handle','teacup','tea surface','cup lip','cup handle')
arrange(lambda o:o.name.startswith(tea_prefixes),(1.43,.35,.75),0,(0,-.20,0))
from notebook import build_notebook
build_notebook(rounded,rod,curve)
if layout_variant=='b':
    from desk_bell import build_bell
    build_bell(curve)
# Match upstream's optical framing, scaled about the tabletop for Mira's wider desk.
# Moving only the camera backward flattened the previous version's desktop view.
reference_scale=3.8/2.5
reference_anchor=Vector((0,0,.75)); desk_anchor=Vector((0,-.02,.75))
def reference_point(point):
    return desk_anchor+reference_scale*(Vector(point)-reference_anchor)
camd=bpy.data.cameras.new('visitor perspective'); cam=bpy.data.objects.new('visitor perspective',camd); s.collection.objects.link(cam)
cam.location=reference_point((0,-1.70,2.56)); target=reference_point((.05,.14,1.06)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); camd.type='PERSP'; camd.lens=23; camd.sensor_width=36; s.camera=cam
def area(name,loc,power,size,color):
    ld=bpy.data.lights.new(name,'AREA'); lo=bpy.data.objects.new(name,ld); s.collection.objects.link(lo); lo.location=loc; lo.rotation_euler=(Vector((0,0,.8))-lo.location).to_track_quat('-Z','Y').to_euler(); ld.energy=power; ld.shape='DISK'; ld.size=size; ld.color=color
area('soft fill',(0,-1.3,3.7),55,3.4,(.82,.9,1))
area('warm window key',(-2.8,-1.35,3.5),240,1.7,(1,.91,.79))
area('cool window rim',(-.4,.72,3.15),90,1.3,(.75,.87,1))
key=bpy.data.objects['warm window key']; key.data.shape='RECTANGLE'; key.data.size=1.7; key.data.size_y=.65
key.rotation_euler=(Vector((-1.1,.25,1.18))-key.location).to_track_quat('-Z','Y').to_euler()
rim=bpy.data.objects['cool window rim']; rim.rotation_euler=(Vector((-1.4,.3,1.2))-rim.location).to_track_quat('-Z','Y').to_euler()
for ob in bpy.data.objects:
    if ob.type=='LIGHT': ob['group']='sky'
sun_data=bpy.data.lights.new('sun','SUN'); sun=bpy.data.objects.new('sun',sun_data); s.collection.objects.link(sun)
sun_data.energy=2.4; sun_data.angle=math.radians(3); sun_data.color=(1,.88,.75)
sun.rotation_euler=Vector((-.55,-.65,-.45)).to_track_quat('-Z','Y').to_euler(); sun['group']='sun'
s.world.color=(.65,.65,.65); s.world.use_nodes=True; bg=s.world.node_tree.nodes.get('Background'); bg.inputs[0].default_value=(.68,.77,.8,1); bg.inputs[1].default_value=.12
s.render.engine='CYCLES'; s.cycles.samples=128; s.cycles.use_denoising=True
try:
    p=bpy.context.preferences.addons['cycles'].preferences; p.compute_device_type='OPTIX'; p.get_devices()
    for dev in p.devices: dev.use=dev.type=='OPTIX'
    if any(dev.type=='OPTIX' for dev in p.devices): s.cycles.device='GPU'
except Exception: pass
s.render.resolution_x=1920; s.render.resolution_y=1080; s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'; s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGB'
s.world.node_tree.nodes.get('Background').inputs[0].default_value=rgb('#cfeaff')
OUT=ROOT/'site/assets'; OUT.mkdir(parents=True,exist_ok=True)
set_mode('beauty'); s.render.filepath=str(OUT/'scene.png'); bpy.ops.render.render(write_still=True)
# Exact visible-pixel object map, same ID-image principle as upstream.
keys=['about','resume','awards','photos','life','travel','cat','notebook']
if layout_variant=='b': keys.append('style')
for ob in bpy.data.objects:
    v=(keys.index(ob['hot'])+1)*28 if ob.get('hot') in keys else 0
    ob.color=(lin(v/255),0,0,1)
mat=bpy.data.materials.new('hotspot emission'); mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
oi=nt.nodes.new('ShaderNodeObjectInfo'); em=nt.nodes.new('ShaderNodeEmission'); out=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(oi.outputs['Color'],em.inputs['Color']); nt.links.new(em.outputs[0],out.inputs['Surface'])
bpy.context.view_layer.material_override=mat; s.view_settings.view_transform='Standard'; s.cycles.samples=1; s.cycles.use_denoising=False; s.cycles.pixel_filter_type='BOX'; s.cycles.filter_width=.01
s.render.filepath=str(OUT/'hot.png'); bpy.ops.render.render(write_still=True)
bpy.context.view_layer.update()
def px(v):
    p=world_to_camera_view(s,cam,v); return [round(p.x*s.render.resolution_x,2),round((1-p.y)*s.render.resolution_y,2)]
surfaces={k:[px(ob.matrix_world@v) for v in corners] for k,(ob,corners) in SURFACES.items()}
(OUT/'scene.json').write_text(json.dumps({'width':s.render.resolution_x,'height':s.render.resolution_y,'keys':keys,'surfaces':surfaces}),encoding='utf8')
from comic_passes import render_comic_passes
render_comic_passes(s,ROOT/'build/passes')
bpy.context.view_layer.material_override=None; s.view_settings.view_transform='AgX'; s.cycles.samples=128; s.cycles.use_denoising=True; s.cycles.pixel_filter_type='BLACKMAN_HARRIS'; s.cycles.filter_width=1.5
s.render.filepath=str(OUT/'scene.png'); bpy.ops.file.pack_all()
# A second camera makes the complete room easy to inspect without moving the homepage camera.
overview_data=bpy.data.cameras.new('Room overview');overview=bpy.data.objects.new('Room overview',overview_data);s.collection.objects.link(overview)
overview.location=(3.6,-7.6,4.9); overview.rotation_euler=(Vector((0,-.7,1.1))-overview.location).to_track_quat('-Z','Y').to_euler();overview_data.lens=40
# Save a useful native inspection view and separate architectural/desk collections.
groups={name:bpy.data.collections.new(name) for name in ['01 Room shell','02 Desk and supports','03 Personal objects','04 Lighting and camera']}
for group in groups.values():s.collection.children.link(group)
for ob in list(s.objects):
    name='04 Lighting and camera' if ob.type in {'LIGHT','CAMERA'} else ('01 Room shell' if ob.name.startswith(('room ','window ','sky')) else ('03 Personal objects' if ob.get('hot') else '02 Desk and supports'))
    groups[name].objects.link(ob)
    for coll in list(ob.users_collection):
        if coll!=groups[name]:coll.objects.unlink(ob)
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA'
            a.spaces.active.region_3d.view_camera_zoom=10
            a.spaces.active.overlay.show_overlays=False
            a.spaces.active.shading.type='MATERIAL'
            a.spaces.active.shading.use_scene_world=True
            a.spaces.active.shading.use_scene_lights=True
(ROOT/'build/room-dimensions.json').write_text(json.dumps(room_dimensions,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'build/mira-desk.blend'))
print('MIRA_SCENE_COMPLETE')
