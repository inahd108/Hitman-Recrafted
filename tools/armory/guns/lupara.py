"""Lupara — a sawn-off side-by-side 12 gauge.

Two barrels cut short with a raw sawn muzzle, colour case-hardened boxlock action with scroll engraving,
external hammers, double triggers and a top lever; the walnut stock is sawn off just behind the wrist and
shows its end grain. The barrels drop open on the hinge pin for reloading.

Coordinates follow TACZ's own sawn-off so its two-handed hold fits: right hand on the wrist, left hand
under the fore-end.
"""
import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'lupara'
K = 16
BORE_Y = 9.125
BX = 0.62                       # barrel axis offset from the centre line
BR = 0.6                        # barrel outer radius
MUZZLE_Z = -11.6
BREECH_Z = 1.6
RIB_TOP = BORE_Y + 0.74
SIGHT_Y = RIB_TOP + 0.18        # top of the brass bead
EYE_Y = RIB_TOP + 0.34          # aiming eye: just above the rib, looking between the hammers
HINGE = [0, 7.62, 1.32]
FP_CAM = ((-3.38, 12.16, 12.5), (-3.38, 11.2, -20), 60)       # preview only: TACZ's hip camera


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    """A side-profile rounded slab (bar along x) with an inset, wider layer: a bevelled edge."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def rig(m):
    """Bones TACZ expects, and the two-handed hold (TACZ's sawn-off hand pose baked into the rest pose)."""
    m.part('root', None, [0, 7, 6.225])
    g = m.part(ID, 'root', [0, 7, 6.625])
    # right hand on the wrist
    off = np.array([-6.725, -13.3, -0.775])
    m.part('righthand', ID, list(np.array([6, 19, 8]) + off), [89.32102, 14.82897, -180.27891])
    rh = m.part('righthand_pos', 'righthand', list(np.array([0, 8, 8]) + off))
    lo = np.array([4, 8, 6]) + off
    rh.box(list(lo), list(lo + [3, 12, 4]), 'arm', data={'k': 2})
    # left hand under the fore-end
    off = np.array([8.4, -13.02, -11.32])
    m.part('lefthand', 'root', list(np.array([-6, 19, 8]) + off), [107.06948, -26.54246, -157.78735])
    lh = m.part('lefthand_pos', 'lefthand', list(np.array([0, 8, 8]) + off))
    lo = np.array([-7, 8, 6]) + off
    lh.box(list(lo), list(lo + [3, 12, 4]), 'arm', data={'k': 2})
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.3])
    m.part('constraint', ID, [0, 10.025, -7.925])
    return g


def views(m):
    m.part('camera', None, [3.38125, 12.15625, 11.525])
    m.part('views', None, [0, 0, 0])
    m.part('idle_view', 'views', [3.38125, 12.15625, 12.525])
    m.part('iron_view', 'views', [0, EYE_Y, 12.5])
    m.part('refit_view', 'views', [25, 9, 0], [0, 89.9, 0])
    m.part('positioning', None, [0, 0, -8])
    m.part('thirdperson_hand', 'positioning', [0, 6.525, 7.65])
    m.part('ground', 'positioning', [0, -0.9, 0.65])
    m.part('fixed', 'positioning', [0, 6.6, 5.6], [0, 90, 0])


def build_action(m):
    a = m.part('action', ID, [0, 8.2, 3.2])
    # boxlock body, with rounded fences around the breech ends of the barrels
    round_bar(a, 'z', (-0.98, 7.0, BREECH_Z + 0.02), (0.98, 9.42, 4.8), 'case', r=0.3, corners=(1, 1, 1, 1),
              data={'decal': 'action'})
    for sx in (BX, -BX):
        octagon(a, 'z', (sx, BORE_Y), 0.66, BREECH_Z + 0.02, BREECH_Z + 0.42, 'case', sides=16)
    disc_x(a, HINGE[1], HINGE[2] + 0.1, 0.5, -0.94, 0.94, 'case', sides=16)          # hinge-pin knuckle
    a.bar(-0.94, 0.94, 7.0, 7.6, HINGE[2] + 0.1, BREECH_Z + 0.4, 'case')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.98, sgn * 1.03))
        disc_x(a, HINGE[1], HINGE[2] + 0.1, 0.16, x0, x1, 'steel')                   # pin head
        disc_x(a, 8.0, 4.15, 0.11, x0, x1, 'steel')                                  # hammer axle
    # top strap and trigger plate running back into the wrist
    round_bar(a, 'z', (-0.38, 9.0, 4.6), (0.38, 9.4, 6.9), 'case', r=0.14, corners=(1, 1, 0, 0), sides=8)
    round_bar(a, 'z', (-0.34, 6.82, 4.6), (0.34, 7.08, 6.6), 'case', r=0.1, corners=(0, 0, 1, 1), sides=8)
    # trigger guard
    guard = [(6.95, 2.9)] + arc_pts(6.4, 3.45, 0.55, 180, 270, 3) + [(5.85, 4.95)] + arc_pts(6.4, 4.95, 0.55, 270, 350, 3) \
        + [(6.85, 6.1)]
    path_yz(a, guard, 0.2, -0.22, 0.22, 'steel')
    t = m.part('trigger', ID, [0, 6.95, 3.7])
    for z0 in (3.7, 4.45):
        path_yz(t, [(7.0, z0)] + arc_pts(6.55, z0 + 0.42, 0.55, 140, 205, 3), 0.15, -0.14, 0.14, 'steel')
    # top lever (swings to the right to open) and safety slide
    lv = m.part('lever', ID, [0, 9.45, 4.9])
    seg_yz(lv, (9.48, 4.75), (9.5, 5.9), 0.18, -0.2, 0.2, 'steel')
    lv.box((-0.62, 9.38, 5.65), (-0.05, 9.6, 6.05), 'steel', pivot=[-0.3, 9.5, 5.85], rotation=[0, -22, 0],
           data={'decal': 'knurl'})
    a.bar(-0.12, 0.12, 9.38, 9.5, 6.25, 6.6, 'steel', data={'decal': 'knurl'})
    # external hammers, cocked
    for sx, name in ((0.5, 'hammer_l'), (-0.5, 'hammer_r')):
        h = m.part(name, ID, [sx, 8.0, 4.15])
        x0, x1 = sx - 0.12, sx + 0.12
        seg_yz(h, (8.0, 4.15), (9.48, 4.52), 0.42, x0, x1, 'steel')
        path_yz(h, [(9.4, 4.5), (9.72, 4.8), (9.82, 5.2), (9.76, 5.55)], 0.24, x0 - 0.05, x1 + 0.05, 'steel',
                data={'decal': 'spur'})


def build_stock(m):
    """The wrist runs straight back from the action; below it the stock flares down to a short, sawn-off butt."""
    s = m.part('stock', ID, [0, 8.15, 4.8], [-4, 0, 0])
    round_bar(s, 'z', (-0.56, 7.0, 4.55), (0.56, 9.2, 11.0), 'walnut', r=0.36, corners=(1, 1, 0, 0),
              data={'decal': 'wrist'})
    # the lower flare: one slab whose bottom edge slopes from behind the guard down to the toe
    seg_yz(s, (7.45, 6.3), (6.45, 11.0), 1.7, -0.6, 0.6, 'walnut', data={'decal': 'wrist'})
    disc_x(s, 7.0, 6.45, 0.45, -0.6, 0.6, 'walnut', sides=16)                          # soft start of the belly
    round_bar(s, 'z', (-0.6, 6.95, 4.55), (0.6, 7.3, 6.6), 'walnut', r=0.25, corners=(0, 0, 1, 1), sides=8)
    # sawn face, flat across the back
    s.bar(-0.6, 0.6, 5.62, 9.1, 10.98, 11.06, 'walnut', data={'decal': 'butt'})
    s.bar(-0.48, 0.48, 9.12, 9.3, 4.55, 10.9, 'walnut')
    disc_x(s, 7.75, 8.0, 0.12, -0.63, 0.63, 'steel')                                    # stock bolt


def build_barrels(m):
    b = m.part('barrels', ID, HINGE)
    for sx in (BX, -BX):
        octagon(b, 'z', (sx, BORE_Y), BR, MUZZLE_Z + 0.12, BREECH_Z, 'barrel', sides=16, data={'decal': 'tube'})
        octagon(b, 'z', (sx, BORE_Y), BR - 0.01, MUZZLE_Z, MUZZLE_Z + 0.12, 'raw', sides=16, data={'decal': 'muzzle'})
    # ribs, lump and hinge hook under the breech
    round_bar(b, 'z', (-0.26, BORE_Y + 0.5, MUZZLE_Z + 0.02), (0.26, RIB_TOP, BREECH_Z), 'barrel', r=0.05,
              corners=(1, 1, 0, 0), sides=8, data={'decal': 'rib'})
    b.bar(-0.24, 0.24, BORE_Y - 0.74, BORE_Y - 0.4, MUZZLE_Z + 0.4, BREECH_Z - 0.1, 'barrel')
    b.bar(-0.5, 0.5, 7.92, BORE_Y - 0.3, -0.6, BREECH_Z, 'barrel')
    disc_x(b, HINGE[1] + 0.05, HINGE[2], 0.36, -0.5, 0.5, 'barrel', sides=16)
    # brass bead
    octagon(b, 'y', (0, MUZZLE_Z + 0.4), 0.09, RIB_TOP - 0.02, SIGHT_Y, 'brass', sides=8)
    # walnut fore-end with a rounded tip and its iron
    round_bar(b, 'z', (-0.86, 7.25, -4.0), (0.86, BORE_Y - 0.45, 0.7), 'walnut', r=0.42, corners=(0, 0, 1, 1),
              data={'decal': 'forend'})
    layered(b, (-0.84, 7.3, -4.65), (0.84, BORE_Y - 0.45, -3.6), 0.5, (0, 0, 1, 0), 'walnut')
    round_bar(b, 'z', (-0.7, 7.3, 0.6), (0.7, BORE_Y - 0.5, 1.25), 'case', r=0.3, corners=(0, 0, 1, 1))
    m.part('muzzle_pos', 'barrels', [0, BORE_Y, MUZZLE_Z])
    # extractor and the two shells in the chambers
    ex = m.part('extractor', 'barrels', [0, BORE_Y - 0.35, BREECH_Z])
    ex.bar(-0.42, 0.42, BORE_Y - 0.62, BORE_Y - 0.12, BREECH_Z - 0.3, BREECH_Z + 0.02, 'steel')
    for name, sx in (('shell_1', BX), ('shell_2', -BX)):
        sh = m.part(name, 'extractor', [sx, BORE_Y, BREECH_Z])
        octagon(sh, 'z', (sx, BORE_Y), 0.47, BREECH_Z - 0.02, BREECH_Z + 0.07, 'brass', sides=16, data={'decal': 'head'})
        octagon(sh, 'z', (sx, BORE_Y), 0.44, BREECH_Z - 0.45, BREECH_Z - 0.02, 'brass', sides=16)
        octagon(sh, 'z', (sx, BORE_Y), 0.42, BREECH_Z - 2.9, BREECH_Z - 0.45, 'hull', sides=16)


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_action(m)
    build_stock(m)
    build_barrels(m)
    views(m)
    return m


BASE = {
    'case': M.case_hardened, 'barrel': M.worn_blue, 'raw': M.raw_steel, 'walnut': M.walnut, 'steel': M.stainless,
    'brass': M.brass, 'hull': M.shell_hull,
}


def shader(p, n, face, c, uv, wh):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    N = len(x)
    d = c.data.get('decal')
    side = abs(n[0]) > 0.5
    mat = c.mat
    if mat == 'arm':
        return arm_colour(p, c)
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'muzzle' and face == 'north':
        holes = M.disc(x, y, BX, BORE_Y, 0.4) | M.disc(x, y, -BX, BORE_Y, 0.4)
        col = np.where(holes[:, None], np.array([[12, 12, 13]]), col)
    if d == 'action' and side:
        cut = M.scrollwork(y, z, 8.85, seed=3 if n[0] > 0 else 5) & (y > 8.35)
        col = np.where(cut[:, None], col * 0.55, col)
        if n[0] > 0:
            t = M.text_mask(y, z, 'LUPARA', 2.2, 8.05, 7.0 / K, reverse=True)
        else:
            t = M.text_mask(y, z, 'CORVARA', 4.6, 8.05, 7.0 / K)
        col = np.where(t[:, None], M.gold(p, n), col)
    if d == 'tube':
        # a little bright wear along the top of each tube
        col = col * (1.0 + 0.12 * np.clip((y - BORE_Y - 0.35) * 3, 0, 1))[:, None]
    if d == 'rib' and face == 'up':
        col = col * M.grooves(z, 0.12, 0.4, 0.72)[:, None]
    if d in ('wrist', 'forend') and side:
        inner = (z > (5.2 if d == 'wrist' else -3.6)) & (z < (8.6 if d == 'wrist' else 0.2))
        col = col * np.where(inner, M.checker(y, z, 0.25, 0.22, 0.72), 1.0)[:, None]
    if d == 'butt' and face == 'south':
        # sawn end grain: rings around the pith, with saw marks
        r = np.sqrt((y - 7.2) ** 2 * 1.4 + x ** 2 * 3.0)
        rings = 0.84 + 0.16 * np.sin(r * 18 + M.fbm(p, 3, 2, 1) * 4)
        col = np.array([[150, 104, 66]]) * rings[:, None] * (0.9 + 0.1 * M.grooves(y + x * 0.2, 0.09, 0.5, 0.8))[:, None]
    if d == 'knurl':
        col = col * M.checker(z, x, 0.08, 0.3, 0.6)[:, None]
    if d == 'spur' and face in ('up', 'south'):
        col = col * M.grooves(z + y, 0.08, 0.4, 0.6)[:, None]
    if d == 'head' and face == 'south':
        primer = M.disc(x, y, BX, BORE_Y, 0.13) | M.disc(x, y, -BX, BORE_Y, 0.13)
        col = np.where(primer[:, None], M.copper(p, n) * 1.1, col)
    metal = mat in ('case', 'barrel', 'raw', 'steel', 'brass')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
