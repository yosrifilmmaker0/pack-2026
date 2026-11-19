import json, struct, sys
d = open('stand.glb', 'rb').read()
magic, ver, ln = struct.unpack('<III', d[:12]); jl, jt = struct.unpack('<II', d[12:20])
js = json.loads(d[20:20 + jl]); rest = d[20 + jl:]
n = 0
for m in js.get('materials', []):
    ext = m.get('extensions', {})
    if 'KHR_materials_volume' in ext: del ext['KHR_materials_volume']; n += 1
    if not ext and 'extensions' in m: del m['extensions']
js['extensionsUsed'] = [e for e in js.get('extensionsUsed', []) if e != 'KHR_materials_volume']
if 'extensionsRequired' in js: js['extensionsRequired'] = [e for e in js['extensionsRequired'] if e != 'KHR_materials_volume']
jb = json.dumps(js, separators=(',', ':')).encode(); jb += b' ' * ((4 - len(jb) % 4) % 4)
out = struct.pack('<III', magic, ver, 12 + 8 + len(jb) + len(rest)) + struct.pack('<II', len(jb), jt) + jb + rest
open('stand.glb', 'wb').write(out); print('removed volume from', n, 'materials;', len(js.get('meshes', [])), 'meshes')
