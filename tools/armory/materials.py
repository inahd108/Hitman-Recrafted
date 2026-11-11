"""Procedural surface shaders for gun textures.

Every function works on arrays of texel positions in model units (Bedrock space) so
patterns stay continuous across faces and line up with the geometry.
"""
import numpy as np

# 5x7 pixel font for engraved lettering
FONT = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01111'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'C': ['01110', '10001', '10000', '10000', '10000', '10001', '01110'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'W': ['10001', '10001', '10001', '10101', '10101', '11011', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    'Z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
    '0': ['01110', '10011', '10101', '10101', '11001', '10001', '01110'],
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['01110', '10001', '00001', '00110', '01000', '10000', '11111'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
    '5': ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00001', '01110'],
    '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
    '-': ['00000', '00000', '00000', '01110', '00000', '00000', '00000'],
    ' ': ['00000'] * 7,
}


def _hash(ix, iy, iz, seed=0):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 144269504) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def vnoise(p, freq, seed=0):
    """Smooth 3D value noise in [0, 1]. p: [N,3]; freq: scalar or (fx, fy, fz)."""
    q = p * np.asarray(freq, dtype=float)
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (np.where(dx, f[:, 0], 1 - f[:, 0]) * np.where(dy, f[:, 1], 1 - f[:, 1])
                     * np.where(dz, f[:, 2], 1 - f[:, 2]))
                out = out + w * _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out


def fbm(p, freq, octaves=3, seed=0):
    total, amp, norm = 0, 1.0, 0
    fr = np.asarray(freq, dtype=float)
    for o in range(octaves):
        total = total + amp * vnoise(p, fr, seed + o * 17)
        norm += amp
        amp *= 0.5
        fr = fr * 2
    return total / norm


def rgba(col, n=None):
    a = np.asarray(col, dtype=float)
    if a.shape[-1] == 3:
        a = np.concatenate([a, np.full(a.shape[:-1] + (1,), 255.0)], -1) if a.ndim > 1 else np.append(a, 255.0)
    if n is not None and a.ndim == 1:
        a = np.tile(a, (n, 1))
    return a


def finish(col):
    return np.clip(col, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# base materials: return float RGB [N,3]
# ---------------------------------------------------------------------------
def face_light(normal):
    """Baked directional shading so small parts read well even under flat lighting."""
    return {(0, 1): 1.10, (0, -1): 0.62}.get((0, int(round(normal[1]))), 1.0) * (0.9 if abs(normal[2]) > 0.5 else 1.0)


def stainless(p, normal, grain=2, seed=0):
    base = np.array([196, 200, 206], dtype=float)
    fr = [24.0, 24.0, 24.0]
    fr[grain] = 0.9                              # long brushed streaks along the grain axis
    streak = fbm(p, fr, 3, seed)
    blotch = fbm(p, 1.6, 2, seed + 5)
    k = 0.86 + 0.16 * streak + 0.06 * (blotch - 0.5)
    # soft "reflection" band that changes with height, like a polished flat
    band = 1 + 0.07 * np.sin(p[:, 1] * 2.3 + p[:, 2] * 0.35)
    return base[None] * (k * band * face_light(normal))[:, None]


def blued(p, normal, seed=0):
    base = np.array([46, 50, 60], dtype=float)
    n = fbm(p, 6, 3, seed)
    return base[None] * ((0.88 + 0.24 * n) * face_light(normal))[:, None]


def matte_black(p, normal, seed=0):
    base = np.array([30, 31, 34], dtype=float)
    n = vnoise(p, 30, seed)
    return base[None] * ((0.9 + 0.18 * n) * face_light(normal))[:, None]


def ivory(p, normal, seed=0):
    base = np.array([226, 216, 192], dtype=float)
    grain = fbm(p * np.array([1, 3.0, 1]), [5, 1.2, 5], 3, seed)
    k = 0.9 + 0.14 * grain
    warm = np.stack([np.ones_like(k), 0.985 + 0 * k, 0.95 + 0.04 * grain], 1)
    return base[None] * warm * (k * face_light(normal))[:, None]


def gold(p, normal, seed=0):
    base = np.array([214, 168, 70], dtype=float)
    n = fbm(p, 9, 2, seed)
    band = 1 + 0.12 * np.sin(p[:, 1] * 5 + p[:, 2] * 1.3)
    return base[None] * ((0.86 + 0.2 * n) * band * face_light(normal))[:, None]


def brass(p, normal, seed=0):
    base = np.array([198, 152, 66], dtype=float)
    return base[None] * ((0.9 + 0.16 * fbm(p, 8, 2, seed)) * face_light(normal))[:, None]


def copper(p, normal, seed=0):
    base = np.array([176, 102, 60], dtype=float)
    return base[None] * ((0.9 + 0.16 * fbm(p, 8, 2, seed)) * face_light(normal))[:, None]


def rubber(p, normal, seed=0):
    base = np.array([38, 38, 40], dtype=float)
    return base[None] * ((0.92 + 0.12 * vnoise(p, 40, seed)) * face_light(normal))[:, None]


# ---------------------------------------------------------------------------
# details
# ---------------------------------------------------------------------------
def edge_bevel(col, uv01, wh, width=0.07, light=1.22, dark=0.72, sides=True):
    """Lighten the top edge and darken the bottom edge of a face: reads as a chamfer."""
    u, v = uv01[:, 0], uv01[:, 1]
    w, h = wh
    dtop = v * h
    dbot = (1 - v) * h
    k = np.ones_like(u)
    k = np.where(dtop < width, light, k)
    k = np.where(dbot < width, np.minimum(k, dark), k)
    if sides:
        dl, dr = u * w, (1 - u) * w
        k = np.where((dl < width * 0.7) | (dr < width * 0.7), k * 0.9, k)
    return col * k[:, None]


def grooves(coord, period, duty=0.45, depth=0.55):
    """Parallel machined grooves along a coordinate: multiplier array."""
    t = np.mod(coord / period, 1.0)
    return np.where(t < duty, depth, 1.0) * np.where(np.abs(t - duty) < 0.08, 1.15, 1.0)


def checker(a, b, period=0.16, line=0.18, depth=0.62):
    t1 = np.mod((a + b) / period, 1.0)
    t2 = np.mod((a - b) / period, 1.0)
    on = (t1 < line) | (t2 < line)
    return np.where(on, depth, 1.0)


def scrollwork(y, z, cy, seed=0):
    """Ornamental engraving: a running vine with curls. Returns a 0..1 'cut' mask."""
    vine = np.abs(np.sin(z * 2.6 + 0.55 * np.sin(z * 1.1)) * 0.34 - (y - cy))
    cut = vine < 0.06
    # curls hanging off the vine, alternating above and below
    period = 1.2
    k = np.floor(z / period)
    cz = (k + 0.5) * period
    side = np.where(np.mod(k, 2) == 0, 1.0, -1.0)
    ccy = cy + side * 0.36
    dz, dy = z - cz, (y - ccy) * side
    r = np.sqrt(dz * dz + dy * dy)
    th = np.arctan2(dy, dz)
    spiral = np.abs(np.mod(th / (2 * np.pi) + r / 0.13, 1.0) - 0.5) < 0.17
    curl = spiral & (r < 0.3) & (r > 0.03)
    # small leaves
    lf = (np.abs(np.sin(z * 9.0) * 0.08 - (y - cy) * 0.6) < 0.025) & (np.abs(y - cy) < 0.22)
    return cut | curl | lf


def text_mask(y, z, text, z0, y_top, height, reverse=False):
    """Pixel-font lettering laid along z (towards the muzzle when reverse=False)."""
    cell = height / 7.0
    gx = (z0 - z) / cell if not reverse else (z - z0) / cell
    gy = (y_top - y) / cell
    col = np.floor(gx).astype(int)
    row = np.floor(gy).astype(int)
    out = np.zeros_like(y, dtype=bool)
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT[' '])
        cx0 = i * 6
        sel = (col >= cx0) & (col < cx0 + 5) & (row >= 0) & (row < 7)
        if not sel.any():
            continue
        gc = col[sel] - cx0
        gr = row[sel]
        bits = np.array([[c == '1' for c in r] for r in glyph])
        out[np.where(sel)[0]] = bits[gr, gc]
    return out


def disc(a, b, ca, cb, r):
    return (a - ca) ** 2 + (b - cb) ** 2 <= r * r
