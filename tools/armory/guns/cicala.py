"""Cicala — the takedown sniper rifle that travels in a briefcase.

An integrally suppressed barrel with gold accent rings, a round receiver with a gold-knobbed bolt on a
gunmetal chassis, a vented fore-end with a gold cicada, a raked pistol grip, a short box magazine and a
folding skeleton stock with a cheek riser. A TACZ scope rides on the rail.

Coordinates follow TACZ's own bolt-action rifle so its hold fits: right hand on the grip, left hand under
the fore-end; the magazine and left hand share a bone.
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'cicala'
K = 13
BORE_Y = 7.25
MUZZLE_Z = -20.8
RAIL_Y = 8.12
FP_CAM = ((-3.0, 10.0, 17.0), (-3.0, 8.6, -20), 60)       # preview only: TACZ's hip camera


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def rig(m):
    m.part('root', None, [0, 6, 7])
    m.part('gun_and_righthand', 'root', [0, 0, 0])
    m.part('mag_and_lefthand', 'root', [0, 5.4, 0])
    g = m.part(ID, 'gun_and_righthand', [0, 8, 0])
    off = np.array([-4.75, -16.45, 11.375])
    m.part('righthand', 'gun_and_righthand', list(np.array([5, 20, 0]) + off), [99.13083, 12.94967, -178.84728])
    rh = m.part('righthand_pos', 'righthand', list(np.array([0, 9, 0]) + off))
    lo = np.array([4, 9, -2]) + off
    rh.box(list(lo), list(lo + [3, 12, 4]), 'arm', data={'k': 2})
    off = np.array([7.925, -16.15, -2.6])
    m.part('lefthand', 'mag_and_lefthand', list(np.array([-6, 20, 0]) + off), [109.65024, -28.44535, -146.28441])
    lh = m.part('lefthand_pos', 'lefthand', list(np.array([0, 9, 0]) + off))
    lo = np.array([-7, 9, -2]) + off
    lh.box(list(lo), list(lo + [3, 12, 4]), 'arm', data={'k': 2})
    m.part('scope_pos', ID, [0, RAIL_Y, 7.25])
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.4])
    m.part('shell', ID, [-0.38, 7.44, 5.97], [0, 20, 0])
    m.part('constraint', ID, [0, 8.38, 9])
    return g


def views(m):
    m.part('views', None, [3.4, 4.17, 0])
    m.part('iron_view', 'views', [0, 8.41, 16.5])
    m.part('idle_view', 'views', [3, 10, 17])
    m.part('refit_view', 'views', [30, 5, 0], [0, 89.9, 0])
    m.part('refit_muzzle_view', 'views', [12.35, 7.85, -30.75], [0, 120, 0])
    m.part('refit_scope_view', 'views', [11.4, 8.18, 11.95], [0, 67.5, 0])
    m.part('refit_extended_mag_view', 'views', [12.88, -4.38, 6], [0, 90, 30])
    m.part('camera', None, [3, 9.75, 16])
    m.part('positioning', None, [0.5, -3.95, -11.22])
    m.part('ground', 'positioning', [0, 0, 0])
    m.part('fixed', 'positioning', [1, 4.88, 10], [0, 90, 0])
    m.part('thirdperson_hand', 'positioning', [0.12, 4.05, 7.17])


def build_barrel(m):
    b = m.part('barrel', ID, [0, BORE_Y, -6])
    # integral suppressor with gold rings, then the fluted barrel
    octagon(b, 'z', (0, BORE_Y), 0.72, MUZZLE_Z + 0.2, -10.2, 'black', sides=16, data={'decal': 'can'})
    octagon(b, 'z', (0, BORE_Y), 0.64, MUZZLE_Z, MUZZLE_Z + 0.22, 'black', sides=16)
    octagon(b, 'z', (0, BORE_Y), 0.56, -10.25, -9.6, 'black', sides=16)
    for z0 in (MUZZLE_Z + 0.7, -11.0):
        octagon(b, 'z', (0, BORE_Y), 0.74, z0, z0 + 0.28, 'gold', sides=16)
    octagon(b, 'z', (0, BORE_Y), 0.2, MUZZLE_Z - 0.01, MUZZLE_Z + 0.02, 'bore', sides=8)
    octagon(b, 'z', (0, BORE_Y), 0.34, -9.7, 0.5, 'black', sides=8, data={'decal': 'flutes'})
    m.part('muzzle_pos', 'barrel', [0, BORE_Y, MUZZLE_Z])


def build_chassis(m):
    c = m.part('chassis', ID, [0, 6.6, 2])
    # vented fore-end around the barrel
    octagon(c, 'z', (0, 6.95), 0.95, -9.2, 0.6, 'gunmetal', sides=8, data={'decal': 'forend'})
    octagon(c, 'z', (0, 6.95), 0.98, -9.4, -9.1, 'gunmetal', sides=8)
    # round receiver with a scope rail
    octagon(c, 'z', (0, 7.4), 0.8, 0.4, 9.2, 'black', sides=16, data={'decal': 'receiver'})
    round_bar(c, 'z', (-0.45, 7.95, 0.6), (0.45, RAIL_Y + 0.1, 9.0), 'black', r=0.06, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    c.bar(-0.82, -0.78, 7.3, 8.0, 4.5, 6.9, 'bore')                                          # ejection port
    # low backup sights for when no scope is fitted: a post on the fore-end, a notch at the back of the rail
    c.bar(-0.07, 0.07, 7.85, 8.38, -8.75, -8.6, 'black')
    c.bar(-0.07, 0.07, 8.3, 8.38, -8.76, -8.59, 'gold')
    for x0 in (-0.3, 0.12):
        c.bar(x0, x0 + 0.18, RAIL_Y + 0.08, 8.55, 8.55, 8.85, 'black')
    # chassis lower, magazine well, trigger guard
    round_bar(c, 'z', (-0.85, 5.8, -0.5), (0.85, 6.75, 10.2), 'gunmetal', r=0.22, corners=(0, 0, 1, 1), sides=8,
              data={'decal': 'lower'})
    layered(c, (-0.75, 5.3, 3.1), (0.75, 6.0, 6.5), 0.25, (0, 1, 1, 0), 'gunmetal', step=0.08)
    path_yz(c, [(5.85, 7.5), (5.05, 7.9), (5.0, 9.7), (5.8, 10.1)], 0.2, -0.28, 0.28, 'gunmetal')
    t = m.part('trigger', ID, [0, 5.85, 8.5])
    path_yz(t, [(5.85, 8.5)] + arc_pts(5.25, 9.1, 0.65, 125, 200, 3), 0.16, -0.12, 0.12, 'gold')
    # raked pistol grip
    g = m.part('grip', ID, [0, 6.0, 10.3], [15, 0, 0])
    layered(g, (-0.6, 1.7, 9.4), (0.6, 6.1, 11.6), 0.42, (0, 1, 1, 0), 'rubber', data={'decal': 'grip'})
    # folding skeleton stock with cheek riser and rubber butt pad
    st = m.part('stock', ID, [0, 6.6, 11.6])
    st.bar(-0.7, 0.7, 5.3, 7.95, 10.9, 11.9, 'gunmetal')                                      # hinge block
    disc_x(st, 7.4, 11.4, 0.18, -0.74, 0.74, 'gold', sides=8)                                 # hinge pin
    seg_yz(st, (7.6, 11.6), (7.6, 19.4), 0.7, -0.45, 0.45, 'gunmetal', data={'decal': 'stockbar'})
    seg_yz(st, (5.6, 11.6), (4.3, 19.2), 0.55, -0.42, 0.42, 'gunmetal', data={'decal': 'stockbar'})
    seg_yz(st, (4.3, 18.9), (7.6, 18.9), 0.7, -0.48, 0.48, 'gunmetal')
    # cheek riser: kept below the sight line (the aiming eye sits at y 8.41 over the comb)
    round_bar(st, 'z', (-0.55, 7.85, 13.6), (0.55, 8.12, 18.4), 'rubber', r=0.1, corners=(1, 1, 0, 0), sides=8)
    layered(st, (-0.62, 3.7, 19.25), (0.62, 8.4, 19.95), 0.3, (1, 1, 1, 1), 'rubber', step=0.08)


def build_bolt(m):
    bb = m.part('bullet_and_bolt', ID, [0, 7.25, 9])
    octagon(bb, 'z', (0, 7.35), 0.5, 9.1, 10.1, 'steel', sides=8)                             # bolt shroud
    bb.bar(-0.42, 0.42, 7.05, 7.7, 4.6, 9.1, 'steel', data={'decal': 'boltbody'})
    # handle out to the right, angled down, with a gold knob
    bb.box((-1.45, 6.95, 8.35), (-0.45, 7.2, 8.65), 'steel', pivot=[-0.45, 7.1, 8.5], rotation=[0, 0, -28])
    octagon(bb, 'x', (6.62, 8.5), 0.27, -1.85, -1.3, 'gold', sides=8, data={'decal': 'knob'})


def build_magazine(m):
    m.part('magazine', 'mag_and_lefthand', [0, 0, 0])
    for name, drop in (('mag_standard', 0), ('mag_extended_1', 0.8), ('mag_extended_2', 1.6), ('mag_extended_3', 2.4)):
        mag = m.part(name, 'magazine', [0, 8, 0])
        mag.bar(-0.5, 0.5, 3.75 - drop, 6.4, 3.4, 6.2, 'gunmetal', data={'decal': 'mag'})
        layered(mag, (-0.58, 3.5 - drop, 3.25), (0.58, 3.8 - drop, 6.35), 0.12, (0, 1, 1, 0), 'black', step=0.05)
        mag.bar(-0.59, 0.59, 3.82 - drop, 3.9 - drop, 3.4, 6.2, 'gold')


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_barrel(m)
    build_chassis(m)
    build_bolt(m)
    build_magazine(m)
    views(m)
    return m


BASE = {
    'black': M.matte_black, 'gunmetal': M.gunmetal, 'gold': M.gold, 'steel': M.parkerized, 'rubber': M.rubber,
}


def cicada(y, z, cy, cz, s):
    """A small stylised cicada: a body with two pairs of swept wings. Returns a mask."""
    dy, dz = (y - cy) / s, (z - cz) / s
    body = (np.abs(dy) < 0.16) & (dz > -0.55) & (dz < 0.6)
    head = (dy ** 2 + (dz + 0.62) ** 2) < 0.05
    wings = np.zeros_like(body)
    for sgn in (1, -1):
        for ang, ln in ((22, 1.0), (40, 0.75)):
            a = math.radians(ang)
            u = dz * math.cos(a) + sgn * dy * math.sin(a)          # along the wing
            v = -dz * math.sin(a) + sgn * dy * math.cos(a)         # across it
            wings |= (u > -0.1) & (u < ln) & (v > 0.05) & (v < 0.32 * ln) & (np.abs(v - 0.16 * ln) < 0.17 * ln)
    return body | head | wings


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    if mat == 'bore':
        return M.finish(M.rgba(np.tile([[8, 8, 9]], (N, 1))))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'can':
        col = col * M.grooves(z, 0.55, 0.12, 0.8)[:, None]
    if d == 'flutes' and not (face in ('north', 'south')):
        col = col * np.where(np.mod(z, 1.2) < 0.9, 0.75, 1.0)[:, None]
    if d == 'forend':
        slots = (np.mod(z + 9.0, 1.6) > 0.3) & (np.mod(z + 9.0, 1.6) < 1.25) & (z > -8.4) & (z < -2.4)
        mid = np.abs((y - 6.95) if side else x) < 0.18
        col = np.where((slots & mid)[:, None], np.array([[16, 16, 18]]), col)
        if side and n[0] > 0:
            emb = cicada(y, z, 6.95, -0.9, 0.85) & ~(slots & mid)
            col = np.where(emb[:, None], M.gold(p, n), col)
    if d == 'lower' and side:
        if n[0] > 0:
            t = M.text_mask(y, z, 'CICALA', 0.6, 6.55, 6.0 / K, reverse=True)
        else:
            t = M.text_mask(y, z, 'CORVARA', 7.2, 6.55, 6.0 / K)
        col = np.where(t[:, None], M.gold(p, n), col)
    if d == 'rail' and face == 'up':
        col = col * M.grooves(z, 0.3, 0.45, 0.6)[:, None]
    if d == 'grip' and side:
        col = col * M.checker(y, z, 0.22, 0.25, 0.75)[:, None]
    if d == 'knob':
        col = col * M.checker(y, z, 0.12, 0.3, 0.75)[:, None]
    if d == 'mag' and side:
        col = col * M.grooves(y, 0.45, 0.15, 0.8)[:, None]
    metal = mat in ('black', 'gunmetal', 'gold', 'steel')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
