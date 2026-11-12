"""Vento .357 — the heavy revolver.

Deep-blued frame and full-lug barrel with a ventilated rib, a polished nickel six-shot fluted
cylinder on a swing-out crane, nickel spur hammer and trigger, rosewood round-butt grips with
nickel medallions, an adjustable rear sight and a red-insert front ramp. A speed loader appears
only while reloading.
"""
import numpy as np

import materials as M
from common import GRIP_PIV, GRIP_ROT, arm_colour, pistol_rig, pistol_views
from geomodel import arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'vento'
K = 16
GB = -1.3
BORE_Y = 5.05
CYL_Y, CYL_R = 4.5, 0.82
CYL_Z0, CYL_Z1 = -1.35, 0.95
CH_R = 0.52                        # radius of the chamber circle (top chamber lines up with the bore)
BARREL_Z0 = -6.4
MUZZLE_Z = BARREL_Z0 - 0.02
STRAP_Y = 5.72                     # top of the top strap and of the barrel rib
SIGHT_Y = 6.1
CRANE_PIV = [0.62, 3.55, -0.2]
CRANE_OPEN = 93                    # crane swing (degrees about z) that clears the cylinder out to the left


def chamber_xy(k):
    a = np.radians(90 + 60 * k)
    return np.cos(a) * CH_R, CYL_Y + np.sin(a) * CH_R


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    """A side-profile rounded slab (bar along x) with a second, inset, wider layer: reads as a bevelled edge."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def build_frame(m):
    f = m.part('gun', ID, [0, 0, 0])
    # top strap, frame post in front of the cylinder, recoil shield behind it
    round_bar(f, 'z', (-0.42, 5.36, -1.78), (0.42, STRAP_Y, 1.78), 'frame', r=0.16, corners=(1, 1, 0, 0), sides=8)
    round_bar(f, 'y', (-0.48, 3.6, -1.78), (0.48, 5.45, CYL_Z0 - 0.03), 'frame', r=0.1, sides=8)
    octagon(f, 'z', (0, CYL_Y), 0.8, CYL_Z1 + 0.03, 1.32, 'frame', sides=16)
    # frame under the cylinder, rounded where it meets the trigger guard
    layered(f, (-0.5, 2.75, -1.78), (0.5, 3.72, 1.3), 0.55, (0, 0, 1, 0), 'frame')
    # rear of the frame: a rounded hump over the web of the hand that runs into the backstrap
    layered(f, (-0.48, 2.75, 1.2), (0.48, 5.55, 3.6), 1.2, (1, 0, 0, 0), 'frame', data={'decal': 'rear'})
    # screws and the cylinder release (left side)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.5, sgn * 0.55))
        disc_x(f, 3.22, 0.35, 0.09, x0, x1, 'nickel')
        x0, x1 = sorted((sgn * 0.48, sgn * 0.53))
        disc_x(f, 4.95, 2.05, 0.09, x0, x1, 'nickel')
    rel = m.part('release', 'gun', [0.55, 4.42, 1.75])
    round_bar(rel, 'z', (0.46, 4.26, 1.45), (0.62, 4.58, 2.1), 'nickel', r=0.07, sides=8, data={'decal': 'knurl'})
    # trigger guard
    guard = [(2.74, -1.15)] + arc_pts(1.75, -0.45, 0.68, 180, 270, 4) + [(1.07, 0.55)] \
        + arc_pts(1.75, 0.55, 0.68, 270, 345, 3) + [(1.75, 1.55)]
    path_yz(f, guard, 0.24, -0.25, 0.25, 'frame')
    t = m.part('trigger', 'gun', [0, 2.7, -0.15])
    path_yz(t, [(2.75, -0.05)] + arc_pts(2.05, 0.65, 0.85, 125, 200, 4), 0.2, -0.17, 0.17, 'nickel')
    # spur hammer
    h = m.part('hammer', 'gun', [0, 4.6, 2.15])
    seg_yz(h, (4.6, 2.12), (5.56, 2.0), 0.4, -0.16, 0.16, 'nickel')
    path_yz(h, [(5.5, 1.96), (5.68, 2.28), (5.72, 2.62), (5.62, 2.94)], 0.24, -0.21, 0.21, 'nickel',
            data={'decal': 'spur'})
    # adjustable rear sight at the back of the top strap
    s = m.part('sight', 'gun', [0, STRAP_Y, 1.3])
    round_bar(s, 'z', (-0.32, STRAP_Y - 0.06, 0.95), (0.32, STRAP_Y + 0.08, 1.7), 'frame', r=0.06,
              corners=(1, 1, 0, 0), sides=8)
    for x0, x1 in ((0.08, 0.3), (-0.3, -0.08)):
        round_bar(s, 'z', (x0, STRAP_Y + 0.06, 1.35), (x1, SIGHT_Y + 0.04, 1.7), 'black', r=0.04, sides=8)
    s.bar(-0.08, 0.08, STRAP_Y + 0.06, STRAP_Y + 0.1, 1.35, 1.7, 'white')

    # barrel: tube, full-length underlug with a rounded nose, ventilated rib, front ramp
    b = m.part('barrel', 'gun', [0, BORE_Y, 0])
    octagon(b, 'z', (0, BORE_Y), 0.34, BARREL_Z0, -1.75, 'frame', sides=16)
    round_bar(b, 'z', (-0.31, 4.0, BARREL_Z0 + 0.32), (0.31, BORE_Y - 0.1, -1.75), 'frame', r=0.28,
              corners=(0, 0, 1, 1), data={'decal': 'lug'})
    disc_x(b, 4.32, BARREL_Z0 + 0.32, 0.32, -0.29, 0.29, 'frame', sides=16)
    b.bar(-0.29, 0.29, 4.32, BORE_Y - 0.1, BARREL_Z0, BARREL_Z0 + 0.34, 'frame')
    b.bar(-0.2, 0.2, BORE_Y + 0.25, STRAP_Y - 0.28, BARREL_Z0 + 0.05, -1.72, 'frame')
    z = BARREL_Z0 + 0.25
    while z < -2.0:
        b.bar(-0.17, 0.17, STRAP_Y - 0.3, STRAP_Y - 0.1, z, z + 0.24, 'frame')
        z += 0.48
    round_bar(b, 'z', (-0.2, STRAP_Y - 0.12, BARREL_Z0 + 0.05), (0.2, STRAP_Y, -1.72), 'frame', r=0.04,
              corners=(1, 1, 0, 0), sides=8, data={'decal': 'rib'})
    round_bar(b, 'z', (-0.08, STRAP_Y - 0.05, BARREL_Z0 + 0.12), (0.08, SIGHT_Y, BARREL_Z0 + 0.62), 'black',
              r=0.03, sides=8)
    seg_yz(b, (STRAP_Y - 0.02, BARREL_Z0 + 0.95), (SIGHT_Y - 0.06, BARREL_Z0 + 0.55), 0.12, -0.08, 0.08, 'black')
    b.bar(-0.085, 0.085, SIGHT_Y - 0.2, SIGHT_Y - 0.05, BARREL_Z0 + 0.3, BARREL_Z0 + 0.5, 'red')
    octagon(b, 'z', (0, BORE_Y), 0.16, MUZZLE_Z, BARREL_Z0, 'bore', sides=8)
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])

    # crane (swings out to the left), ejector rod, cylinder, ejector star and the six rounds
    crane = m.part('crane', 'gun', CRANE_PIV)
    crane.bar(0.2, 0.6, 3.55, 4.1, CYL_Z0 - 0.17, CYL_Z0 - 0.03, 'frame')
    octagon(crane, 'z', (0, CYL_Y), 0.11, -3.6, CYL_Z0, 'nickel', sides=8)
    octagon(crane, 'z', (0, CYL_Y), 0.16, -3.75, -3.6, 'nickel', sides=8, data={'decal': 'knurl'})
    cyl = m.part('cylinder', 'crane', [0, CYL_Y, (CYL_Z0 + CYL_Z1) / 2])
    octagon(cyl, 'z', (0, CYL_Y), CYL_R, CYL_Z0 + 0.12, CYL_Z1 - 0.06, 'nickel', sides=16)
    octagon(cyl, 'z', (0, CYL_Y), CYL_R - 0.09, CYL_Z0, CYL_Z0 + 0.12, 'nickel', sides=16, data={'decal': 'cylinder'})
    octagon(cyl, 'z', (0, CYL_Y), CYL_R - 0.05, CYL_Z1 - 0.06, CYL_Z1, 'nickel', sides=16)
    for k in range(6):
        a = 60 * k
        cx, cy = np.cos(np.radians(a)) * (CYL_R - 0.03), CYL_Y + np.sin(np.radians(a)) * (CYL_R - 0.03)
        cyl.box((cx - 0.06, cy - 0.17, CYL_Z0 + 0.42), (cx + 0.06, cy + 0.17, CYL_Z1 - 0.32), 'flute',
                pivot=[cx, cy, (CYL_Z0 + CYL_Z1) / 2], rotation=[0, 0, -a])
    ej = m.part('ejector', 'cylinder', [0, CYL_Y, CYL_Z1])
    octagon(ej, 'z', (0, CYL_Y), 0.5, CYL_Z1 - 0.02, CYL_Z1 + 0.05, 'nickel', sides=16)
    rounds = m.part('rounds', 'ejector', [0, CYL_Y, CYL_Z1])
    for k in range(6):
        cx, cy = chamber_xy(k)
        octagon(rounds, 'z', (cx, cy), 0.17, CYL_Z0 + 0.3, CYL_Z1 + 0.02, 'brass', sides=8)
        octagon(rounds, 'z', (cx, cy), 0.2, CYL_Z1 + 0.02, CYL_Z1 + 0.07, 'brass', sides=8, data={'decal': 'head'})
    # speed loader (shown only while reloading)
    ld = m.part('loader_and_round', 'crane', [0, CYL_Y, CYL_Z1 + 1.6])
    octagon(ld, 'z', (0, CYL_Y), 0.72, CYL_Z1 + 1.4, CYL_Z1 + 1.72, 'black', sides=16)
    octagon(ld, 'z', (0, CYL_Y), 0.26, CYL_Z1 + 1.72, CYL_Z1 + 2.2, 'black', sides=8, data={'decal': 'knurl'})
    lr = m.part('loader_rounds', 'loader_and_round', [0, CYL_Y, CYL_Z1 + 1.4])
    for k in range(6):
        cx, cy = chamber_xy(k)
        octagon(lr, 'z', (cx, cy), 0.17, CYL_Z1 + 0.3, CYL_Z1 + 1.4, 'brass', sides=8)
        octagon(lr, 'z', (cx, cy), 0.13, CYL_Z1 - 0.05, CYL_Z1 + 0.3, 'copper', sides=8)

    # round-butt rosewood grip, bevelled edges, finger rests, nickel medallions
    g = m.part('grip', 'gun', GRIP_PIV, GRIP_ROT)
    layered(g, (-0.52, GB, 1.12), (0.52, 3.1, 3.78), 0.62, (0, 1, 1, 0), 'rosewood', data={'decal': 'grip'})
    for yc in (1.75, 0.7):
        octagon(g, 'x', (yc, 1.12), 0.16, -0.38, 0.38, 'rosewood')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.52, sgn * 0.56))
        disc_x(g, 1.15, 2.5, 0.22, x0, x1, 'nickel', sides=16, data={'decal': 'medallion'})


def build():
    m = pistol_rig(ID, BORE_Y, MUZZLE_Z)
    del m.parts['shell']                 # a revolver keeps its empties until you punch them out
    m.order.remove('shell')
    build_frame(m)
    pistol_views(m, SIGHT_Y - 0.02, MUZZLE_Z)
    return m


BASE = {
    'frame': M.deep_blue, 'nickel': M.nickel, 'rosewood': M.rosewood, 'black': M.matte_black,
    'brass': M.brass, 'copper': M.copper,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'white':
        return M.finish(M.rgba(np.tile([[236, 236, 226]], (N, 1))))
    if mat == 'red':
        return M.finish(M.rgba(np.tile([[214, 40, 30]], (N, 1))))
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[6, 6, 7]], (N, 1))))
    if mat == 'flute':
        return M.finish(M.rgba(M.bake(M.nickel(p, n) * 0.62, c.data['wn'], metal=True)))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)

    if d == 'cylinder' and face == 'north':
        # chamber mouths on the front face, chamber walls on the back
        holes = np.zeros(N, dtype=bool)
        for k in range(6):
            cx, cy = chamber_xy(k)
            holes |= M.disc(x, y, cx, cy, 0.2)
        col = np.where(holes[:, None], np.array([[20, 18, 16]]), col)
    if d == 'lug' and side and n[0] > 0:
        t = M.text_mask(y, z, 'VENTO .357', -5.9, 4.68, 7.0 / K, reverse=True)
        col = np.where(t[:, None], M.nickel(p, n) * 0.9, col)
    if d == 'lug' and side and n[0] < 0:
        t = M.text_mask(y, z, 'CORVARA', -2.3, 4.68, 7.0 / K)
        col = np.where(t[:, None], M.nickel(p, n) * 0.9, col)
    if d == 'rib' and face == 'up':
        col = col * M.grooves(z, 0.1, 0.35, 0.7)[:, None]
    if d == 'knurl':
        col = col * M.checker(z, y + x, 0.07, 0.3, 0.6)[:, None]
    if d == 'spur' and face in ('up', 'south'):
        col = col * M.grooves(z + y, 0.07, 0.4, 0.6)[:, None]
    if d == 'grip' and side:
        inner = (z > 1.45) & (z < 3.45) & (y > GB + 0.5) & (y < 2.6)
        inner &= ~M.disc(z, y, 2.5, 1.15, 0.34)
        col = col * np.where(inner, M.checker(y, z, 0.25, 0.22, 0.72), 1.0)[:, None]
    if d == 'medallion' and side:
        star = (np.abs(np.abs(z - 2.5) - np.abs(y - 1.15)) < 0.03) | (np.abs(z - 2.5) < 0.03) | (np.abs(y - 1.15) < 0.03)
        col = np.where((star & M.disc(z, y, 2.5, 1.15, 0.16))[:, None], col * 0.6, col)
    if d == 'head' and face == 'south':
        primer = np.zeros(N, dtype=bool)
        for k in range(6):
            cx, cy = chamber_xy(k)
            primer |= M.disc(x, y, cx, cy, 0.07)
        col = np.where(primer[:, None], M.copper(p, n) * 1.1, col)
    metal = mat in ('frame', 'nickel', 'brass', 'copper')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
