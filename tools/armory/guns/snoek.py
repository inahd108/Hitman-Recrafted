"""Snoek — a compact 9 mm submachine gun with an integral suppressor.

A squat stamped-steel receiver in dark pike green with riveted side plates, a fat matte-black
suppressor that runs the full length of the barrel (the barrel is ported inside it), a clamp ring
with a vertical grip under the can, the magazine in the pistol grip, a flip aperture rear sight and
a tall hooded post on the can, a T charging handle at the back and a collapsed wire stock.

Coordinates follow TACZ's own compact PDW (as the Halcyon does) so its two-handed hold fits: right
hand on the pistol grip, left hand on the grip under the can; the magazine and left hand share a bone.
"""
import math

import numpy as np

import materials as M
from common import arm_colour
from geomodel import Model, arc_pts, disc_x, octagon, path_yz, round_bar, seg_yz

ID = 'snoek'
K = 14
BORE_Y = 7.1
CAN_R = 1.22
CAN_Z0, CAN_Z1 = -15.0, -4.45      # integral suppressor (front, rear)
MUZZLE_Z = CAN_Z0 - 0.02
SIGHT_Y = 9.78
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
    """TACZ's PDW hold, exactly as the Halcyon has it."""
    m.part('root', None, [0, 5.5, -1])
    m.part('gun_and_righthand', 'root', [0, 5.5, -1])
    m.part('mag_and_lefthand', 'root', [0, 3, -1])
    g = m.part(ID, 'gun_and_righthand', [0, 5.5, -1])
    off = np.array([-7, -12.25, -2.25])
    m.part('righthand', 'gun_and_righthand', list(np.array([6, 16, 0]) + off), [95.5035, 5.5421, -170.9956])
    rh = m.part('righthand_pos', 'righthand', list(np.array([0, 5, 0]) + off))
    lo = np.array([4, 5, -2]) + off
    rh.box(list(lo), list(lo + [4, 12, 4]), 'arm', data={'k': 2})
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
    m.part('refit_extended_mag_view', 'view', [14, -2, -2], [0, 90, 5])
    m.part('positioning', None, [0, 0, -8])
    m.part('thirdperson_hand', 'positioning', [0, 5.75, -2.15])
    m.part('ground', 'positioning', [0, -3, 0])
    m.part('fixed', 'positioning', [0, 6.11563, -3.75], [0, 90, 0])


def build_receiver(m):
    u = m.part('upper', ID, [0, 7.5, -1])
    # squat stamped receiver, rounded along the top
    round_bar(u, 'z', (-0.92, 5.55, -4.75), (0.92, 9.0, 3.9), 'pike', r=0.45, corners=(1, 1, 0, 0), sides=8,
              data={'decal': 'receiver'})
    # pressed side plates with rivets, both sides
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.92, sgn * 0.97))
        u.bar(x0, x1, 6.0, 8.35, -4.3, -2.75, 'pike', data={'decal': 'plate'})
        u.bar(x0, x1, 6.0, 8.35, 0.55, 3.4, 'pike', data={'decal': 'plate'})
        for (ry, rz) in ((6.25, -4.05), (8.1, -4.05), (6.25, -3.0), (8.1, -3.0), (6.25, 3.15), (8.1, 3.15)):
            xa, xb = sorted((sgn * 0.96, sgn * 1.02))
            disc_x(u, ry, rz, 0.09, xa, xb, 'steel', sides=8)
    # rear cap with the T charging handle above it
    layered(u, (-0.92, 5.55, 3.75), (0.92, 9.0, 4.45), 0.45, (1, 1, 0, 0), 'pike', step=0.1)
    # ejection port on the right with the bolt behind it
    u.bar(-0.95, -0.92, 6.75, 7.75, -2.4, -0.3, 'black')
    b = m.part('bolt', ID, [0, BORE_Y, -1.3])
    b.bar(-0.94, -0.88, 6.85, 7.65, -2.3, -0.4, 'steel', data={'decal': 'bolt'})
    ch = m.part('bolt_pull', ID, [0, 9.4, 4.6])
    ch.bar(-0.18, 0.18, 8.95, 9.45, 3.95, 4.7, 'steel')
    round_bar(ch, 'x', (-0.85, 9.25, 4.45), (0.85, 9.75, 4.85), 'black', r=0.18, sides=8, data={'decal': 'knurl'})
    # flip aperture rear sight with protective ears
    sg = m.part('sight', 'upper', [0, 9.0, 2.3])
    sg.bar(-0.45, 0.45, 8.95, 9.2, 1.9, 2.75, 'black')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.3, sgn * 0.45))
        sg.bar(x0, x1, 9.1, SIGHT_Y + 0.35, 2.2, 2.55, 'black')
    for k in range(12):
        a = 2 * math.pi * k / 12
        cx, cy = math.cos(a) * 0.2, SIGHT_Y + math.sin(a) * 0.2
        sg.box((cx - 0.06, cy - 0.06, 2.3), (cx + 0.06, cy + 0.06, 2.45), 'black')
    sg.bar(-0.3, 0.3, 9.15, SIGHT_Y - 0.24, 2.3, 2.45, 'black')


def build_can(m):
    """The integral suppressor: one fat tube from the receiver face to the muzzle."""
    c = m.part('can', ID, [0, BORE_Y, -9])
    octagon(c, 'z', (0, BORE_Y), CAN_R, CAN_Z0 + 0.35, CAN_Z1, 'can', sides=16, data={'decal': 'can'})
    octagon(c, 'z', (0, BORE_Y), CAN_R + 0.05, CAN_Z0, CAN_Z0 + 0.35, 'can', sides=16, data={'decal': 'cap'})
    octagon(c, 'z', (0, BORE_Y), CAN_R + 0.06, CAN_Z1 - 0.25, CAN_Z1 + 0.15, 'steel', sides=16)      # mount collar
    for zc in (-12.3,):
        octagon(c, 'z', (0, BORE_Y), CAN_R + 0.03, zc - 0.12, zc + 0.12, 'steel', sides=16)           # seam bands
    octagon(c, 'z', (0, BORE_Y), 0.17, CAN_Z0 - 0.02, CAN_Z0, 'bore', sides=8)
    # tall hooded front post on the can
    top = BORE_Y + CAN_R - 0.06
    c.bar(-0.42, 0.42, top, top + 0.3, -14.5, -13.7, 'black')
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.3, sgn * 0.42))
        c.bar(x0, x1, top + 0.25, SIGHT_Y + 0.25, -14.4, -13.8, 'black')
    c.bar(-0.42, 0.42, SIGHT_Y + 0.18, SIGHT_Y + 0.28, -14.4, -13.8, 'black')
    c.bar(-0.06, 0.06, top + 0.25, SIGHT_Y, -14.15, -14.0, 'black')
    c.bar(-0.045, 0.045, SIGHT_Y - 0.1, SIGHT_Y - 0.01, -14.16, -14.0, 'paint')
    # clamp ring and vertical grip under the can (the left hand holds it)
    fg = m.part('foregrip', ID, [0, 5.9, -9.9])
    octagon(fg, 'z', (0, BORE_Y), CAN_R + 0.12, -10.95, -8.85, 'poly', sides=16, data={'decal': 'clamp'})
    fg.bar(-0.5, 0.5, 5.4, 6.2, -10.75, -9.05, 'poly')
    round_bar(fg, 'y', (-0.45, 1.3, -10.45), (0.45, 5.6, -9.35), 'poly', r=0.34, sides=8, data={'decal': 'fgrip'})
    for yc in (4.5, 3.4, 2.3):
        octagon(fg, 'x', (yc, -9.3), 0.14, -0.38, 0.38, 'poly')                  # finger ridges, rear face
    round_bar(fg, 'y', (-0.52, 1.1, -10.55), (0.52, 1.45, -9.25), 'poly', r=0.2, sides=8)
    disc_x(fg, 5.8, -9.9, 0.16, -0.55, 0.55, 'steel', sides=8)


def build_lower(m):
    lw = m.part('lower', ID, [0, 5.5, -2])
    round_bar(lw, 'z', (-0.84, 4.95, -4.6), (0.84, 5.7, 3.9), 'pike', r=0.25, corners=(0, 0, 1, 1), sides=8,
              data={'decal': 'lower'})
    # trigger guard and trigger
    guard = [(4.95, -4.2)] + arc_pts(4.35, -3.55, 0.6, 180, 270, 3) + [(3.75, -2.3)] + [(4.3, -1.6)]
    path_yz(lw, guard, 0.24, -0.28, 0.28, 'pike')
    t = m.part('trigger', ID, [0, 5.0, -3.1])
    path_yz(t, [(5.0, -3.0)] + arc_pts(4.35, -2.4, 0.7, 130, 205, 3), 0.18, -0.13, 0.13, 'steel')
    # three-position selector (both sides)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.84, sgn * 0.92))
        disc_x(lw, 5.35, -1.0, 0.2, x0, x1, 'steel', sides=8, data={'decal': 'selector'})
    # pistol grip, raked back, the magazine well inside it
    g = m.part('grip', ID, GRIP_PIV, [GRIP_DEG, 0, 0])
    layered(g, (-0.62, 1.15, -1.9), (0.62, 5.4, 0.55), 0.42, (0, 1, 1, 0), 'poly', data={'decal': 'grip'})
    for yc in (3.9, 2.9, 1.95):
        octagon(g, 'x', (yc, -1.9), 0.13, -0.5, 0.5, 'poly')                      # finger ridges
    # collapsed wire stock: two rods into a bent-wire butt with a rubber pad
    st = m.part('stock', ID, [0, 6.5, 4.4])
    for y in (5.6, 8.4):
        octagon(st, 'z', (0, y), 0.2, 3.9, 7.0, 'steel', sides=8)
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * 0.5, sgn * 0.72))
        st.bar(x0, x1, 3.6, 9.0, 6.85, 7.15, 'steel')
        seg_yz(st, (3.7, 7.0), (5.6, 6.0), 0.22, x0, x1, 'steel')
    st.bar(-0.72, 0.72, 8.75, 9.05, 6.6, 7.15, 'steel')
    st.bar(-0.66, 0.66, 3.4, 9.1, 7.15, 7.45, 'rubber')


def build():
    m = Model(ID, tex_size=1024, texels_per_unit=K)
    rig(m)
    build_receiver(m)
    build_can(m)
    build_lower(m)
    mag = m.part('magazine', 'mag_and_lefthand', [0, 3, -1])
    for name, bottom in (('mag_standard', MAG_BOTTOM), ('mag_extended_1', MAG_BOTTOM - 0.9),
                         ('mag_extended_2', MAG_BOTTOM - 1.8), ('mag_extended_3', MAG_BOTTOM - 2.7)):
        mb = m.part(name, 'magazine', GRIP_PIV, [GRIP_DEG, 0, 0])
        mb.bar(-0.42, 0.42, bottom + 0.3, 4.8, -1.55, 0.2, 'blued', data={'k': 4})          # hidden in the grip
        layered(mb, (-0.56, bottom, -1.75), (0.56, bottom + 0.42, 0.4), 0.16, (0, 1, 1, 0), 'steel', step=0.06,
                data={'decal': 'baseplate'})
    views(m)
    return m


def pike(p, n):
    """Dark pike-green stamped steel: a phosphate finish with a faint mottle."""
    return M.parkerized(p, n) * np.array([[0.72, 0.84, 0.7]])


BASE = {
    'pike': pike, 'can': lambda p, n: M.matte_black(p, n) * 1.25, 'black': M.matte_black, 'steel': M.blued,
    'blued': M.blued, 'poly': lambda p, n: M.polymer(p, n, stipple=False), 'rubber': M.rubber,
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
    if mat == 'paint':
        return M.finish(M.rgba(np.tile([[226, 214, 120]], (N, 1))))
    col = BASE[mat](p, n) if mat in BASE else np.tile([[255, 0, 255]], (N, 1)).astype(float)
    if d == 'receiver' and side:
        seam = (np.abs(y - 6.0) < 0.03) | (np.abs(z - 0.25) < 0.03)
        col = np.where(seam[:, None], col * 0.7, col)
        if n[0] > 0:
            t = M.text_mask(y, z, 'SNOEK', -2.35, 8.25, 7.0 / K, reverse=True)
            col = np.where(t[:, None], col * 1.6, col)
    if d == 'plate' and side:
        edge = (np.abs(y - 6.0) < 0.05) | (np.abs(y - 8.35) < 0.05)
        col = np.where(edge[:, None], col * 0.75, col * 1.04)
    if d == 'can' and not (abs(n[2]) > 0.5):
        # a fish down the left side of the can: the pike that names the gun
        if n[0] > 0.3:
            dz, dy = z + 6.75, y - BORE_Y
            body = (dz / 1.6) ** 2 + (dy / 0.32) ** 2 < 1
            tail = (dz > 1.45) & (dz < 2.0) & (np.abs(dy) < (dz - 1.45) * 0.75)
            fin = (dz > -0.2) & (dz < 0.7) & (dy > 0.2) & (dy < 0.2 + (0.7 - dz) * 0.35)
            eye = M.disc(z, y, -7.95, BORE_Y + 0.08, 0.05)
            fish = (body | tail | fin) & ~eye
            col = np.where(fish[:, None], np.array([[104, 122, 96]]), col)
        stripe = (np.mod(z + 0.25, 1.5) < 0.05) & (z > CAN_Z0 + 0.6) & (z < CAN_Z1 - 0.5)
        col = np.where(stripe[:, None], col * 0.8, col)
    if d == 'cap' and face == 'north':
        ring = M.disc(x, y, 0, BORE_Y, 0.85) & ~M.disc(x, y, 0, BORE_Y, 0.65)
        col = np.where(ring[:, None], col * 0.6, col)
        holes = np.zeros(N, dtype=bool)
        for k in range(6):
            a = 2 * math.pi * k / 6
            holes |= M.disc(x, y, math.cos(a) * 0.45, BORE_Y + math.sin(a) * 0.45, 0.07)
        col = np.where(holes[:, None], col * 0.3, col)
    if d == 'clamp' and not (abs(n[2]) > 0.5):
        col = col * M.grooves(z, 0.35, 0.25, 0.7)[:, None]
    if d in ('grip', 'fgrip') and side:
        col = col * (0.92 + 0.14 * (M.vnoise(p, 46) > 0.55))[:, None]
    if d == 'knurl':
        col = col * M.checker(x, y, 0.1, 0.3, 0.7)[:, None]
    if d == 'baseplate' and side:
        col = col * M.grooves(z, 0.2, 0.3, 0.75)[:, None]
    if d == 'selector' and side:
        col = col * np.where(np.abs(y - 5.35) < 0.04, 0.55, 1.0)[:, None]
    metal = mat in ('steel', 'blued', 'pike')
    col = M.bake(col, c.data['wn'], metal=metal)
    return M.finish(M.rgba(col))
