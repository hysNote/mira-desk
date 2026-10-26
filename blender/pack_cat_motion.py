"""Pack Blender-rendered frames as seekable browser videos; no pose edits here."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'build/cat-motion';out=ROOT/'site/assets/cat-motion';out.mkdir(exist_ok=True)
meta=json.loads((src/'manifest.json').read_text())
for name,size in [('close',(800,650)),('beauty',(meta['width'],meta['height']))]:
    s=bpy.data.scenes.new('Cat '+name+' video');bpy.context.window.scene=s
    s.render.resolution_x=size[0];s.render.resolution_y=size[1];s.render.resolution_percentage=100;s.render.fps=12;s.frame_start=1;s.frame_end=meta['frames']
    s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.film_transparent=False
    seq=s.sequence_editor_create();strip=seq.strips.new_image('Native cat frames',str(src/'000'/f'{name}.png'),channel=1,frame_start=1)
    # Image sequence elements are relative to one directory; use packed copies.
    import shutil
    folder=src/('sequence-'+name);folder.mkdir(exist_ok=True)
    for i in range(meta['frames']):shutil.copyfile(src/f'{i:03d}'/f'{name}.png',folder/f'{i:03d}.png')
    strip.directory=str(folder);strip.elements[0].filename='000.png'
    for i in range(1,meta['frames']):strip.elements.append(f'{i:03d}.png')
    strip.frame_final_duration=meta['frames']
    s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE'
    s.render.filepath=str(out/f'{name}.mp4');bpy.ops.render.render(animation=True)
meta['duration_ms']=meta['frames']/12*1000
(out/'motion.json').write_text(json.dumps(meta,indent=2))
print('CAT_VIDEOS_READY',flush=True)
