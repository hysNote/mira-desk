"""Render saved room overview; never overwrite homepage camera or save this view."""
from pathlib import Path
import bpy
s=bpy.context.scene
s.camera=bpy.data.objects['Room overview']
s.render.resolution_x=1600;s.render.resolution_y=1200
s.cycles.samples=96
s.render.filepath=str(Path(bpy.data.filepath).parent/'room-overview.png')
bpy.ops.render.render(write_still=True)
