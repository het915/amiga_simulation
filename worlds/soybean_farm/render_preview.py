"""Render a high-quality Blender preview that mirrors the soybean_farm.sdf
scene.  Key fix vs. prior attempts: Blender's OBJ importer applies a 90 deg
X-axis rotation to convert OBJ Y-up to Blender Z-up.  When we create linked
duplicate objects from the imported mesh, the duplicates do NOT inherit that
rotation, so plants end up lying flat.  Fix: after import we bake the
rotation into vertex data via `transform_apply(rotation=True)`.

Usage:
    blender -b -P render_preview.py -- <sdf_path> <output_png>
"""
import bpy
import sys
import os
import math
import re
import xml.etree.ElementTree as ET
from mathutils import Vector

argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
sdf_path = argv[0]
out_png = argv[1]
sdf_dir = os.path.dirname(os.path.abspath(sdf_path))


# ---- MTL sanitization (Blender 3.0's OBJ importer chokes on map_d) ----
mtl_backups = {}

def import_obj_safe(obj_path):
    """Import an OBJ, working around the map_d bug, and bake the importer's
    90 deg X rotation into vertex data. Returns the joined mesh object."""
    # temporarily strip map_d from any referenced MTLs
    obj_dir = os.path.dirname(os.path.abspath(obj_path))
    with open(obj_path) as f:
        mtls = []
        for line in f:
            if line.startswith("mtllib"):
                mtls += [os.path.join(obj_dir, t.strip()) for t in line.split()[1:]]
    for mtl in mtls:
        if not os.path.exists(mtl) or mtl in mtl_backups:
            continue
        with open(mtl) as f:
            original = f.read()
        sanitized = re.sub(r"^map_d\s.*$", "", original, flags=re.MULTILINE)
        if sanitized != original:
            mtl_backups[mtl] = original
            with open(mtl, "w") as f:
                f.write(sanitized)

    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.obj(filepath=obj_path)
    new_objs = [o for o in bpy.context.scene.objects
                if o not in before and o.type == "MESH"]
    if not new_objs:
        raise RuntimeError(f"no mesh imported from {obj_path}")

    # select and join into one object
    bpy.ops.object.select_all(action="DESELECT")
    for o in new_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = new_objs[0]
    if len(new_objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active

    # KEY FIX: bake the importer's rotation into vertex data
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def restore_mtls():
    for mtl, original in mtl_backups.items():
        with open(mtl, "w") as f:
            f.write(original)


# ---- Parse SDF ----
tree = ET.parse(sdf_path)
world = tree.getroot().find("world")

soybeans = []   # (x, y, yaw, mesh_abs)
trees = []      # (x, y, yaw, scale, mesh_abs)
for model in world.findall("model"):
    name = model.get("name", "")
    mesh_el = model.find(".//mesh")
    if mesh_el is None:
        continue
    uri = mesh_el.findtext("uri").strip()
    mesh_abs = os.path.normpath(os.path.join(sdf_dir, uri))
    pose = model.findtext("pose", "0 0 0 0 0 0").split()
    x, y = float(pose[0]), float(pose[1])
    yaw = float(pose[5])
    scale_el = mesh_el.find("scale")
    scale = 1.0
    if scale_el is not None:
        scale = float(scale_el.text.split()[0])
    if name.startswith("soybean_"):
        soybeans.append((x, y, yaw, mesh_abs))
    elif name.startswith("tree_"):
        trees.append((x, y, yaw, scale, mesh_abs))

print(f"parsed {len(soybeans)} soybeans, {len(trees)} trees")


# ---- Scene setup ----
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = out_png
scene.eevee.taa_render_samples = 64
scene.eevee.use_ssr = True
scene.eevee.use_soft_shadows = True
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

# Sky background
world_data = bpy.data.worlds.new("World")
scene.world = world_data
world_data.use_nodes = True
nt = world_data.node_tree
bg = nt.nodes.get("Background")
bg.inputs[0].default_value = (0.62, 0.78, 0.92, 1.0)
bg.inputs[1].default_value = 1.3


# ---- Ground: grass (big plane) + soil patch (smaller, on top) ----
def make_pbr_plane(name, size, tex_path, location=(0, 0, 0), uv_scale=8):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.object
    obj.name = name
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.95
    if os.path.exists(tex_path):
        img = bpy.data.images.load(tex_path)
        tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = img
        # Scale the UVs by adding a mapping node
        mapping = mat.node_tree.nodes.new("ShaderNodeMapping")
        tex_coord = mat.node_tree.nodes.new("ShaderNodeTexCoord")
        mapping.inputs["Scale"].default_value = (uv_scale, uv_scale, uv_scale)
        mat.node_tree.links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
        mat.node_tree.links.new(mapping.outputs["Vector"], tex_node.inputs["Vector"])
        mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (0.45, 0.30, 0.20, 1.0)
    obj.data.materials.append(mat)
    return obj

grass_tex = os.path.join(sdf_dir, "ground/grass_color_1k.jpg")
soil_tex = os.path.join(sdf_dir, "ground/soil_color_1k.jpg")
make_pbr_plane("grass", 40, grass_tex, uv_scale=10)
make_pbr_plane("soil", 7.5, soil_tex, location=(0, 0, 0.002), uv_scale=3)


# ---- Sun ----
sun_data = bpy.data.lights.new("Sun", type="SUN")
sun = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(35))
sun_data.energy = 4.0
sun_data.angle = math.radians(2.0)  # softer shadows


# ---- Import each unique OBJ ONCE as a template, then instance ----
templates = {}

def get_template(mesh_abs):
    if mesh_abs not in templates:
        obj = import_obj_safe(mesh_abs)
        obj.name = "tpl_" + os.path.basename(mesh_abs)
        obj.hide_render = True  # hide the master
        templates[mesh_abs] = obj
    return templates[mesh_abs]


def place_instance(name, mesh_abs, x, y, yaw, scale=1.0):
    tpl = get_template(mesh_abs)
    inst = bpy.data.objects.new(name, tpl.data)  # shares mesh data
    scene.collection.objects.link(inst)
    inst.location = (x, y, 0)
    inst.rotation_mode = "XYZ"
    inst.rotation_euler = (0, 0, yaw)
    inst.scale = (scale, scale, scale)
    return inst


for i, (x, y, yaw, mesh_abs) in enumerate(soybeans):
    place_instance(f"soy_{i:03d}", mesh_abs, x, y, yaw)
for i, (x, y, yaw, scale, mesh_abs) in enumerate(trees):
    place_instance(f"tree_{i:02d}", mesh_abs, x, y, yaw, scale=scale)

restore_mtls()
bpy.context.view_layer.update()


# ---- Two cameras: hero overview + ground-level close-up ----
def add_camera(name, loc, look, lens):
    d = bpy.data.cameras.new(name)
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = loc
    direction = Vector(look) - Vector(loc)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = direction.to_track_quat("-Z", "Y")
    d.lens = lens
    return o

hero = add_camera("cam_hero", (-5.5, -6.0, 3.8), (0.3, 0.0, 0.3), 32)
# Close-up looking between rows at ground level — stems should be visible
# in the gap. Rows are along Y at X-positions ... -0.25, 0.25, 0.75 ... .
# Position the camera in a row-gap (X=-0.75) looking along +Y through the field.
closeup = add_camera("cam_close", (-0.75, -2.8, 0.08), (-0.75, 2.2, 0.15), 28)

os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

# Render hero
scene.camera = hero
scene.render.filepath = out_png
bpy.ops.render.render(write_still=True)
print(f"RENDERED {out_png}")

# Render close-up alongside (same dir, _close.png)
close_png = os.path.splitext(out_png)[0] + "_close.png"
scene.camera = closeup
scene.render.filepath = close_png
bpy.ops.render.render(write_still=True)
print(f"RENDERED {close_png}")
