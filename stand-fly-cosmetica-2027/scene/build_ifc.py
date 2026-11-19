"""FLY & Partners stand — Cosmetica Africa 2027 (CCD05, 8 x 7 m) as IFC4 for Revit.
Plan coords: x = 0..8 along the main facade (left->right seen from the aisle), y = depth 0..7 (facade at y=0).
"""
import math, sys
import numpy as np
import ifcopenshell, ifcopenshell.guid
import ifcopenshell.api as api
import ifcopenshell.api.project, ifcopenshell.api.root, ifcopenshell.api.unit, ifcopenshell.api.context, ifcopenshell.api.aggregate, ifcopenshell.api.geometry, ifcopenshell.api.style, ifcopenshell.api.spatial

OUT = sys.argv[1] if len(sys.argv) > 1 else "stand.ifc"
f = api.project.create_file(version="IFC4")
project = api.root.create_entity(f, ifc_class="IfcProject", name="FLY & Partners - Cosmetica Africa 2027 - CCD05")
length = api.unit.add_si_unit(f, unit_type="LENGTHUNIT")
area = api.unit.add_si_unit(f, unit_type="AREAUNIT")
api.unit.assign_unit(f, units=[length, area])
model = api.context.add_context(f, context_type="Model")
body = api.context.add_context(f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model)
site = api.root.create_entity(f, ifc_class="IfcSite", name="Cosmetica Africa 2027")
bldg = api.root.create_entity(f, ifc_class="IfcBuilding", name="Hall - Stand CCD05")
storey = api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Niveau stand")
api.aggregate.assign_object(f, relating_object=project, products=[site])
api.aggregate.assign_object(f, relating_object=site, products=[bldg])
api.aggregate.assign_object(f, relating_object=bldg, products=[storey])
for o in (site, bldg, storey):
    api.geometry.edit_object_placement(f, product=o, matrix=np.eye(4))

STYLES = {}
def style(name, rgb, transparency=0.0):
    if name in STYLES: return STYLES[name]
    s = api.style.add_style(f, name=name)
    api.style.add_surface_style(f, style=s, ifc_class="IfcSurfaceStyleShading",
        attributes={"SurfaceColour": {"Name": None, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]}, "Transparency": transparency})
    STYLES[name] = s; return s
WHITE = ("Laque blanche brillante", (0.95, 0.95, 0.94))
WOOD = ("Chene clair", (0.78, 0.63, 0.47))
LED = ("Diffuseur LED / backlight", (1.0, 0.98, 0.92))
BLUE = ("Bleu FLY", (0.11, 0.24, 0.55))
GREEN = ("Vegetal", (0.28, 0.45, 0.25))
FLOOR = ("Sol stratifie blanc brillant", (0.91, 0.90, 0.89))
GREY = ("Gris porte", (0.84, 0.83, 0.81))

P3 = lambda x, y, z: f.createIfcCartesianPoint((float(x), float(y), float(z)))
P2 = lambda x, y: f.createIfcCartesianPoint((float(x), float(y)))
def axis3(x=0, y=0, z=0): return f.createIfcAxis2Placement3D(P3(x, y, z), None, None)
UP = f.createIfcDirection((0.0, 0.0, 1.0))

def poly_profile(pts):
    pts = [P2(*p) for p in pts] + [P2(*pts[0])]
    return f.createIfcArbitraryClosedProfileDef("AREA", None, f.createIfcPolyline(pts))
def rect_pts(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def arc(cx, cy, r, a0, a1, n=16):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def rounded_rect(x0, y0, x1, y1, r_fl=0, r_fr=0, r_br=0, r_bl=0):
    pts = []
    pts += arc(x0 + r_fl, y0 + r_fl, r_fl, math.pi, 1.5 * math.pi) if r_fl else [(x0, y0)]
    pts += arc(x1 - r_fr, y0 + r_fr, r_fr, 1.5 * math.pi, 2 * math.pi) if r_fr else [(x1, y0)]
    pts += arc(x1 - r_br, y1 - r_br, r_br, 0, 0.5 * math.pi) if r_br else [(x1, y1)]
    pts += arc(x0 + r_bl, y1 - r_bl, r_bl, 0.5 * math.pi, math.pi) if r_bl else [(x0, y1)]
    return pts

def solid(profile, z0, h):
    return f.createIfcExtrudedAreaSolid(profile, axis3(0, 0, z0), UP, float(h))

def element(ifc_class, name, solids, st, predefined=None, description=None):
    el = api.root.create_entity(f, ifc_class=ifc_class, name=name, predefined_type=predefined)
    if description: el.Description = description
    api.geometry.edit_object_placement(f, product=el, matrix=np.eye(4))
    rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", solids if isinstance(solids, list) else [solids])
    api.geometry.assign_representation(f, product=el, representation=rep)
    api.style.assign_representation_styles(f, shape_representation=rep, styles=[style(*st)])
    api.spatial.assign_container(f, relating_structure=storey, products=[el])
    return el

def box(ifc_class, name, x0, y0, x1, y1, z0, h, st, **kw):
    return element(ifc_class, name, solid(poly_profile(rect_pts(x0, y0, x1, y1)), z0, h), st, **kw)
def cyl(ifc_class, name, cx, cy, r, z0, h, st, **kw):
    prof = f.createIfcCircleProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx, cy), None), float(r))
    return element(ifc_class, name, solid(prof, z0, h), st, **kw)
def ring(ifc_class, name, cx, cy, r, t, z0, h, st, **kw):
    prof = f.createIfcCircleHollowProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx, cy), None), float(r), float(t))
    return element(ifc_class, name, solid(prof, z0, h), st, **kw)

F = 0.105  # finished floor height (raised floor)

# --- raised floor 8 x 7, rounded front corners, LED shadow gap
element("IfcSlab", "Plancher technique 8x7 m (h=10.5 cm)", solid(poly_profile(rounded_rect(0, 0, 8, 7, 0.6, 0.6)), 0.03, 0.075), FLOOR, predefined="FLOOR",
        description="Plancher sureleve, finition blanc brillant, nez arrondi R600 en facade")
element("IfcBuildingElementProxy", "Ruban LED sous plancher (ombre lumineuse)", solid(poly_profile(rounded_rect(0.04, 0.04, 7.96, 6.96, 0.56, 0.56)), 0.0, 0.03), LED)

# --- back wall, left wall, storage room
box("IfcWall", "Cloison fond (h=3.00)", 2.0, 6.85, 8.0, 7.0, F, 3.0, WHITE)
element("IfcWall", "Cloison gauche FREY&LAU / NOURYON (h=2.80)", solid(poly_profile(rounded_rect(0, 0.05, 0.16, 5.0, 0.08, 0.08)), F, 2.8), WHITE)
res_pts = [(0, 5.0)] + arc(2.0 - 0.45, 5.0 + 0.45, 0.45, 1.5 * math.pi, 2 * math.pi) + [(2.0, 7.0), (0, 7.0)]
inner = [(0.1, 5.1)] + arc(1.9 - 0.35, 5.1 + 0.35, 0.35, 1.5 * math.pi, 2 * math.pi) + [(1.9, 6.85), (0.1, 6.85)]
prof = poly_profile(res_pts); prof_in = f.createIfcArbitraryProfileDefWithVoids("AREA", "Reserve", prof.OuterCurve,
    [f.createIfcPolyline([P2(*p) for p in inner] + [P2(*inner[0])])])
element("IfcWall", "Reserve 2x2 m - cloisons (h=3.00)", solid(prof_in, F, 3.0), WHITE, description="Reserve 2,00 x 2,00 m, angle arrondi R450")
door = box("IfcDoor", "Porte reserve 0.86 x 2.10", 1.96, 5.71, 2.01, 6.59, F, 2.1, GREY)
door.OverallHeight, door.OverallWidth = 2.1, 0.86
sp = api.root.create_entity(f, ifc_class="IfcSpace", name="Reserve", predefined_type="INTERNAL")
api.geometry.edit_object_placement(f, product=sp, matrix=np.eye(4))
rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid(poly_profile(inner), F, 2.9)])
api.geometry.assign_representation(f, product=sp, representation=rep)
api.aggregate.assign_object(f, relating_object=storey, products=[sp])

# --- backlit displays (fabric lightboxes, LED edge-lit)
def lightbox(name, x0, y0, x1, y1, z0, h, desc):
    box("IfcFurnishingElement", name, x0, y0, x1, y1, z0, h, LED, description=desc)
lightbox("Backlight FLY 3000x2000", 3.75, 6.77, 6.85, 6.85, F + 0.7, 2.1, "Caisson lumineux textile backlight, visuel FLY 'Cosmetic Ingredients'")
lightbox("Backlight FREY & LAU 1250x1750", 0.16, 0.30, 0.24, 1.60, F + 0.63, 1.85, "Caisson lumineux textile backlight FREY & LAU")
lightbox("Backlight NOURYON 1250x1750", 0.16, 2.70, 0.24, 4.00, F + 0.63, 1.85, "Caisson lumineux textile backlight NOURYON")
# curved NOURYON totem (cintre R420)
_cx, _cy, _r, _th = 7.65, 2.65 + 0.42 - 0.05, 0.42, 0.62 / 0.42
_o = [(_cx + _r * math.sin(a), _cy - _r * math.cos(a)) for a in [(-_th / 2 + _th * i / 24) for i in range(25)]]
_i = [(_cx + (_r - 0.06) * math.sin(a), _cy - (_r - 0.06) * math.cos(a)) for a in [(_th / 2 - _th * i / 24) for i in range(25)]]
element("IfcFurnishingElement", "Totem cintre backlight NOURYON 620x2000", solid(poly_profile(_o + _i), F + 1.05, 2.0), LED, description="Totem lumineux cintre R420, textile backlight NOURYON")
lightbox("Backlight NOURYON lateral 1900x900", 7.95, 0.60, 8.0, 2.50, F + 0.07, 0.9, "Visuel lumineux NOURYON cote allee laterale")

# --- sample presenters: arched niches (FREY & LAU d=2.0, NOURYON d=4.4)
for nm, yc in (("FREY & LAU", 2.0), ("NOURYON", 4.4)):
    box("IfcFurniture", f"Presentoir echantillons {nm} - niche arche", 0.16, yc - 0.53, 0.44, yc + 0.53, F, 2.18, WHITE,
        description="Niche en arche, fond chene, 3 tablettes retroeclairees LED + console basse")
    for k, zz in enumerate((0.75, 1.15, 1.55)):
        box("IfcFurniture", f"Tablette LED {nm} {k+1}", 0.17, yc - 0.45, 0.42, yc + 0.45, F + zz, 0.025, LED)
box("IfcMember", "Fin bois separation zones", 0.16, 2.495, 0.51, 2.545, F, 2.6, WOOD)

# --- wood slats + bench on back wall
for x0, x1 in ((2.2, 3.35), (7.15, 7.95)):
    n = int((x1 - x0) / 0.09)
    for i in range(n + 1):
        xc = x0 + i * 0.09
        box("IfcMember", "Tasseau chene 45x70", xc - 0.0225, 6.745, xc + 0.0225, 6.815, F, 2.7, WOOD)
element("IfcFurniture", "Banquette chene sous backlight FLY", solid(poly_profile(rect_pts(3.7, 6.375, 6.9, 6.825)), F + 0.12, 0.32), WOOD)

# --- reception counter FLY / FREY & LAU (pill shape)
cnt = [(5.9, 0.25), (7.25, 0.25), (7.25, 1.05), (5.9, 1.05)] + arc(5.9, 0.65, 0.4, 0.5 * math.pi, 1.5 * math.pi)[1:-1]
top = [(5.9, 0.2), (7.3, 0.2), (7.3, 1.1), (5.9, 1.1)] + arc(5.9, 0.65, 0.45, 0.5 * math.pi, 1.5 * math.pi)[1:-1]
element("IfcFurniture", "Comptoir accueil FLY | FREY & LAU", solid(poly_profile(cnt), F + 0.06, 1.02), WHITE,
        description="Comptoir laque blanc, socle LED en retrait, logos FLY + FREY & LAU en facade")
element("IfcFurniture", "Plateau chene comptoir", solid(poly_profile(top), F + 1.08, 0.04), WOOD)

# --- NOURYON corner presenter
element("IfcFurniture", "Presentoir angle NOURYON (h=1.00)", solid(poly_profile(rounded_rect(7.35, 0.35, 7.95, 2.8, 0.3, 0.25, 0.1, 0.1)), F, 1.0), WHITE)
element("IfcFurniture", "Plateau chene presentoir NOURYON", solid(poly_profile(rounded_rect(7.33, 0.33, 7.97, 2.82, 0.3, 0.26, 0.1, 0.1)), F + 1.0, 0.03), WOOD)

# --- 3 tables x 4 chairs
for i, (tx, ty) in enumerate(((6.95, 4.25), (4.75, 4.25), (2.85, 2.35)), 1):
    cyl("IfcFurniture", f"Table {i} - plateau chene D840", tx, ty, 0.42, F + 0.72, 0.03, WOOD, predefined="TABLE")
    cyl("IfcFurniture", f"Table {i} - pied tulipe", tx, ty, 0.05, F, 0.72, WHITE)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cx, cy = tx + math.sin(a) * 0.62, ty - math.cos(a) * 0.62
        c = math.cos(a); s = math.sin(a)
        def rot(px, py): return (cx + px * c - py * s, cy + px * s + py * c)
        seat = [rot(-0.23, -0.22), rot(0.23, -0.22), rot(0.23, 0.22), rot(-0.23, 0.22)]
        back = [rot(-0.23, 0.17), rot(0.23, 0.17), rot(0.23, 0.22), rot(-0.23, 0.22)]
        element("IfcFurniture", f"Chaise T{i}-{k+1}", [solid(poly_profile(seat), F + 0.42, 0.06), solid(poly_profile(back), F + 0.48, 0.35)], WHITE, predefined="CHAIR")

# --- planters
for nm, (px, py, r, h, ph) in {"Grand pot facade gauche": (1.25, 0.4, 0.25, 0.6, 0.95), "Grand pot facade centre": (3.85, 0.4, 0.25, 0.6, 0.95),
                               "Grand pot fond": (3.2, 6.45, 0.27, 0.8, 1.5), "Arbre angle fond droit": (7.55, 6.3, 0.32, 0.9, 1.9),
                               "Grand pot cote droit": (7.65, 5.0, 0.25, 0.7, 1.2)}.items():
    cyl("IfcFurnishingElement", f"{nm} - jardiniere blanche", px, py, r, F, h, WHITE)
    cyl("IfcFurnishingElement", f"{nm} - vegetal", px, py, r * 1.5, F + h, ph, GREEN)

# --- suspended ring header + LED halos (rigging from hall ceiling)
ring("IfcBuildingElementProxy", "Couronne suspendue FLY D6100 h850", 4.3, 3.55, 3.05, 0.2, 3.75, 0.85, WHITE,
     description="Couronne textile tendue, logos FLY / FREY & LAU / NOURYON, anneau LED en sous-face. Accroche plafond (rigging) a valider avec l'organisateur")
ring("IfcBuildingElementProxy", "Anneau LED sous couronne", 4.3, 3.55, 3.05, 0.2, 3.73, 0.02, LED)
ring("IfcLightFixture", "Halo LED D2100", 4.75, 4.25, 1.05, 0.05, F + 3.23, 0.05, LED)
ring("IfcLightFixture", "Halo LED D1500", 4.75, 4.25, 0.75, 0.05, F + 2.98, 0.05, LED)

# --- architecture details (v3)
ring("IfcCovering", "Incrustation circulaire chene au sol R2920", 4.3, 3.55, 2.92, 0.12, F, 0.002, WOOD, predefined="FLOORING")
element("IfcCovering", "Auvent lumineux espaces partenaires", solid(poly_profile(rounded_rect(0.16, 0.15, 0.95, 4.85, 0, 0.35, 0.35, 0)), F + 2.75, 0.09), WHITE, predefined="CEILING",
        description="Auvent laque blanc, sous-face LED diffusante")
for nm, (x0, x1, z0, z1) in {"haut": (3.5, 7.1, F + 3.0, F + 3.05), "bas": (3.5, 7.1, F + 0.45, F + 0.5)}.items():
    box("IfcBuildingElementProxy", f"Cadre portail FLY - traverse {nm}", x0, 6.71, x1, 6.85, z0, z1 - z0 if z1 > z0 else 0.05, WHITE)
for nm, (x0, x1) in {"gauche": (3.5, 3.74), "droite": (6.86, 7.1)}.items():
    box("IfcBuildingElementProxy", f"Cadre portail FLY - montant {nm}", x0, 6.71, x1, 6.85, F + 0.45, 2.6, WHITE)
def slat(x, y, a, h=2.85):
    c, s_ = math.cos(a), math.sin(a)
    pts = [(x + px * c - py * s_, y + px * s_ + py * c) for px, py in ((-0.02, -0.03), (0.02, -0.03), (0.02, 0.03), (-0.02, 0.03))]
    element("IfcMember", "Tasseau chene cintre reserve", solid(poly_profile(pts), F, h), WOOD)
xx = 0.25
while xx < 1.55: slat(xx, 4.96, 0); xx += 0.075
a = -math.pi / 2
while a <= 0.001: slat(1.55 + math.cos(a) * 0.49, 5.45 + math.sin(a) * 0.49, -(a + math.pi / 2)); a += 0.075 / 0.49

f.write(OUT)
print("written", OUT, len(list(f.by_type("IfcProduct"))), "products")
