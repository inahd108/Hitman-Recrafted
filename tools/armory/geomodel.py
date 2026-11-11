"""Bedrock-geometry gun models built from code, with painted textures and a preview renderer.

Coordinates are Bedrock model space (what TACZ reads): y up, the muzzle points to -z,
the shooter stands at +z and the shooter's right hand side is -x. One unit is one
model pixel. Internally faces, painting and rendering work in Blockbench space
(x mirrored, bone rotations (-rx, -ry, rz) applied in Z*Y*X order), which is how
Blockbench and TACZ interpret the Bedrock format.
"""
import json
import math

import numpy as np
from PIL import Image

FACES = ('north', 'south', 'east', 'west', 'up', 'down')


# ----------------------------------------------------------------------------
# model structure
# ----------------------------------------------------------------------------
class Cube:
    def __init__(self, lo, hi, mat, inflate=0.0, pivot=None, rotation=None, faces=FACES, data=None):
        self.lo = [float(min(a, b)) for a, b in zip(lo, hi)]
        self.hi = [float(max(a, b)) for a, b in zip(lo, hi)]
        self.mat = mat
        self.inflate = inflate
        self.pivot = list(pivot) if pivot is not None else None
        self.rotation = list(rotation) if rotation is not None else None
        self.faces = tuple(faces)
        self.data = data or {}
        self.uv = {}

    @property
    def size(self):
        return [h - l for l, h in zip(self.lo, self.hi)]


class Part:
    def __init__(self, model, name, parent, pivot, rotation):
        self.model = model
        self.name = name
        self.parent = parent
        self.pivot = [float(v) for v in pivot]
        self.rotation = [float(v) for v in rotation] if rotation else None
        self.cubes = []

    def box(self, lo, hi, mat, **kw):
        c = Cube(lo, hi, mat, **kw)
        self.cubes.append(c)
        return c

    def bar(self, x0, x1, y0, y1, z0, z1, mat, **kw):
        return self.box((x0, y0, z0), (x1, y1, z1), mat, **kw)

    def sym(self, x0, x1, y0, y1, z0, z1, mat, **kw):
        """A pair of boxes mirrored across x = 0 (x0, x1 >= 0 describe the +x one)."""
        self.bar(x0, x1, y0, y1, z0, z1, mat, **kw)
        kw2 = dict(kw)
        if kw2.get('pivot') is not None:
            p = list(kw2['pivot'])
            p[0] = -p[0]
            kw2['pivot'] = p
        if kw2.get('rotation') is not None:
            r = list(kw2['rotation'])
            kw2['rotation'] = [r[0], -r[1], -r[2]]
        return self.bar(-x1, -x0, y0, y1, z0, z1, mat, **kw2)


class Model:
    def __init__(self, identifier, tex_size=512, texels_per_unit=16):
        self.identifier = identifier
        self.parts = {}
        self.order = []
        self.tex = tex_size
        self.k = texels_per_unit
        self.atlas = None
        self.reserved = []          # (u, v, w, h) regions painted by hand (e.g. arm placeholders)

    def part(self, name, parent=None, pivot=(0, 0, 0), rotation=None):
        if name in self.parts:
            return self.parts[name]
        p = Part(self, name, parent, pivot, rotation)
        self.parts[name] = p
        self.order.append(name)
        return p

    def __getitem__(self, name):
        return self.parts[name]

    def cube_count(self):
        return sum(len(p.cubes) for p in self.parts.values())

    # ---- texture atlas -----------------------------------------------------------
    def layout(self):
        """Shelf-pack one texture region per visible face."""
        items = []
        for p in self.parts.values():
            for c in p.cubes:
                sx, sy, sz = c.size
                dims = {'north': (sx, sy), 'south': (sx, sy), 'east': (sz, sy), 'west': (sz, sy),
                        'up': (sx, sz), 'down': (sx, sz)}
                for f in c.faces:
                    w, h = dims[f]
                    if w <= 1e-6 or h <= 1e-6:
                        continue
                    k = c.data.get('k', self.k)
                    tw = max(1, int(math.ceil(w * k - 1e-6)))
                    th = max(1, int(math.ceil(h * k - 1e-6)))
                    items.append((th, tw, c, f))
        items.sort(key=lambda t: (-t[0], -t[1]))
        x, y, shelf = 0, 0, 0
        for (u, v, w, h) in self.reserved:
            y = max(y, v + h + 1)
        pad = 1
        for th, tw, c, f in items:
            if x + tw + pad > self.tex:
                x, y, shelf = 0, y + shelf + pad, 0
            if y + th > self.tex:
                raise RuntimeError(f'atlas full ({self.tex}px); lower texels_per_unit')
            c.uv[f] = (x, y, tw, th)
            x += tw + pad
            shelf = max(shelf, th)
        self.used_height = y + shelf

    # ---- painting --------------------------------------------------------------
    def paint(self, shader, background=(0, 0, 0, 0)):
        """shader(points[N,3] bedrock, normal(3,) bedrock, face, cube, uv01[N,2], (w,h) units) -> uint8 RGBA[N,4]."""
        img = np.zeros((self.tex, self.tex, 4), dtype=np.uint8)
        img[:] = background
        for p in self.parts.values():
            for c in p.cubes:
                corners = face_corners(c)
                sx, sy, sz = c.size
                dims = {'north': (sx, sy), 'south': (sx, sy), 'east': (sz, sy), 'west': (sz, sy),
                        'up': (sx, sz), 'down': (sx, sz)}
                for f, (u, v, w, h) in c.uv.items():
                    TL, TR, BR, BL = corners[f]
                    ii, jj = np.meshgrid((np.arange(w) + .5) / w, (np.arange(h) + .5) / h)
                    uu, vv = ii.ravel(), jj.ravel()
                    pts = TL[None] + uu[:, None] * (TR - TL)[None] + vv[:, None] * (BL - TL)[None]
                    pts = pts * np.array([-1, 1, 1])          # back to bedrock x
                    n = FACE_NORMAL_BEDROCK[f]
                    rgba = shader(pts, n, f, c, np.stack([uu, vv], 1), dims[f])
                    img[v:v + h, u:u + w] = rgba.reshape(h, w, 4)
        self.atlas = img
        return img

    # ---- export ----------------------------------------------------------------
    def to_bedrock(self):
        bones = []
        for name in self.order:
            p = self.parts[name]
            b = {'name': name}
            if p.parent:
                b['parent'] = p.parent
            b['pivot'] = [r6(v) for v in p.pivot]
            if p.rotation and any(abs(v) > 1e-9 for v in p.rotation):
                b['rotation'] = [r6(v) for v in p.rotation]
            cubes = []
            for c in p.cubes:
                cd = {'origin': [r6(v) for v in c.lo], 'size': [r6(v) for v in c.size]}
                if c.inflate:
                    cd['inflate'] = r6(c.inflate)
                if c.rotation and any(abs(v) > 1e-9 for v in c.rotation):
                    cd['pivot'] = [r6(v) for v in c.pivot]
                    cd['rotation'] = [r6(v) for v in c.rotation]
                uvd = {}
                for f, (u, v, w, h) in c.uv.items():
                    if f == 'down':
                        uvd[f] = {'uv': [u, v + h], 'uv_size': [w, -h]}
                    else:
                        uvd[f] = {'uv': [u, v], 'uv_size': [w, h]}
                cd['uv'] = uvd
                cubes.append(cd)
            if cubes:
                b['cubes'] = cubes
            bones.append(b)
        lo = np.array([1e9] * 3)
        hi = -lo
        for p in self.parts.values():
            for c in p.cubes:
                lo = np.minimum(lo, c.lo)
                hi = np.maximum(hi, c.hi)
        return {
            'format_version': '1.12.0',
            'minecraft:geometry': [{
                'description': {
                    'identifier': f'geometry.{self.identifier}',
                    'texture_width': self.tex, 'texture_height': self.tex,
                    'visible_bounds_width': r6(max(4.0, float(hi[2] - lo[2]) / 16 + 1)),
                    'visible_bounds_height': 2.5,
                    'visible_bounds_offset': [0, 0.5, 0],
                },
                'bones': bones,
            }],
        }

    def to_bbmodel(self, texture_png_b64, name):
        """A Blockbench project (Bedrock entity format) with the painted texture embedded."""
        import uuid
        elements, outliner_nodes = [], {}
        for name_ in self.order:
            p = self.parts[name_]
            node = {'name': name_, 'origin': [-p.pivot[0], p.pivot[1], p.pivot[2]],
                    'rotation': [-(p.rotation or [0, 0, 0])[0], -(p.rotation or [0, 0, 0])[1], (p.rotation or [0, 0, 0])[2]],
                    'uuid': str(uuid.uuid4()), 'export': True, 'isOpen': False, 'visibility': True, 'children': []}
            outliner_nodes[name_] = node
            for c in p.cubes:
                cuuid = str(uuid.uuid4())
                frm = [-c.hi[0], c.lo[1], c.lo[2]]
                to = [-c.lo[0], c.hi[1], c.hi[2]]
                piv = c.pivot or p.pivot
                rot = c.rotation or [0, 0, 0]
                faces = {}
                for f in FACES:
                    if f in c.uv:
                        u, v, w, h = c.uv[f]
                        faces[f] = {'uv': [u, v, u + w, v + h], 'texture': 0}
                    else:
                        faces[f] = {'uv': [0, 0, 0, 0], 'texture': None}
                elements.append({'name': f'{name_}_{len(node["children"])}', 'box_uv': False, 'type': 'cube',
                                 'from': frm, 'to': to, 'inflate': c.inflate,
                                 'origin': [-piv[0], piv[1], piv[2]], 'rotation': [-rot[0], -rot[1], rot[2]],
                                 'faces': faces, 'uuid': cuuid})
                node['children'].append(cuuid)
        roots = []
        for name_ in self.order:
            p = self.parts[name_]
            if p.parent:
                outliner_nodes[p.parent]['children'].append(outliner_nodes[name_])
            else:
                roots.append(outliner_nodes[name_])
        return {
            'meta': {'format_version': '4.10', 'model_format': 'bedrock', 'box_uv': False},
            'name': name, 'model_identifier': self.identifier,
            'resolution': {'width': self.tex, 'height': self.tex},
            'elements': elements, 'outliner': roots,
            'textures': [{'name': f'{name}.png', 'id': '0', 'width': self.tex, 'height': self.tex,
                          'uv_width': self.tex, 'uv_height': self.tex, 'particle': True, 'render_mode': 'default',
                          'uuid': str(uuid.uuid4()), 'source': 'data:image/png;base64,' + texture_png_b64}],
        }


def r6(v):
    return float(round(float(v), 5))


FACE_NORMAL_BEDROCK = {
    'north': np.array([0, 0, -1.]), 'south': np.array([0, 0, 1.]),
    # Blockbench "east" is +x in Blockbench space, i.e. -x in Bedrock space
    'east': np.array([-1., 0, 0]), 'west': np.array([1., 0, 0]),
    'up': np.array([0, 1., 0]), 'down': np.array([0, -1., 0]),
}


def face_corners(c):
    """TL, TR, BR, BL of each face in Blockbench space (inflate not applied)."""
    x0, x1 = -c.hi[0], -c.lo[0]
    y0, y1 = c.lo[1], c.hi[1]
    z0, z1 = c.lo[2], c.hi[2]
    P = lambda x, y, z: np.array([x, y, z], dtype=float)
    return {
        'north': (P(x1, y1, z0), P(x0, y1, z0), P(x0, y0, z0), P(x1, y0, z0)),
        'south': (P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1), P(x0, y0, z1)),
        'east': (P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0), P(x1, y0, z1)),
        'west': (P(x0, y1, z0), P(x0, y1, z1), P(x0, y0, z1), P(x0, y0, z0)),
        'up': (P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)),
        'down': (P(x0, y0, z1), P(x1, y0, z1), P(x1, y0, z0), P(x0, y0, z0)),
    }


# ----------------------------------------------------------------------------
# transforms (Blockbench space)
# ----------------------------------------------------------------------------
def rot_matrix(rx, ry, rz):
    """Bedrock rotation (degrees) -> 4x4 matrix in Blockbench space: Rz * Ry * Rx with x/y negated."""
    a, b, c = math.radians(-rx), math.radians(-ry), math.radians(rz)
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    M = np.eye(4)
    M[:3, :3] = Rz @ Ry @ Rx
    return M


def trans(v):
    M = np.eye(4)
    M[:3, 3] = v
    return M


def bb(v):
    return np.array([-v[0], v[1], v[2]], dtype=float)


def world_matrices(model, pose=None):
    """pose: {bone: {'rotation': [..], 'position': [..], 'scale': s}} offsets in Bedrock convention."""
    pose = pose or {}
    out = {}

    def get(name):
        if name in out:
            return out[name]
        p = model.parts[name]
        parent = get(p.parent) if p.parent else np.eye(4)
        rot = list(p.rotation or [0, 0, 0])
        off = np.zeros(3)
        scale = 1.0
        if name in pose:
            pr = pose[name].get('rotation')
            if pr is not None:
                rot = [rot[i] + pr[i] for i in range(3)]
            pp = pose[name].get('position')
            if pp is not None:
                off = bb(pp)
            s = pose[name].get('scale')
            if s is not None:
                scale = s if not isinstance(s, (list, tuple)) else s
        piv = bb(p.pivot)
        S = np.eye(4)
        if isinstance(scale, (list, tuple)):
            S[0, 0], S[1, 1], S[2, 2] = scale
        else:
            S[0, 0] = S[1, 1] = S[2, 2] = scale
        M = parent @ trans(off) @ trans(piv) @ rot_matrix(*rot) @ S @ trans(-piv)
        out[name] = M
        return M

    for n in model.order:
        get(n)
    return out


def model_triangles(model, pose=None, hide=()):
    """List of (3 world points, 3 uv pixel coords, normal) for every face."""
    W = world_matrices(model, pose)
    tris = []
    for name in model.order:
        if name in hide:
            continue
        p = model.parts[name]
        M = W[name]
        for c in p.cubes:
            corners = face_corners(c)
            if c.inflate:
                ctr = np.array([-(c.lo[0] + c.hi[0]) / 2, (c.lo[1] + c.hi[1]) / 2, (c.lo[2] + c.hi[2]) / 2])
                half = np.array([(c.hi[0] - c.lo[0]) / 2, (c.hi[1] - c.lo[1]) / 2, (c.hi[2] - c.lo[2]) / 2])
                scale = (half + c.inflate) / np.maximum(half, 1e-9)
                corners = {f: tuple(ctr + (q - ctr) * scale for q in qs) for f, qs in corners.items()}
            C = np.eye(4)
            if c.rotation:
                cp = bb(c.pivot)
                C = trans(cp) @ rot_matrix(*c.rotation) @ trans(-cp)
            T = M @ C
            for f, (u, v, w, h) in c.uv.items():
                q = [T @ np.append(pt, 1.0) for pt in corners[f]]
                q = [x[:3] for x in q]
                uvq = [(u, v), (u + w, v), (u + w, v + h), (u, v + h)]
                tris.append(((q[0], q[1], q[2]), (uvq[0], uvq[1], uvq[2])))
                tris.append(((q[0], q[2], q[3]), (uvq[0], uvq[2], uvq[3])))
    return tris


# ----------------------------------------------------------------------------
# software renderer
# ----------------------------------------------------------------------------
def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda a: np.array(a, dtype=float), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    V = np.eye(4)
    V[0, :3], V[1, :3], V[2, :3] = r, u, -f
    V[:3, 3] = -V[:3, :3] @ eye
    return V


def render(model, texture, eye, target, size=(960, 640), fov=None, ortho_height=None, pose=None,
           bg=(38, 41, 46), light=(-0.4, 0.8, 0.5), hide=(), ss=2, extra=None):
    """Rasterise the model with its texture. Perspective if fov is given, else orthographic."""
    W, H = size[0] * ss, size[1] * ss
    tex = np.asarray(texture).astype(np.float32)
    th, tw = tex.shape[:2]
    V = look_at(eye, target)
    zbuf = np.full((H, W), np.inf, dtype=np.float32)
    img = np.zeros((H, W, 3), dtype=np.float32)
    img[:] = bg
    # vertical gradient background
    grad = np.linspace(1.12, 0.82, H)[:, None, None]
    img *= grad
    Ld = np.array(light, dtype=float)
    Ld /= np.linalg.norm(Ld)
    tris = model_triangles(model, pose, hide)
    if extra:
        tris += extra
    for (pts, uvs) in tris:
        cam = [V @ np.append(p, 1.0) for p in pts]
        cam = np.array([c[:3] for c in cam])
        if np.any(cam[:, 2] > -0.05) and fov is not None:
            continue
        n = np.cross(cam[1] - cam[0], cam[2] - cam[0])
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n /= nn
        if fov is not None:
            if np.dot(n, cam[0]) >= 0:
                continue
            fy = 1.0 / math.tan(math.radians(fov) / 2)
            sx = (cam[:, 0] / -cam[:, 2]) * fy * (H / 2) + W / 2
            sy = -(cam[:, 1] / -cam[:, 2]) * fy * (H / 2) + H / 2
            depth = -cam[:, 2]
        else:
            if n[2] <= 0:
                continue
            sc = H / ortho_height
            sx = cam[:, 0] * sc + W / 2
            sy = -cam[:, 1] * sc + H / 2
            depth = -cam[:, 2]
        x0, x1 = int(max(0, math.floor(sx.min()))), int(min(W - 1, math.ceil(sx.max())))
        y0, y1 = int(max(0, math.floor(sy.min()))), int(min(H - 1, math.ceil(sy.max())))
        if x0 > x1 or y0 > y1:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
        d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
        if abs(d) < 1e-9:
            continue
        a = ((sy[1] - sy[2]) * (xs - sx[2]) + (sx[2] - sx[1]) * (ys - sy[2])) / d
        b = ((sy[2] - sy[0]) * (xs - sx[2]) + (sx[0] - sx[2]) * (ys - sy[2])) / d
        c = 1 - a - b
        m = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
        if not m.any():
            continue
        if fov is not None:
            iw = np.array([1 / depth[0], 1 / depth[1], 1 / depth[2]])
            wsum = a * iw[0] + b * iw[1] + c * iw[2]
            z = 1 / wsum
            pa, pb, pc = a * iw[0] / wsum, b * iw[1] / wsum, c * iw[2] / wsum
        else:
            z = a * depth[0] + b * depth[1] + c * depth[2]
            pa, pb, pc = a, b, c
        U = pa * uvs[0][0] + pb * uvs[1][0] + pc * uvs[2][0]
        Vv = pa * uvs[0][1] + pb * uvs[1][1] + pc * uvs[2][1]
        ui = np.clip(np.floor(U - 1e-4).astype(int), 0, tw - 1)
        vi = np.clip(np.floor(Vv - 1e-4).astype(int), 0, th - 1)
        texel = tex[vi, ui]
        m &= texel[..., 3] > 8
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        m &= z < sub
        if not m.any():
            continue
        # lighting in world space
        wn = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        wn /= max(np.linalg.norm(wn), 1e-12)
        lam = max(0.0, float(np.dot(wn, Ld)))
        shade = 0.55 + 0.5 * lam
        sub[m] = z[m]
        region = img[y0:y1 + 1, x0:x1 + 1]
        region[m] = texel[..., :3][m] * shade
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    if ss > 1:
        out = out.resize(size, Image.LANCZOS)
    return out
