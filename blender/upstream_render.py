# Rendering helpers copied from upstream MIT blender/scene.py.
import os
import bpy
from kit import ZMAX, lin, rgb, set_mode

def override_mat(kind):
    mat = bpy.data.materials.new(f"__{kind}")
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if kind == "clay":
        n = nt.nodes.new("ShaderNodeBsdfDiffuse")
        n.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
        nt.links.new(n.outputs[0], out.inputs["Surface"])
        return mat
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    if kind == "id":
        nt.links.new(nt.nodes.new("ShaderNodeObjectInfo").outputs["Color"], em.inputs["Color"])
    elif kind == "normal":
        geo, vt, mad = nt.nodes.new("ShaderNodeNewGeometry"), nt.nodes.new("ShaderNodeVectorTransform"), nt.nodes.new("ShaderNodeVectorMath")
        vt.vector_type, vt.convert_from, vt.convert_to = "NORMAL", "WORLD", "CAMERA"
        mad.operation = "MULTIPLY_ADD"
        mad.inputs[1].default_value, mad.inputs[2].default_value = (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)
        nt.links.new(geo.outputs["Normal"], vt.inputs[0])
        nt.links.new(vt.outputs[0], mad.inputs[0])
        nt.links.new(mad.outputs[0], em.inputs["Color"])
    elif kind == "depth":
        cd, m1, m2 = nt.nodes.new("ShaderNodeCameraData"), nt.nodes.new("ShaderNodeMath"), nt.nodes.new("ShaderNodeMath")
        m1.operation, m2.operation = "DIVIDE", "SUBTRACT"
        m1.inputs[1].default_value, m2.inputs[0].default_value = ZMAX, 1.0
        nt.links.new(cd.outputs["View Z Depth"], m1.inputs[0])
        nt.links.new(m1.outputs[0], m2.inputs[1])
        nt.links.new(m2.outputs[0], em.inputs["Color"])
    return mat


def assign_ids():
    """每个网格一个唯一纯色（通道取 16 的倍数，解码时四舍五入即可）。"""
    table, levels = [], list(range(16, 256, 16))
    n = len(levels)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    assert len(meshes) < n ** 3, "ID 颜色不够用了"
    for i, ob in enumerate(meshes):
        k = i + 1
        c = (levels[k % n], levels[(k // n) % n], levels[(k // (n * n)) % n])
        ob.color = tuple(lin(v / 255) for v in c) + (1.0,)
        table.append({"color": c, "object": ob.name, "hot": ob.get("hot")})
    return table


def set_world(scene, hexcol, strength):
    w = scene.world or bpy.data.worlds.new("world")
    scene.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = rgb(hexcol)
    bg.inputs["Strength"].default_value = strength


def render_pass(scene, name, out, *, mode="albedo", override=None, lights=(), world=("#000000", 0.0), samples=24,
                transform="Standard", fmt="PNG", depth="8", denoise=False, box_filter=False):
    set_mode(mode)
    bpy.context.view_layer.material_override = override
    for ob in bpy.data.objects:
        if ob.type == "LIGHT":
            ob.hide_render = ob["group"] not in lights
    set_world(scene, *world)
    cy = scene.cycles
    cy.samples, cy.use_denoising, cy.use_adaptive_sampling = min(samples, scene.get("sample_limit", samples)), denoise, False
    cy.pixel_filter_type, cy.filter_width = ("BOX", 0.01) if box_filter else ("BLACKMAN_HARRIS", 1.5)
    scene.view_settings.view_transform, scene.view_settings.look = transform, "None"
    ims = scene.render.image_settings
    try:
        ims.media_type = "IMAGE"
    except Exception:
        pass
    ims.file_format, ims.color_mode, ims.color_depth = fmt, "RGB", depth
    if fmt == "OPEN_EXR":
        ims.exr_codec = "ZIP"
    scene.render.filepath = os.path.join(out, name)
    bpy.ops.render.render(write_still=True)
    print("PASS", name)


