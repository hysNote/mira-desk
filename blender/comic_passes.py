"""Feed the original comic compositor with genuine scene geometry/light passes."""
import json
import bpy
from kit import set_mode
from upstream_render import assign_ids, override_mat, render_pass

def render_comic_passes(scene, directory):
    directory.mkdir(parents=True,exist_ok=True)
    ids=assign_ids()
    (directory/'scene.json').write_text(json.dumps({'ids':ids,'surfaces':{}}),encoding='utf8')
    render_pass(scene,'albedo',str(directory),mode='albedo',samples=16)
    render_pass(scene,'emit',str(directory),mode='emit',samples=16)
    render_pass(scene,'id',str(directory),override=override_mat('id'),samples=1,box_filter=True)
    render_pass(scene,'normal',str(directory),override=override_mat('normal'),samples=16,transform='Raw')
    render_pass(scene,'depth',str(directory),override=override_mat('depth'),samples=16,transform='Raw',depth='16')
    clay=override_mat('clay')
    for group in ['sun','sky']:
        render_pass(scene,'light_'+group,str(directory),mode='beauty',override=clay,lights=(group,),world=('#cfeaff',.12) if group=='sky' else ('#000000',0),samples=48,transform='Raw',fmt='OPEN_EXR',depth='16',denoise=True)
    set_mode('beauty')
    for ob in bpy.data.objects:
        if ob.type=='LIGHT': ob.hide_render=False
    scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.12
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_depth='8'
