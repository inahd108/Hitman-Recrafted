"""Halcyon PDW — the lab security's compact personal defence weapon.

An off-white polymer shroud over the barrel with a teal band and the company name, a graphite lower with
the magazine in the pistol grip, a folding vertical foregrip, a hooded ring front sight and rear aperture
on a raised rail, a T charging handle at the back and a collapsed telescoping stock.

Coordinates follow TACZ's own compact PDW so its two-handed hold fits: right hand on the pistol grip,
left hand on the foregrip; the magazine and left hand share a bone, as in the pistol rig.
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'halcyon'
K = 14
BORE_Y = 7.1
MUZZLE_Z = -13.0
SIGHT_Y = 11.69
GRIP_PIV = [0, 5.3, -0.7]
GRIP_DEG = 9.0
MAG_BOTTOM = 0.2
FP_CAM = ((-2.5, 12.25, 11), (-2.5, 11.0, -20), 60)       # preview only: TACZ's hip camera


def layered(part, lo, hi, r, corners, mat, step=0.12, **kw):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    round_bar(part, 'x', (x0 + step, y0, z0), (x1 - step, y1, z1), mat, r=r, corners=corners, **kw)
    iy0 = y0 + (step if corners[1] or corners[2] else 0)
    iy1 = y1 - (step if corners[0] or corners[3] else 0)
    iz0 = z0 + (step if corners[2] or corners[3] else 0)
    iz1 = z1 - (step if corners[0] or corners[1] else 0)
    round_bar(part, 'x', (x0, iy0, iz0), (x1, iy1, iz1), mat, r=max(0.05, r - step), corners=corners, **kw)


def rig(m):
    m.part('root', None, [0, 5.5, -1])
    m.part('gun_and_righthand', 'root', [0, 5.5, -1])
    m.part('mag_and_lefthand', 'root', [0, 3, -1])
    g = m.part(ID, 'gun_and_righthand', [0, 5.5, -1])
    # right hand on the pistol grip (TACZ's PDW hand pose baked into the rest pose)
    off = np.array([-7, -12.25, -2.25])
    m.part('righthand', 'gun_and_righthand', list(np.array([6, 16, 0]) + off), [95.5035, 5.5421, -170.9956])
    rh = m.part('righthand_pos', 'righthand', list(np.array([0, 5, 0]) + off))
    lo = np.array([4, 5, -2]) + off
    rh.box(list(lo), list(lo + [4, 12, 4]), 'arm', data={'k': 2})
    # left hand on the foregrip
    off = np.array([6.75, -12.5, -9.75])
    m.part('lefthand', 'mag_and_lefthand', list(np.array([-6, 16, 0]) + off), [100, -16, -200])
    lh = m.part('lefthand_pos', 'lefthand', list(np.array([0, 5, 0]) + off))
    lo = np.array([-8, 5, -2]) + off
    lh.box(list(lo), list(lo + [4, 12, 4]), 'arm', data={'k': 2})
    m.part('muzzle_flash', ID, [0, BORE_Y, MUZZLE_Z - 0.4])
    m.part('shell', ID, [-0.6, BORE_Y + 0.3, -0.8])
    m.part('constraint', ID, [0, 11.6875, -9.5375])
    return g


def views(m):
    m.part('view', None, [0, 0, 0])
    m.part('idle_view', 'view', [2.5, 12.25, 11], [0, 0, -5])
    m.part('camera', 'idle_view', [2.5, 12.25, 11])
    m.part('iron_view', 'view', [0, SIGHT_Y, 10])
    m.part('refit_view', 'view', [24, 7, 0], [0, 89.95, 0])
    m.part('refit_muzzle_view', 'view', [10, 7.5, -19], [180, 70, 180])
    m.part('refit_extended_mag_view', 'view', [14, -2, -2], [0, 90, 5])
    m.part('positioning', None, [0, 0, -8])
    m.part('thirdperson_hand', 'positioning', [0, 5.75, -2.15])
    m.part('ground', 'positioning', [0, -3, 0])
    m.part('fixed', 'positioning', [0, 6.11563, -3.75], [0, 90, 0])


def build_upper(m):
    u = m.part('upper', ID, [0, 7.5, -3])
    # slim vented barrel shroud at the front ...
    round_bar(u, 'z', (-0.78, 6.35, -11.0), (0.78, 8.65, -5.2), 'white', r=0.5, sides=8, data={'decal': 'front'})
    layered(u, (-0.78, 6.35, -11.45), (0.78, 8.65, -10.6), 0.6, (1, 0, 1, 1), 'white', step=0.1)
    round_bar(u, 'z', (-0.8, 6.3, -8.7), (0.8, 8.7, -8.1), 'teal', r=0.52, sides=8)
    # ... rising through a sloped shoulder into the taller receiver
    seg_yz(u, (8.2, -6.0), (8.95, -4.3), 1.0, -0.86, 0.86, 'white', data={'decal': 'front'})
    seg_yz(u, (6.4, -6.2), (6.2, -4.3), 0.6, -0.86, 0.86, 'white')
    round_bar(u, 'z', (-0.95, 5.95, -5.0), (0.95, 9.4, 4.4), 'white', r=0.5, sides=8, data={'decal': 'receiver'})
    layered(u, (-0.95, 5.95, 3.6), (0.95, 9.4, 4.55), 0.6, (1, 1, 0, 0), 'white', step=0.1)
    # sight rail along the top, on a slim riser over the shroud
    round_bar(u, 'z', (-0.42, 9.32, -4.6), (0.42, 9.9, 3.9), 'graphite', r=0.16, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    u.bar(-0.24, 0.24, 8.6, 9.75, -10.6, -4.5, 'graphite')
    round_bar(u, 'z', (-0.3, 9.6, -10.6), (0.3, 9.9, -4.5), 'graphite', r=0.1, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'rail'})
    # front sight: a ring hood around the post
    for k in range(14):
        a = 2 * math.pi * k / 14
        cx, cy = math.cos(a) * 0.42, SIGHT_Y - 0.08 + math.sin(a) * 0.42
        u.box((cx - 0.08, cy - 0.08, -10.45), (cx + 0.08, cy + 0.08, -10.15), 'graphite')
    u.bar(-0.18, 0.18, 9.85, SIGHT_Y - 0.42, -10.45, -10.15, 'graphite')
    u.bar(-0.05, 0.05, 9.9, SIGHT_Y - 0.02, -10.35, -10.25, 'graphite')
    u.bar(-0.05, 0.05, SIGHT_Y - 0.12, SIGHT_Y - 0.02, -10.36, -10.24, 'teal')
    # rear sight: an aperture ring on a post
    for k in range(12):
        a = 2 * math.pi * k / 12
        cx, cy = math.cos(a) * 0.3, SIGHT_Y + math.sin(a) * 0.3
        u.box((cx - 0.07, cy - 0.07, 2.2), (cx + 0.07, cy + 0.07, 2.45), 'graphite')
    u.bar(-0.32, 0.32, 9.85, SIGHT_Y - 0.33, 2.15, 2.5, 'graphite')
    # muzzle: a short ported flash hider out of the shroud's nose
    octagon(u, 'z', (0, BORE_Y), 0.32, MUZZLE_Z, -11.3, 'black', sides=16, data={'decal': 'hider'})
    octagon(u, 'z', (0, BORE_Y), 0.16, MUZZLE_Z - 0.01, MUZZLE_Z + 0.02, 'bore', sides=8)
    m.part('muzzle_pos', 'upper', [0, BORE_Y, MUZZLE_Z])
    # ejection port on the right with the bolt behind it
    u.bar(-0.97, -0.94, 6.85, 7.75, -2.4, -0.3, 'black')
    b = m.part('bolt', ID, [0, BORE_Y, -1.3])
    b.bar(-0.96, -0.9, 6.95, 7.65, -2.3, -0.4, 'steel', data={'decal': 'bolt'})
    # T charging handle at the back
    ch = m.part('bolt_pull', ID, [0, 9.7, 4.6])
    ch.bar(-0.18, 0.18, 9.4, 9.8, 3.8, 4.75, 'graphite')
    round_bar(ch, 'x', (-0.9, 9.35, 4.55), (0.9, 9.9, 4.95), 'graphite', r=0.18, sides=8, data={'decal': 'knurl'})


def build_lower(m):
    lw = m.part('lower', ID, [0, 5.5, -2])
    round_bar(lw, 'z', (-0.82, 5.0, -7.8), (0.82, 6.3, 3.9), 'graphite', r=0.3, corners=(0, 0, 1, 1), sides=8, data={'decal': 'poly'})
    # trigger guard and trigger
    guard = [(5.0, -4.2)] + arc_pts(4.35, -3.55, 0.65, 180, 270, 3) + [(3.7, -2.3)] + [(4.3, -1.6)]
    path_yz(lw, guard, 0.26, -0.3, 0.3, 'graphite')
    t = m.part('trigger', ID, [0, 5.0, -3.1])
    path_yz(t, [(5.0, -3.0)] + arc_pts(4.35, -2.4, 0.7, 130, 205, 3), 0.18, -0.13, 0.13, 'steel')
    # selector (both sides)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.82, sgn * 0.9))
        disc_x(lw, 5.75, -0.9, 0.18, x0, x1, 'teal', sides=8)
    # pistol grip, raked back, the magazine well inside it
    g = m.part('grip', ID, GRIP_PIV, [GRIP_DEG, 0, 0])
    layered(g, (-0.62, 1.15, -1.9), (0.62, 5.4, 0.55), 0.42, (0, 1, 1, 0), 'graphite', data={'decal': 'grip'})
    for yc in (3.9, 2.9, 1.95):
        octagon(g, 'x', (yc, -1.9), 0.13, -0.5, 0.5, 'graphite')                # finger ridges
    # folding vertical foregrip, unfolded
    fg = m.part('foregrip', ID, [0, 6.0, -9.9])
    fg.bar(-0.55, 0.55, 5.7, 6.45, -10.7, -9.1, 'graphite')                       # hinge block
    round_bar(fg, 'y', (-0.45, 1.3, -10.45), (0.45, 5.8, -9.35), 'graphite', r=0.34, sides=8, data={'decal': 'fgrip'})
    for yc in (4.5, 3.4, 2.3):
        octagon(fg, 'x', (yc, -9.3), 0.14, -0.38, 0.38, 'graphite')               # finger ridges, rear face
    disc_x(fg, 6.05, -9.9, 0.2, -0.6, 0.6, 'steel', sides=8)                     # hinge pin
    # collapsed telescoping stock: two rods and a butt pad
    st = m.part('stock', ID, [0, 6.5, 4.4])
    for y in (5.35, 8.6):
        octagon(st, 'z', (0, y), 0.22, 3.9, 6.9, 'steel', sides=8)
    layered(st, (-0.82, 2.6, 6.8), (0.82, 9.3, 7.6), 0.4, (1, 1, 1, 1), 'graphite')
    st.bar(-0.72, 0.72, 2.7, 9.2, 7.55, 7.75, 'rubber')


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_upper(m)
    build_lower(m)
    mag = m.part('magazine', 'mag_and_lefthand', [0, 3, -1])
    for name, bottom in (('mag_standard', MAG_BOTTOM), ('mag_extended_1', MAG_BOTTOM - 0.9),
                         ('mag_extended_2', MAG_BOTTOM - 1.8), ('mag_extended_3', MAG_BOTTOM - 2.7)):
        mb = m.part(name, 'magazine', GRIP_PIV, [GRIP_DEG, 0, 0])
        mb.bar(-0.42, 0.42, bottom + 0.3, 5.2, -1.55, 0.2, 'black', data={'k': 4})        # hidden in the grip
        layered(mb, (-0.55, bottom, -1.75), (0.55, bottom + 0.42, 0.4), 0.16, (0, 1, 1, 0), 'teal' if name == 'mag_standard' else 'graphite',
                step=0.06, data={'decal': 'baseplate'})
    views(m)
    return m


BASE = {
    'white': M.lab_white, 'teal': M.teal, 'graphite': lambda p, n: M.polymer(p, n, stipple=False) * 0.78,
    'black': M.matte_black, 'steel': M.parkerized, 'rubber': M.rubber,
}


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
    if d in ('front', 'receiver') and side:
        seam = (np.abs(y - 6.62) < 0.03) & (z < -5.4) if d == 'front' else (np.abs(z - 0.9) < 0.035) & (y > 6.2)
        col = np.where(seam[:, None], col * 0.72, col)
    if d == 'front' and side:
        vents = (z > -7.6) & (z < -5.6) & (np.mod(z * 2.2, 1.0) < 0.42) & (y > 7.0) & (y < 8.2)
        col = np.where(vents[:, None], np.array([[30, 32, 36]]), col)
    if d == 'receiver' and side:
        if n[0] > 0:
            t = M.text_mask(y, z, 'HALCYON', -3.4, 8.9, 7.0 / K, reverse=True)
            ring = M.disc(z, y, -4.0, 8.62, 0.3) & ~M.disc(z, y, -4.0, 8.62, 0.19) | M.disc(z, y, -4.0, 8.62, 0.08)
        else:
            t = M.text_mask(y, z, 'HALCYON', 1.6, 8.9, 7.0 / K)
            ring = M.disc(z, y, 2.2, 8.62, 0.3) & ~M.disc(z, y, 2.2, 8.62, 0.19) | M.disc(z, y, 2.2, 8.62, 0.08)
        col = np.where((t | ring)[:, None], M.teal(p, n), col)
        stripe = (y > 6.25) & (y < 6.4) & (z > -4.6) & (z < 3.9)
        col = np.where(stripe[:, None], M.teal(p, n) * 0.95, col)
    if d in ('front', 'receiver') and face == 'up':
        col = col * 0.97
    if d == 'rail' and face == 'up':
        col = col * M.grooves(z, 0.32, 0.5, 0.65)[:, None]
    if d == 'hider' and not side and face not in ('north', 'south'):
        col = col * M.grooves(z, 0.3, 0.35, 0.4)[:, None]
    if d == 'hider' and side:
        col = col * M.grooves(z, 0.3, 0.35, 0.4)[:, None]
    if d in ('grip', 'fgrip', 'poly') and side:
        col = col * (0.95 + 0.1 * (M.vnoise(p, 46) > 0.55))[:, None]
    if d == 'knurl':
        col = col * M.checker(x, y, 0.1, 0.3, 0.7)[:, None]
    if d == 'baseplate' and side:
        col = col * M.grooves(z, 0.2, 0.3, 0.75)[:, None]
    metal = mat in ('black', 'steel')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
