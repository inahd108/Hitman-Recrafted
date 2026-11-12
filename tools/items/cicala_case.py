"""Writes the Cicala briefcase item texture (32x32) used by models/item/cicala_case.json.

Layout (pixels): front/back 0..24 x 0..18, top/bottom 0..24 x 18..24, ends 24..30 x 0..18,
latch 26..30 x 20..24, handle 26..32 x 26..32.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'src', 'main', 'resources', 'assets', 'recrafted', 'textures', 'item', 'cicala_case.png')


def noise(h, w, seed):
    rng = np.random.default_rng(seed)
    return rng.random((h, w))


def main():
    img = np.zeros((32, 32, 4), dtype=float)
    body = np.array([58, 60, 66, 255], dtype=float)
    n = noise(32, 32, 3)
    img[:, :] = body
    img[..., :3] *= (0.92 + 0.12 * n)[..., None]
    # bevelled edges on the front/back panel
    for y in range(18):
        for x in range(24):
            if x in (0, 23) or y in (0, 17):
                img[y, x, :3] *= 0.7
            elif x in (1, 22) or y in (1, 16):
                img[y, x, :3] *= 1.12
    # lid seam on the front, a third of the way down
    img[6, 1:23, :3] *= 0.6
    # gold cicada emblem, lower middle of the front
    gold = np.array([212, 172, 70], dtype=float)
    cx, cy = 12.0, 11.5
    for y in range(18):
        for x in range(24):
            dx, dy = (x + 0.5 - cx) / 3.2, (y + 0.5 - cy) / 3.2
            body_m = abs(dx) < 0.18 and -0.6 < dy < 0.7
            wing = False
            for sgn in (1, -1):
                for ang, ln in ((22, 1.0), (42, 0.75)):
                    a = math.radians(ang)
                    u = dy * math.cos(a) + sgn * dx * math.sin(a)
                    v = -dy * math.sin(a) + sgn * dx * math.cos(a)
                    wing |= (-0.1 < u < ln) and (0.05 < v < 0.33 * ln)
            if body_m or wing:
                img[y, x, :3] = gold * (0.9 + 0.1 * n[y, x])
    # top/bottom and ends: same shell, a groove along the middle
    img[21, 0:24, :3] *= 0.75
    img[0:18, 27, :3] *= 0.75
    # latch: polished gold
    img[20:24, 26:30, :3] = gold
    img[20, 26:30, :3] *= 1.15
    img[23, 26:30, :3] *= 0.75
    # handle: black rubber
    img[26:32, 26:32, :3] = np.array([24, 24, 26], dtype=float) * (0.9 + 0.2 * n[26:32, 26:32, None])
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGBA').save(OUT)
    print('wrote', os.path.relpath(OUT))


if __name__ == '__main__':
    sys.exit(main())
