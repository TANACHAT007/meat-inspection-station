"""STEP -> web GLB with one node per module (merged by colour inside each module) + modules.json.
Needs: pip install cascadio trimesh numpy.  Run: python make_glb.py"""
import json, os, re, numpy as np, trimesh, cascadio
H = os.path.dirname(os.path.abspath(__file__))
STEP = os.path.join(H, '..', '06_cad_export', 'meat-quality-sorting-conveyor_assembly.step')
raw = os.path.join(H, '_raw.glb')
assert cascadio.step_to_glb(STEP, raw, tol_linear=0.4, tol_angular=0.5) == 0
sc = trimesh.load(raw)
MODS = [  # key, Thai name, components
 ('frame', 'โครงอะลูมิเนียม 2020', ('Frame_2020', 'Bracket_2020')),
 ('conveyor', 'สายพานและลูกกลิ้ง', ('Belt', 'Rollers', 'Shafts_Bearings', 'Bearing_Blocks', 'Bed_Deck', 'Bed_Supports', 'Shaft_Coupler')),
 ('drive', 'ชุดขับมอเตอร์', ('DC_Gearmotor', 'Motor_Bracket', 'Motor_Cable', 'Wire_Duct')),
 ('tunnel', 'อุโมงค์ปิดแสงและไฟ', ('Tunnel_Panels', 'Tunnel_Posts', 'Light_Seal', 'Lighting', 'Roof_Rails', 'Cassettes', 'Ref_Tiles')),
 ('sensing', 'กล้องและเซนเซอร์', ('Camera', 'Sensor', 'Sensor_Boards', 'Lid_Connectors', 'Connectors_Cables')),
 ('control', 'กล่องควบคุมและไฟเข้า', ('Ctrl_Box_A_PSU', 'Ctrl_Box_B_Control', 'PSU_Bucks', 'Control_Board', 'Mains_Inlet')),
 ('meat', 'แพ็กเนื้อวัว', ('Meat_Pack',)),
 ('fasteners', 'น็อตและสกรู', ()),
]
def mod_of(top):
    nm = top.split(':')[0]
    for k, _, comps in MODS:
        if any(nm.startswith(c) for c in comps): return k
    return 'fasteners'
def parents(n):
    p = []
    while True:
        par = sc.graph.transforms.parents.get(n)
        if par is None or par == sc.graph.base_frame: break
        p.append(par); n = par
    return list(reversed(p))
groups = {k: {} for k, _, _ in MODS}
for node in sc.graph.nodes_geometry:
    T, g = sc.graph[node]
    ps = parents(node); top = ps[1] if len(ps) > 1 else node
    m = sc.geometry[g].copy(); m.apply_transform(T)
    try:
        c = np.array(m.visual.material.baseColorFactor, float); c = c / (255.0 if c.max() > 1 else 1.0)
    except Exception:
        c = np.array([.6, .6, .6, 1.])
    groups[mod_of(top)].setdefault(tuple(np.round(c, 2)), []).append(m)
out = trimesh.Scene(); info = []
for k, th, _ in MODS:
    n = 0
    for i, (c, ms) in enumerate(groups[k].items()):
        m = trimesh.util.concatenate(ms); n += len(m.faces)
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=list(c), metallicFactor=0.1, roughnessFactor=0.6, alphaMode='BLEND' if c[3] < 0.99 else 'OPAQUE'))
        out.add_geometry(m, node_name=f'{k}__{i}')
    info.append({'key': k, 'th': th, 'tris': n})
out.export(os.path.join(H, 'machine.glb'))
json.dump(info, open(os.path.join(H, 'modules.json'), 'w'), ensure_ascii=False, indent=1)
print(info, round(os.path.getsize(os.path.join(H, 'machine.glb')) / 1e6, 1), 'MB')
os.remove(raw)
