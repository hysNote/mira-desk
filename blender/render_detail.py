"""Material inspection: same saved scene, same lights, closer camera. No scene edits saved."""
import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
s.camera.location=(-2.25,-1.65,2.05)
s.camera.rotation_euler=(Vector((-1.435,.31,1.22))-s.camera.location).to_track_quat('-Z','Y').to_euler()
s.camera.data.lens=63
s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.cycles.samples=128
s.render.filepath=str(Path(bpy.data.filepath).parent/'carousel-material.png')
bpy.ops.render.render(write_still=True)
