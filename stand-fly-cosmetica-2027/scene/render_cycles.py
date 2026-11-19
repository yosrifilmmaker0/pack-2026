"""Photoreal path-traced render of the FLY stand with Blender Cycles.
usage: python3 render_cycles.py VIEW WIDTH HEIGHT SAMPLES OUT.png [exposure]
"""
import bpy, sys, math, time
from mathutils import Vector

VIEW, W, H, SPP, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
EXPO = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="stand.glb")
sc = bpy.context.scene

def principled(mat):
    if not mat.use_nodes: mat.use_nodes = True
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED': return n
    return None
def setin(n, key, val):
    if n and key in n.inputs: n.inputs[key].default_value = val
def find_image(mat):
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE': return n
    return None
def make_emission(mat, color=(1, 0.9, 0.78), strength=10.0, use_image=True):
    mat.use_nodes = True
    nt = mat.node_tree; img = find_image(mat) if use_image else None
    img_img = img.image if img else None
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = strength
    if img_img:
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img_img
        uv = nt.nodes.new('ShaderNodeUVMap')
        nt.links.new(uv.outputs['UV'], tex.inputs['Vector'])
        nt.links.new(tex.outputs['Color'], em.inputs['Color'])
    else:
        em.inputs['Color'].default_value = (*color, 1)
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])

WARM = (1.0, 0.86, 0.70)  # ~3500 K
for mat in bpy.data.materials:
    nm = mat.name; p = principled(mat)
    if p: setin(p, 'Alpha', 1.0)
    if nm.startswith('M_ledSoft'): make_emission(mat, WARM, 6.0, False)
    elif nm.startswith('M_led'): make_emission(mat, WARM, 22.0, False)
    elif nm.startswith('BACKLIT'): make_emission(mat, strength=2.0)
    elif nm.startswith('UNLIT_'):
        hx, k = nm.split('_')[1], float(nm.split('_')[2].split('.')[0] + '.' + nm.split('_')[2].split('.')[1][:2])
        col = tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)); lum = max(col)
        if lum < 0.2: make_emission(mat, (col[0] * 0.4, col[1] * 0.4, col[2] * 0.4), 1.0, False)   # dark ceiling: practically black
        else: make_emission(mat, col, 6.0 * k, False)                                            # hall ceiling lamps
    elif nm.startswith('LOGOALPHA'):
        img = find_image(mat); im = img.image if img else None
        nt = mat.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = im
        nt.links.new(tex.outputs['Color'], bs.inputs['Base Color']); nt.links.new(tex.outputs['Alpha'], bs.inputs['Alpha'])
        bs.inputs['Roughness'].default_value = 0.35; nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    elif nm.startswith('M_floor'):
        setin(p, 'Base Color', (0.78, 0.77, 0.75, 1))
        setin(p, 'Roughness', 0.05); setin(p, 'Coat Weight', 0.7); setin(p, 'Coat Roughness', 0.02); setin(p, 'Specular IOR Level', 0.6)
    elif nm.startswith('M_whiteMatte'): setin(p, 'Roughness', 0.55)
    elif nm.startswith('M_white'): setin(p, 'Base Color', (0.80, 0.79, 0.77, 1)); setin(p, 'Roughness', 0.18); setin(p, 'Coat Weight', 0.5); setin(p, 'Coat Roughness', 0.05)
    elif nm.startswith('M_wood'):
        setin(p, 'Roughness', 0.42); setin(p, 'Coat Weight', 0.15)
        img = find_image(mat)
        if img:
            nt = mat.node_tree; bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15
            nt.links.new(img.outputs['Color'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    elif nm.startswith('CARPET'):
        setin(p, 'Roughness', 1.0); setin(p, 'Specular IOR Level', 0.1)
    elif nm.startswith('GOLD'):
        setin(p, 'Base Color', (0.80, 0.66, 0.46, 1)); setin(p, 'Metallic', 1.0); setin(p, 'Roughness', 0.16)
    elif nm.startswith('PM_amber'):
        setin(p, 'Base Color', (0.62, 0.30, 0.08, 1)); setin(p, 'Transmission Weight', 1.0); setin(p, 'Roughness', 0.02); setin(p, 'IOR', 1.5)
    elif nm.startswith('PM_glassBlue'):
        setin(p, 'Base Color', (0.18, 0.30, 0.62, 1)); setin(p, 'Transmission Weight', 0.85); setin(p, 'Roughness', 0.03)
    elif nm.startswith('PM_frost'): setin(p, 'Transmission Weight', 0.7); setin(p, 'Roughness', 0.32)
    elif nm.startswith('PM_chrome'): setin(p, 'Metallic', 1.0); setin(p, 'Roughness', 0.08)
    elif nm.startswith('PM_whiteGloss'): setin(p, 'Roughness', 0.08); setin(p, 'Coat Weight', 1.0)
    elif nm.startswith('LEAF'):
        setin(p, 'Roughness', 0.42); setin(p, 'Subsurface Weight', 0.15); setin(p, 'Coat Weight', 0.2)
    elif nm.startswith('CUSHION'): setin(p, 'Roughness', 1.0); setin(p, 'Sheen Weight', 0.5)
    elif nm.startswith('CHAIRSHELL'): setin(p, 'Roughness', 0.3)
    elif p and p.inputs['Transmission Weight'].default_value > 0.5:
        setin(p, 'Roughness', 0.02)  # acrylic

# --- world + hall fill light (soft overhead hall lighting, no spots on the stand)
world = bpy.data.worlds.new("hall"); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.010, 0.011, 0.014, 1); bg.inputs['Strength'].default_value = 1.0
def area(name, loc, size, power, color=(1, 0.95, 0.88), rot=(0, 0, 0), shape='SQUARE', sy=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.color = color; ld.shape = shape; ld.size = size
    if sy: ld.shape = 'RECTANGLE'; ld.size_y = sy
    ob = bpy.data.objects.new(name, ld); ob.location = loc; ob.rotation_euler = rot; sc.collection.objects.link(ob); return ob
# hall ceiling grid (high, dim) -> gives the hall its ambient level
for ix in range(-2, 3):
    for iy in range(-2, 2):
        area(f"hall_{ix}_{iy}", (4 + ix * 9, 3.5 + iy * 9, 11.5), 4.0, 220)
# soft key from the aisle side, high (simulates hall light bouncing), stand-friendly
area("aisle_fill", (4, -8, 8), 10, 260, (1, 0.97, 0.92), rot=(math.radians(55), 0, 0))
# reinforce LED lines with true area lights (less noise): ring underside (12 segments)
RC = Vector((4.3, 3.55, 3.75))
for i in range(16):
    a = i / 16 * 2 * math.pi
    o = area(f"ring_{i}", (RC.x + math.sin(a) * 2.95, RC.y + math.cos(a) * 2.95, RC.z - 0.02), 0.2, 28, WARM, sy=1.2, rot=(math.pi, 0, -a)); o.visible_glossy = False; o.visible_camera = False
# halos above central table
area("halo", (4.75, 4.25, 3.15), 1.6, 60, WARM, rot=(math.pi, 0, 0), shape='DISK')
# coves / canopy / portal / niches
area("cove_left", (0.55, 2.5, 2.84), 0.5, 120, WARM, rot=(math.pi, 0, 0), sy=4.6)
area("cove_back", (5.0, 6.7, 3.05), 0.3, 110, WARM, rot=(math.radians(150), 0, 0), sy=1, shape='RECTANGLE')
bpy.data.objects["cove_back"].data.size = 5.8; bpy.data.objects["cove_back"].data.size_y = 0.3
for yy in (2.0, 4.4):
    area(f"niche_{yy}", (0.5, yy, 1.4), 0.25, 18, WARM, rot=(0, math.radians(-90), 0), sy=1.3)

# --- camera (three.js -> blender: (x, y, z) -> (x, -z, y))
views = {
    'front':   ((4.1, 1.7, 7.4),  (4.1, 1.9, -3.4), 55),
    'right34': ((12.6, 2.1, 5.2), (3.9, 1.45, -3.6), 48),
    'left34':  ((-4.2, 2.0, 6.3), (4.6, 1.45, -3.6), 48),
    'aerial':  ((10.5, 9.5, 7.5), (4.0, 0.6, -3.5), 45),
    'inside':  ((6.3, 1.6, -1.8), (1.0, 1.4, -4.6), 62),
    'hero':    ((11.2, 1.6, 5.0), (4.3, 2.05, -3.2), 47),
    'hero2':   ((-3.0, 1.6, 4.8), (4.6, 2.05, -3.4), 50),
}
pos, tgt, fov = views[VIEW]
cv = lambda v: Vector((v[0], -v[2], v[1]))
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = cv(pos); cam.rotation_euler = (cv(tgt) - cv(pos)).to_track_quat('-Z', 'Y').to_euler()
cam_d.sensor_fit = 'VERTICAL'; cam_d.angle_y = math.radians(fov); cam_d.clip_end = 300
cam_d.dof.use_dof = VIEW not in ('aerial',); cam_d.dof.focus_distance = (cv(tgt) - cv(pos)).length * 0.95; cam_d.dof.aperture_fstop = 4.0

# --- render settings
sc.render.engine = 'CYCLES'
cy = sc.cycles; cy.device = 'CPU'; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.015
cy.use_denoising = True
try: cy.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
cy.max_bounces = 10; cy.diffuse_bounces = 4; cy.glossy_bounces = 6; cy.transmission_bounces = 8; cy.transparent_max_bounces = 8
cy.sample_clamp_indirect = 6.0; cy.blur_glossy = 0.6; cy.caustics_reflective = False; cy.caustics_refractive = False
cy.light_sampling_threshold = 0.01
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.film_transparent = False
vs = sc.view_settings
try: vs.view_transform = 'AgX'; vs.look = 'AgX - Medium High Contrast'
except Exception:
    try: vs.look = 'Medium High Contrast'
    except Exception: pass
vs.exposure = EXPO
print('view', vs.view_transform, vs.look)

sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = OUT
print(f"setup {time.time() - t0:.1f}s, objects {len(bpy.data.objects)}", flush=True)
bpy.ops.render.render(write_still=True)
print(f"rendered {OUT} in {time.time() - t0:.1f}s", flush=True)
